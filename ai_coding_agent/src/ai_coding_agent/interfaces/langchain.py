"""LangChain interface for the AI Coding Agent."""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from langchain.tools import BaseTool as LangChainBaseTool

from ..core.base import BaseTool
from ..core.file_system import ListDirectoryTool, FileSearchTool, GrepSearchTool
from ..core.web import WebSearchTool, ReadUrlTool
from ..core.code_modification import ProposeCodeTool, ViewCodeTool, ViewFileTool
from ..core.lsp import SemanticSearchTool, SymbolInfoTool, CodeNavigationTool
from ..core.control import PushActionTool, ShowActionsTool, GetNextActionTool, ClearActionsTool

class AICodingAgentToolkit:
    """Toolkit for integrating AI Coding Agent tools with LangChain."""
    
    def __init__(self):
        """Initialize the toolkit."""
        self.tools = self._create_tools()
        
    def _create_tools(self) -> List[LangChainBaseTool]:
        """Create LangChain tools from AI Coding Agent tools.
        
        Returns:
            List of LangChain tools
        """
        # Convert AI Coding Agent tools to LangChain tools
        return [
            self._convert_tool(ListDirectoryTool()),
            self._convert_tool(FileSearchTool()),
            self._convert_tool(GrepSearchTool()),
            self._convert_tool(WebSearchTool()),
            self._convert_tool(ReadUrlTool()),
            self._convert_tool(ProposeCodeTool()),
            self._convert_tool(ViewCodeTool()),
            self._convert_tool(ViewFileTool()),
            self._convert_tool(SemanticSearchTool()),
            self._convert_tool(SymbolInfoTool()),
            self._convert_tool(CodeNavigationTool()),
            self._convert_tool(PushActionTool()),
            self._convert_tool(ShowActionsTool()),
            self._convert_tool(GetNextActionTool()),
            self._convert_tool(ClearActionsTool())
        ]
        
    def _convert_tool(self, tool: BaseTool) -> LangChainBaseTool:
        """Convert an AI Coding Agent tool to a LangChain tool.
        
        Args:
            tool: AI Coding Agent tool to convert
            
        Returns:
            LangChain tool
        """
        # Create a Pydantic model for the tool's arguments
        args_schema_class = type(
            f'{tool.name.capitalize()}Arguments',
            (BaseModel,),
            {
                '__annotations__': {
                    param.name: (str if param.type == "string" else bool, Field(
                        description=param.description,
                        required=param.required
                    ))
                    for param in tool.parameters
                }
            }
        )
        
        class LangChainTool(LangChainBaseTool):
            name = tool.name
            description = tool.description
            args_schema = args_schema_class
            
            def _run(self, **kwargs) -> str:
                """Run the tool.
                
                Args:
                    **kwargs: Tool arguments
                    
                Returns:
                    Tool result as string
                """
                import asyncio
                result = asyncio.run(tool.execute(**kwargs))
                return str(result.data if result.success else result.error)
                
            async def _arun(self, **kwargs) -> str:
                """Run the tool asynchronously.
                
                Args:
                    **kwargs: Tool arguments
                    
                Returns:
                    Tool result as string
                """
                result = await tool.execute(**kwargs)
                return str(result.data if result.success else result.error)
                
        return LangChainTool() 