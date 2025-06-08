"""File search tool."""

from pathlib import Path
from typing import List

from ..base import BaseTool, ToolParameter, ToolResult


class FileSearchTool(BaseTool):
    """Tool for searching files by name."""

    name = "file_search"
    description = "Search for files by name"
    parameters = [
        ToolParameter(
            name="query",
            type="string",
            description="Fuzzy filename to search for",
            required=True
        )
    ]

    async def execute(self, query: str) -> ToolResult:
        """Execute the file search operation.

        Args:
            query: Fuzzy filename to search for

        Returns:
            ToolResult containing the search results
        """
        try:
            # Get all files in the workspace
            workspace_path = Path(".")
            all_files = list(workspace_path.rglob("*"))

            # Filter for files only (not directories)
            files = [f for f in all_files if f.is_file()]

            # Convert query to lowercase for case-insensitive matching
            query_lower = query.lower()

            # Find matches
            matches: List[str] = []
            for file_path in files:
                # Check if query is in the filename (case-insensitive)
                if query_lower in file_path.name.lower():
                    matches.append(str(file_path))

            # Sort matches by relevance (exact matches first, then partial matches)
            matches.sort(key=lambda x: (
                not x.lower().endswith(query_lower),  # Exact matches first
                len(x)  # Shorter paths first
            ))

            return ToolResult(
                success=True,
                data={
                    "matches": matches[:10]  # Limit to 10 matches
                }
            )

        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Error performing file search: {str(e)}"
            ) 