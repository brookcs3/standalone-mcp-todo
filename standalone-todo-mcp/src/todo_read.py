"""TodoRead tool implementation for standalone todo management.

This module provides the TodoRead tool for reading current todo lists.
Framework-agnostic and can be used with any MCP implementation.

Now enhanced with professional Awwwards-style formatting that applies:
- Swiss Grid System principles (Müller-Brockmann)
- Typography Hierarchy (Ellen Lupton)
- Awwwards Evaluation Criteria (40/30/20/10 weighting)
- Contextual styling and professional branding
"""

import json
from typing import Any, Optional

from todo_base import TodoBaseTool
from todo_storage import TodoStorage
from awwwards_formatter import AwwwardsTodoFormatter


class TodoReadTool(TodoBaseTool):
    """Tool for reading todo lists from storage."""

    def __init__(self, storage: TodoStorage):
        """Initialize with storage backend and professional formatter.
        
        Args:
            storage: TodoStorage instance to use
        """
        self.storage = storage
        self.formatter = AwwwardsTodoFormatter()  # Professional Awwwards formatter
        self._previous_todos = {}  # Track previous states for contextual styling

    @property
    def name(self) -> str:
        """Get the tool name."""
        return "todo_read"

    @property
    def description(self) -> str:
        """Get the tool description."""
        return """Read the current todo list for a session. This tool should be used proactively 
and frequently to ensure you are aware of the current task status and progress.

Use this tool frequently, especially in these situations:
- At the beginning of work sessions to see what's pending
- Before starting new tasks to prioritize work
- When asked about progress on tasks or projects
- Whenever you're uncertain about what to do next
- After completing tasks to update your understanding of remaining work
- After every few actions to ensure you're on track

Usage:
- Requires a session_id parameter to identify the work session
- Returns a list of todo items with their status, priority, and content
- Use this information to track progress and plan next steps
- If no todos exist for the session, returns an empty list

This tool helps with:
- Project management and task tracking
- Workflow organization and progress monitoring
- Breaking down complex work into manageable steps
- Demonstrating thoroughness and systematic approach"""

    def read_todos(
        self, 
        session_id: str,
        status_filter: Optional[str] = None,
        priority_filter: Optional[str] = None,
        include_stats: bool = False,
        context: str = 'user_request',
        show_scorecard: bool = True
    ) -> str:  # Now returns formatted string instead of dict
        """Read todos for a session with professional Awwwards formatting.

        Args:
            session_id: Session identifier
            status_filter: Optional filter by status (pending, in_progress, completed, cancelled)
            priority_filter: Optional filter by priority (high, medium, low)
            include_stats: Whether to include statistics in the response
            context: Context for styling (user_request, completion, progress, etc.)
            show_scorecard: Whether to show Awwwards evaluation scorecard

        Returns:
            Professionally formatted string with Swiss Grid design and Awwwards evaluation
        """
        # Validate session ID
        is_valid, error_msg = self.validate_session_id(session_id)
        if not is_valid:
            return f"❌ Invalid session_id: {error_msg}"

        try:
            # Get todos from storage
            todos = self.storage.get_todos(session_id)
            
            # Store previous state for contextual detection
            previous_todos = self._previous_todos.get(session_id)
            self._previous_todos[session_id] = todos.copy()
            
            # Apply filters if specified
            if status_filter or priority_filter:
                todos = self.filter_todos(todos, status_filter, priority_filter)

            # Build result dictionary
            result = {
                "session_id": session_id,
                "todos": todos,
                "count": len(todos)
            }

            # Add statistics if requested
            if include_stats:
                result["stats"] = self.get_todo_stats(todos)
                
            # Add session info
            last_updated = self.storage.get_session_last_updated(session_id)
            if last_updated:
                result["last_updated"] = last_updated

            # Return professionally formatted display
            return self.formatter.format_professional_todo_display(
                result=result,
                context=context,
                show_scorecard=show_scorecard,
                previous_todos=previous_todos
            )

        except Exception as e:
            return f"❌ Error reading todos: {str(e)}"

    def get_all_sessions(self) -> str:  # Now returns formatted string
        """Get information about all active sessions with professional formatting.
        
        Returns:
            Professionally formatted string with session overview
        """
        try:
            session_ids = self.storage.get_all_session_ids()
            sessions_info = []
            
            for session_id in session_ids:
                todos = self.storage.get_todos(session_id)
                last_updated = self.storage.get_session_last_updated(session_id)
                stats = self.get_todo_stats(todos)
                
                sessions_info.append({
                    "session_id": session_id,
                    "todo_count": len(todos),
                    "last_updated": last_updated,
                    "completion_rate": stats["completion_rate"],
                    "status_counts": stats["status_counts"]
                })
            
            result = {
                "total_sessions": len(session_ids),
                "sessions": sessions_info,
                "storage_stats": self.storage.get_stats()
            }
            
            # Return professionally formatted session overview
            return self.formatter.format_session_overview(result)
            
        except Exception as e:
            return f"❌ Error getting sessions: {str(e)}"

    def find_active_work(self) -> dict[str, Any]:
        """Find the most recent session with unfinished work.
        
        Returns:
            Dictionary with active session information
        """
        try:
            latest_session = self.storage.find_latest_active_session()
            
            if not latest_session:
                return {
                    "message": "No active sessions with unfinished work found",
                    "active_session": None
                }
            
            # Get details about the active session
            todos = self.storage.get_todos(latest_session)
            pending_todos = self.filter_todos(todos, status="pending")
            in_progress_todos = self.filter_todos(todos, status="in_progress")
            
            return {
                "active_session": latest_session,
                "total_todos": len(todos),
                "pending_count": len(pending_todos),
                "in_progress_count": len(in_progress_todos),
                "next_pending_todos": pending_todos[:3],  # Show first 3 pending
                "current_in_progress": in_progress_todos,
                "last_updated": self.storage.get_session_last_updated(latest_session)
            }
            
        except Exception as e:
            return {"error": f"Error finding active work: {str(e)}"}

    def continue_from_last_conversation(self) -> str:  # New method!
        """Continue from Last Conversation - shows active work with professional formatting.
        
        This is the main entry point for the 'Continue from Last Conversation' feature.
        It finds active work and presents it with full Awwwards professional styling.
        
        Returns:
            Professionally formatted string with continuation information
        """
        try:
            # Get active work data
            continuation_data = self.find_active_work()
            
            # Return professionally formatted continuation display
            return self.formatter.format_continuation_display(continuation_data)
            
        except Exception as e:
            return f"❌ Error continuing from last conversation: {str(e)}"
