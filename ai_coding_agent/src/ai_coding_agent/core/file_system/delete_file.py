"""Delete file tool."""

from pathlib import Path

from ..base import BaseTool, ToolParameter, ToolResult


class DeleteFileTool(BaseTool):
    """Tool for deleting files."""

    name = "delete_file"
    description = "Delete a file"
    parameters = [
        ToolParameter(
            name="target_file",
            type="string",
            description="Path of the file to delete",
            required=True
        )
    ]

    async def execute(self, target_file: str) -> ToolResult:
        """Execute the delete file operation.

        Args:
            target_file: Path of the file to delete

        Returns:
            ToolResult containing the deletion result
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

            path.unlink()
            return ToolResult(
                success=True,
                data={
                    "message": f"File deleted successfully: {target_file}"
                }
            )

        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Error deleting file: {str(e)}"
            ) 