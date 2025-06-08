import aiohttp
from bs4 import BeautifulSoup
from typing import Dict, List, Optional

from .base import BaseTool, ToolParameter, ToolResult


class WebSearchTool(BaseTool):
    """Tool for performing web searches."""
    
    name = "search_web"
    description = "Perform a web search"
    parameters = [
        ToolParameter(
            name="query",
            description="Search query",
            required=True,
            type="string"
        ),
        ToolParameter(
            name="domain",
            description="Optional domain to filter results",
            required=False,
            type="string"
        )
    ]
    
    async def execute(
        self,
        query: str,
        domain: Optional[str] = None
    ) -> ToolResult:
        try:
            # Note: In a real implementation, you would use a proper search API
            # This is a placeholder implementation
            async with aiohttp.ClientSession() as session:
                search_url = f"https://www.google.com/search?q={query}"
                if domain:
                    search_url += f" site:{domain}"
                
                async with session.get(search_url) as response:
                    if response.status != 200:
                        return ToolResult(
                            success=False,
                            error=f"Search failed with status {response.status}"
                        )
                    
                    html = await response.text()
                    soup = BeautifulSoup(html, "html.parser")
                    
                    results = []
                    for result in soup.select("div.g"):
                        title_elem = result.select_one("h3")
                        link_elem = result.select_one("a")
                        snippet_elem = result.select_one("div.VwiC3b")
                        
                        if title_elem and link_elem and snippet_elem:
                            results.append({
                                "title": title_elem.text,
                                "url": link_elem["href"],
                                "snippet": snippet_elem.text
                            })
                    
                    return ToolResult(success=True, data=results)
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class ReadUrlContentTool(BaseTool):
    """Tool for reading content from a URL."""
    
    name = "read_url_content"
    description = "Read content from a URL"
    parameters = [
        ToolParameter(
            name="url",
            description="URL to read content from",
            required=True,
            type="string"
        ),
        ToolParameter(
            name="timeout",
            description="Request timeout in seconds",
            required=False,
            type="integer",
            default=30
        )
    ]
    
    async def execute(self, url: str, timeout: int = 30) -> ToolResult:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=timeout) as response:
                    if response.status != 200:
                        return ToolResult(
                            success=False,
                            error=f"Failed to fetch URL with status {response.status}"
                        )
                    
                    content_type = response.headers.get("content-type", "")
                    if "text/html" in content_type:
                        html = await response.text()
                        soup = BeautifulSoup(html, "html.parser")
                        
                        # Remove script and style elements
                        for script in soup(["script", "style"]):
                            script.decompose()
                        
                        # Get text content
                        text = soup.get_text(separator="\n", strip=True)
                        
                        return ToolResult(success=True, data={
                            "type": "html",
                            "content": text,
                            "title": soup.title.string if soup.title else None
                        })
                    else:
                        # For non-HTML content, return raw bytes
                        content = await response.read()
                        return ToolResult(success=True, data={
                            "type": "binary",
                            "content": content,
                            "content_type": content_type
                        })
        except Exception as e:
            return ToolResult(success=False, error=str(e)) 