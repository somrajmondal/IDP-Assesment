# DocuScan – Document Digitization Platform

A full-stack AI-powered document processing platform with dynamic template management.

## 🏗️ Project Structure

```
doc-digitization/
├── backend/                  # FastAPI Python backend
│   ├── app/
│   │   ├── api/              # Route handlers
│   │   │   ├── admin.py      # Document types CRUD
│   │   │   ├── documents.py  # File & extraction results
│   │   │   ├── folders.py    # Folder management & file upload
│   │   │   ├── process.py    # LLM processing pipeline
│   │   │   └── templates.py  # Templates & entities CRUD
│   │   ├── db/
│   │   │   └── database.py   # SQLAlchemy DB setup
│   │   ├── models/
│   │   │   └── models.py     # DB models (all tables)
│   │   ├── schemas/
│   │   │   └── schemas.py    # Pydantic request/response schemas
│   │   └── main.py           # FastAPI app entry point
│   ├── requirements.txt
│   └── run.sh
│
└── frontend/                 # React + TypeScript frontend
    ├── src/
    │   ├── components/
    │   │   └── common/
    │   │       ├── Layout.tsx     # App shell with sidebar nav
    │   │       └── Layout.css
    │   ├── pages/
    │   │   ├── Dashboard.tsx      # Main processing dashboard
    │   │   ├── Dashboard.css
    │   │   ├── FolderDetail.tsx   # 2-panel folder view
    │   │   ├── FolderDetail.css
    │   │   └── admin/
    │   │       ├── AdminLayout.tsx
    │   │       ├── AdminDocumentTypes.tsx  # Document type CRUD
    │   │       ├── AdminTemplates.tsx      # Template + entity CRUD
    │   │       └── Admin.css
    │   ├── store/
    │   │   └── appStore.ts    # Zustand state management
    │   ├── utils/
    │   │   └── api.ts         # Axios API client
    │   ├── App.tsx
    │   ├── main.tsx
    │   └── index.css          # Global styles
    ├── package.json
    ├── vite.config.ts
    └── index.html
```

## 🚀 Setup & Run

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API docs available at: http://localhost:8000/docs

### Frontend

```bash
cd frontend
npm install
npm run dev
```

App available at: http://localhost:3000

### Seed Sample Data

After starting both servers, go to **Admin > Document Types** and click **Seed Sample Data** to load the Passport, Emirates ID, and Salary Certificate templates from the provided JSON structure.

## 🔑 Key Features

### User Flow
1. **Dashboard** – Create folders, upload up to 5 files per folder
2. **Process** – Click Process to send files + template JSON to your LLM endpoint
3. **Folder Detail** – 2-panel view: left shows files, right shows extracted entities
4. **Download** – Get ZIP of all uploaded files or JSON of all extracted data

### Admin Panel
1. **Document Types** – Create/edit/delete document categories (Passport, Emirates ID, etc.)
2. **Templates** – Manage templates per document type with description, keywords
3. **Entities** – Add/edit/delete extraction fields with:
   - Entity name (T24 & DMS)
   - Backend key
   - Data type (Alphabet, AlphaNumeric, Numeric, Date, etc.)
   - Customer type
   - LLM description prompt
4. **JSON Preview** – See the exact JSON that gets sent to the LLM backend

### LLM Integration
- Connects to your existing LLM endpoint (default: `http://127.0.0.1:5002/up_remm1`)
- Sends multipart form: `files` + `json` (template data)
- Parses response format: `{"1": {"classification": {...}, "extraction": [...]}}`
- Stores results in DB, displays page-by-page in UI

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/folders/` | List all folders |
| POST | `/api/folders/` | Create folder |
| POST | `/api/folders/{id}/upload` | Upload files (max 5) |
| GET | `/api/folders/{id}/download-zip` | Download folder as ZIP |
| POST | `/api/process/` | Start LLM processing |
| GET | `/api/process/folder/{id}/results` | Get extraction results |
| GET | `/api/process/folder/{id}/download-json` | Download results JSON |
| GET | `/api/admin/document-types` | List document types |
| POST | `/api/admin/document-types` | Create document type |
| GET | `/api/templates/` | List templates |
| POST | `/api/templates/` | Create template |
| GET | `/api/templates/{id}/json-preview` | Get template JSON |
| POST | `/api/templates/{id}/entities` | Add entity |
| PUT | `/api/templates/entities/{id}` | Update entity |
| DELETE | `/api/templates/entities/{id}` | Delete entity |

## 🗄️ Database

Uses SQLite by default (stored as `doc_digitization.db`). Switch to PostgreSQL via env var:
```bash
DATABASE_URL=postgresql://user:pass@localhost/docdb
```

## 🔧 Configuration

Customize LLM endpoint when processing:
```json
{
  "folder_id": 1,
  "llm_endpoint": "http://your-llm-server/up_remm1"
}
```
