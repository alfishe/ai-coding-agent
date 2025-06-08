import pytest
from ai_coding_agent.core.file_system import FileSearchTool

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
class TestFileSearchTool:
    async def test_file_search_basic(self, test_dir):
        """Test basic file search."""
        # Create test files
        test_file1 = test_dir / "test1.txt"
        test_file1.write_text("test")
        test_file2 = test_dir / "test2.txt"
        test_file2.write_text("test")

        tool = FileSearchTool()
        result = await tool.execute(query="test")
        assert result.success
        assert len(result.data["matches"]) == 2

    async def test_file_search_no_results(self):
        """Test file search with no results."""
        tool = FileSearchTool()
        result = await tool.execute(query="nonexistent")
        assert result.success
        assert len(result.data["matches"]) == 0

    async def test_file_search_specific_extension(self, test_dir):
        """Test file search with specific extension."""
        # Create test files
        test_file1 = test_dir / "test1.txt"
        test_file1.write_text("test")
        test_file2 = test_dir / "test2.py"
        test_file2.write_text("test")

        tool = FileSearchTool()
        result = await tool.execute(query="test.py")
        assert result.success
        assert len(result.data["matches"]) == 1
        assert result.data["matches"][0].endswith("test2.py") 