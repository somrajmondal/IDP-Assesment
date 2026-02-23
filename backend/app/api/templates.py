import os

from flask import Blueprint, jsonify, request
from pydantic import ValidationError

from app.api.process import build_template_json
from app.db.database import SessionLocal
from app.models.models import DocumentType, Entity, Template
from app.schemas.schemas import (
    EntityCreate,
    EntityOut,
    EntityUpdate,
    TemplateCreate,
    TemplateOut,
    TemplateUpdate,
)

bp = Blueprint("templates", __name__)
TEMPLATE_FILES_DIR = "template_files"
os.makedirs(TEMPLATE_FILES_DIR, exist_ok=True)


@bp.get("/")
def list_templates():
    db = SessionLocal()
    try:
        document_type_id = request.args.get("document_type_id", type=int)
        q = db.query(Template)
        if document_type_id:
            q = q.filter(Template.document_type_id == document_type_id)
        payload = [TemplateOut.model_validate(item, from_attributes=True).model_dump(mode="json") for item in q.all()]
        return jsonify(payload)
    finally:
        db.close()


@bp.post("/")
def create_template():
    db = SessionLocal()
    try:
        try:
            template = TemplateCreate.model_validate(request.get_json(silent=True) or {})
        except ValidationError as exc:
            return jsonify({"detail": exc.errors()}), 422

        doc_type = db.query(DocumentType).filter(DocumentType.id == template.document_type_id).first()
        if not doc_type:
            return jsonify({"detail": "Document type not found"}), 404
        db_tmpl = Template(**template.model_dump())
        db.add(db_tmpl)
        db.commit()
        db.refresh(db_tmpl)
        payload = TemplateOut.model_validate(db_tmpl, from_attributes=True).model_dump(mode="json")
        return jsonify(payload), 201
    finally:
        db.close()


@bp.get("/<int:template_id>")
def get_template(template_id: int):
    db = SessionLocal()
    try:
        tmpl = db.query(Template).filter(Template.id == template_id).first()
        if not tmpl:
            return jsonify({"detail": "Template not found"}), 404
        payload = TemplateOut.model_validate(tmpl, from_attributes=True).model_dump(mode="json")
        return jsonify(payload)
    finally:
        db.close()


@bp.put("/<int:template_id>")
def update_template(template_id: int):
    db = SessionLocal()
    try:
        tmpl = db.query(Template).filter(Template.id == template_id).first()
        if not tmpl:
            return jsonify({"detail": "Template not found"}), 404
        try:
            update = TemplateUpdate.model_validate(request.get_json(silent=True) or {})
        except ValidationError as exc:
            return jsonify({"detail": exc.errors()}), 422
        for k, v in update.model_dump(exclude_none=True).items():
            setattr(tmpl, k, v)
        db.commit()
        db.refresh(tmpl)
        payload = TemplateOut.model_validate(tmpl, from_attributes=True).model_dump(mode="json")
        return jsonify(payload)
    finally:
        db.close()


@bp.delete("/<int:template_id>")
def delete_template(template_id: int):
    db = SessionLocal()
    try:
        tmpl = db.query(Template).filter(Template.id == template_id).first()
        if not tmpl:
            return jsonify({"detail": "Template not found"}), 404
        db.delete(tmpl)
        db.commit()
        return jsonify({"message": "Template deleted"})
    finally:
        db.close()


@bp.post("/<int:template_id>/upload-sample")
def upload_sample_file(template_id: int):
    db = SessionLocal()
    try:
        tmpl = db.query(Template).filter(Template.id == template_id).first()
        if not tmpl:
            return jsonify({"detail": "Template not found"}), 404
        file = request.files.get("file")
        if not file:
            return jsonify({"detail": "No file uploaded"}), 400
        path = os.path.join(TEMPLATE_FILES_DIR, f"template_{template_id}_{file.filename}")
        file.save(path)
        tmpl.sample_file_path = path
        db.commit()
        return jsonify({"path": path})
    finally:
        db.close()


@bp.get("/<int:template_id>/json-preview")
def get_template_json(template_id: int):
    db = SessionLocal()
    try:
        tmpl = db.query(Template).filter(Template.id == template_id).first()
        if not tmpl:
            return jsonify({"detail": "Template not found"}), 404
        doc_type = db.query(DocumentType).filter(DocumentType.id == tmpl.document_type_id).first()

        return jsonify(
            {
                "document_type": doc_type.document_backend_key if doc_type else None,
                "document_name": doc_type.document_name if doc_type else None,
                "template_id": tmpl.id,
                "template_name": tmpl.template_name,
                "description": tmpl.description,
                "describe_document": tmpl.describe_document,
                "keywords": tmpl.keywords,
                "is_active": tmpl.is_active,
                "entities": [
                    {
                        "entity_name_for_t24": getattr(e, "entity_name_for_t24", None),
                        "entity_name_for_dms": e.entity_name_for_dms,
                        "entity_key_customer_type": e.entity_key_customer_type,
                        "entity_key_rp_type": getattr(e, "entity_key_rp_type", None),
                        "entity_context": e.entity_context,
                        "entity_data_type": e.entity_data_type,
                        "backend_entity_key": e.backend_entity_key,
                        "entity_description": e.entity_description,
                        "is_active": e.is_active,
                    }
                    for e in tmpl.entities
                    if e.is_active
                ],
            }
        )
    finally:
        db.close()


@bp.get("/json-preview/all")
def get_all_templates_json():
    db = SessionLocal()
    try:
        return jsonify(build_template_json(db=db))
    finally:
        db.close()


@bp.post("/<int:template_id>/entities")
def add_entity(template_id: int):
    db = SessionLocal()
    try:
        tmpl = db.query(Template).filter(Template.id == template_id).first()
        if not tmpl:
            return jsonify({"detail": "Template not found"}), 404
        try:
            entity = EntityCreate.model_validate(request.get_json(silent=True) or {})
        except ValidationError as exc:
            return jsonify({"detail": exc.errors()}), 422
        db_entity = Entity(template_id=template_id, **entity.model_dump())
        db.add(db_entity)
        db.commit()
        db.refresh(db_entity)
        payload = EntityOut.model_validate(db_entity, from_attributes=True).model_dump(mode="json")
        return jsonify(payload), 201
    finally:
        db.close()


@bp.put("/entities/<int:entity_id>")
def update_entity(entity_id: int):
    db = SessionLocal()
    try:
        entity = db.query(Entity).filter(Entity.id == entity_id).first()
        if not entity:
            return jsonify({"detail": "Entity not found"}), 404
        try:
            update = EntityUpdate.model_validate(request.get_json(silent=True) or {})
        except ValidationError as exc:
            return jsonify({"detail": exc.errors()}), 422
        for k, v in update.model_dump(exclude_none=True).items():
            setattr(entity, k, v)
        db.commit()
        db.refresh(entity)
        payload = EntityOut.model_validate(entity, from_attributes=True).model_dump(mode="json")
        return jsonify(payload)
    finally:
        db.close()


@bp.delete("/entities/<int:entity_id>")
def delete_entity(entity_id: int):
    db = SessionLocal()
    try:
        entity = db.query(Entity).filter(Entity.id == entity_id).first()
        if not entity:
            return jsonify({"detail": "Entity not found"}), 404
        db.delete(entity)
        db.commit()
        return jsonify({"message": "Entity deleted"})
    finally:
        db.close()
