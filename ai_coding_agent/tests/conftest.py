import pytest
import os
import sys
import httpx
from pathlib import Path

# Add the src directory to the Python path
src_path = str(Path(__file__).parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Add the root directory to the Python path
root_path = str(Path(__file__).parent.parent)
if root_path not in sys.path:
    sys.path.insert(0, root_path)

def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers",
        "mcp_server: mark test to require MCP server to be running"
    )

@pytest.fixture(scope="session")
def mcp_server():
    """Check if MCP server is running."""
    try:
        response = httpx.get("http://localhost:8000/health")
        return response.status_code == 200
    except httpx.RequestError:
        return False

@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup and teardown for each test."""
    # Store original working directory
    original_cwd = os.getcwd()
    
    # Create a temporary directory for tests
    test_dir = Path(original_cwd) / "test_temp"
    test_dir.mkdir(exist_ok=True)
    
    # Change to test directory
    os.chdir(test_dir)
    
    yield
    
    # Restore original working directory
    os.chdir(original_cwd)
    
    # Cleanup test directory
    if test_dir.exists():
        for file in test_dir.glob("*"):
            if file.is_file():
                file.unlink()
        test_dir.rmdir()

@pytest.fixture
def test_dir(tmp_path):
    """Create a temporary directory with test files."""
    # Create test files
    (tmp_path / "test.txt").write_text("Hello, World!")
    (tmp_path / "test.py").write_text("def test_function():\n    pass")
    (tmp_path / "subdir").mkdir()
    (tmp_path / "subdir" / "test2.txt").write_text("Test content")
    return tmp_path

def pytest_runtest_setup(item):
    """Skip tests that require MCP server if it's not running."""
    if "mcp_server" in item.keywords:
        try:
            response = httpx.get("http://localhost:8000/health")
            if response.status_code != 200:
                pytest.skip("MCP server is not running")
        except httpx.RequestError:
            pytest.skip("MCP server is not running") 