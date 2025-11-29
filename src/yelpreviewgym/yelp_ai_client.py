"""Yelp AI API Client

Handles communication with Yelp AI Chat API for review analysis
and feedback generation.
"""

from __future__ import annotations

import json
from typing import Any, Dict, Optional

import requests

from .config import get_settings


YELP_AI_URL = "https://api.yelp.com/ai/chat/v2"


class YelpAIError(Exception):
    """Exception raised for Yelp AI API errors."""
    pass


class YelpAIClient:
    """Client for interacting with Yelp AI Chat API."""
    
    def __init__(self, api_key: Optional[str] = None) -> None:
        settings = get_settings()
        self.api_key = api_key or settings.yelp_api_key

    def chat(self, query: str, chat_id: Optional[str] = None) -> Dict[str, Any]:
        """Send chat request to Yelp AI API."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload: Dict[str, Any] = {"query": query}
        if chat_id:
            payload["chat_id"] = chat_id

        resp = requests.post(
            YELP_AI_URL,
            headers=headers,
            json=payload,
            timeout=30,
        )
        if not resp.ok:
            raise YelpAIError(
                f"Yelp AI API error {resp.status_code}: {resp.text[:400]}"
            )
        try:
            return resp.json()
        except Exception as e:
            raise YelpAIError(f"Failed to parse Yelp AI JSON: {e}") from e

    @staticmethod
    def _extract_json_block(text: str) -> Optional[str]:
        """Extract JSON block from response text."""
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            return None
        return text[start : end + 1]

    @staticmethod
    def json_from_response(raw: Dict[str, Any]) -> tuple[Optional[Dict[str, Any]], str]:
        """Parse JSON from API response."""
        text = ""
        try:
            text = raw.get("response", {}).get("text", "") or ""
        except Exception:
            text = ""

        if not text:
            return None, ""

        block = YelpAIClient._extract_json_block(text)
        if not block:
            return None, text

        try:
            parsed = json.loads(block)
            return parsed, text
        except Exception:
            return None, text
