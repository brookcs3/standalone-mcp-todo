"""Base functionality for standalone todo tools.

This module provides common validation and normalization functionality for todo tools.
Can be used for any type of project or workflow management.
"""

import re
from abc import ABC
from typing import Any


class TodoBaseTool(ABC):
    """Base class for todo tools.

    Provides common functionality for working with todo lists, including
    validation and normalization of todo structures.
    
    This is framework-agnostic and can be used with any MCP implementation
    or even as a standalone library.
    """

    def normalize_todo_item(self, todo: dict[str, Any], index: int) -> dict[str, Any]:
        """Normalize a single todo item by auto-generating missing required fields.

        Args:
            todo: Todo item to normalize
            index: Index of the todo item for generating unique IDs

        Returns:
            Normalized todo item with all required fields
        """
        normalized = dict(todo)  # Create a copy

        # Auto-generate ID if missing or normalize existing ID to string
        if "id" not in normalized or not str(normalized.get("id")).strip():
            normalized["id"] = f"todo-{index + 1}"
        else:
            # Ensure ID is stored as a string for consistency
            normalized["id"] = str(normalized["id"]).strip()

        # Auto-generate priority if missing (but don't fix invalid values)
        if "priority" not in normalized:
            normalized["priority"] = "medium"

        # Ensure status defaults to pending if missing (but don't fix invalid values)
        if "status" not in normalized:
            normalized["status"] = "pending"

        return normalized

    def normalize_todos_list(self, todos: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Normalize a list of todo items by auto-generating missing fields.

        Args:
            todos: List of todo items to normalize

        Returns:
            Normalized list of todo items with all required fields
        """
        if not isinstance(todos, list):
            return []  # Return empty list for invalid input

        normalized_todos = []
        used_ids = set()

        for i, todo in enumerate(todos):
            if not isinstance(todo, dict):
                continue  # Skip invalid items

            normalized = self.normalize_todo_item(todo, i)

            # Don't auto-fix duplicate IDs - let validation catch them
            used_ids.add(normalized["id"])
            normalized_todos.append(normalized)

        return normalized_todos

    def validate_session_id(self, session_id: str | None) -> tuple[bool, str]:
        """Validate session ID format and security.

        Args:
            session_id: Session ID to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check for None or empty first
        if session_id is None or session_id == "":
            return False, "Session ID is required but was empty"

        # Check if it's a string
        if not isinstance(session_id, str):
            return False, "Session ID must be a string"

        # Check length (reasonable bounds)
        if len(session_id) < 3:
            return False, "Session ID too short (minimum 3 characters)"

        if len(session_id) > 100:
            return False, "Session ID too long (maximum 100 characters)"

        # Check format - allow alphanumeric, hyphens, underscores, dots
        # This prevents path traversal and other security issues
        if not re.match(r"^[a-zA-Z0-9._-]+$", session_id):
            return (
                False,
                "Session ID can only contain alphanumeric characters, dots, hyphens, and underscores",
            )

        return True, ""

    def validate_todo_item(self, todo: dict[str, Any]) -> tuple[bool, str]:
        """Validate a single todo item structure.

        Args:
            todo: Todo item to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(todo, dict):
            return False, "Todo item must be an object"

        # Check required fields
        required_fields = ["content", "status", "priority", "id"]
        for field in required_fields:
            if field not in todo:
                return False, f"Todo item missing required field: {field}"

        # Validate content
        content = todo.get("content")
        if not isinstance(content, str) or not content.strip():
            return False, "Todo content must be a non-empty string"

        # Validate status
        valid_statuses = ["pending", "in_progress", "completed", "cancelled"]
        status = todo.get("status")
        if status not in valid_statuses:
            return False, f"Todo status must be one of: {', '.join(valid_statuses)}"

        # Validate priority
        valid_priorities = ["high", "medium", "low"]
        priority = todo.get("priority")
        if priority not in valid_priorities:
            return False, f"Todo priority must be one of: {', '.join(valid_priorities)}"

        # Validate ID
        todo_id = todo.get("id")
        if todo_id is None:
            return False, "Todo id is required"

        # Accept string, int, or float IDs
        if not isinstance(todo_id, (str, int, float)):
            return False, "Todo id must be a string, integer, or number"

        # Convert to string and check if it's non-empty after stripping
        todo_id_str = str(todo_id).strip()
        if not todo_id_str:
            return False, "Todo id must not be empty"

        return True, ""

    def validate_todos_list(self, todos: list[dict[str, Any]]) -> tuple[bool, str]:
        """Validate a list of todo items.

        Args:
            todos: List of todo items to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(todos, list):
            return False, "Todos must be a list"

        # Check each todo item
        for i, todo in enumerate(todos):
            is_valid, error_msg = self.validate_todo_item(todo)
            if not is_valid:
                return False, f"Todo item {i}: {error_msg}"

        # Check for duplicate IDs
        todo_ids = [todo.get("id") for todo in todos]
        if len(todo_ids) != len(set(todo_ids)):
            return False, "Todo items must have unique IDs"

        return True, ""

    def filter_todos(
        self, 
        todos: list[dict[str, Any]], 
        status: str | None = None,
        priority: str | None = None
    ) -> list[dict[str, Any]]:
        """Filter todos by status and/or priority.
        
        Args:
            todos: List of todo items
            status: Optional status filter
            priority: Optional priority filter
            
        Returns:
            Filtered list of todos
        """
        filtered = todos
        
        if status:
            filtered = [t for t in filtered if t.get("status") == status]
            
        if priority:
            filtered = [t for t in filtered if t.get("priority") == priority]
            
        return filtered

    def get_todo_stats(self, todos: list[dict[str, Any]]) -> dict[str, Any]:
        """Get statistics about a todo list.
        
        Args:
            todos: List of todo items
            
        Returns:
            Dictionary with statistics
        """
        if not todos:
            return {
                "total": 0,
                "status_counts": {},
                "priority_counts": {},
                "completion_rate": 0.0
            }

        status_counts = {}
        priority_counts = {}
        
        for todo in todos:
            if isinstance(todo, dict):
                status = todo.get("status", "unknown")
                priority = todo.get("priority", "unknown")
                
                status_counts[status] = status_counts.get(status, 0) + 1
                priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        completed = status_counts.get("completed", 0)
        total = len(todos)
        completion_rate = (completed / total) * 100 if total > 0 else 0.0
        
        return {
            "total": total,
            "status_counts": status_counts,
            "priority_counts": priority_counts,
            "completion_rate": round(completion_rate, 1)
        }
