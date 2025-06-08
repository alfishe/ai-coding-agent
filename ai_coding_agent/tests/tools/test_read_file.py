import pytest
from ai_coding_agent.core.file_system import ReadFileTool

@pytest.mark.asyncio
class TestReadFileTool:
    async def test_read_file_basic(self, test_dir):
        """Test basic file reading."""
        # Create a test file
        test_file = test_dir / "test.txt"
        test_file.write_text("Hello, World!")

        tool = ReadFileTool()
        result = await tool.execute(
            target_file=str(test_file),
            should_read_entire_file=True
        )
        assert result.success
        assert result.data == "Hello, World!"

    async def test_read_file_with_range(self, test_dir):
        """Test reading a specific range of lines."""
        # Create a test file with multiple lines
        test_file = test_dir / "test.txt"
        test_file.write_text("Line 1\nLine 2\nLine 3\nLine 4\nLine 5")

        tool = ReadFileTool()
        result = await tool.execute(
            target_file=str(test_file),
            start_line_one_indexed=2,
            end_line_one_indexed_inclusive=4
        )
        assert result.success
        assert result.data == "Line 2\nLine 3\nLine 4"

    async def test_read_file_nonexistent(self):
        """Test reading a nonexistent file."""
        tool = ReadFileTool()
        result = await tool.execute(
            target_file="nonexistent.txt",
            should_read_entire_file=True
        )
        assert not result.success
        assert "does not exist" in result.error 