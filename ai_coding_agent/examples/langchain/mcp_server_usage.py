from langchain.tools import BaseTool
from typing import Type, ClassVar, Dict, Any
from pydantic import BaseModel, Field
import json
import requests
import httpx
from langchain_ollama import OllamaLLM
from langchain.agents import AgentExecutor, AgentType, initialize_agent
from langchain.prompts import MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from langchain.schema import SystemMessage
import sys
from sseclient import SSEClient
import asyncio
from mcp_sse_client import MCPClient


def build_mcp_tool_description(client: MCPClient) -> str:
    """
    Connects to the MCP server, fetches the list of available tools,
    and formats them into a detailed markdown description for the LLM.
    """
    try:
        print("Building dynamic tool description from MCP server...")
        # Use asyncio.run to execute the async method from a sync context
        tools: list[ToolDefinition] = asyncio.run(client.list_tools())
        
        description_parts = [
            "A gateway to interact with the MCP server. You MUST provide a 'tool_name' and a 'parameters' dictionary.",
            "Here are the available tools and their required parameters:\n"
        ]
        
        for tool in tools:
            description_parts.append(f"- Tool: {tool.name}")
            description_parts.append(f"  Description: {tool.description}")
            if hasattr(tool, 'parameters') and tool.parameters:
                description_parts.append("  Parameters:")
                for param in tool.parameters:
                    param_type = getattr(param, 'type', 'string')
                    required_str = "required" if param.required else "optional"
                    # Use a clean format the LLM can easily parse
                    description_parts.append(f"    - {param.name} ({param.parameter_type}, {required_str})")
                    if param.description:
                        description_parts.append(": {param.description}")
            else:
                description_parts.append("  Parameters: None")
            description_parts.append("") # Add a blank line for readability

        final_description = "\n".join(description_parts)
        print("Successfully built tool description.")
        return final_description
    except Exception as e:
        print(f"Error building tool description: {e}. Using a fallback.")
        return "A gateway to interact with the MCP server. You must provide a 'tool_name' and a 'parameters' dictionary. Example tools: 'list_dir', 'find_by_name'."

# 1. Define the input schema for your tool. This is what the agent will see.
class MCPToolInput(BaseModel):
    """Input model for the CustomMCPTool."""
    tool_name: str = Field(..., description="The name of the MCP tool to execute (e.g., 'list_dir', 'find_by_name').")
    parameters: Dict[str, Any] = Field(default_factory=dict,
                                       description="A dictionary of parameters for the specified tool.")


class CustomMCPTool(BaseTool):
    # Use simple class attributes for name and description
    name: str = "mcp_tool"
    description: str = "A gateway to interact with the MCP server."
    args_schema: Type[BaseModel] = MCPToolInput

    # 2. Assign the Pydantic model as the args_schema. THIS IS THE KEY.
    args_schema: Type[BaseModel] = MCPToolInput

    # 3. Update the method signature to accept keyword arguments
    def _run(self, tool_name: str, parameters: Dict[str, Any] = None) -> str:
        """Synchronous execution of the MCP tool."""
        # The agent will now call this with tool_name="...", parameters={...}
        if parameters is None:
            parameters = {}

        print(f"\n[DEBUG] _run received: tool_name='{tool_name}', parameters={parameters}")

        # Your existing async logic works well here
        async def async_run():
            client = MCPClient("http://localhost:8000/sse")
            result = await client.invoke_tool(tool_name, parameters)
            # Ensure the result is always a string for LangChain
            return str(result.content) if result else "No content returned from tool."

        try:
            # Use asyncio.run() to execute the async function
            return asyncio.run(async_run())
        except Exception as e:
            return f"Error running async tool: {e}"

    async def _arun(self, tool_name: str, parameters: Dict[str, Any] = None) -> str:
        """Asynchronous execution of the MCP tool."""
        if parameters is None:
            parameters = {}

        print(f"\n[DEBUG] _arun received: tool_name='{tool_name}', parameters={parameters}")

        client = MCPClient("http://localhost:8000/sse")
        result = await client.invoke_tool(tool_name, parameters)
        return str(result.content) if result else "No content returned from tool."


async def main():
    # Connect to an MCP endpoint with optional timeout and retry settings
    # IMPORTANT: URL must end with /sse for Server-Sent Events
    client = MCPClient(
        "http://localhost:8000/sse",  # Note the /sse suffix!
        timeout=30.0,      # Connection timeout in seconds
        max_retries=3      # Maximum retry attempts
    )
    
    # List available tools
    tools = await client.list_tools()
    print(f"Found {len(tools)} tools")
    print("\nAvailable MCP Tools:")
    print("-------------------")
    for tool in tools:
        print(f"- {tool.name}: {tool.description}")
        if hasattr(tool, 'parameters'):
            print("  Parameters:")
            for param in tool.parameters:
                required = "required" if param.required else "optional"
                param_type = getattr(param, 'type', 'string')  # Default to string if type not found
                print(f"    - {param.name} ({param_type}, {required}): {param.description}")
        print()

if __name__ == "__main__":
    asyncio.run(main())


# Initialize components
llm = OllamaLLM(
    base_url="http://localhost:11434",
    model="llama3",
    temperature=0.7
)

# Create memory for the agent
memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True,
    output_key="output"
)

# Create agent with return_intermediate_steps
agent = initialize_agent(
    tools=[CustomMCPTool()],
    llm=llm,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True,
    return_intermediate_steps=True,
    memory=memory,
    system_message=SystemMessage(content="""You are an AI assistant that helps users interact with the MCP server tools.

⚠️ CRITICAL: You MUST provide the input in this EXACT format:
{
    "tool_name": "list_dir",
    "parameters": {
        "directory_path": ".",
        "sort_by": "name",
        "sort_order": "asc"
    }
}

❌ DO NOT wrap the input in an "action" or "action_input" object
❌ DO NOT leave the parameters dictionary empty
❌ DO NOT omit required parameters

✅ COMPLETE EXAMPLE:
User: List the contents of the current directory
Assistant: I'll use the list_dir tool to show the contents of the current directory.
- Tool: list_dir
  Description: List directory contents.
  Parameters:
    - directory_path (string, **required**)
    - sort_by (string, optional)
    - sort_order (string, optional)
Since directory_path marked as **required** - we must provide it.

Valid generated tool calls:
{
    "tool_name": "list_dir",
    "parameters": {
        "directory_path": ".",
        "sort_by": "name",
        "sort_order": "asc"
    }
}

User: Show contents of / folder
Assistant: I'll use the list_dir tool to show the contents of the root directory.
{
    "tool_name": "list_dir",
    "parameters": {
        "directory_path": "/",
        "sort_by": "name",
        "sort_order": "asc"
    }
}

❌ INCORRECT EXAMPLES (DO NOT USE):
{
    "action": "mcp_tool",
    "action_input": {
        "tool_name": "list_dir",
        "parameters": {}
    }
}

{
    "tool_name": "list_dir",
    "parameters": {}
}

IMPORTANT RULES:
1. The input MUST be a direct dictionary with "tool_name" and "parameters" keys
2. The "parameters" dictionary MUST include ALL required parameters
3. For directory paths, use "." for current directory
4. Always check the tool description for required parameters
5. If unsure about parameters, ask the user for clarification

Remember: The tool will fail if any required parameters are missing!"""),
    max_iterations=3
)

# Example usage
if __name__ == "__main__":
    try:
        # First, check if server is running
        try:
            with httpx.stream('GET', 'http://localhost:8000/sse') as response:
                print("MCP server is running!")
        except httpx.RequestError:
            print("Error: MCP server is not running!")
            print("Please start the server first with:")
            print("cd ai_coding_agent && PYTHONPATH=src python -m ai_coding_agent.interfaces.mcp")
            sys.exit(1)

        # 1. Create a temporary client to build the description
        mcp_client_for_setup = MCPClient("http://localhost:8000/sse")
        dynamic_description = build_mcp_tool_description(mcp_client_for_setup)
        print("\nDynamic tool description:")
        print(dynamic_description)
        print("\n\n")
        
        # 2. Instantiate the tool and inject the dynamic description
        mcp_tool = CustomMCPTool(description=dynamic_description)
        
        # Example: List current directory contents
        print("\nMaking tool call to list directory contents...")

        # Create a test tool call directly - NOTE THE NEW CALLING STYLE
        print("\nTesting tool directly...")
        tool = CustomMCPTool()
        result = tool._run(
            tool_name="list_dir", 
            parameters={
                "directory_path": ".",
                "sort_by": "name",
                "sort_order": "asc"
            }
        )
        print(f"\nDirect tool test result: {result}")
        
        # Now try through the agent - this should now work!
        print("\nTrying through agent...")
        response = agent.invoke({
            "input": "Show contents of / folder using list_dir tool. Retrieve information from the tool, parse JSON, print <type> <name> pair per line"
        })

        print("\n=== FINAL RESULT ===")
        if "output" in response:
            print(response["output"])
        else:
            print("No output in response")

        print("\n=== TOOL EXECUTION DETAILS ===")
        if "intermediate_steps" in response and response["intermediate_steps"]:
            for step in response["intermediate_steps"]:
                action, observation = step
                print(f"\nAction taken: {action.tool}")
                # action.tool_input is already a dict, so we can dump it
                print(f"Action input: {json.dumps(action.tool_input, indent=2)}")
                print(f"Tool response: {observation}")
        else:
            print("No intermediate steps in response.")
            # Print response in a more readable format
            print("\nResponse contents:")
            for key, value in response.items():
                if key == "chat_history":
                    print("\nChat History:")
                    for msg in value:
                        print(f"- {msg.type}: {msg.content}")
                else:
                    print(f"\n{key}:")
                    print(value)

    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()