"""View file tool."""

from pathlib import Path
from typing import Optional, Dict, Any

from ..base import BaseTool, ToolParameter, ToolResult


class ViewFileTool(BaseTool):
    """Tool for viewing file contents."""

    name = "view_file"
    description = "View file contents"
    parameters = [
        ToolParameter(
            name="file_path",
            type="string",
            description="Path of the file to view",
            required=True
        ),
        ToolParameter(
            name="start_line",
            type="integer",
            description="Start line number (1-indexed)",
            required=False
        ),
        ToolParameter(
            name="end_line",
            type="integer",
            description="End line number (1-indexed)",
            required=False
        ),
        ToolParameter(
            name="include_summary",
            type="boolean",
            description="Whether to include a summary",
            required=False,
            default=False
        )
    ]

    async def execute(
        self,
        file_path: str,
        start_line: Optional[int] = None,
        end_line: Optional[int] = None,
        include_summary: bool = False
    ) -> ToolResult:
        """Execute the file viewing operation.

        Args:
            file_path: Path of the file to view
            start_line: Start line number (1-indexed)
            end_line: End line number (1-indexed)
            include_summary: Whether to include a summary

        Returns:
            ToolResult containing the file contents
        """
        try:
            path = Path(file_path)
            if not path.exists():
                return ToolResult(
                    success=False,
                    error=f"File does not exist: {file_path}"
                )

            if not path.is_file():
                return ToolResult(
                    success=False,
                    error=f"Path is not a file: {file_path}"
                )

            with open(path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            if start_line is not None and end_line is not None:
                if start_line < 1 or end_line > len(lines):
                    return ToolResult(
                        success=False,
                        error=f"Line range {start_line}-{end_line} is invalid for file with {len(lines)} lines"
                    )
                content = ''.join(lines[start_line - 1:end_line])
            else:
                content = ''.join(lines)

            result_data = {
                "content": content,
                "total_lines": len(lines)
            }

            if include_summary:
                result_data["summary"] = {
                    "file_size": path.stat().st_size,
                    "language": path.suffix[1:] if path.suffix else "unknown"
                }

            return ToolResult(
                success=True,
                data=result_data
            )

        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Error viewing file: {str(e)}"
            ) 