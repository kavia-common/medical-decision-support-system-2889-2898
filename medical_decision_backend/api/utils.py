from typing import Tuple, Optional, Dict


# PUBLIC_INTERFACE
def safety_guardrails(text: str) -> Tuple[bool, Optional[str]]:
    """
    Lightweight safety guardrails to flag potentially dangerous content.
    Returns (flagged, category).
    """
    t = text.lower()
    urgent_keywords = [
        "suicide", "kill myself", "overdose", "chest pain", "severe bleeding", "stroke", "can't breathe",
        "cannot breathe", "anaphylaxis", "heart attack", "unconscious", "fainted", "poisoned"
    ]
    for kw in urgent_keywords:
        if kw in t:
            return True, "URGENT"
    return False, None


# PUBLIC_INTERFACE
def disclaimer_payload(extra_category: Optional[str] = None) -> Dict:
    """
    Standard disclaimer data for responses to emphasize non-diagnostic nature and privacy.
    """
    disclaimer = {
        "disclaimer": (
            "This service does not provide medical diagnosis. "
            "Always consult a qualified healthcare professional. "
            "In emergencies, call local emergency services."
        ),
        "privacy": "No personally identifiable information is stored. Session notes are de-identified.",
        "category": extra_category or "GENERAL",
    }
    return disclaimer


# PUBLIC_INTERFACE
def ocean_professional_openapi_branding() -> Dict:
    """
    Provide Ocean Professional theme metadata for API docs.
    """
    return {
        "title": "Medical Decision Support API",
        "description": (
            "Modern, privacy-first multi-agent backend for patient chat and clinical recommendations. "
            "Styled with Ocean Professional theme (blue & amber accents)."
        ),
        "version": "v1.0.0",
        "contact": {"name": "Medical Decision Support", "email": "support@example.com"},
        "x-theme": {
            "name": "Ocean Professional",
            "primary": "#2563EB",
            "secondary": "#F59E0B",
            "error": "#EF4444",
            "background": "#f9fafb",
            "surface": "#ffffff",
            "text": "#111827",
            "gradient": "from-blue-500/10 to-gray-50",
        },
    }
