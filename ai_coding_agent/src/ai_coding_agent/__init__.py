"""
AI Coding Agent Toolset

A comprehensive Python package that implements an AI coding agent toolset
with both native LLM and MCP server interfaces.
"""

# Import core tools first
from .core import (
    BaseTool,
    ToolResult,
    ListDirectoryTool,
    ReadFileTool,
    EditFileTool,
    DeleteFileTool,
    GrepSearchTool,
    FileSearchTool,
    WebSearchTool,
    ReadUrlTool,
    ProposeCodeTool,
    ViewCodeTool,
    ViewFileTool,
    SemanticSearchTool,
    SymbolInfoTool,
    CodeNavigationTool,
    PushActionTool,
    ShowActionsTool,
    GetNextActionTool,
    ClearActionsTool
)

# Import interfaces after core tools
from .interfaces.langchain import AICodingAgentToolkit
from .interfaces.mcp import MCPServer

__version__ = "0.1.0"
__all__ = [
    # Core Tools
    "BaseTool",
    "ToolResult",
    "ListDirectoryTool",
    "ReadFileTool",
    "EditFileTool",
    "DeleteFileTool",
    "GrepSearchTool",
    "FileSearchTool",
    "WebSearchTool",
    "ReadUrlTool",
    "ProposeCodeTool",
    "ViewCodeTool",
    "ViewFileTool",
    "SemanticSearchTool",
    "SymbolInfoTool",
    "CodeNavigationTool",
    "PushActionTool",
    "ShowActionsTool",
    "GetNextActionTool",
    "ClearActionsTool",
    
    # Interfaces
    "AICodingAgentToolkit",
    "MCPServer"
]