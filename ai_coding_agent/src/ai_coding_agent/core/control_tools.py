from collections import deque
from typing import Dict, List, Optional, Any, Deque

from .base import BaseTool, ToolParameter, ToolResult


class Action:
    """Represents an action in the queue."""
    def __init__(self, tool_name: str, parameters: Dict[str, Any]):
        self.tool_name = tool_name
        self.parameters = parameters
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert action to dictionary format."""
        return {
            "tool_name": self.tool_name,
            "parameters": self.parameters
        }


class ActionQueue:
    """Singleton class to manage the action queue."""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._queue: Deque[Action] = deque()
        return cls._instance
    
    def push(self, action: Action) -> None:
        """Add an action to the queue."""
        self._queue.append(action)
    
    def pop(self) -> Optional[Action]:
        """Remove and return the next action from the queue."""
        return self._queue.popleft() if self._queue else None
    
    def peek(self) -> Optional[Action]:
        """Return the next action without removing it."""
        return self._queue[0] if self._queue else None
    
    def clear(self) -> None:
        """Clear the action queue."""
        self._queue.clear()
    
    def get_all(self) -> List[Action]:
        """Get all actions in the queue."""
        return list(self._queue)


class PushActionTool(BaseTool):
    """Tool for pushing an action to the queue."""
    
    name = "push_action"
    description = "Push an action to the FIFO queue"
    parameters = [
        ToolParameter(
            name="tool_name",
            description="Name of the tool to execute",
            required=True,
            type="string"
        ),
        ToolParameter(
            name="parameters",
            description="Parameters for the tool",
            required=True,
            type="object"
        )
    ]
    
    async def execute(
        self,
        tool_name: str,
        parameters: Dict[str, Any]
    ) -> ToolResult:
        try:
            action = Action(tool_name, parameters)
            ActionQueue().push(action)
            
            return ToolResult(
                success=True,
                data={
                    "message": "Action pushed to queue",
                    "action": action.to_dict()
                }
            )
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class ShowActionsTool(BaseTool):
    """Tool for showing all actions in the queue."""
    
    name = "show_actions"
    description = "Show all actions in the FIFO queue"
    parameters = []
    
    async def execute(self) -> ToolResult:
        try:
            actions = ActionQueue().get_all()
            
            return ToolResult(
                success=True,
                data={
                    "count": len(actions),
                    "actions": [action.to_dict() for action in actions]
                }
            )
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class GetNextActionTool(BaseTool):
    """Tool for getting the next action from the queue."""
    
    name = "get_next_action"
    description = "Get and remove the next action from the FIFO queue"
    parameters = []
    
    async def execute(self) -> ToolResult:
        try:
            action = ActionQueue().pop()
            
            if action is None:
                return ToolResult(
                    success=True,
                    data={
                        "message": "Queue is empty",
                        "action": None
                    }
                )
            
            return ToolResult(
                success=True,
                data={
                    "message": "Action retrieved from queue",
                    "action": action.to_dict()
                }
            )
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class ClearActionsTool(BaseTool):
    """Tool for clearing the action queue."""
    
    name = "clear_actions"
    description = "Clear all actions from the FIFO queue"
    parameters = []
    
    async def execute(self) -> ToolResult:
        try:
            ActionQueue().clear()
            
            return ToolResult(
                success=True,
                data={
                    "message": "Action queue cleared"
                }
            )
        except Exception as e:
            return ToolResult(success=False, error=str(e)) 