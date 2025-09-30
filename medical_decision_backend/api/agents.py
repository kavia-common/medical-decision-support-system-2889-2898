from typing import Dict, Tuple, Any, List
from .rag_service import RAGIndex, compose_recommendation
from .onedrive_integration import OneDriveClient
from .utils import safety_guardrails, disclaimer_payload


class ConversationMemory:
    """Simple in-memory conversation store keyed by session_id."""
    def __init__(self):
        self.store: Dict[str, List[Dict[str, str]]] = {}

    def add(self, session_id: str, role: str, content: str):
        self.store.setdefault(session_id, []).append({"role": role, "content": content})

    def get(self, session_id: str) -> List[Dict[str, str]]:
        return self.store.get(session_id, [])

    def summary(self, session_id: str) -> str:
        lines = []
        for item in self.get(session_id):
            tag = "P" if item["role"] == "patient" else "A"
            lines.append(f"{tag}: {item['content']}")
        return "\n".join(lines[-20:])  # last 20 turns


_MEMORY = ConversationMemory()


class PatientAgent:
    """
    PatientAgent conducts structured patient chats, collects symptoms and context,
    and writes session notes to OneDrive (with local fallback).
    """
    def __init__(self):
        self.drive = OneDriveClient()

    # PUBLIC_INTERFACE
    def reply(self, session_id: str, message: str) -> Tuple[str, Dict[str, Any]]:
        """
        Generate a structured, empathetic reply, update session memory, and save notes.
        Returns (reply_text, safety_payload).
        """
        _MEMORY.add(session_id, "patient", message)
        context = _MEMORY.summary(session_id)
        # Basic heuristic reply scaffold
        reply = (
            "Thank you for sharing. To help further, please clarify:\n"
            "- Onset and duration of symptoms\n"
            "- Severity (mild/moderate/severe)\n"
            "- Associated factors (fever, cough, chest pain, etc.)\n"
            "- Relevant history and medications\n"
            "I will maintain your privacy and will not store personally identifiable information."
        )
        _MEMORY.add(session_id, "assistant", reply)
        # Prepare structured notes (de-identified)
        notes = {
            "session_summary": context,
            "latest_patient_message": message[:1000],
            "latest_agent_reply": reply,
        }
        self.drive.save_session_notes(session_id, notes)
        safety = disclaimer_payload()
        return reply, safety

    # PUBLIC_INTERFACE
    def get_notes_location(self, session_id: str) -> Tuple[str, str]:
        """
        Return the location of the most recent notes for the session ('onedrive' or 'local', path/id).
        """
        # Save empty minimal notes to make sure a file exists
        location_type, path_or_id = self.drive.save_session_notes(session_id, {"heartbeat": "ok"})
        return location_type, path_or_id


class ClinicalAgent:
    """
    ClinicalAgent uses RAG to provide evidence-linked recommendations.
    """
    def __init__(self, rag_index: RAGIndex):
        self.rag = rag_index

    # PUBLIC_INTERFACE
    def recommend(self, session_id: str, question: str, top_k: int = 4) -> Tuple[str, List[Dict[str, Any]], Dict[str, Any]]:
        """
        Perform a RAG search and compose a recommendation with citations.
        Returns (answer, citations, safety_payload)
        """
        flagged, category = safety_guardrails(question)
        hits = self.rag.query(question, top_k=top_k)
        answer, citations = compose_recommendation(question, hits)
        if flagged:
            answer = (
                "Your question may indicate an urgent or high-risk situation. "
                "Please seek immediate medical attention or contact local emergency services. "
            ) + "\n\n" + answer
        safety = disclaimer_payload(extra_category=category if flagged else None)
        return answer, citations, safety

    # PUBLIC_INTERFACE
    def refine_report(self, session_id: str, report_text: str) -> Tuple[str, Dict[str, Any]]:
        """
        Produce a refined, structured plain-text summary of an uploaded test report.
        Returns (refined_text, safety_payload)
        """
        # Simple transformation scaffold: normalize whitespace and extract basic sections
        lines = [ln.strip() for ln in report_text.splitlines() if ln.strip()]
        refined = [
            "Report Summary (auto-structured)",
            "-------------------------------",
            f"Total lines parsed: {len(lines)}",
            "",
            "Key Findings:",
        ]
        # naive heuristics
        findings = [ln for ln in lines if any(k in ln.lower() for k in ["impression", "finding", "diagnosis", "result"])]
        if findings:
            refined.extend([f"- {f}" for f in findings[:10]])
        else:
            refined.append("- No explicit findings detected; please review the full text.")
        refined.append("")
        refined.append("Recommendations:")
        recommendations = [ln for ln in lines if "recommend" in ln.lower()]
        if recommendations:
            refined.extend([f"- {r}" for r in recommendations[:10]])
        else:
            refined.append("- Consider correlating with clinical presentation and current guidelines.")

        safety = disclaimer_payload()
        return "\n".join(refined), safety
