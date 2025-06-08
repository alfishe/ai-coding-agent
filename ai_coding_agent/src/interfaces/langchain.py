from typing import Any, Dict, List, Optional, Type

from langchain.tools import BaseTool as LangChainBaseTool
from langchain.tools.base import ToolException

from ..core.base import BaseTool
from ..core.file_system import ListDirectoryTool, FindByNameTool, GrepSearchTool
from ..core.web import WebSearchTool, ReadUrlContentTool
from ..core.code_modification import (
    ProposeCodeTool,
    ViewCodeItemTool,
    ViewFileTool
)


class AICodingAgentToolkit:
    """Toolkit for using AI Coding Agent tools with LangChain."""
    
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {
            tool.name: tool()
            for tool in [
                ListDirectoryTool,
                FindByNameTool,
                GrepSearchTool,
                WebSearchTool,
                ReadUrlContentTool,
                ProposeCodeTool,
                ViewCodeItemTool,
                ViewFileTool
            ]
        }
    
    def get_tools(self) -> List[LangChainBaseTool]:
        """Convert internal tools to LangChain tools."""
        return [
            self._create_langchain_tool(tool)
            for tool in self._tools.values()
        ]
    
    def _create_langchain_tool(self, tool: BaseTool) -> LangChainBaseTool:
        """Convert an internal tool to a LangChain tool."""
        
        class LangChainTool(LangChainBaseTool):
            name = tool.name
            description = tool.description
            
            def _run(self, **kwargs: Any) -> Any:
                try:
                    # Convert sync to async execution
                    import asyncio
                    result = asyncio.run(tool.execute(**kwargs))
                    
                    if not result.success:
                        raise ToolException(result.error)
                    
                    return result.data
                except Exception as e:
                    raise ToolException(str(e))
            
            def _arun(self, **kwargs: Any) -> Any:
                try:
                    result = asyncio.run(tool.execute(**kwargs))
                    
                    if not result.success:
                        raise ToolException(result.error)
                    
                    return result.data
                except Exception as e:
                    raise ToolException(str(e))
        
        return LangChainTool() 