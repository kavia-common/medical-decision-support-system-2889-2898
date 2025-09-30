import json
import os
from datetime import datetime
from typing import Optional, Tuple


class OneDriveClient:
    """
    Minimal OneDrive client facade with local filesystem fallback.
    Environment variables required (must be provided by user via .env):
        - ONEDRIVE_ENABLED=true|false
        - ONEDRIVE_TOKEN=... (OAuth token)
        - ONEDRIVE_BASE_FOLDER=/MedicalDecisionSupport
    """

    def __init__(self):
        self.enabled = str(os.getenv("ONEDRIVE_ENABLED", "false")).lower() == "true"
        self.token = os.getenv("ONEDRIVE_TOKEN")
        self.base_folder = os.getenv("ONEDRIVE_BASE_FOLDER", "/MedicalDecisionSupport")
        self.local_base = os.getenv("LOCAL_NOTES_DIR", os.path.join(os.getcwd(), "storage", "notes"))
        os.makedirs(self.local_base, exist_ok=True)

    def _onedrive_available(self) -> bool:
        # In this scaffold we just check env flags; real HTTP calls would go here.
        return self.enabled and bool(self.token)

    # PUBLIC_INTERFACE
    def save_session_notes(self, session_id: str, notes: dict) -> Tuple[str, str]:
        """
        Save session notes to OneDrive if available; otherwise save locally.

        Returns:
            location_type: 'onedrive' or 'local'
            path_or_id: path (local) or placeholder OneDrive file id/path
        """
        timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        filename = f"{session_id}_{timestamp}.json"
        payload = {
            "session_id": session_id,
            "timestamp": timestamp,
            "notes": notes,
        }
        if self._onedrive_available():
            # Placeholder: in production, use Microsoft Graph API.
            # We return a pseudo-path to indicate destination.
            remote_path = f"{self.base_folder}/{filename}"
            return "onedrive", remote_path
        # Fallback to local
        full_path = os.path.join(self.local_base, filename)
        with open(full_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        return "local", full_path

    # PUBLIC_INTERFACE
    def get_session_notes(self, session_id: str) -> Optional[dict]:
        """
        Attempt to retrieve latest session notes for a session_id from local fallback.
        OneDrive retrieval is not implemented in scaffold; in a real integration, query Graph.
        """
        if not os.path.isdir(self.local_base):
            return None
        files = [f for f in os.listdir(self.local_base) if f.startswith(session_id) and f.endswith(".json")]
        if not files:
            return None
        files.sort(reverse=True)
        path = os.path.join(self.local_base, files[0])
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None
