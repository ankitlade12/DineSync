"""Session Manager for DineSync

Handles creation, storage, and retrieval of group dining sessions.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict


@dataclass
class Participant:
    """A participant in a dining session"""
    name: str
    cuisines: List[str]
    dietary_restrictions: List[str]
    budget: str
    max_distance: float
    ambiance: List[str]
    veto_items: List[str]  # NEW: Absolute dealbreakers
    submitted_at: str


@dataclass
class DineSession:
    """A group dining session"""
    session_id: str
    location: str
    created_at: str
    participants: List[Participant]
    results_ready: bool = False


class SessionManager:
    """Manages dining sessions with JSON file storage"""
    
    def __init__(self, storage_path: str = "sessions.json"):
        self.storage_path = Path(storage_path)
        self._ensure_storage_exists()
    
    def _ensure_storage_exists(self):
        """Create storage file if it doesn't exist"""
        if not self.storage_path.exists():
            self.storage_path.write_text("{}")
    
    def _load_sessions(self) -> Dict[str, Dict]:
        """Load all sessions from storage"""
        try:
            return json.loads(self.storage_path.read_text())
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    def _save_sessions(self, sessions: Dict[str, Dict]):
        """Save all sessions to storage"""
        self.storage_path.write_text(
            json.dumps(sessions, indent=2)
        )
    
    def create_session(self, location: str) -> str:
        """
        Create a new dining session.
        Returns session_id
        """
        session_id = self._generate_session_id()
        
        session = DineSession(
            session_id=session_id,
            location=location,
            created_at=datetime.now().isoformat(),
            participants=[],
            results_ready=False
        )
        
        sessions = self._load_sessions()
        sessions[session_id] = asdict(session)
        self._save_sessions(sessions)
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[DineSession]:
        """Get a session by ID"""
        sessions = self._load_sessions()
        session_data = sessions.get(session_id)
        
        if not session_data:
            return None
        
        # Convert dict to DineSession
        participants = [
            Participant(**p) for p in session_data.get("participants", [])
        ]
        
        return DineSession(
            session_id=session_data["session_id"],
            location=session_data["location"],
            created_at=session_data["created_at"],
            participants=participants,
            results_ready=session_data.get("results_ready", False)
        )
    
    def add_participant(
        self,
        session_id: str,
        name: str,
        cuisines: List[str],
        dietary_restrictions: List[str],
        budget: str,
        max_distance: float,
        ambiance: List[str],
        veto_items: List[str] = None  # NEW: Dealbreakers
    ) -> bool:
        """
        Add a participant to a session.
        Returns True if successful, False if session not found
        """
        sessions = self._load_sessions()
        
        if session_id not in sessions:
            return False
        
        participant = Participant(
            name=name,
            cuisines=cuisines,
            dietary_restrictions=dietary_restrictions,
            budget=budget,
            max_distance=max_distance,
            ambiance=ambiance,
            veto_items=veto_items or [],
            submitted_at=datetime.now().isoformat()
        )
        
        sessions[session_id]["participants"].append(asdict(participant))
        self._save_sessions(sessions)
        
        return True
    
    def mark_results_ready(self, session_id: str) -> bool:
        """Mark session as having results ready"""
        sessions = self._load_sessions()
        
        if session_id not in sessions:
            return False
        
        sessions[session_id]["results_ready"] = True
        self._save_sessions(sessions)
        
        return True
    
    def get_all_sessions(self) -> List[DineSession]:
        """Get all sessions (for debugging/admin)"""
        sessions = self._load_sessions()
        
        result = []
        for session_data in sessions.values():
            participants = [
                Participant(**p) for p in session_data.get("participants", [])
            ]
            result.append(DineSession(
                session_id=session_data["session_id"],
                location=session_data["location"],
                created_at=session_data["created_at"],
                participants=participants,
                results_ready=session_data.get("results_ready", False)
            ))
        
        return result
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        sessions = self._load_sessions()
        
        if session_id not in sessions:
            return False
        
        del sessions[session_id]
        self._save_sessions(sessions)
        
        return True
    
    @staticmethod
    def _generate_session_id() -> str:
        """Generate a unique session ID"""
        # Use timestamp + short UUID for readability
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        short_uuid = str(uuid.uuid4())[:8]
        return f"{timestamp}-{short_uuid}"
