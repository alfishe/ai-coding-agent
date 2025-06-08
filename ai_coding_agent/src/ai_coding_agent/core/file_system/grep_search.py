"""Grep search tool."""

import re
from pathlib import Path
from typing import Optional, List, Dict

from ..base import BaseTool, ToolParameter, ToolResult


class GrepSearchTool(BaseTool):
    """Tool for searching text in files."""

    name = "grep_search"
    description = "Search for text in files"
    parameters = [
        ToolParameter(
            name="query",
            type="string",
            description="The regex pattern to search for",
            required=True
        ),
        ToolParameter(
            name="include_pattern",
            type="string",
            description="Glob pattern for files to include",
            required=False
        ),
        ToolParameter(
            name="exclude_pattern",
            type="string",
            description="Glob pattern for files to exclude",
            required=False
        ),
        ToolParameter(
            name="case_sensitive",
            type="boolean",
            description="Whether the search should be case sensitive",
            required=False,
            default=True
        )
    ]

    async def execute(
        self,
        query: str,
        include_pattern: Optional[str] = None,
        exclude_pattern: Optional[str] = None,
        case_sensitive: bool = True
    ) -> ToolResult:
        """Execute the grep search operation.

        Args:
            query: The regex pattern to search for
            include_pattern: Glob pattern for files to include
            exclude_pattern: Glob pattern for files to exclude
            case_sensitive: Whether the search should be case sensitive

        Returns:
            ToolResult containing the search results
        """
        try:
            # Compile the regex pattern
            flags = 0 if case_sensitive else re.IGNORECASE
            pattern = re.compile(query, flags)

            # Get all files in the workspace
            workspace_path = Path(".")
            all_files = list(workspace_path.rglob("*"))

            # Filter files based on include/exclude patterns
            if include_pattern:
                include_regex = re.compile(include_pattern.replace("*", ".*"))
                all_files = [f for f in all_files if include_regex.match(str(f))]

            if exclude_pattern:
                exclude_regex = re.compile(exclude_pattern.replace("*", ".*"))
                all_files = [f for f in all_files if not exclude_regex.match(str(f))]

            # Search in each file
            matches: List[Dict] = []
            for file_path in all_files:
                if not file_path.is_file():
                    continue

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        for line_num, line in enumerate(f, 1):
                            if pattern.search(line):
                                matches.append({
                                    "file": str(file_path),
                                    "line": line_num,
                                    "content": line.strip()
                                })
                except Exception as e:
                    # Skip files that can't be read
                    continue

            return ToolResult(
                success=True,
                data={
                    "matches": matches[:50]  # Limit to 50 matches to avoid overwhelming output
                }
            )

        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Error performing grep search: {str(e)}"
            ) 