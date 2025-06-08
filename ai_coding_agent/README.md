# AI Coding Agent Toolset

A comprehensive Python package that implements an AI coding agent toolset with both native LLM and MCP server interfaces. This package provides a set of tools for AI-assisted coding, code analysis, and development automation.

## Features

- Native LLM interface for direct integration with language models
- MCP server interface for remote access
- Comprehensive set of coding tools including:
  - Codebase search and analysis
  - File operations and content management
  - Web search and content retrieval
  - Memory management for context preservation
  - Code modification and suggestion capabilities

## Installation

```bash
pip install ai-coding-agent
```

## Quick Start

### Using with LangChain

```python
from ai_coding_agent.interfaces.langchain import AICodingAgentToolkit
from langchain.agents import initialize_agent
from langchain.llms import Ollama

# Initialize the toolkit
toolkit = AICodingAgentToolkit()

# Create an agent with the toolkit
llm = Ollama(model="codellama")
agent = initialize_agent(
    toolkit.get_tools(),
    llm,
    agent="zero-shot-react-description",
    verbose=True
)

# Use the agent
agent.run("Search for all Python files in the current directory")
```

### Using with MCP Server

```python
from ai_coding_agent.interfaces.mcp import MCPServer

# Start the MCP server
server = MCPServer()
server.start()
```

## Available Tools

The package provides the following tools:

- `codebase_search`: Find relevant code snippets across the codebase
- `create_memory`: Save important context to memory
- `find_by_name`: Search for files/directories
- `grep_search`: Find exact pattern matches in files
- `list_dir`: List directory contents
- `list_resources`: List available MCP server resources
- `propose_code`: Propose code changes
- `read_resource`: Read resource contents
- `read_url_content`: Read content from a URL
- `search_in_file`: Search within a specific file
- `search_web`: Perform a web search
- `suggested_responses`: Provide response suggestions
- `view_code_item`: View a specific code item
- `view_content_chunk`: View a specific content chunk
- `view_file`: View file contents

## Development

1. Clone the repository
2. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```
3. Run tests:
   ```bash
   pytest
   ```

## License

MIT License 