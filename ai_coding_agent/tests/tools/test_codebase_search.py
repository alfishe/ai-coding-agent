import pytest
import json
from pathlib import Path
from ai_coding_agent.tools import CodeNavigationTool

@pytest.fixture
def test_dir(tmp_path):
    """Create a temporary directory with test files."""
    # Create test files
    (tmp_path / "test.txt").write_text("Hello, World!")
    (tmp_path / "test.py").write_text("def test_function():\n    pass")
    (tmp_path / "subdir").mkdir()
    (tmp_path / "subdir" / "test2.txt").write_text("Test content")
    return tmp_path

@pytest.mark.mcp_server
class TestCodebaseSearchTool:
    def test_codebase_search_basic(self, test_dir):
        tool = CodeNavigationTool()
        result = tool._run(
            query="test function",
            target_directories=[str(test_dir)]
        )
        data = json.loads(result)
        assert data["success"] is True
        assert len(data["results"]) > 0

    def test_codebase_search_no_results(self, test_dir):
        tool = CodeNavigationTool()
        result = tool._run(
            query="nonexistent term",
            target_directories=[str(test_dir)]
        )
        data = json.loads(result)
        assert data["success"] is True
        assert len(data["results"]) == 0

    def test_codebase_search_specific_directory(self, test_dir):
        tool = CodeNavigationTool()
        result = tool._run(
            query="test",
            target_directories=[str(test_dir / "subdir")]
        )
        data = json.loads(result)
        assert data["success"] is True
        assert len(data["results"]) > 0
        assert all("subdir" in result["file"] for result in data["results"]) 