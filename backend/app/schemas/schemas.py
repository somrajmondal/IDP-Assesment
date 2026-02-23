from pydantic import BaseModel
from typing import Optional, List, Any, Dict
from datetime import datetime


# Entity Schemas
class EntityBase(BaseModel):
    entity_name: str
    entity_name_for_dms: Optional[str] = None
    entity_key_customer_type: Optional[str] = "Individual"
    entity_key_rp_type: Optional[str] = "Individual-RP"
    entity_context: Optional[Dict] = {}
    entity_data_type: Optional[str] = "AlphaNumeric"
    backend_entity_key: str
    entity_description: Optional[str] = None
    example_value: Optional[str] = None
    is_required: Optional[bool] = False
    is_active: Optional[bool] = True

class EntityCreate(EntityBase):
    pass

class EntityUpdate(BaseModel):
    entity_name: Optional[str] = None
    entity_name_for_dms: Optional[str] = None
    entity_data_type: Optional[str] = None
    backend_entity_key: Optional[str] = None
    entity_description: Optional[str] = None
    example_value: Optional[str] = None
    is_required: Optional[bool] = None
    is_active: Optional[bool] = None

class EntityOut(EntityBase):
    id: int
    template_id: int
    class Config:
        from_attributes = True


# Template Schemas
class TemplateBase(BaseModel):
    template_name: Optional[str] = None
    description: Optional[str] = None
    description_for_non_individual: Optional[str] = None
    describe_document: Optional[str] = None
    keywords: Optional[str] = None
    version: Optional[str] = "1.0"
    is_active: Optional[bool] = True

class TemplateCreate(TemplateBase):
    document_type_id: int

class TemplateUpdate(TemplateBase):
    pass

class TemplateOut(TemplateBase):
    id: int
    document_type_id: int
    sample_file_path: Optional[str] = None
    is_complete: bool
    created_at: datetime
    entities: List[EntityOut] = []
    class Config:
        from_attributes = True


# Document Type Schemas
class DocumentTypeBase(BaseModel):
    document_name: str
    document_backend_key: str
    features: Optional[str] = None
    is_active: Optional[bool] = True

class DocumentTypeCreate(DocumentTypeBase):
    pass

class DocumentTypeUpdate(BaseModel):
    document_name: Optional[str] = None
    features: Optional[str] = None
    is_active: Optional[bool] = None

class DocumentTypeOut(DocumentTypeBase):
    id: int
    created_at: datetime
    templates: List[TemplateOut] = []
    class Config:
        from_attributes = True


# Folder Schemas
class FolderCreate(BaseModel):
    name: str
    document_type_id: Optional[int] = None

class FolderUpdate(BaseModel):
    name: Optional[str] = None
    document_type_id: Optional[int] = None
    status: Optional[str] = None

class DocumentFileOut(BaseModel):
    id: int
    filename: str
    original_filename: Optional[str]
    file_path: Optional[str]
    file_type: Optional[str]
    file_size: Optional[int]
    page_count: int
    status: str
    created_at: datetime
    class Config:
        from_attributes = True

class FolderOut(BaseModel):
    id: int
    name: str
    document_type_id: Optional[int]
    status: str
    created_at: datetime
    updated_at: Optional[datetime]
    files: List[DocumentFileOut] = []
    class Config:
        from_attributes = True


# Extraction Result Schemas
class ExtractionResultOut(BaseModel):
    id: int
    document_file_id: int
    page_number: int
    classification: Optional[Dict]
    extracted_entities: Optional[List]
    confidence_score: Optional[float]
    model_used: Optional[str]
    status: str
    error_message: Optional[str]
    created_at: datetime
    class Config:
        from_attributes = True


# Process Schemas
class ProcessRequest(BaseModel):
    folder_id: int
    template_id: Optional[int] = None
    llm_endpoint: Optional[str] = "http://127.0.0.1:5002/up_doc"
