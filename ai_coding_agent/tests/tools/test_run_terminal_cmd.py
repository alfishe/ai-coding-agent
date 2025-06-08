import pytest
from ai_coding_agent.core.control import RunTerminalCmdTool

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
class TestRunTerminalCmdTool:
    async def test_run_terminal_cmd_basic(self):
        """Test basic terminal command execution."""
        tool = RunTerminalCmdTool()
        result = await tool.execute(
            command="echo 'Hello, World!'",
            is_background=False,
            require_user_approval=True
        )
        assert result.success
        assert "Hello, World!" in result.data["output"]

    async def test_run_terminal_cmd_invalid(self):
        """Test invalid terminal command execution."""
        tool = RunTerminalCmdTool()
        result = await tool.execute(
            command="nonexistent_command",
            is_background=False,
            require_user_approval=True
        )
        assert not result.success
        assert "error" in result.data

    async def test_run_terminal_cmd_background(self):
        """Test background terminal command execution."""
        tool = RunTerminalCmdTool()
        result = await tool.execute(
            command="sleep 1",
            is_background=True,
            require_user_approval=True
        )
        assert result.success
        assert result.data["pid"] > 0 