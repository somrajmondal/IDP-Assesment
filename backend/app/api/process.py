import json
import logging
import os
import threading
from typing import Any, Optional

import requests
from flask import Blueprint, jsonify, request
from pydantic import ValidationError

from app.db.database import SessionLocal
from app.models.models import DocumentFile, DocumentType, ExtractionResult, Folder, Template
from app.schemas.schemas import ProcessRequest

bp = Blueprint("process", __name__)
logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {"tiff", "tif", "pdf", "jpg", "jpeg", "png"}
MIME_TYPES = {
    "tiff": "image/tiff",
    "tif": "image/tiff",
    "pdf": "application/pdf",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "png": "image/png",
}


def _serialize_template(template: Template) -> dict:
    entities = [
        {
            "template": {
                "file": template.sample_file_path or "",
                "description": template.description or "",
                "description_for_non_individual": template.description_for_non_individual or "",
                "describe_document": template.describe_document or "",
                "keywords": template.keywords or "",
                "is_active": template.is_active,
                "is_complete": template.is_complete,
            },
            "entity_name": e.entity_name,
            "entity_name_for_dms": e.entity_name_for_dms or e.entity_name,
            "entity_key_customer_type": e.entity_key_customer_type,
            "entity_context": e.entity_context or {},
            "entity_data_type": e.entity_data_type,
            "backend_entity_key": e.backend_entity_key,
            "entity_description": e.entity_description or "",
            "is_active": e.is_active,
        }
        for e in template.entities
        if e.is_active
    ]
    return {"template_id": template.id, "entities": entities}


def build_template_json(db, template_id: Optional[int] = None) -> list[dict]:
    doc_types = db.query(DocumentType).order_by(DocumentType.id).all()
    payload: list[dict] = []

    for doc_type in doc_types:
        active_templates = [t for t in doc_type.templates if t.is_active]
        if template_id is not None:
            active_templates = [t for t in active_templates if t.id == template_id]
        if not active_templates:
            continue

        payload.append(
            {
                "id": doc_type.id,
                "document_name": doc_type.document_name,
                "document_backend_key": doc_type.document_backend_key,
                "features": doc_type.features or "",
                "templates": [_serialize_template(t) for t in active_templates],
            }
        )

    return payload


def _call_llm(file_path: str, filename: str, template_json: Any, llm_url: str) -> dict:
    file_ext = filename.rsplit(".", 1)[-1].lower()
    mime = MIME_TYPES.get(file_ext, "application/octet-stream")

    with open(file_path, "rb") as f:
        files_payload = [("files", (filename, f, mime))]
        data_payload = {"json": json.dumps(template_json)}
        response = requests.post(llm_url, files=files_payload, data=data_payload, timeout=120)

    logger.info("LLM status=%s file=%s", response.status_code, filename)
    return response.json()


def _parse_llm_response(resp_json: dict) -> dict:
    extracted = resp_json.get("extracted_data")
    if isinstance(extracted, dict):
        return extracted
    if resp_json and all(str(k).isdigit() for k in resp_json.keys()):
        return resp_json
    logger.warning("Unexpected LLM response keys: %s", list(resp_json.keys()))
    return {"1": {"classification": {}, "extraction": []}}


def process_files_task(folder_id: int, template_id: Optional[int], llm_url: str):
    db = SessionLocal()
    try:
        folder = db.query(Folder).filter(Folder.id == folder_id).first()
        if not folder:
            return

        folder.status = "processing"
        db.commit()

        template_json = build_template_json(db=db, template_id=template_id)
        if not template_json:
            logger.error("No active templates found for folder %s", folder_id)
            folder.status = "failed"
            db.commit()
            return

        for doc_file in folder.files:
            if not doc_file.file_path or not os.path.exists(doc_file.file_path):
                logger.warning("Missing on disk: %s", doc_file.file_path)
                doc_file.status = "failed"
                db.commit()
                continue

            file_ext = (doc_file.file_type or "").lower()
            if file_ext not in ALLOWED_EXTENSIONS:
                logger.warning("Skipping unsupported type .%s: %s", file_ext, doc_file.original_filename)
                doc_file.status = "failed"
                db.commit()
                continue

            doc_file.status = "processing"
            db.commit()

            try:
                raw_response = _call_llm(
                    file_path=doc_file.file_path,
                    filename=doc_file.original_filename,
                    template_json=template_json,
                    llm_url=llm_url,
                )

                page_results = _parse_llm_response(raw_response)
                for page_key, page_data in page_results.items():
                    try:
                        page_num = int(page_key)
                    except (ValueError, TypeError):
                        page_num = 1

                    classification = page_data.get("classification", {}) if isinstance(page_data, dict) else {}
                    extraction = page_data.get("extraction", []) if isinstance(page_data, dict) else []

                    db.add(
                        ExtractionResult(
                            document_file_id=doc_file.id,
                            page_number=page_num,
                            classification=classification,
                            extracted_entities=extraction,
                            raw_response=raw_response,
                            confidence_score=classification.get("score") if classification else None,
                            model_used=classification.get("technique", "openai") if classification else "openai",
                            status="completed",
                        )
                    )

                doc_file.status = "completed"
            except Exception as exc:
                err = f"Failed to process {doc_file.original_filename}: {exc}"
                logger.error(err)
                db.add(
                    ExtractionResult(
                        document_file_id=doc_file.id,
                        page_number=1,
                        raw_response={"error": err},
                        status="failed",
                        error_message=err,
                    )
                )
                doc_file.status = "failed"

            db.commit()

        statuses = [f.status for f in folder.files]
        if statuses and all(s == "completed" for s in statuses):
            folder.status = "completed"
        elif statuses and all(s == "failed" for s in statuses):
            folder.status = "failed"
        else:
            folder.status = "completed"
        db.commit()
        logger.info("Folder %s finished with status: %s", folder_id, folder.status)
    finally:
        db.close()


@bp.post("/")
def start_processing():
    db = SessionLocal()
    try:
        try:
            req = ProcessRequest.model_validate(request.get_json(silent=True) or {})
        except ValidationError as exc:
            return jsonify({"detail": exc.errors()}), 422

        folder = db.query(Folder).filter(Folder.id == req.folder_id).first()
        if not folder:
            return jsonify({"detail": "Folder not found"}), 404
        if folder.status == "processing":
            return jsonify({"detail": "Already processing"}), 400

        llm_url = req.llm_endpoint or "http://127.0.0.1:5002/up_doc"
        thread = threading.Thread(
            target=process_files_task,
            args=(req.folder_id, req.template_id, llm_url),
            daemon=True,
        )
        thread.start()

        return jsonify({"message": "Processing started", "folder_id": req.folder_id, "llm_url": llm_url})
    finally:
        db.close()


@bp.get("/folder/<int:folder_id>/results")
def get_folder_results(folder_id: int):
    db = SessionLocal()
    try:
        folder = db.query(Folder).filter(Folder.id == folder_id).first()
        if not folder:
            return jsonify({"detail": "Folder not found"}), 404

        results = []
        for doc_file in folder.files:
            extractions = db.query(ExtractionResult).filter(
                ExtractionResult.document_file_id == doc_file.id
            ).all()
            results.append(
                {
                    "file_id": doc_file.id,
                    "filename": doc_file.original_filename,
                    "status": doc_file.status,
                    "extractions": [
                        {
                            "page": e.page_number,
                            "classification": e.classification,
                            "entities": e.extracted_entities,
                            "confidence": e.confidence_score,
                            "model": e.model_used,
                            "error": e.error_message,
                        }
                        for e in extractions
                    ],
                }
            )

        return jsonify(
            {"folder_id": folder_id, "folder_name": folder.name, "status": folder.status, "files": results}
        )
    finally:
        db.close()


@bp.get("/folder/<int:folder_id>/download-json")
def download_folder_json(folder_id: int):
    db = SessionLocal()
    try:
        folder = db.query(Folder).filter(Folder.id == folder_id).first()
        if not folder:
            return jsonify({"detail": "Folder not found"}), 404

        results = []
        for doc_file in folder.files:
            extractions = db.query(ExtractionResult).filter(
                ExtractionResult.document_file_id == doc_file.id
            ).all()
            results.append(
                {
                    "file_name": doc_file.original_filename,
                    "status": doc_file.status,
                    "pages": [
                        {
                            "page": e.page_number,
                            "classification": e.classification,
                            "extraction": e.extracted_entities,
                        }
                        for e in extractions
                    ],
                }
            )

        response = jsonify(
            {"folder_name": folder.name, "processed_at": str(folder.updated_at), "files": results}
        )
        response.headers["Content-Disposition"] = f"attachment; filename={folder.name}_results.json"
        return response
    finally:
        db.close()


@bp.get("/debug-payload/template/<int:template_id>")
def debug_template_payload(template_id: int):
    db = SessionLocal()
    try:
        template = (
            db.query(Template).filter(Template.id == template_id, Template.is_active.is_(True)).first()
        )
        if not template:
            return jsonify({"detail": "Template not found"}), 404

        payload = build_template_json(db=db, template_id=template_id)
        return jsonify(
            {
                "note": "This dict is JSON-serialised and sent as the form field 'json'",
                "form_field_name": "json",
                "form_field_value": payload,
                "serialised_preview": json.dumps(payload)[:400] + "...",
            }
        )
    finally:
        db.close()


@bp.post("/debug-call/folder/<int:folder_id>")
def debug_call_llm(folder_id: int):
    db = SessionLocal()
    try:
        folder = db.query(Folder).filter(Folder.id == folder_id).first()
        if not folder:
            return jsonify({"detail": "Folder not found"}), 404
        if not folder.files:
            return jsonify({"detail": "Folder has no files"}), 400

        doc_file = folder.files[0]
        if not doc_file.file_path or not os.path.exists(doc_file.file_path):
            return jsonify({"detail": "First file not found on disk"}), 400

        llm_url = "http://127.0.0.1:5002/up_doc"
        template_json = build_template_json(db=db)
        if not template_json:
            return jsonify({"detail": "No active templates found"}), 400

        try:
            raw = _call_llm(doc_file.file_path, doc_file.original_filename, template_json, llm_url)
            parsed = _parse_llm_response(raw)
            return jsonify(
                {
                    "file": doc_file.original_filename,
                    "llm_url": llm_url,
                    "raw_response": raw,
                    "parsed_pages": parsed,
                    "page_count": len(parsed),
                }
            )
        except Exception as exc:
            return jsonify({"detail": f"LLM call failed: {exc}"}), 502
    finally:
        db.close()
