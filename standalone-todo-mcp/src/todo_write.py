"""TodoWrite tool implementation for standalone todo management.

This module provides the TodoWrite tool for creating and managing todo lists.
Framework-agnostic and can be used with any MCP implementation.
"""

from typing import Any, Optional

from todo_base import TodoBaseTool
from todo_storage import TodoStorage


class TodoWriteTool(TodoBaseTool):
    """Tool for creating and managing todo lists."""

    def __init__(self, storage: TodoStorage):
        """Initialize with storage backend.
        
        Args:
            storage: TodoStorage instance to use
        """
        self.storage = storage

    @property
    def name(self) -> str:
        """Get the tool name."""
        return "todo_write"

    @property
    def description(self) -> str:
        """Get the tool description."""
        return """Create and manage structured task lists for any type of project or workflow.
This helps track progress, organize complex tasks, and demonstrate systematic approach.

## When to Use This Tool
Use this tool proactively for:

1. **Complex multi-step tasks** - Break down large projects into manageable pieces
2. **Project planning** - Organize work phases and deliverables  
3. **Workflow management** - Track progress through systematic processes
4. **Goal tracking** - Convert objectives into actionable steps
5. **User requests explicit task lists** - When someone asks to see steps or progress

## Example Usage Scenarios

**Software Development:**
1. Plan feature implementation steps
2. Track bug fix progress  
3. Organize testing and deployment tasks
4. Manage code review and documentation

**Project Management:**
1. Break down project phases
2. Track deliverable status
3. Organize team responsibilities
4. Monitor milestone progress

**Personal Productivity:**
1. Plan learning goals and study sessions
2. Organize household or administrative tasks
3. Track habit building and personal goals
4. Manage multi-step processes

## Task States and Management

1. **Task States**: Use these states to track progress:
   - pending: Task not yet started
   - in_progress: Currently working on (recommend limiting to 1-3 active tasks)
   - completed: Task finished successfully
   - cancelled: Task no longer needed

2. **Priority Levels**:
   - high: Critical tasks that need immediate attention
   - medium: Important tasks for steady progress
   - low: Nice-to-have tasks for when time permits

3. **Task Management Best Practices**:
   - Update task status in real-time as you work
   - Mark tasks complete immediately after finishing
   - Keep number of in_progress tasks manageable
   - Review and update todo lists regularly

This tool helps create clear, actionable task breakdowns that make complex work 
more manageable and progress more visible."""

    def write_todos(
        self, 
        session_id: str, 
        todos: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Write todos to storage.

        Args:
            session_id: Session identifier
            todos: List of todo items to store

        Returns:
            Dictionary with operation result
        """
        # Validate session ID
        is_valid, error_msg = self.validate_session_id(session_id)
        if not is_valid:
            return {"error": f"Invalid session_id: {error_msg}"}

        # Normalize todos list (auto-generate missing fields)
        todos = self.normalize_todos_list(todos)

        # Validate todos list
        is_valid, error_msg = self.validate_todos_list(todos)
        if not is_valid:
            return {"error": f"Invalid todos: {error_msg}"}

        try:
            # Store todos in storage
            self.storage.set_todos(session_id, todos)

            # Generate summary
            if todos:
                stats = self.get_todo_stats(todos)
                
                summary_parts = []
                if stats["status_counts"]:
                    status_summary = ", ".join(
                        [f"{count} {status}" for status, count in stats["status_counts"].items()]
                    )
                    summary_parts.append(f"Status: {status_summary}")

                if stats["priority_counts"]:
                    priority_summary = ", ".join(
                        [f"{count} {priority}" for priority, count in stats["priority_counts"].items()]
                    )
                    summary_parts.append(f"Priority: {priority_summary}")

                message = (
                    f"Successfully stored {len(todos)} todos for session {session_id}.\n"
                    + "; ".join(summary_parts)
                )

                return {
                    "success": True,
                    "message": message,
                    "session_id": session_id,
                    "todo_count": len(todos),
                    "stats": stats
                }
            else:
                return {
                    "success": True,
                    "message": f"Successfully cleared todos for session {session_id} (stored empty list).",
                    "session_id": session_id,
                    "todo_count": 0
                }

        except Exception as e:
            return {"error": f"Error storing todos: {str(e)}"}

    def update_todo_status(
        self, 
        session_id: str, 
        todo_id: str, 
        new_status: str
    ) -> dict[str, Any]:
        """Update the status of a specific todo item.

        Args:
            session_id: Session identifier
            todo_id: ID of the todo to update
            new_status: New status (pending, in_progress, completed, cancelled)

        Returns:
            Dictionary with operation result
        """
        # Validate inputs
        is_valid, error_msg = self.validate_session_id(session_id)
        if not is_valid:
            return {"error": f"Invalid session_id: {error_msg}"}

        valid_statuses = ["pending", "in_progress", "completed", "cancelled"]
        if new_status not in valid_statuses:
            return {"error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"}

        try:
            # Get current todos
            todos = self.storage.get_todos(session_id)
            
            # Find and update the todo
            todo_found = False
            for todo in todos:
                if todo.get("id") == todo_id:
                    old_status = todo.get("status")
                    todo["status"] = new_status
                    todo_found = True
                    break

            if not todo_found:
                return {"error": f"Todo with ID '{todo_id}' not found in session {session_id}"}

            # Save updated todos
            self.storage.set_todos(session_id, todos)

            return {
                "success": True,
                "message": f"Updated todo '{todo_id}' status from '{old_status}' to '{new_status}'",
                "session_id": session_id,
                "todo_id": todo_id,
                "old_status": old_status,
                "new_status": new_status
            }

        except Exception as e:
            return {"error": f"Error updating todo status: {str(e)}"}

    def add_todo(
        self, 
        session_id: str, 
        content: str, 
        priority: str = "medium",
        status: str = "pending",
        todo_id: Optional[str] = None
    ) -> dict[str, Any]:
        """Add a single todo to an existing session.

        Args:
            session_id: Session identifier
            content: Todo content/description
            priority: Priority level (high, medium, low)
            status: Initial status (pending, in_progress, completed, cancelled)
            todo_id: Optional custom ID, will be auto-generated if not provided

        Returns:
            Dictionary with operation result
        """
        # Validate inputs
        is_valid, error_msg = self.validate_session_id(session_id)
        if not is_valid:
            return {"error": f"Invalid session_id: {error_msg}"}

        # Get current todos
        current_todos = self.storage.get_todos(session_id)
        
        # Generate ID if not provided
        if not todo_id:
            existing_ids = {todo.get("id") for todo in current_todos}
            counter = len(current_todos) + 1
            while f"todo-{counter}" in existing_ids:
                counter += 1
            todo_id = f"todo-{counter}"

        # Create new todo
        new_todo = {
            "id": todo_id,
            "content": content,
            "status": status,
            "priority": priority
        }

        # Validate the new todo
        is_valid, error_msg = self.validate_todo_item(new_todo)
        if not is_valid:
            return {"error": f"Invalid todo: {error_msg}"}

        # Check for duplicate ID
        existing_ids = {todo.get("id") for todo in current_todos}
        if todo_id in existing_ids:
            return {"error": f"Todo with ID '{todo_id}' already exists in session {session_id}"}

        try:
            # Add to current todos and save
            updated_todos = current_todos + [new_todo]
            self.storage.set_todos(session_id, updated_todos)

            return {
                "success": True,
                "message": f"Added todo '{todo_id}' to session {session_id}",
                "session_id": session_id,
                "todo_id": todo_id,
                "total_todos": len(updated_todos)
            }

        except Exception as e:
            return {"error": f"Error adding todo: {str(e)}"}

    def delete_session(self, session_id: str) -> dict[str, Any]:
        """Delete an entire session and all its todos.

        Args:
            session_id: Session identifier to delete

        Returns:
            Dictionary with operation result
        """
        # Validate session ID
        is_valid, error_msg = self.validate_session_id(session_id)
        if not is_valid:
            return {"error": f"Invalid session_id: {error_msg}"}

        try:
            # Get current todo count for reporting
            todos = self.storage.get_todos(session_id)
            todo_count = len(todos)
            
            # Delete the session
            deleted = self.storage.delete_session(session_id)
            
            if deleted:
                return {
                    "success": True,
                    "message": f"Deleted session {session_id} and {todo_count} todos",
                    "session_id": session_id,
                    "deleted_todo_count": todo_count
                }
            else:
                return {
                    "success": False,
                    "message": f"Session {session_id} not found",
                    "session_id": session_id
                }

        except Exception as e:
            return {"error": f"Error deleting session: {str(e)}"}
