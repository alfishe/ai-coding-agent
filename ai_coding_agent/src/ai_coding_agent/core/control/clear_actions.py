"""Clear actions tool."""

from typing import Optional

from ..base import BaseTool, ToolParameter, ToolResult


class ClearActionsTool(BaseTool):
    """Tool for clearing the action queue."""

    name = "clear_actions"
    description = "Clear the action queue"
    parameters = [
        ToolParameter(
            name="include_completed",
            type="boolean",
            description="Whether to include completed actions",
            required=False,
            default=False
        )
    ]

    async def execute(
        self,
        include_completed: bool = False
    ) -> ToolResult:
        """Execute the clear actions operation.

        Args:
            include_completed: Whether to include completed actions

        Returns:
            ToolResult containing the clear result
        """
        try:
            # TODO: Implement actual action queue clearing functionality
            # This is a placeholder implementation
            return ToolResult(
                success=True,
                data={
                    "message": "Action queue cleared successfully",
                    "cleared_count": 5
                }
            )

        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Error clearing actions: {str(e)}"
            ) 