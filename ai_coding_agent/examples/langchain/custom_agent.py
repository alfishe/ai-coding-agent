"""
Example of creating a custom agent with specific tools.
"""

from ai_coding_agent import AICodingAgentToolkit
from langchain.agents import AgentExecutor, create_react_agent
from langchain.llms import Ollama
from langchain.prompts import PromptTemplate


def main():
    # Initialize the toolkit
    toolkit = AICodingAgentToolkit()
    
    # Get specific tools
    tools = [
        tool for tool in toolkit.get_tools()
        if tool.name in ["list_dir", "grep_search", "view_file"]
    ]
    
    # Create an LLM
    llm = Ollama(model="codellama")
    
    # Create a custom prompt template
    template = """
    You are an AI code analyzer. Your task is to analyze code and provide insights.
    Use the available tools to examine the codebase.
    
    Available tools:
    {tools}
    
    Task: {input}
    
    Think through the steps needed to analyze the code, then use the tools to gather information.
    Provide a detailed analysis of what you find.
    """
    
    prompt = PromptTemplate(
        input_variables=["input", "tools"],
        template=template
    )
    
    # Create a custom agent
    agent = create_react_agent(llm, tools, prompt)
    
    # Create an agent executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True
    )
    
    # Example analysis tasks
    tasks = [
        "Analyze the project structure and list all Python files",
        "Find all functions that use async/await",
        "Examine the main entry points of the application"
    ]
    
    # Run each task
    for task in tasks:
        print(f"\nExecuting analysis task: {task}")
        try:
            result = agent_executor.invoke({"input": task})
            print(f"Analysis result: {result['output']}")
        except Exception as e:
            print(f"Error: {str(e)}")


if __name__ == "__main__":
    main() 