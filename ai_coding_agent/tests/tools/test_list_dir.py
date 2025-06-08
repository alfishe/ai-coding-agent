"""Tests for the list directory tool."""

import pytest
import json
from pathlib import Path
from ai_coding_agent.core.file_system import ListDirectoryTool

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
class TestListDirectoryTool:
    async def test_list_dir_basic(self, test_dir):
        """Test basic directory listing."""
        tool = ListDirectoryTool()
        result = await tool.execute(directory_path=str(test_dir))
        assert result.success
        assert "contents" in result.data
        assert len(result.data["contents"]) > 0

    async def test_list_dir_empty(self, test_dir):
        """Test listing an empty directory."""
        empty_dir = test_dir / "empty"
        empty_dir.mkdir()
        
        tool = ListDirectoryTool()
        result = await tool.execute(directory_path=str(empty_dir))
        assert result.success
        assert "contents" in result.data
        assert len(result.data["contents"]) == 0

    async def test_list_dir_nonexistent(self):
        """Test listing a nonexistent directory."""
        tool = ListDirectoryTool()
        result = await tool.execute(directory_path="nonexistent")
        assert not result.success
        assert "does not exist" in result.error

    async def test_list_dir_not_directory(self, test_dir):
        """Test listing a path that is not a directory."""
        test_file = test_dir / "test.txt"
        test_file.write_text("test")
        
        tool = ListDirectoryTool()
        result = await tool.execute(directory_path=str(test_file))
        assert not result.success
        assert "not a directory" in result.error

    async def test_list_dir_sorting(self, test_dir):
        """Test that directory contents are sorted alphabetically."""
        # Create test files with different names
        (test_dir / "c.txt").write_text("")
        (test_dir / "a.txt").write_text("")
        (test_dir / "b.txt").write_text("")
        
        tool = ListDirectoryTool()
        result = await tool.execute(directory_path=str(test_dir))
        assert result.success
        assert "contents" in result.data
        
        # Get just the filenames
        filenames = [item["name"] for item in result.data["contents"]]
        
        # Check that they're sorted
        assert filenames == sorted(filenames)

    async def test_list_dir_patterns(self, test_dir):
        """Test directory listing with include/exclude patterns."""
        # Create test files with specific names for pattern testing
        (test_dir / "test1.txt").write_text("")
        (test_dir / "test2.py").write_text("")
        (test_dir / "other.txt").write_text("")
        (test_dir / "test.txt").write_text("test")
        
        # Ensure subdir exists
        subdir = test_dir / "subdir"
        if not subdir.exists():
            subdir.mkdir()
        
        tool = ListDirectoryTool()
        
        # Test include pattern - should only match test1.txt
        result = await tool.execute(
            directory_path=str(test_dir),
            include_pattern="test[0-9].txt"
        )
        assert result.success
        assert "contents" in result.data
        assert len(result.data["contents"]) == 1
        assert result.data["contents"][0]["name"] == "test1.txt"
        
        # Test exclude pattern - should exclude test2.py
        result = await tool.execute(
            directory_path=str(test_dir),
            exclude_pattern="*.py"
        )
        assert result.success
        assert "contents" in result.data
        contents = result.data["contents"]
        assert len(contents) == 4  # other.txt, subdir, test.txt, test1.txt
        assert all(not item["name"].endswith(".py") for item in contents)
        assert any(item["name"] == "subdir" and item["type"] == "directory" for item in contents)
        
        # Test both patterns together
        result = await tool.execute(
            directory_path=str(test_dir),
            include_pattern="test*.txt",
            exclude_pattern="test.txt"
        )
        assert result.success
        assert "contents" in result.data
        assert len(result.data["contents"]) == 1
        assert result.data["contents"][0]["name"] == "test1.txt"

    async def test_list_dir_invalid_path(self):
        """Test listing an invalid path."""
        tool = ListDirectoryTool()
        result = await tool.execute(directory_path="/nonexistent/path")
        assert not result.success
        assert result.error == "Path does not exist: /nonexistent/path"

    async def test_list_dir_sort_by_name(self, test_dir):
        """Test sorting by name."""
        # Create test files with different names
        (test_dir / "z.txt").write_text("")
        (test_dir / "a.txt").write_text("")
        (test_dir / "m.txt").write_text("")
        
        tool = ListDirectoryTool()
        result = await tool.execute(
            directory_path=str(test_dir),
            sort_by="name"
        )
        assert result.success
        filenames = [item["name"] for item in result.data["contents"]]
        assert filenames == sorted(filenames)

    async def test_list_dir_sort_by_type(self, test_dir):
        """Test sorting by type."""
        # Create test files and directories
        (test_dir / "file1.txt").write_text("")
        (test_dir / "dir1").mkdir()
        (test_dir / "file2.py").write_text("")
        (test_dir / "dir2").mkdir()
        
        tool = ListDirectoryTool()
        result = await tool.execute(
            directory_path=str(test_dir),
            sort_by="type"
        )
        assert result.success
        contents = result.data["contents"]
        
        # Check that directories come before files
        dirs = [item for item in contents if item["type"] == "directory"]
        files = [item for item in contents if item["type"] == "file"]
        assert all(d["type"] == "directory" for d in dirs)
        assert all(f["type"] == "file" for f in files)
        assert len(dirs) == 3  # dir1, dir2, and subdir from fixture
        assert len(files) == 4  # file1.txt, file2.py, test.txt, test.py from fixture
        
        # Verify directory names
        dir_names = {d["name"] for d in dirs}
        assert dir_names == {"dir1", "dir2", "subdir"}
        
        # Verify file names
        file_names = {f["name"] for f in files}
        assert file_names == {"file1.txt", "file2.py", "test.txt", "test.py"}

    async def test_list_dir_sort_by_size(self, test_dir):
        """Test sorting by size."""
        # Create test files with different sizes
        (test_dir / "small.txt").write_text("a")
        (test_dir / "medium.txt").write_text("a" * 100)
        (test_dir / "large.txt").write_text("a" * 1000)
        
        tool = ListDirectoryTool()
        result = await tool.execute(
            directory_path=str(test_dir),
            sort_by="size"
        )
        assert result.success
        contents = result.data["contents"]
        sizes = [item["size"] for item in contents if item["type"] == "file"]
        assert sizes == sorted(sizes)

    async def test_list_dir_sort_by_modified(self, test_dir):
        """Test sorting by modification time."""
        # Create test files
        (test_dir / "old.txt").write_text("")
        (test_dir / "new.txt").write_text("")
        
        tool = ListDirectoryTool()
        result = await tool.execute(
            directory_path=str(test_dir),
            sort_by="modified"
        )
        assert result.success
        contents = result.data["contents"]
        modified_times = [item["modified"] for item in contents]
        assert modified_times == sorted(modified_times)

    async def test_list_dir_invalid_sort_by(self, test_dir):
        """Test invalid sort_by parameter."""
        tool = ListDirectoryTool()
        result = await tool.execute(
            directory_path=str(test_dir),
            sort_by="invalid"
        )
        assert not result.success
        assert "Invalid sort_by value" in result.error

    async def test_list_dir_include_pattern_nonexistent(self, test_dir):
        """Test include pattern that matches no files."""
        tool = ListDirectoryTool()
        result = await tool.execute(
            directory_path=str(test_dir),
            include_pattern="nonexistent.*"
        )
        assert result.success
        assert len(result.data["contents"]) == 0

    async def test_list_dir_exclude_all(self, test_dir):
        """Test exclude pattern that excludes all files."""
        tool = ListDirectoryTool()
        result = await tool.execute(
            directory_path=str(test_dir),
            exclude_pattern="*"
        )
        assert result.success
        assert len(result.data["contents"]) == 0

    async def test_list_dir_complex_patterns(self, test_dir):
        """Test complex include/exclude patterns."""
        # Create test files with various extensions
        (test_dir / "test.py").write_text("")
        (test_dir / "test.pyc").write_text("")
        (test_dir / "test.pyo").write_text("")
        (test_dir / "test.txt").write_text("")
        
        tool = ListDirectoryTool()
        result = await tool.execute(
            directory_path=str(test_dir),
            include_pattern="*.py*",  # Should match .py, .pyc, .pyo
            exclude_pattern="*.pyc"   # Should exclude .pyc
        )
        assert result.success
        contents = result.data["contents"]
        filenames = [item["name"] for item in contents]
        assert "test.py" in filenames
        assert "test.pyo" in filenames
        assert "test.pyc" not in filenames
        assert "test.txt" not in filenames 