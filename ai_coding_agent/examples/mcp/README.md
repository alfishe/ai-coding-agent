# MCP Server Examples

This directory contains examples demonstrating how to use the AI Coding Agent tools through the MCP (Model Control Protocol) server interface.

## Overview

The MCP server provides a RESTful API interface for all AI Coding Agent tools, allowing you to:
- Access tools remotely over HTTP
- Integrate with any programming language that supports HTTP requests
- Scale tool usage across multiple clients
- Monitor and manage tool execution

## Examples

### 1. Server Example (`server_example.py`)

This example demonstrates how to:
- Start the MCP server
- Make direct API calls to the server
- Use basic tools like directory listing and file search

To run:
```bash
PYTHONPATH=ai_coding_agent/src python ai_coding_agent/examples/mcp/server_example.py
```

Expected output:
```
Available tools:
- list_dir: List contents of a directory
- find_by_name: Search for files and directories by name pattern
...

Directory listing result:
{
    "success": true,
    "data": [
        {"name": "example.py", "type": "file", "size": 1234},
        ...
    ]
}

Python files found:
{
    "success": true,
    "data": ["example.py", "test.py", ...]
}
```

### 2. Client Example (`client_example.py`)

This example shows how to:
- Create a reusable client for the MCP server
- Make asynchronous API calls
- Use more complex tools like code search and modification

To run:
```bash
python client_example.py
```

Expected output:
```
Available tools:
- grep_search: Search for patterns in files
- view_file: View file contents
...

Search results for async functions:
{
    "success": true,
    "data": [
        {
            "file": "example.py",
            "line": 10,
            "content": "async def main():"
        },
        ...
    ]
}
```

## API Endpoints

The MCP server provides the following endpoints:

1. `GET /tools`
   - Lists all available tools and their parameters
   - No authentication required

2. `POST /tools/{tool_name}`
   - Executes a specific tool
   - Request body:
     ```json
     {
         "tool_name": "string",
         "parameters": {
             "param1": "value1",
             "param2": "value2"
         }
     }
     ```

## Prerequisites

Before running the examples:

1. Install the package in development mode:
   ```bash
   pip install -e ".[dev]"
   ```

2. Ensure no other service is running on port 8000

3. Install required dependencies:
   ```bash
   pip install aiohttp
   ```

## Running the Server

You can start the MCP server in two ways:

1. Using the example:
   ```python
   from ai_coding_agent import MCPServer
   
   server = MCPServer(host="localhost", port=8000)
   server.start()  # Synchronous
   # or
   await server.start_async()  # Asynchronous
   ```

2. Using the command line:
   ```bash
   python -m ai_coding_agent.interfaces.mcp
   ```

## Error Handling

The examples include error handling for common scenarios:
- Server not running
- Invalid tool names
- Missing required parameters
- File system errors

## Customization

You can customize the server by:
1. Changing the host/port:
   ```python
   server = MCPServer(host="0.0.0.0", port=8080)
   ```

2. Adding authentication:
   ```python
   # Add to your client requests
   headers = {"Authorization": "Bearer your-token"}
   ```

3. Using SSL/TLS:
   ```python
   server = MCPServer(ssl_keyfile="key.pem", ssl_certfile="cert.pem")
   ```

## Notes

- The server runs asynchronously for better performance
- All tools maintain their async nature through the HTTP interface
- The client examples use `aiohttp` for async HTTP requests
- Response times may vary depending on the complexity of the tool being used 

## Server Execution Details

### Starting the Server

When you run `server_example.py`, you'll see:
```
Starting MCP server on http://localhost:8000
Server started successfully
```

The server will continue running until you stop it (Ctrl+C) or the program ends.

### Testing the Server

#### 1. Using a Web Browser

1. List available tools:
   - Open `http://localhost:8000/tools` in your browser
   - You should see a JSON response like:
   ```json
   [
     {
       "name": "list_dir",
       "description": "List contents of a directory",
       "parameters": {
         "directory_path": {
           "type": "string",
           "description": "Path to list contents of"
         }
       }
     },
     // ... more tools
   ]
   ```

#### 2. Using Postman

1. List tools:
   - Method: GET
   - URL: `http://localhost:8000/tools`
   - No body required

2. Execute a tool (e.g., list directory):
   - Method: POST
   - URL: `http://localhost:8000/tools/list_dir`
   - Headers: `Content-Type: application/json`
   - Body:
   ```json
   {
     "tool_name": "list_dir",
     "parameters": {
       "directory_path": "."
     }
   }
   ```

3. Search for files:
   - Method: POST
   - URL: `http://localhost:8000/tools/find_by_name`
   - Body:
   ```json
   {
     "tool_name": "find_by_name",
     "parameters": {
       "search_directory": ".",
       "pattern": "*.py",
       "type": "file"
     }
   }
   ```

### Expected Responses

1. Successful response:
```json
{
  "success": true,
  "data": {
    // Tool-specific response data
  }
}
```

2. Error response:
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Detailed error message"
  }
}
```

## Troubleshooting Guide

### Common Issues and Solutions

1. **Server won't start**
   - Error: `OSError: [Errno 98] Address already in use`
   - Solution: 
     ```bash
     # Find process using port 8000
     lsof -i :8000
     # Kill the process
     kill -9 <PID>
     ```

2. **Connection refused**
   - Error: `ConnectionRefusedError: [Errno 111] Connection refused`
   - Check:
     - Server is running (`ps aux | grep python`)
     - Correct port number
     - No firewall blocking

3. **Invalid tool name**
   - Error: `{"success": false, "error": {"code": "INVALID_TOOL", "message": "Tool not found"}}`
   - Solution:
     - Check tool name in `/tools` endpoint
     - Verify spelling and case

4. **Missing parameters**
   - Error: `{"success": false, "error": {"code": "MISSING_PARAMETER", "message": "Required parameter missing"}}`
   - Solution:
     - Check tool documentation in `/tools` endpoint
     - Include all required parameters

### Debugging Tips

1. Enable verbose logging:
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. Check server logs:
   ```bash
   # If running in terminal
   python server_example.py 2>&1 | tee server.log
   ```

3. Test server health:
   ```bash
   curl http://localhost:8000/tools
   ```

4. Monitor server resources:
   ```bash
   # Check memory usage
   ps -o pid,ppid,cmd,%mem,%cpu --sort=-%mem | grep python
   ```

### Performance Considerations

1. **Response Time**
   - Directory listing: < 100ms
   - File search: < 500ms
   - Code search: < 1s (depends on codebase size)

2. **Memory Usage**
   - Base server: ~50MB
   - Per active tool: ~10-20MB
   - Monitor with: `top -p $(pgrep -f "python.*server_example.py")`

3. **Concurrent Requests**
   - Default: 100 concurrent connections
   - Adjust with: `server = MCPServer(max_connections=200)`

## Advanced Usage

### 1. Custom Headers

```python
headers = {
    "Content-Type": "application/json",
    "X-API-Key": "your-api-key",
    "X-Request-ID": "unique-id"
}

async with aiohttp.ClientSession() as session:
    async with session.post(
        "http://localhost:8000/tools/list_dir",
        json=request_data,
        headers=headers
    ) as response:
        result = await response.json()
```

### 2. Timeout Configuration

```python
# Server side
server = MCPServer(
    request_timeout=30,  # seconds
    keep_alive_timeout=60
)

# Client side
async with aiohttp.ClientSession() as session:
    async with session.post(
        "http://localhost:8000/tools/list_dir",
        json=request_data,
        timeout=aiohttp.ClientTimeout(total=30)
    ) as response:
        result = await response.json()
```

### 3. Error Recovery

```python
async def execute_with_retry(client, tool_name, parameters, max_retries=3):
    for attempt in range(max_retries):
        try:
            return await client.execute_tool(tool_name, parameters)
        except aiohttp.ClientError as e:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(1 * (attempt + 1))  # Exponential backoff 
```

# MCP SSE Client Example

This example demonstrates how to connect to the MCP server using Server-Sent Events (SSE), send a tool request, and listen for events.

## Prerequisites

- Python 3.6+
- Required packages:
  - `httpx`
  - `sseclient-py`

Install the required packages:
```bash
pip install httpx sseclient-py
```

## Running the Server

1. **Start the MCP server** (if using the SSE/Starlette version):
   ```bash
   cd ai_coding_agent
   PYTHONPATH=src python -m ai_coding_agent.interfaces.mcp
   ```
   This will start the server on `http://localhost:8000`.

2. **Verify the server is running**:
   - Connect to `http://localhost:8000/sse` (e.g., with `curl` or a browser) to see the SSE stream.
   - You should see an event like:
     ```
     event: endpoint
     data: /messages/?session_id=...
     ```

## Running the Client

Run the SSE client example:
```bash
cd ai_coding_agent/examples/mcp
python mcp_sse_client.py
```

## What This Example Does

1. **Connects to the SSE endpoint** (`/sse`) and retrieves the session URL.
2. **Sends a tool request** (e.g., `list_dir`) to the `/messages/?session_id=...` endpoint.
3. **Listens for events** on the SSE stream and prints them.

## Expected Output

- The client will print the session URL, the tool request payload, and the response status/body.
- It will then listen for events and print them as they arrive.

## Troubleshooting

- If the server is not running, you will see connection errors.
- If the tool request fails, check the response body for error details.

## Further Reading

- For more details on the MCP protocol, refer to the [MCP documentation](https://github.com/your-org/mcp).
- For more examples, see the `examples/mcp` directory. 