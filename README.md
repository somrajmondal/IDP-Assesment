📄 Intelligent Document Processing Software

Upload, process, and break down data barriers with AI to extract valuable information from documents.

An enterprise-grade AI Document Digitization Platform that automates document classification, data extraction, and structured output generation using configurable templates and an external LLM service.

🚀 Overview

This platform enables organizations to digitize, classify, and extract structured data from documents such as:

Passports

Emirates IDs

Salary Certificates


It provides a modern UI, admin-driven configuration, and LLM-powered intelligence while keeping the architecture modular and scalable.

✨ Core Features
📁 Document Management

Folder-based document organization

Upload up to 5 files per folder

Support for multi-page documents

ZIP download of original files

🧠 AI Processing

Automatic document classification

Entity extraction using dynamic templates

Page-wise extraction results

Confidence scoring per extracted field

🛠️ Admin Configuration

Document type management

Template creation per document type

Entity definition with:

Backend keys

Data types (Text, Numeric, Date, etc.)

Customer type

LLM prompt descriptions

Live JSON preview sent to AI engine

📤 Export Options

Download extracted data as JSON

Page-wise structured output

API-accessible extraction results

🏗️ System Architecture
Frontend (React + TypeScript)
        ↓
Backend API (FastAPI)
        ↓
External LLM Service
  • Document Classification
  • Entity Extraction

The AI engine is integrated as an external service, ensuring flexibility and easy replacement or scaling.

📁 Project Structure
doc-digitization/
├── backend/                  # FastAPI backend
│   ├── app/
│   │   ├── api/              # API routes
│   │   ├── models/           # Database models
│   │   ├── schemas/          # Request/response schemas
│   │   ├── db/               # Database configuration
│   │   └── main.py           # App entry point
│   └── requirements.txt
│
└── frontend/                 # React + TypeScript frontend
    ├── src/
    │   ├── components/       # Reusable UI components
    │   ├── pages/            # Dashboard & Admin views
    │   ├── store/            # State management
    │   ├── utils/            # API utilities
    │   └── App.tsx
    └── package.json

⚙️ Setup & Run
Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

API documentation available at:

http://localhost:8000/docs
Frontend
cd frontend
npm install
npm run dev

Application runs at:

http://localhost:3000
🧠 AI Processing Integration

The platform connects to an external AI/LLM service during document processing.

Processing Request Example
{
  "folder_id": 1,
  "llm_endpoint": "http://127.0.0.1:5002/up_doc"
}
Expected AI Response Format
{
  "1": {
    "classification": {
      "document_type": "Passport",
      "confidence": 0.97
    },
    "extraction": [
      {
        "entity": "passport_number",
        "value": "A12345678",
        "confidence": 0.93,
        "page": 1
      }
    ]
  }
}

🗄️ Database

Default: SQLite

Optional: PostgreSQL

DATABASE_URL=postgresql://user:password@localhost/docdb
🔐 Security & Scalability

Clean separation between UI, backend, and AI engine

Stateless AI processing

Easily deployable as microservices

Ready for cloud & enterprise environments

📌 Use Cases

Banking & KYC automation

HR document processing

Government ID digitization

Enterprise document indexing

Data migration & validation

