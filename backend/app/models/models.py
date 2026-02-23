from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class DocumentType(Base):
    __tablename__ = "document_types"

    id = Column(Integer, primary_key=True, index=True)
    document_name = Column(String(200), nullable=False)
    document_backend_key = Column(String(100), unique=True, nullable=False)
    features = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    templates = relationship("Template", back_populates="document_type", cascade="all, delete-orphan")


class Template(Base):
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, index=True)
    document_type_id = Column(Integer, ForeignKey("document_types.id"), nullable=False)
    template_name = Column(String(200))
    description = Column(Text)
    description_for_non_individual = Column(Text)
    describe_document = Column(Text)
    keywords = Column(String(500))
    sample_file_path = Column(String(500))
    version = Column(String(20), default="1.0")
    is_active = Column(Boolean, default=True)
    is_complete = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    document_type = relationship("DocumentType", back_populates="templates")
    entities = relationship("Entity", back_populates="template", cascade="all, delete-orphan")


class Entity(Base):
    __tablename__ = "entities"

    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("templates.id"), nullable=False)
    entity_name = Column(String(300))
    entity_name_for_dms = Column(String(300))
    entity_key_customer_type = Column(String(100))
    entity_context = Column(JSON, default={})
    entity_data_type = Column(String(50))
    backend_entity_key = Column(String(200))
    entity_description = Column(Text)
    example_value = Column(String(500))
    is_required = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    template = relationship("Template", back_populates="entities")


class Folder(Base):
    __tablename__ = "folders"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    document_type_id = Column(Integer, ForeignKey("document_types.id"), nullable=True)
    status = Column(String(50), default="pending")  # pending, processing, completed, failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    document_type = relationship("DocumentType")
    files = relationship("DocumentFile", back_populates="folder", cascade="all, delete-orphan")


class DocumentFile(Base):
    __tablename__ = "document_files"

    id = Column(Integer, primary_key=True, index=True)
    folder_id = Column(Integer, ForeignKey("folders.id"), nullable=False)
    filename = Column(String(500), nullable=False)
    original_filename = Column(String(500))
    file_path = Column(String(1000))
    file_type = Column(String(50))
    file_size = Column(Integer)
    page_count = Column(Integer, default=1)
    status = Column(String(50), default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    folder = relationship("Folder", back_populates="files")
    extractions = relationship("ExtractionResult", back_populates="document_file", cascade="all, delete-orphan")


class ExtractionResult(Base):
    __tablename__ = "extraction_results"

    id = Column(Integer, primary_key=True, index=True)
    document_file_id = Column(Integer, ForeignKey("document_files.id"), nullable=False)
    page_number = Column(Integer, default=1)
    classification = Column(JSON)
    extracted_entities = Column(JSON)
    raw_response = Column(JSON)
    confidence_score = Column(Float)
    model_used = Column(String(100))
    status = Column(String(50), default="pending")
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    document_file = relationship("DocumentFile", back_populates="extractions")
