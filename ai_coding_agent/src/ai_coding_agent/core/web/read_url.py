"""Tool for reading content from URLs."""

from typing import Optional
import httpx
from ..base import BaseTool, ToolResult

class ReadUrlTool(BaseTool):
    """Tool for reading content from URLs.
    
    This tool allows fetching and reading content from web URLs.
    It supports both GET and POST requests with optional headers and data.
    """
    
    name: str = "read_url"
    description: str = "Read content from a URL"
    
    async def execute(
        self,
        url: str,
        method: str = "GET",
        headers: Optional[dict] = None,
        data: Optional[dict] = None,
        timeout: Optional[float] = 30.0
    ) -> ToolResult:
        """Execute the read URL tool.
        
        Args:
            url: URL to read from
            method: HTTP method to use (GET or POST)
            headers: Optional HTTP headers
            data: Optional data to send with POST request
            timeout: Optional timeout in seconds
            
        Returns:
            ToolResult containing success status and URL content
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data if method == "POST" else None,
                    timeout=timeout
                )
                
                response.raise_for_status()
                
                return ToolResult(
                    success=True,
                    data={
                        "content": response.text,
                        "status_code": response.status_code,
                        "headers": dict(response.headers)
                    }
                )
                
        except httpx.HTTPError as e:
            return ToolResult(
                success=False,
                error=f"HTTP error: {str(e)}"
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e)
            ) 