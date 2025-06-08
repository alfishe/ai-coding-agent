import os
import re
from pathlib import Path
from typing import List, Optional, Set, Union, Dict, Any

from .base import BaseTool, ToolParameter, ToolResult


class ListDirectoryTool(BaseTool):
    """Tool for listing directory contents with support for recursive listing and pagination."""
    
    name = "list_dir"
    description = "List contents of a directory with optional recursion and pagination"
    parameters = [
        ToolParameter(
            name="directory_path",
            description="Path to the directory to list",
            required=True,
            type="string"
        ),
        ToolParameter(
            name="recursive",
            description="Whether to list contents recursively",
            required=False,
            default=False,
            type="boolean"
        ),
        ToolParameter(
            name="max_depth",
            description="Maximum recursion depth (only used if recursive=True)",
            required=False,
            default=None,
            type="integer"
        ),
        ToolParameter(
            name="page",
            description="Page number for pagination (1-based)",
            required=False,
            default=1,
            type="integer"
        ),
        ToolParameter(
            name="page_size",
            description="Number of items per page",
            required=False,
            default=100,
            type="integer"
        ),
        ToolParameter(
            name="include_hidden",
            description="Whether to include hidden files and directories",
            required=False,
            default=False,
            type="boolean"
        ),
        ToolParameter(
            name="sort_by",
            description="Field to sort by (name, size, modified, type)",
            required=False,
            default="type",
            type="string"
        ),
        ToolParameter(
            name="sort_order",
            description="Sort order (asc or desc)",
            required=False,
            default="asc",
            type="string"
        )
    ]
    
    async def execute(
        self,
        directory_path: str,
        recursive: bool = False,
        max_depth: Optional[int] = None,
        page: int = 1,
        page_size: int = 100,
        include_hidden: bool = False,
        sort_by: str = "type",
        sort_order: str = "asc"
    ) -> ToolResult:
        try:
            path = Path(directory_path)
            if not path.exists():
                return ToolResult(
                    success=False,
                    error=f"Directory does not exist: {directory_path}"
                )
            
            if not path.is_dir():
                return ToolResult(
                    success=False,
                    error=f"Path is not a directory: {directory_path}"
                )
            
            contents = []
            total_items = 0
            
            if recursive:
                contents, total_items = self._list_recursive(
                    path,
                    max_depth,
                    include_hidden
                )
            else:
                contents, total_items = self._list_directory(
                    path,
                    include_hidden
                )
            
            # Sort contents
            contents = self._sort_contents(contents, sort_by, sort_order)
            
            # Apply pagination
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            paginated_contents = contents[start_idx:end_idx]
            
            return ToolResult(
                success=True,
                data={
                    "items": paginated_contents,
                    "pagination": {
                        "total_items": total_items,
                        "total_pages": (total_items + page_size - 1) // page_size,
                        "current_page": page,
                        "page_size": page_size
                    }
                }
            )
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    def _sort_contents(
        self,
        contents: List[Dict[str, Any]],
        sort_by: str,
        sort_order: str
    ) -> List[Dict[str, Any]]:
        """Sort contents based on specified criteria."""
        reverse = sort_order.lower() == "desc"
        
        def get_sort_key(item: Dict[str, Any]) -> Any:
            if sort_by == "type":
                # For type sorting, we want directories first, then files
                # Within each type, sort by name
                return (0 if item["type"] == "directory" else 1, item["name"].lower())
            elif sort_by == "name":
                return item["name"].lower()
            elif sort_by == "size":
                # For size, handle None values (directories) by putting them first
                return (0 if item["size"] is None else 1, item["size"] or 0)
            elif sort_by == "modified":
                return item["modified"]
            else:
                return item["name"].lower()  # Default to name sorting
        
        return sorted(contents, key=get_sort_key, reverse=reverse)
    
    def _list_directory(
        self,
        path: Path,
        include_hidden: bool
    ) -> tuple[List[Dict[str, Any]], int]:
        """List contents of a single directory."""
        contents = []
        for item in path.iterdir():
            if not include_hidden and item.name.startswith('.'):
                continue
                
            contents.append({
                "name": item.name,
                "path": str(item),
                "type": "directory" if item.is_dir() else "file",
                "size": item.stat().st_size if item.is_file() else None,
                "modified": item.stat().st_mtime
            })
        return contents, len(contents)
    
    def _list_recursive(
        self,
        path: Path,
        max_depth: Optional[int],
        include_hidden: bool
    ) -> tuple[List[Dict[str, Any]], int]:
        """List contents recursively with depth control."""
        contents = []
        total_items = 0
        
        def _walk(current_path: Path, current_depth: int):
            nonlocal total_items
            
            if max_depth is not None and current_depth > max_depth:
                return
                
            try:
                for item in current_path.iterdir():
                    if not include_hidden and item.name.startswith('.'):
                        continue
                        
                    relative_path = item.relative_to(path)
                    contents.append({
                        "name": item.name,
                        "path": str(relative_path),
                        "type": "directory" if item.is_dir() else "file",
                        "size": item.stat().st_size if item.is_file() else None,
                        "modified": item.stat().st_mtime,
                        "depth": current_depth
                    })
                    total_items += 1
                    
                    if item.is_dir():
                        _walk(item, current_depth + 1)
            except PermissionError:
                pass  # Skip directories we don't have permission to access
        
        _walk(path, 0)
        return contents, total_items


class FindByNameTool(BaseTool):
    """Tool for finding files and directories by name pattern."""
    
    name = "find_by_name"
    description = "Search for files and directories by name pattern"
    parameters = [
        ToolParameter(
            name="search_directory",
            description="Directory to search in",
            required=True,
            type="string"
        ),
        ToolParameter(
            name="pattern",
            description="Glob pattern to match",
            required=True,
            type="string"
        ),
        ToolParameter(
            name="type",
            description="Type of items to find (file, directory, or any)",
            required=False,
            default="any",
            type="string"
        ),
        ToolParameter(
            name="max_depth",
            description="Maximum directory depth to search",
            required=False,
            default=None,
            type="integer"
        )
    ]
    
    async def execute(
        self,
        search_directory: str,
        pattern: str,
        type: str = "any",
        max_depth: Optional[int] = None
    ) -> ToolResult:
        try:
            path = Path(search_directory)
            if not path.exists() or not path.is_dir():
                return ToolResult(
                    success=False,
                    error=f"Invalid search directory: {search_directory}"
                )
            
            results = []
            for item in path.rglob(pattern):
                if max_depth is not None:
                    depth = len(item.relative_to(path).parts)
                    if depth > max_depth:
                        continue
                
                if type == "file" and not item.is_file():
                    continue
                if type == "directory" and not item.is_dir():
                    continue
                
                results.append(str(item))
            
            return ToolResult(success=True, data=results)
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class GrepSearchTool(BaseTool):
    """Tool for searching file contents using regex patterns."""
    
    name = "grep_search"
    description = "Search for patterns in files"
    parameters = [
        ToolParameter(
            name="search_path",
            description="Path to search in",
            required=True,
            type="string"
        ),
        ToolParameter(
            name="query",
            description="Search pattern (regex)",
            required=True,
            type="string"
        ),
        ToolParameter(
            name="case_insensitive",
            description="Whether to perform case-insensitive search",
            required=False,
            default=False,
            type="boolean"
        )
    ]
    
    async def execute(
        self,
        search_path: str,
        query: str,
        case_insensitive: bool = False
    ) -> ToolResult:
        try:
            path = Path(search_path)
            if not path.exists():
                return ToolResult(
                    success=False,
                    error=f"Path does not exist: {search_path}"
                )
            
            flags = re.IGNORECASE if case_insensitive else 0
            pattern = re.compile(query, flags)
            
            results = []
            if path.is_file():
                results.extend(self._search_file(path, pattern))
            else:
                for file in path.rglob("*"):
                    if file.is_file():
                        results.extend(self._search_file(file, pattern))
            
            return ToolResult(success=True, data=results)
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    def _search_file(self, file_path: Path, pattern: re.Pattern) -> List[dict]:
        """Search a single file for matches."""
        results = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for i, line in enumerate(f, 1):
                    if pattern.search(line):
                        results.append({
                            "file": str(file_path),
                            "line": i,
                            "content": line.strip()
                        })
        except Exception:
            pass
        return results 