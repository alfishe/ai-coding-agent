from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class ToolParameter(BaseModel):
    """Base class for tool parameters."""
    name: str
    description: str
    required: bool = False
    default: Optional[Any] = None
    type: str = "string"


class ToolResult(BaseModel):
    """Base class for tool results."""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None


class BaseTool(ABC):
    """Base class for all tools in the AI coding agent."""
    
    name: str
    description: str
    parameters: List[ToolParameter]
    
    def __init__(self):
        self.validate_parameters()
    
    def validate_parameters(self) -> None:
        """Validate that all required parameters are properly defined."""
        required_params = [p for p in self.parameters if p.required]
        if not required_params:
            return
        
        param_names = [p.name for p in self.parameters]
        for param in required_params:
            if param.name not in param_names:
                raise ValueError(f"Required parameter {param.name} is not defined")
    
    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """Execute the tool with the given parameters."""
        pass
    
    def get_schema(self) -> Dict[str, Any]:
        """Get the tool's schema for API documentation."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": [p.dict() for p in self.parameters]
        } 