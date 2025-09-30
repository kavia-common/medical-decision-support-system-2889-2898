Medical Decision Support Backend (Django + DRF)

Endpoints (prefix: /api):
- GET /health/ -> Health check
- POST /chat -> Patient chat with PatientAgent
- POST /recommend -> ClinicalAgent RAG recommendations
- POST /upload_report -> Upload and refine test report
- POST /get_recommendation -> Combined recommendation and notes location

Docs:
- /docs (Swagger UI, Ocean Professional branding)
- /redoc
- /openapi.json

Environment variables (place in .env via orchestrator; do not commit secrets):
- ONEDRIVE_ENABLED=true|false
- ONEDRIVE_TOKEN=<token> (required if ONEDRIVE_ENABLED=true)
- ONEDRIVE_BASE_FOLDER=/MedicalDecisionSupport
- LOCAL_NOTES_DIR=<local path for fallback>
- MEDICAL_DOCS_DIR=<path to local guideline snippets>

Vector DB:
- Code supports FAISS/Chroma optionally; it falls back to in-memory linear search if unavailable.

CLI demo:
- python manage.py demo

Privacy & Safety:
- No PII/PHI storage; notes are de-identified and saved to OneDrive or local fallback.
- Responses include disclaimers and basic urgency detection.
