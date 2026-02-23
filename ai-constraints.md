1. Trust Model

The AI/LLM is never trusted to enforce correctness

All AI output is treated as untrusted user input

The backend is the single source of truth

The database is never written to directly by AI output

All AI responses must pass backend validation before being accepted.

2. Model Switching & Replacement Strategy

The system is explicitly designed to support multiple AI models for both
document classification and entity extraction.

Supported Capabilities

Classification and extraction models can be switched via environment variables

No UI or backend business logic changes are required

Only the AI adapter layer is replaced

Supported Model Types

Cloud LLMs (OpenAI, Azure OpenAI, etc.)

Open-source models (e.g. vision-language models such as Qwen-VL, Nougat, Donut)

Hybrid approaches:

OCR + TF-IDF similarity scoring

Azure OCR + classical text similarity for classification confidence

Classification Flexibility

Document classification can be performed using:

LLM-based reasoning

OCR-extracted text + TF-IDF similarity scoring

Combined scoring strategies for higher reliability

AI is an implementation detail, not a dependency risk.

3. Output Constraints

The AI must:

Return valid JSON only

Follow the schema provided in the prompt

Use backend-defined keys exactly as provided

Respect declared data types

The AI must NOT:

Add new keys

Rename existing keys

Modify backend identifiers

Return free-form text or explanations

Any violation results in rejection.

4. Schema Enforcement (Backend)

Before any AI output is accepted:

JSON structure is validated

Required fields are enforced

Entity backend keys are verified

Page number bounds are checked

If validation fails:

The response is rejected

No partial data is stored

The error is logged for observability and debugging

5. Classification Safety Rules

Classification output must include:

class_name

(Optional) confidence score if supported by the model

Invalid classification results trigger:

Request failure

Diagnostic logging

Prevention of downstream extraction

Classification must always resolve to exactly one document type.

6. Entity Extraction Safety Rules

Every extracted entity must exist in the provided schema

Entity values must match declared data types

Missing or unknown values must be returned as null

The system explicitly forbids:

Guessing or inferring values

Filling missing fields creatively

Cross-page inference without explicit evidence

7. Observability & Debugging

All AI interactions are logged with:

Request ID

Prompt version hash

Model identifier

Validation result

Error reason (if any)

This enables:

Debugging incorrect outputs

Prompt tuning

Regression detection

Model comparison over time

8. Failure Isolation

AI failures do not affect system stability

AI errors do not corrupt stored data

Each AI request is stateless and isolated

Partial failures are safely discarded

9. Security Boundary Summary

UI defines configuration and intent

Backend enforces validation and rules

AI executes instructions only

Database accepts validated data only

No single layer can compromise system integrity.