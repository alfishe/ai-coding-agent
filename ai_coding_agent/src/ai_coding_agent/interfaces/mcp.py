import asyncio
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field

from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Mount, Route
from mcp.server import Server
import uvicorn

from ..core.base import BaseTool
from ..core.file_system import ListDirectoryTool, FindByNameTool, GrepSearchTool
from ..core.web import WebSearchTool, ReadUrlContentTool
from ..core.code_modification import (
    ProposeCodeTool,
    ViewCodeItemTool,
    ViewFileTool
)
from ..core.lsp_tools import (
    SemanticSearchTool,
    SymbolInfoTool,
    CodeNavigationTool
)
from ..core.control_tools import (
    PushActionTool,
    ShowActionsTool,
    GetNextActionTool,
    ClearActionsTool
)


# File System Tool Models
class ListDirectoryRequest(BaseModel):
    directory_path: str = Field(..., description="Path to the directory to list")
    sort_by: str = Field("name", description="Field to sort by (name, type, size, modified)")
    sort_order: str = Field("asc", description="Sort order (asc, desc)")

    class Config:
        json_schema_extra = {
            "example": {
                "directory_path": ".",
                "sort_by": "type",
                "sort_order": "asc"
            }
        }


class FindByNameRequest(BaseModel):
    search_path: str = Field(..., description="Path to start search from")
    pattern: str = Field(..., description="File name pattern to match")
    recursive: bool = Field(True, description="Whether to search recursively")

    class Config:
        json_schema_extra = {
            "example": {
                "search_path": ".",
                "pattern": "*.py",
                "recursive": True
            }
        }


class GrepSearchRequest(BaseModel):
    search_path: str = Field(..., description="Path to search in")
    query: str = Field(..., description="Text to search for")
    case_insensitive: bool = Field(True, description="Whether to ignore case")

    class Config:
        json_schema_extra = {
            "example": {
                "search_path": ".",
                "query": "class",
                "case_insensitive": True
            }
        }


# Web Tool Models
class WebSearchRequest(BaseModel):
    query: str = Field(..., description="Search query")
    num_results: int = Field(5, description="Number of results to return")

    class Config:
        json_schema_extra = {
            "example": {
                "query": "Python FastAPI tutorial",
                "num_results": 5
            }
        }


class ReadUrlContentRequest(BaseModel):
    url: str = Field(..., description="URL to read from")
    timeout: int = Field(30, description="Request timeout in seconds")

    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://example.com",
                "timeout": 30
            }
        }


# Code Modification Tool Models
class CodeChange(BaseModel):
    type: str = Field(..., description="Type of change (add, remove, modify)")
    line: int = Field(..., description="Line number to change")
    content: str = Field(..., description="Content to add/modify")


class ProposeCodeRequest(BaseModel):
    file_path: str = Field(..., description="Path to the file to modify")
    changes: List[CodeChange] = Field(..., description="List of changes to apply")

    class Config:
        json_schema_extra = {
            "example": {
                "file_path": "src/main.py",
                "changes": [
                    {
                        "type": "add",
                        "line": 10,
                        "content": "def new_function():"
                    }
                ]
            }
        }


class ViewCodeItemRequest(BaseModel):
    file_path: str = Field(..., description="Path to the file")
    line: int = Field(..., description="Line number to view")

    class Config:
        json_schema_extra = {
            "example": {
                "file_path": "src/main.py",
                "line": 10
            }
        }


class ViewFileRequest(BaseModel):
    file_path: str = Field(..., description="Path to the file")
    start_line: int = Field(..., description="First line to view")
    end_line: int = Field(..., description="Last line to view")

    class Config:
        json_schema_extra = {
            "example": {
                "file_path": "src/main.py",
                "start_line": 1,
                "end_line": 20
            }
        }


# LSP Tool Models
class Position(BaseModel):
    line: int = Field(..., description="Line number")
    character: int = Field(..., description="Character position")


class SemanticSearchRequest(BaseModel):
    query: str = Field(..., description="Semantic search query")
    workspace_path: str = Field(..., description="Path to the workspace")
    language: str = Field(..., description="Programming language to search in")

    class Config:
        json_schema_extra = {
            "example": {
                "query": "function that handles user authentication",
                "workspace_path": ".",
                "language": "python"
            }
        }


class SymbolInfoRequest(BaseModel):
    file_path: str = Field(..., description="Path to the file")
    position: Position = Field(..., description="Position in the file")
    language: str = Field(..., description="Programming language")

    class Config:
        json_schema_extra = {
            "example": {
                "file_path": "src/main.py",
                "position": {
                    "line": 10,
                    "character": 5
                },
                "language": "python"
            }
        }


class CodeNavigationRequest(BaseModel):
    file_path: str = Field(..., description="Path to the file")
    position: Position = Field(..., description="Position in the file")
    language: str = Field(..., description="Programming language")
    action: str = Field(..., description="Navigation action to perform")

    class Config:
        json_schema_extra = {
            "example": {
                "file_path": "src/main.py",
                "position": {
                    "line": 10,
                    "character": 5
                },
                "language": "python",
                "action": "definition"
            }
        }


# Control Tool Models
class ToolParameters(BaseModel):
    tool_name: str = Field(..., description="Name of the tool to execute")
    parameters: Dict[str, Any] = Field(..., description="Parameters for the tool")


class PushActionRequest(BaseModel):
    tool_name: str = Field(..., description="Name of the tool to execute")
    parameters: Dict[str, Any] = Field(..., description="Parameters for the tool")

    class Config:
        json_schema_extra = {
            "example": {
                "tool_name": "list_dir",
                "parameters": {
                    "directory_path": ".",
                    "sort_by": "type",
                    "sort_order": "asc"
                }
            }
        }


class EmptyRequest(BaseModel):
    """Empty request model for tools that don't require parameters."""
    pass


class ToolResponse(BaseModel):
    """Response model for tool execution."""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "summary": "Successful response",
                    "value": {
                        "success": True,
                        "data": [
                            {
                                "name": "src",
                                "type": "directory",
                                "size": 4096
                            }
                        ],
                        "error": None
                    }
                },
                {
                    "summary": "Error response",
                    "value": {
                        "success": False,
                        "data": None,
                        "error": "Invalid parameters"
                    }
                }
            ]
        }
    }


class MCPServer:
    """MCP server for exposing AI Coding Agent tools."""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8000):
        self.host = host
        self.port = port
        self.mcp = FastMCP("ai_coding_agent")
        self._register_tools()
    
    def _register_tools(self) -> None:
        """Register all tools with the MCP server."""
        
        @self.mcp.tool()
        async def list_dir(directory_path: str, sort_by: str = "name", sort_order: str = "asc") -> Dict[str, Any]:
            """List directory contents."""
            tool = ListDirectoryTool()
            result = await tool.execute(
                directory_path=directory_path,
                sort_by=sort_by,
                sort_order=sort_order
            )
            return {"success": result.success, "data": result.data, "error": result.error}
        
        @self.mcp.tool()
        async def find_by_name(search_path: str, pattern: str, recursive: bool = True) -> Dict[str, Any]:
            """Find files by name pattern."""
            tool = FindByNameTool()
            result = await tool.execute(search_path=search_path, pattern=pattern, recursive=recursive)
            return {"success": result.success, "data": result.data, "error": result.error}
        
        @self.mcp.tool()
        async def grep_search(search_path: str, query: str, case_insensitive: bool = True) -> Dict[str, Any]:
            """Search for text in files."""
            tool = GrepSearchTool()
            result = await tool.execute(search_path=search_path, query=query, case_insensitive=case_insensitive)
            return {"success": result.success, "data": result.data, "error": result.error}
        
        @self.mcp.tool()
        async def web_search(query: str, num_results: int = 5) -> Dict[str, Any]:
            """Search the web."""
            tool = WebSearchTool()
            result = await tool.execute(query=query, num_results=num_results)
            return {"success": result.success, "data": result.data, "error": result.error}
        
        @self.mcp.tool()
        async def read_url_content(url: str, timeout: int = 30) -> Dict[str, Any]:
            """Read content from a URL."""
            tool = ReadUrlContentTool()
            result = await tool.execute(url=url, timeout=timeout)
            return {"success": result.success, "data": result.data, "error": result.error}
        
        @self.mcp.tool()
        async def propose_code(file_path: str, changes: List[Dict[str, Any]]) -> Dict[str, Any]:
            """Propose code changes."""
            tool = ProposeCodeTool()
            result = await tool.execute(file_path=file_path, changes=changes)
            return {"success": result.success, "data": result.data, "error": result.error}
        
        @self.mcp.tool()
        async def view_code_item(file_path: str, line: int) -> Dict[str, Any]:
            """View code item details."""
            tool = ViewCodeItemTool()
            result = await tool.execute(file_path=file_path, line=line)
            return {"success": result.success, "data": result.data, "error": result.error}
        
        @self.mcp.tool()
        async def view_file(file_path: str, start_line: int, end_line: int) -> Dict[str, Any]:
            """View file contents."""
            tool = ViewFileTool()
            result = await tool.execute(file_path=file_path, start_line=start_line, end_line=end_line)
            return {"success": result.success, "data": result.data, "error": result.error}
        
        @self.mcp.tool()
        async def semantic_search(query: str, workspace_path: str, language: str) -> Dict[str, Any]:
            """Search code semantically."""
            tool = SemanticSearchTool()
            result = await tool.execute(query=query, workspace_path=workspace_path, language=language)
            return {"success": result.success, "data": result.data, "error": result.error}
        
        @self.mcp.tool()
        async def symbol_info(file_path: str, position: Dict[str, int], language: str) -> Dict[str, Any]:
            """Get symbol information."""
            tool = SymbolInfoTool()
            result = await tool.execute(file_path=file_path, position=position, language=language)
            return {"success": result.success, "data": result.data, "error": result.error}
        
        @self.mcp.tool()
        async def code_navigation(file_path: str, position: Dict[str, int], language: str, action: str) -> Dict[str, Any]:
            """Navigate code."""
            tool = CodeNavigationTool()
            result = await tool.execute(file_path=file_path, position=position, language=language, action=action)
            return {"success": result.success, "data": result.data, "error": result.error}
        
        @self.mcp.tool()
        async def push_action(tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
            """Push an action to the queue."""
            tool = PushActionTool()
            result = await tool.execute(tool_name=tool_name, parameters=parameters)
            return {"success": result.success, "data": result.data, "error": result.error}
        
        @self.mcp.tool()
        async def show_actions() -> Dict[str, Any]:
            """Show all actions in the queue."""
            tool = ShowActionsTool()
            result = await tool.execute()
            return {"success": result.success, "data": result.data, "error": result.error}
        
        @self.mcp.tool()
        async def get_next_action() -> Dict[str, Any]:
            """Get the next action from the queue."""
            tool = GetNextActionTool()
            result = await tool.execute()
            return {"success": result.success, "data": result.data, "error": result.error}
        
        @self.mcp.tool()
        async def clear_actions() -> Dict[str, Any]:
            """Clear all actions from the queue."""
            tool = ClearActionsTool()
            result = await tool.execute()
            return {"success": result.success, "data": result.data, "error": result.error}
    
    def create_starlette_app(self, debug: bool = False) -> Starlette:
        """Create a Starlette application that can serve the MCP server with SSE."""
        sse = SseServerTransport("/messages/")
        mcp_server = self.mcp._mcp_server

        async def handle_sse(request: Request) -> None:
            async with sse.connect_sse(
                    request.scope,
                    request.receive,
                    request._send,  # noqa: SLF001
            ) as (read_stream, write_stream):
                await mcp_server.run(
                    read_stream,
                    write_stream,
                    mcp_server.create_initialization_options(),
                )

        return Starlette(
            debug=debug,
            routes=[
                Route("/sse", endpoint=handle_sse),
                Mount("/messages/", app=sse.handle_post_message),
            ],
        )
    
    def start(self) -> None:
        """Start the MCP server."""
        starlette_app = self.create_starlette_app(debug=True)
        uvicorn.run(
            starlette_app,
            host=self.host,
            port=self.port
        )
    
    async def start_async(self) -> None:
        """Start the MCP server asynchronously."""
        starlette_app = self.create_starlette_app(debug=True)
        config = uvicorn.Config(
            starlette_app,
            host=self.host,
            port=self.port
        )
        server = uvicorn.Server(config)
        await server.serve() 