"""Tool for listing directory contents."""

from typing import Optional, List, Dict, Any
from pathlib import Path
from ai_coding_agent.core.base import BaseTool, ToolResult, ToolParameter

class ListDirectoryTool(BaseTool):
    """Tool for listing directory contents.
    
    This tool allows listing the contents of a directory, optionally filtering
    by file patterns and excluding certain paths.
    """
    
    name: str = "list_dir"
    description: str = "List contents of a directory"
    parameters = [
        ToolParameter(
            name="directory_path",
            type="string",
            description="Path to list contents from",
            required=True
        ),
        ToolParameter(
            name="include_pattern",
            type="string",
            description="Glob pattern for files to include (e.g. '*.txt' for text files)",
            required=False
        ),
        ToolParameter(
            name="exclude_pattern",
            type="string",
            description="Glob pattern for files to exclude",
            required=False
        ),
        ToolParameter(
            name="sort_by",
            type="string",
            description="Field to sort by (name, type, size, modified). Defaults to name.",
            required=False
        ),
        ToolParameter(
            name="sort_order",
            type="string",
            description="Sorting order (asc or desc)",
            required=False
        )
    ]
    
    async def execute(
        self,
        directory_path: str,
        include_pattern: Optional[str] = None,
        exclude_pattern: Optional[str] = None,
        sort_by: Optional[str] = None
    ) -> ToolResult:
        """Execute the list directory tool.
        
        Args:
            directory_path: Path to list contents of, relative to workspace root
            include_pattern: Optional glob pattern for files to include
            exclude_pattern: Optional glob pattern for files to exclude
            sort_by: Optional field to sort by (name, type, size, modified)
            
        Returns:
            ToolResult containing success status and directory contents
        """
        try:
            path = Path(directory_path)
            if not path.exists():
                return ToolResult(
                    success=False,
                    error=f"Path does not exist: {directory_path}"
                )
                
            if not path.is_dir():
                return ToolResult(
                    success=False,
                    error=f"Path is not a directory: {directory_path}"
                )
                
            # Get directory contents
            items = []
            for item in path.iterdir():
                # Skip if excluded by pattern
                if exclude_pattern and item.match(exclude_pattern):
                    continue
                    
                # Skip if not included by pattern
                if include_pattern and not item.match(include_pattern):
                    continue
                    
                items.append({
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else None,
                    "modified": item.stat().st_mtime
                })
            
            # Sort items
            if sort_by:
                if sort_by == "name":
                    items.sort(key=lambda x: x["name"].lower())
                elif sort_by == "type":
                    items.sort(key=lambda x: (x["type"], x["name"].lower()))
                elif sort_by == "size":
                    items.sort(key=lambda x: (x["size"] or 0, x["name"].lower()))
                elif sort_by == "modified":
                    items.sort(key=lambda x: (x["modified"], x["name"].lower()))
                else:
                    return ToolResult(
                        success=False,
                        error=f"Invalid sort_by value: {sort_by}. Must be one of: name, type, size, modified"
                    )
            else:
                # Default sort by name
                items.sort(key=lambda x: x["name"].lower())
                
            return ToolResult(
                success=True,
                data={"contents": items}
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Error listing directory: {str(e)}"
            ) 