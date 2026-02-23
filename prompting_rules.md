# Prompting Rules & Strategy

This document defines how prompts are designed, generated, and constrained
for document classification and entity extraction.

The goal is to ensure:
- Predictable AI behavior
- Schema-driven extraction
- Safe interaction between UI, Backend, and LLM
- No hallucination or uncontrolled inference

---

## 1. Prompt Ownership Model

- Prompts are NOT hardcoded, excep to global Prompt.
- Prompts are NOT authored directly by the LLM.
- Prompts are dynamically constructed by the backend
  using admin-defined configuration from the UI.

The backend is the single authority responsible for:
- Prompt assembly
- Schema injection
- Context boundaries

---

## 2. Admin-Driven Prompt Configuration (UI Level)

From the Admin UI, users can configure:

### Classification Prompt
- What defines a document type
- How similar documents should be distinguished
- Priority rules when multiple document types appear similar

Example (configured in UI):
- “A Salary Certificate usually contains employer name, salary breakdown,
   employee details, and issuing date.”

---

### Entity Extraction Prompt
Each entity has:
- Entity name
- Backend key (immutable)
- Data type
- Description (used verbatim in prompt)

Admins can:
- Add new entities
- Edit descriptions
- Remove entities
- Change prompts without code changes

---

## 3. Prompt Construction Flow (Backend)

At runtime, the backend:
1. Fetches document type configuration
2. Fetches template + entity definitions
3. Builds a structured JSON schema
4. Injects schema + instructions into the prompt
5. Sends the final prompt to the LLM service

The LLM never sees:
- Database structure
- Internal business logic
- UI implementation details

---

## 4. Prompt Design Principles

All prompts must follow these principles:

### Schema-First
- The expected JSON structure is always provided
- The model is instructed to output JSON only

### Deterministic
- No creative language
- No explanations
- No reasoning text
- Only structured fields

### Minimal Context
- Only information required for the task is included
- No unrelated text or historical data

---

## 5. Classification Prompt Rules

- The model must select EXACTLY ONE document type
- Confidence score must be between 0 and 1
- If classification is uncertain, the model must still select the best match
  and reduce confidence score accordingly

Invalid outputs include:
- Multiple document types
- Free-text explanations
- Missing confidence score

---

## 6. Entity Extraction Prompt Rules

For each entity:
- Value must match declared data type
- If value is not found, return null
- Do not guess or infer missing values
- Do not invent entities

Entities not defined in the schema must NEVER appear in output.

---

## 7. Prompt Evolution Strategy

Prompts are expected to evolve over time:
- Admins can refine descriptions to improve accuracy
- No backend code changes are required
- Changes take effect immediately

Prompt evolution is treated as configuration, not deployment.

---

## 8. Failure Handling

If the model:
- Violates schema
- Returns malformed JSON
- Includes hallucinated fields

The backend will reject the response and log the failure.

Prompt correctness is validated indirectly via schema enforcement.