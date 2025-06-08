import pytest
import json
from pathlib import Path
from ai_coding_agent.tools import GrepSearchTool

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
class TestGrepSearchTool:
    async def test_grep_search_basic(self, test_dir):
        """Test basic grep search functionality."""
        tool = GrepSearchTool()
        result = await tool.execute(
            query="test",
            include_pattern="*.txt",
            exclude_pattern=None,
            case_sensitive=True
        )
        assert result.success
        assert len(result.data["matches"]) > 0

    async def test_grep_search_with_patterns(self, test_dir):
        """Test grep search with include/exclude patterns."""
        tool = GrepSearchTool()
        result = await tool.execute(
            query="test",
            include_pattern="*.py",
            exclude_pattern="*_test.py",
            case_sensitive=True
        )
        assert result.success
        assert len(result.data["matches"]) > 0

    async def test_grep_search_case_sensitive(self, test_dir):
        """Test case sensitivity in grep search."""
        tool = GrepSearchTool()
        result = await tool.execute(
            query="TEST",
            include_pattern="*.txt",
            exclude_pattern=None,
            case_sensitive=True
        )
        assert result.success
        assert len(result.data["matches"]) == 0 