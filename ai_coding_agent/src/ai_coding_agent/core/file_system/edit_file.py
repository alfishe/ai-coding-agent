"""Edit file contents tool."""

from pathlib import Path
from typing import Optional

from ..base import BaseTool, ToolParameter, ToolResult


class EditFileTool(BaseTool):
    """Tool for editing file contents."""

    name = "edit_file"
    description = "Edit contents of a file"
    parameters = [
        ToolParameter(
            name="target_file",
            type="string",
            description="Path of the file to edit",
            required=True
        ),
        ToolParameter(
            name="instructions",
            type="string",
            description="Instructions for the edit",
            required=True
        ),
        ToolParameter(
            name="code_edit",
            type="string",
            description="The code edit to apply",
            required=True
        )
    ]

    async def execute(
        self,
        target_file: str,
        instructions: str,
        code_edit: str
    ) -> ToolResult:
        """Execute the edit file operation.

        Args:
            target_file: Path of the file to edit
            instructions: Instructions for the edit
            code_edit: The code edit to apply

        Returns:
            ToolResult containing the edit result
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

            # Read the current content
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Apply the edit
            # This is a simple implementation that assumes the edit is a complete replacement
            # In a real implementation, you would want to use a more sophisticated diff/patch system
            with open(path, 'w', encoding='utf-8') as f:
                f.write(code_edit)

            return ToolResult(
                success=True,
                data={
                    "message": "File edited successfully",
                    "instructions": instructions
                }
            )

        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Error editing file: {str(e)}"
            ) 