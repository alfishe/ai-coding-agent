"""
AI Coding Agent Toolset

A comprehensive Python package that implements an AI coding agent toolset
with both native LLM and MCP server interfaces.
"""

from .interfaces.langchain import AICodingAgentToolkit
from .interfaces.mcp import MCPServer

__version__ = "0.1.0"
__all__ = ["AICodingAgentToolkit", "MCPServer", "core"]