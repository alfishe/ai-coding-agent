"""Example of using MCP server with LangChain."""

from langchain.tools import BaseTool
from typing import Type, ClassVar, Dict, Any
from pydantic import BaseModel, Field
import json
import httpx
from langchain_ollama import OllamaLLM
from langchain.agents import AgentExecutor, AgentType, initialize_agent
from langchain.memory import ConversationBufferMemory
from langchain.schema import SystemMessage
import sys
import asyncio
from mcp_sse_client import MCPClient


def build_mcp_tool_description(client: MCPClient) -> str:
    """
    Connects to the MCP server, fetches the list of available tools,
    and formats them into a detailed markdown description for the LLM.
    """
    try:
        print("Building dynamic tool description from MCP server...")
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
                    description_parts.append(f"    - {param.name} ({param_type}, {required_str})")
                    if param.description:
                        description_parts.append(f"      {param.description}")
            else:
                description_parts.append("  Parameters: None")
            description_parts.append("")

        final_description = "\n".join(description_parts)
        print("Successfully built tool description.")
        return final_description
    except Exception as e:
        print(f"Error building tool description: {e}. Using a fallback.")
        return "A gateway to interact with the MCP server. You must provide a 'tool_name' and a 'parameters' dictionary."

class MCPToolInput(BaseModel):
    """Input model for the CustomMCPTool."""
    tool_name: str = Field(..., description="The name of the MCP tool to execute.")
    parameters: Dict[str, Any] = Field(..., description="A dictionary of parameters for the specified tool.")

class CustomMCPTool(BaseTool):
    name: str = "mcp_tool"
    description: str = "A gateway to interact with the MCP server."
    args_schema: Type[BaseModel] = MCPToolInput

    def _run(self, tool_name: str, parameters: Dict[str, Any]) -> str:
        """Synchronous execution of the MCP tool."""
        print(f"\n[DEBUG] _run received: tool_name='{tool_name}', parameters={parameters}")

        async def async_run():
            client = MCPClient("http://localhost:8000/sse")
            result = await client.invoke_tool(tool_name, parameters)
            return str(result.content) if result else "No content returned from tool."

        try:
            return asyncio.run(async_run())
        except Exception as e:
            return f"Error running async tool: {e}"

    async def _arun(self, tool_name: str, parameters: Dict[str, Any]) -> str:
        """Asynchronous execution of the MCP tool."""
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
    model="gemma3",
    temperature=0.7
)

# Create memory for the agent
memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True,
    output_key="output"
)

# AgentType Options and Their Use Cases:
# -------------------------------------
# 1. ZERO_SHOT_REACT_DESCRIPTION
#    - Basic agent using ReAct (Reason + Act) format
#    - No memory/context between calls
#    - Each response is independent
#    - Uses "Thought", "Action", "Observation" format
#    - Best for: Simple, stateless tasks
#    - Not ideal for: Conversations requiring context
#
# 2. STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION (current)
#    - Enhanced zero-shot with structured output
#    - Enforces strict output format
#    - Uses "Thought", "Action", "Observation" format
#    - Best for: When you need consistent, structured outputs
#    - Not ideal for: Free-form conversations
#
# 3. CHAT_CONVERSATIONAL_REACT_DESCRIPTION
#    - Chat-focused agent with memory
#    - Maintains conversation history
#    - Uses chat format instead of ReAct
#    - Best for: Conversational interfaces
#    - Not ideal for: Strict output formatting
#
# 4. SELF_ASK_WITH_SEARCH
#    - Agent that can ask itself questions and search
#    - Uses "Question", "Answer" format
#    - Good at research and fact-finding
#    - Best for: Research tasks
#    - Not ideal for: Direct tool execution
#
# 5. PLAN_AND_EXECUTE
#    - Agent that plans before executing
#    - Creates a plan before taking action
#    - Good at breaking down complex tasks
#    - Best for: Complex multi-step tasks
#    - Not ideal for: Simple tool calls
#
# 6. OPENAI_FUNCTIONS
#    - Specialized for OpenAI's function calling
#    - Uses OpenAI's function calling format
#    - Very good at following function schemas
#    - Best for: OpenAI models with function calling
#    - Not ideal for: Non-OpenAI models
#
# 7. OPENAI_MULTI_FUNCTIONS
#    - Enhanced version of OpenAI functions
#    - Can handle multiple function calls
#    - Better at complex reasoning
#    - Best for: Complex tasks with multiple functions
#    - Not ideal for: Simple tool calls
#
# For MCP tool execution, recommended options:
# 1. OPENAI_FUNCTIONS/MULTI_FUNCTIONS: Best for strict function schemas
# 2. CHAT_CONVERSATIONAL_REACT_DESCRIPTION: Best for natural conversation
# 3. ZERO_SHOT_REACT_DESCRIPTION: Best for simple tool calls without ReAct format

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
    "tool_name": "<tool_name>",
    "parameters": {
        "<param1>": "<value1>",
        "<param2": "<value2>",
        "<param3>": "<value3>"
    }
}
⚠️ CRITICAL: Use only specified parameter names

❌ DO NOT skip required parameters
❌ DO NOT substitute parameter names

✅ COMPLETE EXAMPLE:
User: List the contents of the current directory
Assistant: I'll use the list_dir tool to show the contents of the current directory.
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
                                 {
    "tool_name": "list_dir",
    "parameters": {
        "path": "/"
    }
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
        
        # Now try through the agent
        print("\nTrying through agent...")
        response = agent.invoke({
            "input": "List the contents of the current directory using the list_dir tool. Use '.' for the directory path."
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
                print(f"Action input: {json.dumps(action.tool_input, indent=2)}")
                print(f"Tool response: {observation}")
        else:
            print("No intermediate steps in response.")
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