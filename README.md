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

## Usage Example

```python
# Initialize the agent
agent = initialize_agent(
    tools=[CustomMCPTool()],
    llm=OllamaLLM(model="gemma3"),  # Local LLM
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# Execute a tool
response = agent.invoke({
    "input": "List the contents of the current directory"
})
```

## Tool Call Format

The agent must format tool calls exactly as follows:
```json
{
    "tool_name": "list_dir",
    "parameters": {
        "directory_path": ".",
        "sort_by": "name",
        "sort_order": "asc"
    }
}
```

## Important Rules

1. Tool calls must be direct dictionaries with `tool_name` and `parameters` keys
2. All required parameters must be included
3. Parameter names must match exactly (e.g., `directory_path` not `path`)
4. Use "." for current directory paths
5. Always check tool descriptions for required parameters

## Error Handling

The integration includes robust error handling for:
- Invalid parameter formats
- Missing required parameters
- Server connection issues
- Tool execution errors
- Local resource constraints

## Development

To run the example:
1. Start the local MCP server:
```bash
python examples/mcp/server_example.py
```
It will listen on http://localhost:8000/sse

You can test it using https://github.com/modelcontextprotocol/inspector
Use Tools->List Tools after connection.
You can call any method providing valid parameter.

2. Run the client example:
```bash
python examples/langchain/mcp_server_usage.py
```
For now it just attempts to call list_dir and print list of files:
- Direct MCP call (using SSE client)
- From selected LLM (I use ollama with gemma3 model for testing)

## SDLC Integration

The agent is designed to be integrated into various SDLC stages:

### 1. Development
- Code generation and completion
- Refactoring assistance
- Documentation generation
- Test case creation

### 2. Code Review
- Static analysis
- Best practice checking
- Security vulnerability scanning
- Performance optimization suggestions

### 3. Testing
- Test case generation
- Test coverage analysis
- Test result interpretation
- Test optimization

### 4. Deployment
- Configuration validation
- Environment setup
- Deployment script generation
- Rollback planning

## Security and Privacy

- All processing happens locally
- No code or data is sent to external servers
- Supports air-gapped environments
- Maintains code confidentiality
- Compliant with strict security requirements

## Notes

- The agent uses the ReAct format (Reason + Act) for structured responses
- Tool parameters are validated against the MCPToolInput schema
- The system message enforces proper tool call formatting
- Debug logging is available for troubleshooting
- Designed for offline-first operation
- Supports integration with local development tools 