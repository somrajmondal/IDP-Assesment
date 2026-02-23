📄 Intelligent Document Processing (IDP) Platform

An enterprise-grade AI Document Digitization Platform that dynamically classifies documents, extracts structured data, and generates machine-readable outputs using configurable templates and an external LLM service — without any hardcoded logic.

🚀 Overview

This platform enables organizations to upload, classify, and extract structured information from documents such as:

Passports

Emirates IDs

Salary Certificates

Bank Statements

Invoices

Any custom document type (added dynamically)

The system is fully configurable via Admin UI, allowing document intelligence logic to evolve without redeployment or code changes.

✨ Core Capabilities
📁 Document Management

Folder-based document organization

Upload up to 5 files per folder

Multi-page document support

Page-wise processing & extraction

🧠 AI-Powered Processing

Prompt-based dynamic document classification

Entity extraction using admin-defined templates

Page-wise extraction results

Confidence scoring per extracted field

Stateless external LLM integration

🛠️ Fully Dynamic Admin Configuration (No Code Changes)

Admins can add, edit, or delete everything at runtime:

📄 Document Types

Define document name & description

Configure classification prompt

Add unlimited document types dynamically

📑 Templates

Multiple templates per document type

Support different layouts/formats

Enable/disable templates anytime

🧾 Entities

Each entity is fully configurable:

Entity name

Backend key

Data type (Text, Numeric, Date, Boolean, etc.)

Customer type (Individual / Non-Individual)

LLM prompt description

Runtime editable & removable

➡️ Nothing is hardcoded. Everything is prompt-driven.

🔁 Dynamic AI Execution Flow

Admin configures document types, templates & entities

Backend builds a live JSON schema

JSON + prompt sent to external LLM

LLM performs:

Document classification

Entity extraction

Structured output returned & stored

📤 Export & Integration

Download extracted data as JSON

Page-wise structured output

API-accessible extraction results

Ready for downstream systems

🏗️ System Architecture
Frontend (React + TypeScript)
        ↓
Backend API (FastAPI)
        ↓
External LLM Service
  • Document Classification
  • Entity Extraction

Clean separation of concerns

AI engine is pluggable & replaceable

Microservice-ready architecture

📁 Project Structure
doc-digitization/
├── backend/
│   ├── api/
│   ├── models/
│   ├── services/
│   └── main.py
│
├── frontend/
│   ├── src/
│   ├── components/
│   └── pages/
│
└── LLM/
    ├── main.py
    └── prompts/
⚙️ Setup & Run
Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

Backend runs at:

http://localhost:8000
Frontend
cd frontend
npm install
npm run dev

Frontend runs at:

http://localhost:3000
LLM Service
cd LLM
python main.py

LLM service runs at:

http://localhost:5002
🧠 AI Processing Integration
Processing Request
{
  "folder_id": 1,
  "llm_endpoint": "http://127.0.0.1:5002/up_doc"
}
Expected AI Response Format
{
  "classification": {
    "class_name": "Salary Certificate",
    "score": 1,
    "technique": "openai - level 1"
  },
  "confidence": 1,
  "entities": [
    {
      "backend_entity_key": "employer_name",
      "entity_name": "Employer Name",
      "entity_value": "Imaginorlabs Private Limited",
      "entity_data_type": "AlphaNumeric",
      "entity_description": "Name of the company employing the individual.",
      "entity_key_customer_type": "Individual",
      "model": "openai"
    }
  ],
  "page": 1,
  "error": null
}
🗄️ Database Configuration

Default:

SQLite

Production (Example):

DATABASE_URL=postgresql://user:password@localhost/docdb
🔐 Security & Scalability

Stateless AI processing

Clear separation between UI, Backend & AI

Easily deployable as microservices

Cloud & enterprise ready

Supports horizontal scaling

📌 Use Cases

Banking & KYC automation

HR document processing

Government ID digitization

Enterprise document indexing

Data migration & validation