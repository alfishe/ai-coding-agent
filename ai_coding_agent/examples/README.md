# AI Coding Agent Examples

This directory contains examples demonstrating how to use the AI Coding Agent tools with different interfaces.

## LangChain Examples

### Basic Usage (`langchain/basic_usage.py`)

This example shows how to:
- Initialize the AI Coding Agent toolkit
- Create a basic agent with all available tools
- Run common coding tasks using the agent

To run:
```bash
python examples/langchain/basic_usage.py
```

### Custom Agent (`langchain/custom_agent.py`)

This example demonstrates:
- Creating a custom agent with specific tools
- Using a custom prompt template
- Implementing a code analysis agent

To run:
```bash
python examples/langchain/custom_agent.py
```

## MCP Server Examples

### Server Example (`mcp/server_example.py`)

This example shows how to:
- Start the MCP server
- Make API calls to the server
- Use various tools through the HTTP interface

To run:
```bash
python examples/mcp/server_example.py
```

### Client Example (`mcp/client_example.py`)

This example demonstrates:
- Creating a client for the MCP server
- Making asynchronous API calls
- Using different tools through the client

To run:
```bash
python examples/mcp/client_example.py
```

## Prerequisites

Before running the examples, make sure you have:

1. Installed the package in development mode:
   ```bash
   pip install -e ".[dev]"
   ```

2. For LangChain examples:
   - Ollama installed and running
   - CodeLlama model pulled (`ollama pull codellama`)

3. For MCP server examples:
   - No other service running on port 8000

## Notes

- The examples use async/await for better performance
- Error handling is included to demonstrate proper usage
- The examples can be modified to use different LLMs or configurations
- The MCP server examples can be adapted to use different host/port settings 