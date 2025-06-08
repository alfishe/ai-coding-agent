"""
Example of starting and using the MCP server.
"""

import asyncio
import logging
import signal
import sys
from typing import Optional

import aiohttp
from ai_coding_agent import MCPServer





# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ServerManager:
    """Manages the MCP server lifecycle and API calls."""
    
    def __init__(self, host: str = "localhost", port: int = 8000):
        self.host = host
        self.port = port
        self.server: Optional[MCPServer] = None
        self.server_task: Optional[asyncio.Task] = None
        self.shutdown_event = asyncio.Event()
    
    async def start_server(self) -> None:
        """Start the MCP server asynchronously."""
        try:
            # Create the MCPServer instance
            self.server = MCPServer(
                host=self.host, 
                port=self.port
            )
            self.server_task = asyncio.create_task(self.server.start_async())
            logger.info(f"Starting MCP server on http://{self.host}:{self.port}")
            
            # Wait for server to start
            await asyncio.sleep(1)
            logger.info("Server started successfully")
        except Exception as e:
            logger.error(f"Failed to start server: {str(e)}")
            raise
    
    async def stop_server(self) -> None:
        """Stop the MCP server gracefully."""
        if self.server_task:
            logger.info("Stopping server...")
            self.server_task.cancel()
            try:
                await self.server_task
            except asyncio.CancelledError:
                logger.info("Server stopped gracefully")
            except Exception as e:
                logger.error(f"Error stopping server: {str(e)}")
    
    async def make_api_call(self, method: str, endpoint: str, data: dict = None) -> dict:
        """Make an API call to the server with error handling."""
        url = f"http://{self.host}:{self.port}{endpoint}"
        try:
            async with aiohttp.ClientSession() as session:
                if method.upper() == "GET":
                    async with session.get(url) as response:
                        response.raise_for_status()
                        return await response.json()
                elif method.upper() == "POST":
                    async with session.post(url, json=data) as response:
                        response.raise_for_status()
                        return await response.json()
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
        except aiohttp.ClientError as e:
            logger.error(f"API call failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during API call: {str(e)}")
            raise
    
    async def list_tools(self) -> None:
        """List all available tools."""
        try:
            tools = await self.make_api_call("GET", "/tools")
            print("\nAvailable tools:")
            for tool in tools:
                print(f"- {tool['name']}: {tool['description']}")
        except Exception as e:
            logger.error(f"Failed to list tools: {str(e)}")
    
    async def list_directory(self, directory_path: str = ".") -> None:
        """List directory contents."""
        try:
            result = await self.make_api_call(
                "POST",
                "/tools/list_dir",
                {
                    "directory_path": directory_path,
                    "sort_by": "name",
                    "sort_order": "asc"
                }
            )
            print("\nDirectory listing result:")
            print(result)
        except Exception as e:
            logger.error(f"Failed to list directory: {str(e)}")
    
    async def find_files(self, pattern: str = "*.py", directory: str = ".") -> None:
        """Search for files matching a pattern."""
        try:
            result = await self.make_api_call(
                "POST",
                "/tools/find_by_name",
                {
                    "search_path": directory,
                    "pattern": pattern,
                    "recursive": True
                }
            )
            print(f"\nFiles matching '{pattern}' found:")
            print(result)
        except Exception as e:
            logger.error(f"Failed to find files: {str(e)}")


async def main():
    """Main function to run the server example."""
    server_manager = ServerManager()
    
    # Set up signal handlers for graceful shutdown
    def signal_handler(sig, frame):
        logger.info("Received shutdown signal")
        asyncio.create_task(server_manager.stop_server())
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Start the server
        await server_manager.start_server()
        
        # Make example API calls
        await server_manager.list_tools()
        await server_manager.list_directory()
        await server_manager.find_files()
        
        # Keep the server running until shutdown signal
        while True:
            await asyncio.sleep(1)
            
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        await server_manager.stop_server()
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        sys.exit(1) 