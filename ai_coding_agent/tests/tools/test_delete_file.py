import pytest
from ai_coding_agent.core.file_system import DeleteFileTool

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
class TestDeleteFileTool:
    async def test_delete_file_basic(self, test_dir):
        """Test basic file deletion."""
        # Create a test file
        test_file = test_dir / "test.txt"
        test_file.write_text("test")

        tool = DeleteFileTool()
        result = await tool.execute(target_file=str(test_file))
        assert result.success
        assert not test_file.exists()

    async def test_delete_nonexistent_file(self):
        """Test deleting a nonexistent file."""
        tool = DeleteFileTool()
        result = await tool.execute(target_file="nonexistent.txt")
        assert not result.success
        assert "does not exist" in result.error 