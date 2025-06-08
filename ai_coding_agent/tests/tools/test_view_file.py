import pytest
import json
from pathlib import Path
from ai_coding_agent.core.code_modification import ViewFileTool

@pytest.fixture
def test_dir(tmp_path):
    """Create a temporary directory with test files."""
    # Create test files
    (tmp_path / "test.txt").write_text("Hello, World!")
    (tmp_path / "test.py").write_text("def test_function():\n    pass")
    (tmp_path / "subdir").mkdir()
    (tmp_path / "subdir" / "test2.txt").write_text("Test content")
    return tmp_path

class TestViewFileTool:
    @pytest.mark.asyncio
    async def test_view_file_basic(self, test_dir):
        tool = ViewFileTool()
        result = await tool.execute(file_path=str(test_dir / "test.txt"))
        assert result.success is True
        assert result.data["content"] == "Hello, World!"
        assert result.data["type"] == "text"

    @pytest.mark.asyncio
    async def test_view_file_with_range(self, test_dir):
        tool = ViewFileTool()
        result = await tool.execute(
            file_path=str(test_dir / "test.py"),
            start_line=1,
            end_line=1
        )
        assert result.success is True
        assert result.data["content"] == "def test_function():\n"
        assert result.data["type"] == "text"

    @pytest.mark.asyncio
    async def test_view_file_nonexistent(self):
        tool = ViewFileTool()
        result = await tool.execute(file_path="nonexistent.txt")
        assert result.success is False
        assert result.error == "Invalid file path: nonexistent.txt" 