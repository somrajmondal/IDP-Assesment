import os

from flask import Blueprint, jsonify, send_file

from app.db.database import SessionLocal
from app.models.models import DocumentFile, ExtractionResult
from app.schemas.schemas import DocumentFileOut, ExtractionResultOut

bp = Blueprint("documents", __name__)


@bp.get("/<int:file_id>")
def get_file(file_id: int):
    db = SessionLocal()
    try:
        doc = db.query(DocumentFile).filter(DocumentFile.id == file_id).first()
        if not doc:
            return jsonify({"detail": "File not found"}), 404
        payload = DocumentFileOut.model_validate(doc, from_attributes=True).model_dump(mode="json")
        return jsonify(payload)
    finally:
        db.close()


@bp.get("/<int:file_id>/extractions")
def get_extractions(file_id: int):
    db = SessionLocal()
    try:
        records = db.query(ExtractionResult).filter(ExtractionResult.document_file_id == file_id).all()
        payload = [
            ExtractionResultOut.model_validate(item, from_attributes=True).model_dump(mode="json")
            for item in records
        ]
        return jsonify(payload)
    finally:
        db.close()


@bp.get("/<int:file_id>/download")
def download_file(file_id: int):
    db = SessionLocal()
    try:
        doc = db.query(DocumentFile).filter(DocumentFile.id == file_id).first()
        if not doc or not doc.file_path or not os.path.exists(doc.file_path):
            return jsonify({"detail": "File not found on disk"}), 404
        return send_file(doc.file_path, as_attachment=True, download_name=doc.original_filename)
    finally:
        db.close()


@bp.get("/<int:file_id>/json")
def get_extraction_json(file_id: int):
    db = SessionLocal()
    try:
        doc = db.query(DocumentFile).filter(DocumentFile.id == file_id).first()
        if not doc:
            return jsonify({"detail": "File not found"}), 404

        extractions = db.query(ExtractionResult).filter(
            ExtractionResult.document_file_id == file_id
        ).all()

        result = {
            "file_id": file_id,
            "filename": doc.original_filename,
            "status": doc.status,
            "pages": [],
        }
        for ext in extractions:
            result["pages"].append(
                {
                    "page": ext.page_number,
                    "classification": ext.classification,
                    "entities": ext.extracted_entities,
                    "confidence": ext.confidence_score,
                    "model": ext.model_used,
                }
            )
        return jsonify(result)
    finally:
        db.close()
