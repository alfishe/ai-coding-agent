"""Read file contents tool."""

from pathlib import Path
from typing import Optional

from ..base import BaseTool, ToolParameter, ToolResult


class ReadFileTool(BaseTool):
    """Tool for reading file contents."""

    name = "read_file"
    description = "Read contents of a file"
    parameters = [
        ToolParameter(
            name="target_file",
            type="string",
            description="Path of the file to read",
            required=True
        ),
        ToolParameter(
            name="should_read_entire_file",
            type="boolean",
            description="Whether to read the entire file",
            required=False,
            default=False
        ),
        ToolParameter(
            name="start_line_one_indexed",
            type="integer",
            description="The one-indexed line number to start reading from (inclusive)",
            required=False
        ),
        ToolParameter(
            name="end_line_one_indexed_inclusive",
            type="integer",
            description="The one-indexed line number to end reading at (inclusive)",
            required=False
        )
    ]

    async def execute(
        self,
        target_file: str,
        should_read_entire_file: bool = False,
        start_line_one_indexed: Optional[int] = None,
        end_line_one_indexed_inclusive: Optional[int] = None
    ) -> ToolResult:
        """Execute the read file operation.

        Args:
            target_file: Path of the file to read
            should_read_entire_file: Whether to read the entire file
            start_line_one_indexed: The one-indexed line number to start reading from (inclusive)
            end_line_one_indexed_inclusive: The one-indexed line number to end reading at (inclusive)

        Returns:
            ToolResult containing the file contents
        """
        try:
            path = Path(target_file)
            if not path.exists():
                return ToolResult(
                    success=False,
                    error=f"File does not exist: {target_file}"
                )

            if not path.is_file():
                return ToolResult(
                    success=False,
                    error=f"Path is not a file: {target_file}"
                )

            with open(path, 'r', encoding='utf-8') as f:
                if should_read_entire_file:
                    content = f.read()
                    return ToolResult(
                        success=True,
                        data=content
                    )

                if start_line_one_indexed is None or end_line_one_indexed_inclusive is None:
                    return ToolResult(
                        success=False,
                        error="Both start_line_one_indexed and end_line_one_indexed_inclusive must be provided when not reading entire file"
                    )

                if start_line_one_indexed < 1:
                    return ToolResult(
                        success=False,
                        error="start_line_one_indexed must be >= 1"
                    )

                if end_line_one_indexed_inclusive < start_line_one_indexed:
                    return ToolResult(
                        success=False,
                        error="end_line_one_indexed_inclusive must be >= start_line_one_indexed"
                    )

                lines = f.readlines()
                if end_line_one_indexed_inclusive > len(lines):
                    return ToolResult(
                        success=False,
                        error=f"end_line_one_indexed_inclusive ({end_line_one_indexed_inclusive}) exceeds file length ({len(lines)})"
                    )

                content = ''.join(lines[start_line_one_indexed - 1:end_line_one_indexed_inclusive])
                return ToolResult(
                    success=True,
                    data=content
                )

        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Error reading file: {str(e)}"
            ) 