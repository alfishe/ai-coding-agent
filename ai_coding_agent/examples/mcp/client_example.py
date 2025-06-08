"""
Example of using the MCP server as a client.
"""

import asyncio
import aiohttp
from typing import Dict, Any


class MCPClient:
    """Client for interacting with the MCP server."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
    
    async def list_tools(self) -> Dict[str, Any]:
        """List all available tools."""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/tools") as response:
                return await response.json()
    
    async def execute_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a tool with the given parameters."""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/tools/{tool_name}",
                json={"tool_name": tool_name, "parameters": parameters}
            ) as response:
                return await response.json()


async def main():
    # Create client
    client = MCPClient()
    
    # List available tools
    tools = await client.list_tools()
    print("Available tools:")
    for tool in tools:
        print(f"- {tool['name']}: {tool['description']}")
    
    # Example: Search for code patterns
    search_result = await client.execute_tool(
        "grep_search",
        {
            "search_path": ".",
            "query": "async def",
            "case_insensitive": True
        }
    )
    print("\nSearch results for async functions:")
    print(search_result)
    
    # Example: View file contents
    file_result = await client.execute_tool(
        "view_file",
        {
            "absolute_path": "README.md",
            "include_summary": True
        }
    )
    print("\nFile contents:")
    print(file_result)
    
    # Example: Propose code changes
    code_change = await client.execute_tool(
        "propose_code",
        {
            "target_file": "example.py",
            "code_edit": """
def new_function():
    \"\"\"A new function to demonstrate code changes.\"\"\"
    print("Hello, World!")
            """,
            "instruction": "Add a new function to demonstrate code changes"
        }
    )
    print("\nProposed code changes:")
    print(code_change)


if __name__ == "__main__":
    asyncio.run(main()) 