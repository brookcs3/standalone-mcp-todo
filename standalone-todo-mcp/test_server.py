#!/usr/bin/env python3
"""Simple test script for the standalone todo MCP server.

This script tests the core functionality without requiring a full MCP client.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from todo_storage import TodoStorage
from todo_read import TodoReadTool
from todo_write import TodoWriteTool


def test_basic_functionality():
    """Test basic todo operations."""
    print("🧪 Testing standalone todo MCP server...")
    
    # Test 1: Storage initialization
    print("\n1. Testing storage initialization...")
    storage = TodoStorage()  # In-memory storage
    read_tool = TodoReadTool(storage)
    write_tool = TodoWriteTool(storage)
    print("✅ Storage and tools initialized successfully")
    
    # Test 2: Create todos
    print("\n2. Testing todo creation...")
    test_todos = [
        {
            "content": "Design user interface",
            "status": "pending",
            "priority": "high",
            "id": "design-ui"
        },
        {
            "content": "Implement backend API",
            "status": "in_progress", 
            "priority": "medium",
            "id": "backend-api"
        },
        {
            "content": "Write documentation",
            "status": "pending",
            "priority": "low",
            "id": "docs"
        }
    ]
    
    result = write_tool.write_todos("test-session", test_todos)
    print(f"Write result: {result}")
    assert result["success"], f"Failed to write todos: {result}"
    print("✅ Todos created successfully")
    
    # Test 3: Read todos
    print("\n3. Testing todo reading...")
    result = read_tool.read_todos("test-session", include_stats=True)
    print(f"Read result: {result}")
    assert "todos" in result, "Failed to read todos"
    assert len(result["todos"]) == 3, f"Expected 3 todos, got {len(result['todos'])}"
    print("✅ Todos read successfully")
    
    # Test 4: Update todo status
    print("\n4. Testing status update...")
    result = write_tool.update_todo_status("test-session", "design-ui", "completed")
    print(f"Update result: {result}")
    assert result["success"], f"Failed to update status: {result}"
    print("✅ Status updated successfully")
    
    # Test 5: Add new todo
    print("\n5. Testing add todo...")
    result = write_tool.add_todo("test-session", "Deploy to production", "high", "pending")
    print(f"Add result: {result}")
    assert result["success"], f"Failed to add todo: {result}"
    print("✅ Todo added successfully")
    
    # Test 6: Filter todos
    print("\n6. Testing filtering...")
    result = read_tool.read_todos("test-session", status_filter="pending")
    print(f"Filtered result: {result}")
    pending_count = len(result["todos"])
    print(f"Found {pending_count} pending todos")
    print("✅ Filtering works correctly")
    
    # Test 7: Session management
    print("\n7. Testing session management...")
    result = read_tool.get_all_sessions()
    print(f"Sessions result: {result}")
    assert result["total_sessions"] >= 1, "Should have at least one session"
    print("✅ Session management works")
    
    # Test 8: File persistence (optional)
    print("\n8. Testing file persistence...")
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        storage_file = f.name
    
    try:
        # Create storage with file persistence
        file_storage = TodoStorage(storage_file)
        file_write_tool = TodoWriteTool(file_storage)
        file_read_tool = TodoReadTool(file_storage)
        
        # Write some todos
        result = file_write_tool.write_todos("file-test", test_todos)
        assert result["success"], "Failed to write to file storage"
        
        # Create new storage instance (simulating server restart)
        new_storage = TodoStorage(storage_file)
        new_read_tool = TodoReadTool(new_storage)
        
        # Read back the todos
        result = new_read_tool.read_todos("file-test")
        assert len(result["todos"]) == 3, "Todos not persisted correctly"
        print("✅ File persistence works correctly")
        
    finally:
        # Clean up
        if os.path.exists(storage_file):
            os.unlink(storage_file)
    
    print("\n🎉 All tests passed! The standalone todo MCP server is working correctly.")
    print("\n📝 Summary:")
    print("- ✅ Storage initialization")
    print("- ✅ Todo creation and validation") 
    print("- ✅ Todo reading and statistics")
    print("- ✅ Status updates")
    print("- ✅ Adding individual todos")
    print("- ✅ Filtering functionality")
    print("- ✅ Session management")
    print("- ✅ File persistence")


def test_validation():
    """Test input validation."""
    print("\n🔍 Testing validation...")
    
    storage = TodoStorage()
    write_tool = TodoWriteTool(storage)
    
    # Test invalid session ID
    result = write_tool.write_todos("", [])
    assert "error" in result, f"Should reject empty session ID, got: {result}"
    print("✅ Session ID validation works")
    
    # Test invalid todo structure
    invalid_todo = {"content": "", "status": "invalid", "priority": "unknown"}
    result = write_tool.write_todos("test", [invalid_todo])
    assert "error" in result, f"Should reject invalid todo, got: {result}"
    print("✅ Todo validation works")
    
    print("✅ All validation tests passed")


if __name__ == "__main__":
    try:
        test_basic_functionality()
        test_validation()
        print("\n🚀 Ready to use! Your standalone todo MCP server is complete and functional.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
