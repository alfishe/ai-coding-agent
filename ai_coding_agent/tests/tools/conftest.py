import pytest
from pathlib import Path

@pytest.fixture
def test_dir(tmp_path):
    """Create a temporary directory with test files."""
    # Create test files
    (tmp_path / "test.txt").write_text("Hello, World!")
    (tmp_path / "test.py").write_text("def test_function():\n    pass")
    (tmp_path / "subdir").mkdir()
    (tmp_path / "subdir" / "test2.txt").write_text("Test content")
    return tmp_path 