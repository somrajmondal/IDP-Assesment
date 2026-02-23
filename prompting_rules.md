# 🧠 Prompting Rules & Strategy

This document defines how prompts are designed, generated, and constrained for document classification and entity extraction.

**Goals:**
- Predictable AI behavior
- Schema-driven extraction
- Safe interaction between UI, Backend, and LLM
- Zero hallucination or uncontrolled inference

---

## 1. 🏛️ Prompt Ownership Model

| Layer | Role |
|-------|------|
| Admin UI | Configures prompt logic (descriptions, rules, priorities) |
| Backend | Assembles, injects schema, and sends the final prompt |
| LLM | Receives and executes the prompt only |

- Prompts are **not hardcoded** (except the global system prompt)
- Prompts are **not authored by the LLM**
- The backend is the **single authority** for prompt assembly, schema injection, and context boundaries

---

## 2. 🖥️ Admin-Driven Prompt Configuration (UI Level)

### Classification Prompt

Admins define what makes a document type distinct:

```
"A Salary Certificate usually contains employer name, 
salary breakdown, employee details, and issuing date."
```

Admins can also configure:
- How similar document types should be distinguished
- Priority rules when multiple types appear similar

### Entity Extraction Prompt

Each entity is fully configurable:

| Field | Description |
|-------|-------------|
| Entity name | Human-readable label |
| Backend key | Immutable identifier used in JSON output |
| Data type | `Text`, `Numeric`, `Date`, `Boolean`, etc. |
| Description | Used verbatim in the LLM prompt |
| Customer type | `Individual` or `Non-Individual` |

Admins can add, edit, or remove entities at any time — **no code changes required**.

---

## 3. 🔁 Prompt Construction Flow (Backend)

At runtime, the backend builds the prompt dynamically:

```
1. Fetch document type configuration
2. Fetch template + entity definitions
3. Build a structured JSON schema
4. Inject schema + instructions into the prompt
5. Send the final prompt to the LLM service
```

### What the LLM Never Sees

```
✘ Database structure
✘ Internal business logic  
✘ UI implementation details
```

---

## 4. 📐 Prompt Design Principles

### Schema-First
The expected JSON structure is always provided upfront. The model is instructed to output **JSON only**.

### Deterministic
```
✔ Structured fields only
✘ No creative language
✘ No explanations
✘ No reasoning text
```

### Minimal Context
Only information required for the task is included. No unrelated text or historical data.

---

## 5. 🗂️ Classification Prompt Rules

```
✔ Select EXACTLY ONE document type
✔ Confidence score must be between 0.0 and 1.0
✔ If uncertain → pick best match, reduce confidence score
```

**Invalid outputs:**

```
✘ Multiple document types selected
✘ Free-text explanation returned
✘ Confidence score missing
```

### Example Valid Output

```json
{
  "class_name": "Salary Certificate",
  "score": 0.94,
  "technique": "openai - level 1"
}
```

---

## 6. 🧾 Entity Extraction Prompt Rules

| Rule | Expected Behavior |
|------|-------------------|
| Value found | Return with correct data type |
| Value not found | Return `null` |
| Entity not in schema | Never appear in output |
| Uncertain value | Return `null` — do not guess |

```
✘ Do not guess or infer missing values
✘ Do not invent entities
✘ Do not use cross-page inference without explicit evidence
```

### Example Valid Output

```json
{
  "backend_entity_key": "employer_name",
  "entity_name": "Employer Name",
  "entity_value": "Imaginorlabs Private Limited",
  "entity_data_type": "AlphaNumeric"
}
```

### Example When Value Is Missing

```json
{
  "backend_entity_key": "end_date",
  "entity_name": "End Date",
  "entity_value": null,
  "entity_data_type": "Date"
}
```

---

## 7. 🔄 Prompt Evolution Strategy

Prompts are expected to improve over time:

```
Admin refines entity descriptions in UI
        ↓
Backend picks up changes immediately (no deploy)
        ↓
Next LLM request uses the updated prompt
```

> Prompt evolution is treated as **configuration**, not deployment.

No backend code changes are required for prompt tuning.

---

## 8. ⚠️ Failure Handling

If the model violates any rule:

| Violation | Action |
|-----------|--------|
| Schema violated | Response rejected |
| Malformed JSON | Response rejected |
| Hallucinated fields | Response rejected |
| Missing required fields | Response rejected |

All rejections are **logged** with full diagnostic context. Prompt correctness is validated indirectly via schema enforcement.

---

## 🔗 Related

- [`README.md`](./README.md) — Platform overview and setup
- [`ai-constraints.md`](./ai-constraints.md) — AI trust model and security boundaries