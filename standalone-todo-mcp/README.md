# Standalone Todo MCP Server

A comprehensive Model Context Protocol (MCP) server for todo and task management. This server provides AI assistants with powerful todo management capabilities, enabling them to help you organize projects, track progress, and manage workflows systematically.

## 🚀 Features

- **Session-based Organization** - Organize todos by project, context, or timeframe
- **Status Tracking** - Track tasks through pending → in_progress → completed workflow
- **Priority Management** - Set priorities (high, medium, low) for better task organization
- **Persistent Storage** - Choose between in-memory or file-based persistence
- **Progress Monitoring** - Get statistics and progress reports
- **Flexible Filtering** - Filter by status, priority, or other criteria
- **Multi-session Support** - Manage multiple projects simultaneously

## 📦 Installation

### From Source

```bash
# Clone or download the project
cd standalone-todo-mcp

# Install dependencies
pip install mcp

# Install the package in development mode
pip install -e .
```

### Using pip (if published)

```bash
pip install standalone-todo-mcp
```

## 🔧 Configuration

### Basic Setup

Add to your MCP client configuration (e.g., Claude Desktop):

```json
{
  "mcpServers": {
    "standalone-todo-mcp": {
      "command": "python",
      "args": ["/path/to/standalone-todo-mcp/src/server.py"]
    }
  }
}
```

### With Persistent Storage

To enable file-based storage that persists between sessions:

```json
{
  "mcpServers": {
    "standalone-todo-mcp": {
      "command": "python", 
      "args": [
        "/path/to/standalone-todo-mcp/src/server.py",
        "--storage-file",
        "/path/to/your/todos.json"
      ]
    }
  }
}
```

### Using the Packaged Version

If installed via pip:

```json
{
  "mcpServers": {
    "standalone-todo-mcp": {
      "command": "standalone-todo-mcp",
      "args": ["--storage-file", "/path/to/your/todos.json"]
    }
  }
}
```

## 🛠️ Available Tools

### `todo_read`
Read the current todo list for a session.

**Parameters:**
- `session_id` (required): Unique identifier for the work session
- `status_filter` (optional): Filter by status (pending, in_progress, completed, cancelled)
- `priority_filter` (optional): Filter by priority (high, medium, low)
- `include_stats` (optional): Include progress statistics

**Example:**
```python
todo_read(session_id="project-alpha", status_filter="pending", include_stats=True)
```

### `todo_write` 
Create and manage structured task lists.

**Parameters:**
- `session_id` (required): Unique identifier for the work session
- `todos` (required): Array of todo items with content, status, priority, and optional id

**Example:**
```python
todo_write(
    session_id="project-alpha",
    todos=[
        {
            "content": "Design user interface mockups",
            "status": "pending", 
            "priority": "high",
            "id": "ui-design"
        },
        {
            "content": "Set up development environment",
            "status": "in_progress",
            "priority": "medium", 
            "id": "dev-setup"
        }
    ]
)
```

### `todo_update_status`
Update the status of a specific todo item.

**Parameters:**
- `session_id` (required): Session identifier
- `todo_id` (required): ID of the todo to update
- `new_status` (required): New status (pending, in_progress, completed, cancelled)

### `todo_add_item`
Add a single todo item to an existing session.

**Parameters:**
- `session_id` (required): Session identifier
- `content` (required): Task description
- `priority` (optional): Priority level (default: medium)
- `status` (optional): Initial status (default: pending)
- `todo_id` (optional): Custom ID (auto-generated if not provided)

### `todo_get_sessions`
Get information about all active sessions.

### `todo_find_active_work`
Find the most recent session with unfinished work.

## 📋 Usage Examples

### Project Planning
```python
# Start a new project
todo_write(
    session_id="website-redesign-2024",
    todos=[
        {"content": "Research competitor websites", "status": "pending", "priority": "high"},
        {"content": "Create wireframes", "status": "pending", "priority": "high"},
        {"content": "Design color scheme", "status": "pending", "priority": "medium"},
        {"content": "Code frontend components", "status": "pending", "priority": "medium"},
        {"content": "User testing", "status": "pending", "priority": "low"}
    ]
)

# Check progress
todo_read(session_id="website-redesign-2024", include_stats=True)

# Mark task as started
todo_update_status(
    session_id="website-redesign-2024",
    todo_id="todo-1", 
    new_status="in_progress"
)
```

### Daily Task Management
```python
# Create daily todos
todo_write(
    session_id="2024-01-15",
    todos=[
        {"content": "Review pull requests", "status": "pending", "priority": "high"},
        {"content": "Weekly team meeting", "status": "pending", "priority": "medium"},
        {"content": "Update project documentation", "status": "pending", "priority": "low"}
    ]
)

# Add urgent task that came up
todo_add_item(
    session_id="2024-01-15",
    content="Fix critical bug in production",
    priority="high",
    status="in_progress"
)
```

### Multi-Project Workflow
```python
# Check all active work
todo_find_active_work()

# Get overview of all projects
todo_get_sessions()

# Work on specific project
todo_read(session_id="mobile-app", status_filter="in_progress")
```

## 🏗️ Architecture

The server is built with a modular architecture:

- **`todo_base.py`** - Base validation and utility functions
- **`todo_storage.py`** - Storage layer with in-memory and file persistence
- **`todo_read.py`** - Read operations and filtering
- **`todo_write.py`** - Write operations and task management
- **`server.py`** - MCP server implementation

## 🔒 Data Storage

### In-Memory Mode (Default)
- Fast performance
- Data lost when server restarts
- Good for temporary or session-based workflows

### File-Based Persistence
- Data persists between server restarts
- Automatic backup and recovery
- JSON format for easy inspection and portability

Storage file format:
```json
{
  "sessions": {
    "session-id": {
      "todos": [...],
      "last_updated": 1640995200.0
    }
  },
  "last_saved": 1640995200.0
}
```

## 🧪 Development

### Setup Development Environment
```bash
# Install with development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src/
isort src/

# Type checking
mypy src/
```

### Running Tests
```bash
pytest tests/
```

## 🤝 Integration Examples

### With Claude Desktop
Perfect for project management, breaking down complex tasks, and tracking progress through conversations.

### With Custom MCP Clients
Use the server programmatically for:
- Project management tools
- Workflow automation
- Task tracking systems
- Personal productivity apps

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Support

For issues, questions, or contributions:
1. Check existing issues
2. Create a new issue with detailed description
3. Include your configuration and error messages

## 🔮 Roadmap

- [ ] Due date support
- [ ] Task dependencies
- [ ] Tagging system
- [ ] Export/import functionality
- [ ] Web interface
- [ ] Integration with external task managers
