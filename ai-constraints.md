# 🔐 AI Constraints & Safety Model

This document defines how the system interacts with AI/LLM services — covering trust boundaries, output rules, validation enforcement, and failure handling.

> **Core principle:** The AI executes instructions only. The backend is the single source of truth.

---

## 1. 🛡️ Trust Model

| Layer | Trust Level | Responsibility |
|-------|-------------|----------------|
| UI | Trusted (admin-controlled) | Defines configuration and intent |
| Backend | Trusted | Enforces validation and rules |
| AI / LLM | **Untrusted** | Executes instructions only |
| Database | Trusted | Accepts validated data only |

- All AI output is treated as **untrusted user input**
- The database is **never written to directly** by AI output
- All AI responses must **pass backend validation** before being accepted
- No single layer can compromise system integrity

---

## 2. 🔄 Model Switching & Replacement

The system is explicitly designed to support multiple AI models. Switching models requires **no UI or backend changes** — only the adapter layer is replaced.

### Supported Model Types

| Type | Examples |
|------|----------|
| Cloud LLMs | OpenAI, Azure OpenAI |
| Open-source VLMs | Qwen-VL, Nougat, Donut |
| Hybrid (OCR + scoring) | Azure OCR + TF-IDF similarity |

### Switching via Environment Variable

```bash
# Example: switch classification model
CLASSIFICATION_MODEL=qwen-vl

# Example: switch extraction model  
EXTRACTION_MODEL=azure-openai
```

> AI is an implementation detail, not a dependency risk.

---

## 3. 📤 Output Constraints

### ✅ The AI Must

- Return **valid JSON only**
- Follow the **schema provided in the prompt**
- Use **backend-defined keys exactly** as provided
- Respect declared **data types**
- Return `null` for any value that is not found

### ❌ The AI Must NOT

- Add new keys
- Rename existing keys
- Modify backend identifiers
- Return free-form text or explanations
- Guess, infer, or creatively fill missing fields

> Any violation results in **immediate rejection**. No partial data is stored.

---

## 4. ✅ Schema Enforcement (Backend)

Before any AI output is accepted, the backend validates:

```
✔ JSON structure is valid
✔ Required fields are present
✔ Entity backend keys match the schema
✔ Page number bounds are within range
✔ Data types match declarations
```

### On Validation Failure

```
✘ Response is rejected
✘ No partial data is stored
✘ Error is logged with full diagnostic context
```

---

## 5. 🗂️ Classification Safety Rules

Classification output **must include**:

```json
{
  "class_name": "Salary Certificate",
  "score": 0.97
}
```

| Rule | Detail |
|------|--------|
| Exactly one document type | Multi-type output is invalid |
| Confidence score required | Range: `0.0` to `1.0` |
| Uncertain? Still pick one | Lower the score, don't omit |

**Invalid outputs trigger:**
- Request failure
- Diagnostic logging
- Prevention of downstream extraction

---

## 6. 🧾 Entity Extraction Safety Rules

| Rule | Behavior |
|------|----------|
| Entity must exist in schema | Unknown entities are rejected |
| Value matches declared type | Type mismatch causes rejection |
| Value not found | Return `null` — never guess |
| Cross-page inference | Only allowed with explicit evidence |

**Explicitly forbidden:**
- Guessing or inferring missing values
- Filling fields creatively
- Inventing entities not in the schema

---

## 7. 📊 Observability & Debugging

Every AI interaction is logged with:

```
• Request ID
• Prompt version hash
• Model identifier
• Validation result (pass / fail)
• Error reason (if applicable)
```

This enables:
- Debugging incorrect outputs
- Prompt tuning and A/B testing
- Regression detection across model versions
- Model comparison over time

---

## 8. 🔒 Failure Isolation

| Property | Guarantee |
|----------|-----------|
| AI failures affect system stability | ❌ No — fully isolated |
| AI errors corrupt stored data | ❌ No — rejected before storage |
| Each request shares state | ❌ No — fully stateless |
| Partial failures are stored | ❌ No — safely discarded |

---

## 9. 🗺️ Security Boundary Summary

```
┌─────────────────────────────────────────┐
│  UI — defines configuration and intent  │
├─────────────────────────────────────────┤
│  Backend — enforces validation & rules  │
├─────────────────────────────────────────┤
│  AI — executes instructions only        │
├─────────────────────────────────────────┤
│  Database — accepts validated data only │
└─────────────────────────────────────────┘
```

---

## 🔗 Related

- [`README.md`](./README.md) — Platform overview and setup
- [`prompting_rules.md`](./prompting_rules.md) — Prompt design and construction rules