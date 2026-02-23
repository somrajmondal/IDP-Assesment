from flask import Blueprint, jsonify, request
from pydantic import ValidationError

from app.db.database import SessionLocal
from app.models.models import DocumentType
from app.schemas.schemas import DocumentTypeCreate, DocumentTypeOut, DocumentTypeUpdate

bp = Blueprint("admin", __name__)


@bp.get("/document-types")
def list_document_types():
    db = SessionLocal()
    try:
        rows = db.query(DocumentType).order_by(DocumentType.id).all()
        payload = [DocumentTypeOut.model_validate(item, from_attributes=True).model_dump(mode="json") for item in rows]
        return jsonify(payload)
    finally:
        db.close()


@bp.post("/document-types")
def create_document_type():
    db = SessionLocal()
    try:
        try:
            doc_type = DocumentTypeCreate.model_validate(request.get_json(silent=True) or {})
        except ValidationError as exc:
            return jsonify({"detail": exc.errors()}), 422

        existing = db.query(DocumentType).filter(
            DocumentType.document_backend_key == doc_type.document_backend_key
        ).first()
        if existing:
            return jsonify({"detail": "Backend key already exists"}), 400
        db_dt = DocumentType(**doc_type.model_dump())
        db.add(db_dt)
        db.commit()
        db.refresh(db_dt)
        payload = DocumentTypeOut.model_validate(db_dt, from_attributes=True).model_dump(mode="json")
        return jsonify(payload), 201
    finally:
        db.close()


@bp.get("/document-types/<int:dt_id>")
def get_document_type(dt_id: int):
    db = SessionLocal()
    try:
        dt = db.query(DocumentType).filter(DocumentType.id == dt_id).first()
        if not dt:
            return jsonify({"detail": "Not found"}), 404
        payload = DocumentTypeOut.model_validate(dt, from_attributes=True).model_dump(mode="json")
        return jsonify(payload)
    finally:
        db.close()


@bp.put("/document-types/<int:dt_id>")
def update_document_type(dt_id: int):
    db = SessionLocal()
    try:
        dt = db.query(DocumentType).filter(DocumentType.id == dt_id).first()
        if not dt:
            return jsonify({"detail": "Not found"}), 404

        try:
            update = DocumentTypeUpdate.model_validate(request.get_json(silent=True) or {})
        except ValidationError as exc:
            return jsonify({"detail": exc.errors()}), 422

        for k, v in update.model_dump(exclude_none=True).items():
            setattr(dt, k, v)
        db.commit()
        db.refresh(dt)
        payload = DocumentTypeOut.model_validate(dt, from_attributes=True).model_dump(mode="json")
        return jsonify(payload)
    finally:
        db.close()


@bp.delete("/document-types/<int:dt_id>")
def delete_document_type(dt_id: int):
    db = SessionLocal()
    try:
        dt = db.query(DocumentType).filter(DocumentType.id == dt_id).first()
        if not dt:
            return jsonify({"detail": "Not found"}), 404
        db.delete(dt)
        db.commit()
        return jsonify({"message": "Document type deleted"})
    finally:
        db.close()


@bp.post("/seed")
def seed_data():
    db = SessionLocal()
    try:
        """Seed the database with example document types from the provided JSON structure."""
        from app.models.models import Entity, Template

        passport = DocumentType(
            document_name="Passport",
            document_backend_key="passport",
            features="Feature of passport",
            is_active=True,
        )
        db.add(passport)
        db.flush()

        p_tmpl = Template(
            document_type_id=passport.id,
            template_name="Standard Passport",
            description="Government-issued personal identification for travel and citizenship verification.",
            describe_document="Purpose: Government-issued personal identification for travel and citizenship verification. Key Features: Contains a photo, passport number, name, nationality, issue date, expiration date, and government seals or holograms.",
            keywords="passport",
            is_active=True,
        )
        db.add(p_tmpl)
        db.flush()

        passport_entities = [
            {
                "entity_name": "Expiry date (Passport)",
                "backend_entity_key": "passport_expiry_date",
                "entity_data_type": "AlphaNumeric",
                "entity_description": "The date on which the passport will expire.",
            },
            {
                "entity_name": "Place of birth",
                "backend_entity_key": "place_of_birth",
                "entity_data_type": "AlphaNumeric",
                "entity_description": "The place where the passport holder was born.",
            },
            {
                "entity_name": "Customer Name (as per Passport)",
                "backend_entity_key": "customer_name_passport",
                "entity_data_type": "Alphabet",
                "entity_description": "Full name exactly as it appears in the passport.",
            },
            {
                "entity_name": "Date of Birth",
                "backend_entity_key": "date_of_birth",
                "entity_data_type": "Date",
                "entity_description": "Date of birth of the passport holder.",
            },
            {
                "entity_name": "Passport Document (Number)",
                "backend_entity_key": "passport_number",
                "entity_data_type": "AlphaNumeric",
                "entity_description": "Passport number, alphanumeric, max 9 characters.",
            },
        ]
        for ent in passport_entities:
            db.add(
                Entity(
                    template_id=p_tmpl.id,
                    entity_name=ent["entity_name"],
                    backend_entity_key=ent["backend_entity_key"],
                    entity_data_type=ent["entity_data_type"],
                    entity_description=ent["entity_description"],
                    entity_key_customer_type="Individual",
                    entity_key_rp_type="Individual-RP",
                    is_active=True,
                )
            )

        eid = DocumentType(
            document_name="Emirates ID",
            document_backend_key="emirates_id",
            features="Feature of Emirates ID",
            is_active=True,
        )
        db.add(eid)
        db.flush()

        eid_tmpl = Template(
            document_type_id=eid.id,
            template_name="Standard Emirates ID",
            description="UAE national identification card used for official verification.",
            keywords="Identity Card, Resident Identity Card, Gold Card",
            is_active=True,
        )
        db.add(eid_tmpl)
        db.flush()

        eid_entities = [
            {
                "entity_name": "Emirates ID (Number)",
                "backend_entity_key": "emirates_id_number",
                "entity_data_type": "Numeric",
                "entity_description": "ID number on the Emirates ID card, max 15 digits.",
            },
            {
                "entity_name": "Expiry date (EID)",
                "backend_entity_key": "eid_expiry_date",
                "entity_data_type": "Date",
                "entity_description": "Date when the Emirates ID expires.",
            },
            {
                "entity_name": "Issuance date (EID)",
                "backend_entity_key": "eid_issuance_date",
                "entity_data_type": "Date",
                "entity_description": "Date when the Emirates ID was issued.",
            },
            {
                "entity_name": "Country of Residency",
                "backend_entity_key": "country_of_residency",
                "entity_data_type": "Alphabet",
                "entity_description": "Cardholder's country of residence.",
            },
        ]
        for ent in eid_entities:
            db.add(
                Entity(
                    template_id=eid_tmpl.id,
                    entity_name=ent["entity_name"],
                    backend_entity_key=ent["backend_entity_key"],
                    entity_data_type=ent["entity_data_type"],
                    entity_description=ent["entity_description"],
                    entity_key_customer_type="Individual",
                    entity_key_rp_type="Individual-RP",
                    is_active=True,
                )
            )

        sc = DocumentType(
            document_name="Salary Certificate",
            document_backend_key="salary_certificate",
            features="Feature of Salary Certificate",
            is_active=True,
        )
        db.add(sc)
        db.flush()

        sc_tmpl = Template(
            document_type_id=sc.id,
            template_name="Standard Salary Certificate",
            description="Proof of income issued by an employer.",
            keywords="SC",
            is_active=True,
        )
        db.add(sc_tmpl)
        db.flush()
        db.add(
            Entity(
                template_id=sc_tmpl.id,
                entity_name="Employer Name",
                backend_entity_key="employer_name",
                entity_data_type="AlphaNumeric",
                entity_description="Name of the company employing the individual.",
                entity_key_customer_type="Individual",
                entity_key_rp_type="Individual-RP",
                is_active=True,
            )
        )

        db.commit()
        return jsonify({"message": "Seed data inserted successfully"})
    finally:
        db.close()
