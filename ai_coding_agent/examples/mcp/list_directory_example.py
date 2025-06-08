import asyncio
import json
from ai_coding_agent.interfaces.mcp import MCPClient

async def main():
    # Initialize MCP client
    client = MCPClient("http://localhost:8000")
    
    # Example 1: Basic directory listing
    print("\n1. Basic directory listing:")
    result = await client.execute_tool(
        "list_dir",
        {"directory_path": "."}
    )
    print(json.dumps(result, indent=2))
    
    # Example 2: Recursive listing with depth limit
    print("\n2. Recursive listing with depth limit:")
    result = await client.execute_tool(
        "list_dir",
        {
            "directory_path": ".",
            "recursive": True,
            "max_depth": 2
        }
    )
    print(json.dumps(result, indent=2))
    
    # Example 3: Paginated results
    print("\n3. Paginated results:")
    result = await client.execute_tool(
        "list_dir",
        {
            "directory_path": ".",
            "page": 1,
            "page_size": 10
        }
    )
    print(json.dumps(result, indent=2))
    
    # Example 4: Full recursive listing with hidden files
    print("\n4. Full recursive listing with hidden files:")
    result = await client.execute_tool(
        "list_dir",
        {
            "directory_path": ".",
            "recursive": True,
            "include_hidden": True
        }
    )
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    asyncio.run(main()) 