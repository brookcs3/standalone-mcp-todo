"""Standalone Todo Storage System.

This module provides persistent storage for todo lists with session isolation.
Can be used for any type of project or workflow management.
"""

import json
import time
from pathlib import Path
from typing import Any, Optional


class TodoStorage:
    """Flexible storage for todo lists with both in-memory and file persistence.
    
    This class provides storage for todo lists with session isolation, supporting
    both in-memory storage (for speed) and optional file persistence (for durability).
    Perfect for project management, workflow tracking, and task organization.
    """

    # Class-level storage for in-memory mode
    _sessions: dict[str, dict[str, Any]] = {}
    
    def __init__(self, storage_file: Optional[str] = None):
        """Initialize todo storage.
        
        Args:
            storage_file: Optional path to JSON file for persistent storage.
                         If None, uses in-memory storage only.
        """
        self.storage_file = Path(storage_file) if storage_file else None
        self._load_from_file()

    def _load_from_file(self) -> None:
        """Load sessions from file if file storage is enabled."""
        if not self.storage_file or not self.storage_file.exists():
            return
            
        try:
            with open(self.storage_file, 'r') as f:
                data = json.load(f)
                self._sessions = data.get('sessions', {})
        except (json.JSONDecodeError, IOError):
            # If file is corrupted or unreadable, start fresh
            self._sessions = {}

    def _save_to_file(self) -> None:
        """Save sessions to file if file storage is enabled."""
        if not self.storage_file:
            return
            
        try:
            # Ensure directory exists
            self.storage_file.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                'sessions': self._sessions,
                'last_saved': time.time()
            }
            
            with open(self.storage_file, 'w') as f:
                json.dump(data, f, indent=2)
        except IOError:
            # Silent fail - in-memory storage will still work
            pass

    def get_todos(self, session_id: str) -> list[dict[str, Any]]:
        """Get the todo list for a specific session.

        Args:
            session_id: Unique identifier for the session

        Returns:
            List of todo items for the session, empty list if session doesn't exist
        """
        session_data = self._sessions.get(session_id, {})
        return session_data.get("todos", [])

    def set_todos(self, session_id: str, todos: list[dict[str, Any]]) -> None:
        """Set the todo list for a specific session.

        Args:
            session_id: Unique identifier for the session
            todos: Complete list of todo items to store
        """
        self._sessions[session_id] = {
            "todos": todos, 
            "last_updated": time.time()
        }
        self._save_to_file()

    def get_session_count(self) -> int:
        """Get the number of active sessions.

        Returns:
            Number of sessions with stored todos
        """
        return len(self._sessions)

    def get_all_session_ids(self) -> list[str]:
        """Get all active session IDs.

        Returns:
            List of all session IDs with stored todos
        """
        return list(self._sessions.keys())

    def delete_session(self, session_id: str) -> bool:
        """Delete a session and its todos.

        Args:
            session_id: Session ID to delete

        Returns:
            True if session was deleted, False if it didn't exist
        """
        if session_id in self._sessions:
            del self._sessions[session_id]
            self._save_to_file()
            return True
        return False

    def get_session_last_updated(self, session_id: str) -> float | None:
        """Get the last updated timestamp for a session.

        Args:
            session_id: Session ID to check

        Returns:
            Timestamp when session was last updated, or None if session doesn't exist
        """
        session_data = self._sessions.get(session_id)
        if session_data:
            return session_data.get("last_updated")
        return None

    def find_latest_active_session(self) -> str | None:
        """Find the most recently updated session with unfinished todos.

        Returns:
            Session ID with unfinished todos that was most recently updated, or None
        """
        latest_session = None
        latest_timestamp = 0

        for session_id, session_data in self._sessions.items():
            todos = session_data.get("todos", [])
            has_unfinished = any(
                todo.get("status") in ["pending", "in_progress"]
                for todo in todos if isinstance(todo, dict)
            )

            if has_unfinished:
                last_updated = session_data.get("last_updated", 0)
                if last_updated > latest_timestamp:
                    latest_timestamp = last_updated
                    latest_session = session_id

        return latest_session

    def get_stats(self) -> dict[str, Any]:
        """Get storage statistics.
        
        Returns:
            Dictionary with storage statistics
        """
        total_todos = 0
        status_counts = {"pending": 0, "in_progress": 0, "completed": 0}
        priority_counts = {"high": 0, "medium": 0, "low": 0}
        
        for session_data in self._sessions.values():
            todos = session_data.get("todos", [])
            total_todos += len(todos)
            
            for todo in todos:
                if isinstance(todo, dict):
                    status = todo.get("status", "unknown")
                    priority = todo.get("priority", "unknown")
                    
                    if status in status_counts:
                        status_counts[status] += 1
                    if priority in priority_counts:
                        priority_counts[priority] += 1
        
        return {
            "total_sessions": self.get_session_count(),
            "total_todos": total_todos,
            "status_breakdown": status_counts,
            "priority_breakdown": priority_counts,
            "has_file_persistence": self.storage_file is not None,
            "storage_file": str(self.storage_file) if self.storage_file else None
        }
