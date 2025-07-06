#!/usr/bin/env python3
"""Standalone Todo MCP Server.

A Model Context Protocol (MCP) server that provides todo management capabilities.
This server can be used with any MCP client to manage tasks, projects, and workflows.

Features:
- Create and manage todo lists with session isolation
- Track task status (pending, in_progress, completed, cancelled)
- Set task priorities (high, medium, low)
- Persistent storage with both in-memory and file-based options
- Session-based organization for different projects or contexts
- Statistics and progress tracking

Usage:
    python server.py [--storage-file path/to/storage.json]

The server will start on stdin/stdout for MCP communication.
"""

import argparse
import asyncio
import os
import sys
from typing import Any, Sequence

# Add src directory to path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from mcp.server import Server, NotificationOptions
    from mcp.server.models import InitializationOptions
    import mcp.server.stdio
    import mcp.types as types
except ImportError:
    print("Error: MCP library not found. Install with: pip install mcp", file=sys.stderr)
    sys.exit(1)

from todo_storage import TodoStorage
from todo_read import TodoReadTool
from todo_write import TodoWriteTool


# Global storage instance
storage = None
read_tool = None
write_tool = None


def setup_storage(storage_file: str | None = None) -> None:
    """Initialize storage and tools."""
    global storage, read_tool, write_tool
    
    storage = TodoStorage(storage_file)
    read_tool = TodoReadTool(storage)
    write_tool = TodoWriteTool(storage)


# Create the MCP server instance
server = Server("standalone-todo-mcp")


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools."""
    return [
        types.Tool(
            name="todo_read",
            description="""Read the current todo list for a session. Use this tool proactively
and frequently to stay aware of current task status and progress.

Use this tool frequently, especially:
- At the beginning of work sessions to see what's pending
- Before starting new tasks to prioritize work  
- When asked about progress on tasks or projects
- Whenever you're uncertain about what to do next
- After completing tasks to update your understanding of remaining work
- After every few actions to ensure you're on track

Returns a list of todo items with their status, priority, and content.
If no todos exist for the session, returns an empty list.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Unique identifier for the work session (generate using timestamp or meaningful name)"
                    },
                    "status_filter": {
                        "type": "string",
                        "enum": ["pending", "in_progress", "completed", "cancelled"],
                        "description": "Optional filter by status"
                    },
                    "priority_filter": {
                        "type": "string", 
                        "enum": ["high", "medium", "low"],
                        "description": "Optional filter by priority"
                    },
                    "include_stats": {
                        "type": "boolean",
                        "description": "Whether to include statistics in the response",
                        "default": False
                    }
                },
                "required": ["session_id"]
            }
        ),
        types.Tool(
            name="todo_write",
            description="""Create and manage structured task lists for any type of project or workflow.
This helps track progress, organize complex tasks, and demonstrate systematic approach.

## When to Use This Tool
Use this tool proactively for:

1. **Complex multi-step tasks** - Break down large projects into manageable pieces
2. **Project planning** - Organize work phases and deliverables  
3. **Workflow management** - Track progress through systematic processes
4. **Goal tracking** - Convert objectives into actionable steps
5. **User requests explicit task lists** - When someone asks to see steps or progress

## Task States and Management

**Task States**: Use these states to track progress:
- pending: Task not yet started
- in_progress: Currently working on (recommend limiting to 1-3 active tasks)
- completed: Task finished successfully  
- cancelled: Task no longer needed

**Priority Levels**:
- high: Critical tasks that need immediate attention
- medium: Important tasks for steady progress
- low: Nice-to-have tasks for when time permits

This tool helps create clear, actionable task breakdowns that make complex work
more manageable and progress more visible.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Unique identifier for the work session (generate using timestamp or meaningful name)"
                    },
                    "todos": {
                        "type": "array",
                        "description": "The complete todo list to store for this session",
                        "items": {
                            "type": "object",
                            "properties": {
                                "content": {
                                    "type": "string",
                                    "description": "Description of the task to be completed"
                                },
                                "status": {
                                    "type": "string",
                                    "enum": ["pending", "in_progress", "completed", "cancelled"],
                                    "description": "Current status of the task"
                                },
                                "priority": {
                                    "type": "string", 
                                    "enum": ["high", "medium", "low"],
                                    "description": "Priority level of the task"
                                },
                                "id": {
                                    "type": "string",
                                    "description": "Unique identifier for the task (will be auto-generated if not provided)"
                                }
                            },
                            "required": ["content", "status", "priority"]
                        },
                        "minItems": 1
                    }
                },
                "required": ["session_id", "todos"]
            }
        ),
        types.Tool(
            name="todo_update_status",
            description="""Update the status of a specific todo item. Use this to mark tasks as 
in_progress when you start working on them, or completed when finished.

Recommended workflow:
- Mark ONE task as in_progress when you start working on it
- Complete current tasks before starting new ones
- Update status immediately after state changes""",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Session identifier"
                    },
                    "todo_id": {
                        "type": "string", 
                        "description": "ID of the todo to update"
                    },
                    "new_status": {
                        "type": "string",
                        "enum": ["pending", "in_progress", "completed", "cancelled"],
                        "description": "New status for the task"
                    }
                },
                "required": ["session_id", "todo_id", "new_status"]
            }
        ),
        types.Tool(
            name="todo_add_item",
            description="""Add a single todo item to an existing session. Useful for adding
tasks that come up during work without recreating the entire list.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Session identifier"
                    },
                    "content": {
                        "type": "string",
                        "description": "Todo content/description"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["high", "medium", "low"], 
                        "description": "Priority level",
                        "default": "medium"
                    },
                    "status": {
                        "type": "string",
                        "enum": ["pending", "in_progress", "completed", "cancelled"],
                        "description": "Initial status",
                        "default": "pending"
                    },
                    "todo_id": {
                        "type": "string",
                        "description": "Optional custom ID (will be auto-generated if not provided)"
                    }
                },
                "required": ["session_id", "content"]
            }
        ),
        types.Tool(
            name="todo_get_sessions",
            description="""Get information about all active sessions with todos. 
Useful for finding previous work or understanding overall progress.""",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        ),
        types.Tool(
            name="todo_find_active_work", 
            description="""Find the most recent session with unfinished work.
Helpful for resuming previous tasks or finding what to work on next.""",
            inputSchema={
                "type": "object", 
                "properties": {},
                "additionalProperties": False
            }
        ),
        types.Tool(
            name="todo_continue_from_last_conversation",
            description="""🔄 Continue from Last Conversation - Smart session resumption with professional Awwwards styling.

This tool provides the ultimate 'pick up where you left off' experience by:

✅ Finding your most recent active work session automatically
✅ Showing current in-progress tasks with Swiss Grid design
✅ Suggesting next priority actions from pending queue  
✅ Displaying progress metrics and completion rates
✅ Providing smart recommendations for immediate next steps
✅ Professional Awwwards evaluation and achievement tracking

PERFECT FOR:
- Starting new chat sessions and wanting to continue previous work
- Quickly understanding current project status and priorities  
- Getting context-aware suggestions for immediate next actions
- Seeing beautiful professional displays of work progress

No parameters needed - just call it and get instantly oriented with your active projects!""",
            inputSchema={
                "type": "object", 
                "properties": {},
                "additionalProperties": False
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict[str, Any] | None
) -> list[types.TextContent]:
    """Handle tool calls."""
    if not arguments:
        arguments = {}
        
    try:
        if name == "todo_read":
            session_id = arguments.get("session_id")
            status_filter = arguments.get("status_filter")
            priority_filter = arguments.get("priority_filter") 
            include_stats = arguments.get("include_stats", False)
            
            result = read_tool.read_todos(
                session_id=session_id,
                status_filter=status_filter,
                priority_filter=priority_filter,
                include_stats=include_stats
            )
            
            return [types.TextContent(type="text", text=str(result))]
            
        elif name == "todo_write":
            session_id = arguments.get("session_id")
            todos = arguments.get("todos", [])
            
            result = write_tool.write_todos(session_id=session_id, todos=todos)
            return [types.TextContent(type="text", text=str(result))]
            
        elif name == "todo_update_status":
            session_id = arguments.get("session_id")
            todo_id = arguments.get("todo_id")
            new_status = arguments.get("new_status")
            
            result = write_tool.update_todo_status(
                session_id=session_id,
                todo_id=todo_id, 
                new_status=new_status
            )
            return [types.TextContent(type="text", text=str(result))]
            
        elif name == "todo_add_item":
            session_id = arguments.get("session_id")
            content = arguments.get("content")
            priority = arguments.get("priority", "medium")
            status = arguments.get("status", "pending")
            todo_id = arguments.get("todo_id")
            
            result = write_tool.add_todo(
                session_id=session_id,
                content=content,
                priority=priority,
                status=status,
                todo_id=todo_id
            )
            return [types.TextContent(type="text", text=str(result))]
            
        elif name == "todo_get_sessions":
            result = read_tool.get_all_sessions()
            return [types.TextContent(type="text", text=str(result))]
            
        elif name == "todo_find_active_work":
            result = read_tool.find_active_work()
            return [types.TextContent(type="text", text=str(result))]

        elif name == "todo_continue_from_last_conversation":
            result = read_tool.continue_from_last_conversation()
            return [types.TextContent(type="text", text=str(result))]


            
        else:
            return [types.TextContent(
                type="text", 
                text=f"Unknown tool: {name}"
            )]
            
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"Error executing tool {name}: {str(e)}"
        )]


async def main():
    """Main entry point for the MCP server."""
    parser = argparse.ArgumentParser(description="Standalone Todo MCP Server")
    parser.add_argument(
        "--storage-file",
        help="Path to JSON file for persistent storage (optional, uses in-memory if not provided)"
    )
    
    args = parser.parse_args()
    
    # Initialize storage
    setup_storage(args.storage_file)
    
    # Run the server
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream, 
            InitializationOptions(
                server_name="standalone-todo-mcp",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities=None,
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
