# Local-Only AI Coding Agent with MCP Integration

This project demonstrates the foundation for a local-only AI coding agent that can be embedded into any Software Development Life Cycle (SDLC) without requiring cloud connectivity. By leveraging the Model Control Protocol (MCP) server and LangChain, we create a powerful, privacy-focused development assistant that runs entirely on your local machine.

## Vision

Our goal is to create an AI coding agent that:
- Runs completely locally, with no cloud dependencies
- Can be integrated into any SDLC workflow
- Respects code privacy and security
- Provides powerful coding assistance without external API calls
- Works offline and in air-gapped environments

## Overview

The integration allows an AI agent to:
- Connect to a local MCP server
- List available tools
- Execute tools with proper parameter handling
- Handle responses in a structured format
- Operate entirely within your development environment

## Key Components

### 1. MCP Tool Integration
- `CustomMCPTool`: A LangChain tool wrapper for MCP server tools
- Handles tool execution with proper parameter validation
- Supports both synchronous and asynchronous execution
- Enables local tool execution without cloud dependencies

### 2. Tool Input Schema
```python
class MCPToolInput(BaseModel):
    tool_name: str
    parameters: Dict[str, Any]
```
- Enforces proper tool call structure
- Validates required parameters
- Ensures consistent parameter format
- Maintains type safety for local execution

### 3. Agent Configuration
- Uses `STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION` agent type
- Includes memory for conversation context
- Custom system message for proper tool usage
- Optimized for local execution

## Available Tools

| Tool Name | Category | Description |
|-----------|----------|-------------|
| `list_dir` | File System | Lists contents of a directory with sorting and filtering options |
| `read_file` | File System | Reads and returns the contents of a file |
| `edit_file` | File System | Makes changes to a file with proper context preservation |
| `grep_search` | File System | Performs fast text-based regex search across files |
| `file_search` | File System | Fuzzy file search based on path patterns |
| `delete_file` | File System | Safely deletes files with proper error handling |
| `view_code` | Code Analysis | Analyzes and returns information about code structure |
| `view_file` | Code Analysis | Provides detailed view of file contents with metadata |
| `propose_code` | Code Analysis | Suggests code improvements and modifications |
| `code_navigation` | LSP | Navigates through code structure using LSP capabilities |
| `symbol_info` | LSP | Retrieves detailed information about code symbols |
| `semantic_search` | LSP | Performs semantic code search using LSP features |
| `push_action` | Control | Adds a new action to the execution queue |
| `clear_actions` | Control | Clears all pending actions from the queue |
| `get_next_action` | Control | Retrieves the next action to be executed |
| `show_actions` | Control | Displays all pending actions in the queue |

Each tool is designed to work locally and can be used in combination to perform complex development tasks. The tools are organized into four main categories:

1. **File System Tools**
   - Basic file operations (list, read, edit, delete)
   - Search capabilities (grep, fuzzy search)
   - All operations maintain local file system integrity

2. **Code Analysis Tools**
   - Code structure analysis
   - File content analysis
   - Code improvement suggestions
   - Maintains code quality standards

3. **LSP (Language Server Protocol) Tools**
   - Advanced code navigation
   - Symbol information retrieval
   - Semantic code search
   - Language-aware operations

4. **Control Tools**
   - Action queue management
   - Execution flow control
   - Task scheduling
   - Workflow orchestration

For detailed parameter information and usage examples, use the MCP Inspector tool.

## Usage Example

```