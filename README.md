# 📄 Intelligent Document Processing (IDP) Platform

> An enterprise-grade AI Document Digitization Platform that dynamically classifies documents, extracts structured data, and generates machine-readable outputs — **without any hardcoded logic**.

![Python](https://img.shields.io/badge/Python-Flask-blue?logo=python) ![React](https://img.shields.io/badge/Frontend-React%20%2B%20TypeScript-61DAFB?logo=react) ![LLM](https://img.shields.io/badge/AI-LLM%20Powered-orange) ![License](https://img.shields.io/badge/License-MIT-green)

---

## 🚀 Overview

This platform enables organizations to upload, classify, and extract structured information from documents using a configurable AI pipeline. Everything — document types, templates, entities, and prompts — is managed through an Admin UI with **no redeployment required**.

### Supported Document Types

| Document | Example Fields |
|----------|----------------|
| Passport | Name, DOB, Expiry, Nationality |
| Emirates ID | ID Number, Name, Expiry |
| Salary Certificate | Employer, Salary, Issue Date |
| Bank Statement | Account, Transactions, Balance |
| Invoice | Vendor, Amount, Line Items |
| *Any custom type* | *Admin-defined at runtime* |

---

## ✨ Core Capabilities

### 📁 Document Management
- Folder-based document organization
- Upload up to 5 files per folder
- Multi-page document support with page-wise processing

### 🧠 AI-Powered Processing
- Prompt-based dynamic document classification
- Entity extraction using admin-defined templates
- Confidence scoring per extracted field
- Stateless, pluggable LLM integration

### 🛠️ Fully Dynamic Admin Configuration
Everything is runtime-configurable — no code changes needed:

- **Document Types** — Define name, description, and classification prompt
- **Templates** — Multiple layouts per document type; enable/disable anytime
- **Entities** — Name, backend key, data type, customer type, LLM prompt description

> ➡️ Nothing is hardcoded. Everything is prompt-driven.

---

## 🏗️ Architecture

```
Frontend (React + TypeScript)
        ↓
Backend API (FastAPI)
        ↓
External LLM Service
  • Document Classification
  • Entity Extraction
```

- **Clean separation of concerns** — UI configures, backend validates, AI executes
- **AI is an implementation detail** — swap models via environment variable only
- **Microservice-ready** — each layer is independently deployable

---

## 🔁 AI Execution Flow

```
1. Admin configures document types, templates & entities
2. Backend builds a live JSON schema at runtime
3. JSON schema + prompt sent to external LLM
4. LLM classifies the document and extracts entities
5. Output validated by backend before storage
```

---

## 📁 Project Structure

```
doc-digitization/
├── backend/
│   ├── api/
│   ├── models/
│   ├── services/
│   └── main.py
├── frontend/
│   ├── src/
│   ├── components/
│   └── pages/
└── LLM/
    ├── main.py
    └── prompts/
```

---

## ⚙️ Setup & Run

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
# Runs at http://localhost:8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
# Runs at http://localhost:3000
```

### LLM Service

```bash
cd LLM
python main.py
# Runs at http://localhost:5002
```

---

## 🧠 AI Integration Reference

### Processing Request

```json
{
  "folder_id": 1,
  "llm_endpoint": "http://127.0.0.1:5002/up_doc"
}
```

### Expected AI Response Format

```json
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
```

---

## 🗄️ Database Configuration

| Environment | Config |
|-------------|--------|
| Development | SQLite (default) |
| Production | `DATABASE_URL=postgresql://user:password@localhost/docdb` |

---

## 📤 Export & Integration

- Download extracted data as JSON
- Page-wise structured output
- API-accessible extraction results
- Ready for downstream systems (KYC, HR, ERP, etc.)

---

## 📌 Use Cases

- 🏦 Banking & KYC automation
- 👔 HR document processing
- 🪪 Government ID digitization
- 📂 Enterprise document indexing
- 🔄 Data migration & validation

---

## 📚 Further Reading

- [`ai-constraints.md`](./ai-constraints.md) — AI trust model, output rules, and security boundaries
- [`prompting_rules.md`](./prompting_rules.md) — Prompt design principles, construction flow, and failure handling

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
