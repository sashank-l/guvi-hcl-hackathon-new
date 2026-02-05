"""GUVI callback helper."""

import requests
from typing import Dict, List

from app.config import GUVI_CALLBACK_URL


def send_guvi_callback(
    session_id: str,
    total_messages: int,
    intelligence: Dict[str, List[str]],
    agent_notes: str,
) -> None:
    payload = {
        "sessionId": session_id,
        "scamDetected": True,
        "totalMessagesExchanged": total_messages,
        "extractedIntelligence": intelligence,
        "agentNotes": agent_notes,
    }
    try:
        requests.post(GUVI_CALLBACK_URL, json=payload, timeout=5)
    except Exception:
        pass
