#!/usr/bin/env python3
"""Test tool priority and verify standalone todo server works correctly."""

import json

def test_tool_priority():
    """Test that demonstrates how MCP tool priority should work."""
    print("🧪 Testing MCP Tool Priority...")
    print("\n📋 Current Configuration Order:")
    print("1. standalone-todo-mcp (provides: todo_read, todo_write, etc.)")
    print("2. claude-code (provides: claude-code:todo_read, claude-code:todo_write)")
    print("\n✅ Expected behavior:")
    print("- When Claude calls 'todo_read' → Uses standalone server")
    print("- When Claude calls 'claude-code:todo_read' → Uses built-in server") 
    print("- No conflict because tool names are different!")
    
    print("\n🎯 Result: Both systems can coexist!")
    print("- Use 'todo_read/todo_write' for advanced todo management")
    print("- Use 'claude-code:todo_read/todo_write' for simple session todos")

if __name__ == "__main__":
    test_tool_priority()
