import pytest
from ai_coding_agent.core.file_system import EditFileTool

@pytest.fixture
def test_dir(tmp_path):
    """Create a temporary directory with test files."""
    # Create test files
    (tmp_path / "test.txt").write_text("Hello, World!")
    (tmp_path / "test.py").write_text("def test_function():\n    pass")
    (tmp_path / "subdir").mkdir()
    (tmp_path / "subdir" / "test2.txt").write_text("Test content")
    return tmp_path

@pytest.mark.asyncio
class TestEditFileTool:
    async def test_edit_file_basic(self, test_dir):
        """Test basic file editing."""
        # Create a test file
        test_file = test_dir / "test.txt"
        test_file.write_text("Original content")

        tool = EditFileTool()
        result = await tool.execute(
            target_file=str(test_file),
            instructions="Replace the content",
            code_edit="New content"
        )
        assert result.success
        assert test_file.read_text() == "New content"

    async def test_edit_file_with_context(self, test_dir):
        """Test file editing with context."""
        # Create a test file
        test_file = test_dir / "test.py"
        test_file.write_text("def test_function():\n    pass")

        tool = EditFileTool()
        result = await tool.execute(
            target_file=str(test_file),
            instructions="Replace the function with context",
            code_edit="def new_function():\n    return True"
        )
        assert result.success
        assert test_file.read_text() == "def new_function():\n    return True"

    async def test_edit_file_nonexistent(self):
        """Test editing a nonexistent file."""
        tool = EditFileTool()
        result = await tool.execute(
            target_file="nonexistent.txt",
            instructions="Replace the content",
            code_edit="New content"
        )
        assert not result.success
        assert "does not exist" in result.error 