import difflib
from pathlib import Path
from typing import Dict, List, Optional, Union

from .base import BaseTool, ToolParameter, ToolResult


class ProposeCodeTool(BaseTool):
    """Tool for proposing code changes."""
    
    name = "propose_code"
    description = "Propose code changes to a file"
    parameters = [
        ToolParameter(
            name="target_file",
            description="File to modify",
            required=True,
            type="string"
        ),
        ToolParameter(
            name="code_edit",
            description="Code changes with {{ ... }} for unchanged parts",
            required=True,
            type="string"
        ),
        ToolParameter(
            name="instruction",
            description="Description of the changes",
            required=True,
            type="string"
        )
    ]
    
    async def execute(
        self,
        target_file: str,
        code_edit: str,
        instruction: str
    ) -> ToolResult:
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
            
            # Read current file content
            with open(path, "r", encoding="utf-8") as f:
                current_content = f.read()
            
            # Generate diff
            diff = self._generate_diff(current_content, code_edit)
            
            return ToolResult(success=True, data={
                "file": str(path),
                "instruction": instruction,
                "diff": diff,
                "preview": code_edit
            })
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    def _generate_diff(self, original: str, modified: str) -> str:
        """Generate a unified diff between original and modified content."""
        diff = difflib.unified_diff(
            original.splitlines(),
            modified.splitlines(),
            lineterm=""
        )
        return "\n".join(diff)


class ViewCodeItemTool(BaseTool):
    """Tool for viewing specific code items."""
    
    name = "view_code_item"
    description = "View a specific code item in a file"
    parameters = [
        ToolParameter(
            name="file",
            description="Path to the file",
            required=True,
            type="string"
        ),
        ToolParameter(
            name="node_path",
            description="Path to the code item (e.g., function name, class name)",
            required=True,
            type="string"
        )
    ]
    
    async def execute(
        self,
        file: str,
        node_path: str
    ) -> ToolResult:
        try:
            path = Path(file)
            if not path.exists() or not path.is_file():
                return ToolResult(
                    success=False,
                    error=f"Invalid file path: {file}"
                )
            
            # Note: In a real implementation, you would use a proper AST parser
            # This is a simplified placeholder implementation
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Simple text-based search for the node
            lines = content.splitlines()
            for i, line in enumerate(lines):
                if node_path in line:
                    # Find the start and end of the code block
                    start = max(0, i - 2)
                    end = min(len(lines), i + 3)
                    
                    return ToolResult(success=True, data={
                        "file": str(path),
                        "node_path": node_path,
                        "content": "\n".join(lines[start:end]),
                        "line_number": i + 1
                    })
            
            return ToolResult(
                success=False,
                error=f"Code item not found: {node_path}"
            )
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class ViewFileTool(BaseTool):
    """Tool for viewing file contents."""
    
    name = "view_file"
    description = "View file contents"
    parameters = [
        ToolParameter(
            name="file_path",
            description="Path to the file (can be relative or absolute)",
            required=True,
            type="string"
        ),
        ToolParameter(
            name="start_line",
            description="Start line number (only for text files)",
            required=False,
            type="integer"
        ),
        ToolParameter(
            name="end_line",
            description="End line number (only for text files)",
            required=False,
            type="integer"
        ),
        ToolParameter(
            name="include_summary",
            description="Include summary of other lines (only for text files)",
            required=False,
            default=False,
            type="boolean"
        )
    ]
    
    async def execute(
        self,
        file_path: str,
        start_line: Optional[int] = None,
        end_line: Optional[int] = None,
        include_summary: bool = False
    ) -> ToolResult:
        try:
            # Convert to absolute path if relative
            path = Path(file_path).resolve()
            if not path.exists() or not path.is_file():
                return ToolResult(
                    success=False,
                    error=f"Invalid file path: {file_path}"
                )
            
            # Check if file is binary
            is_binary = self._is_binary_file(path)
            
            if is_binary:
                # For binary files, return file info only
                result = {
                    "file": str(path),
                    "type": "binary",
                    "size": path.stat().st_size,
                    "mime_type": self._get_mime_type(path)
                }
                return ToolResult(success=True, data=result)
            
            # For text files, read content
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            if start_line is None:
                start_line = 1
            if end_line is None:
                end_line = len(lines)
            
            # Adjust for 1-based line numbers
            start_line = max(1, start_line)
            end_line = min(len(lines), end_line)
            
            content = "".join(lines[start_line - 1:end_line])
            
            result = {
                "file": str(path),
                "type": "text",
                "content": content,
                "start_line": start_line,
                "end_line": end_line
            }
            
            if include_summary:
                result["summary"] = {
                    "total_lines": len(lines),
                    "shown_lines": end_line - start_line + 1,
                    "language": path.suffix[1:] if path.suffix else None
                }
            
            return ToolResult(success=True, data=result)
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    def _is_binary_file(self, path: Path) -> bool:
        """Check if a file is binary by reading its first few bytes."""
        try:
            with open(path, 'rb') as f:
                chunk = f.read(1024)
                return b'\0' in chunk
        except Exception:
            return True  # If we can't read the file, assume it's binary
    
    def _get_mime_type(self, path: Path) -> str:
        """Get the MIME type of a file based on its extension."""
        import mimetypes
        mime_type, _ = mimetypes.guess_type(str(path))
        return mime_type or 'application/octet-stream' 