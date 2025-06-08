"""
Basic example of using AI Coding Agent tools with LangChain.
"""

from ai_coding_agent import AICodingAgentToolkit
from langchain.agents import initialize_agent
from langchain.llms import Ollama
from langchain.prompts import PromptTemplate


def main():
    # Initialize the toolkit
    toolkit = AICodingAgentToolkit()
    
    # Create an LLM (using Ollama with CodeLlama model)
    llm = Ollama(model="codellama")
    
    # Create a prompt template
    template = """
    You are an AI coding assistant. Use the available tools to help with the task.
    
    Task: {task}
    
    Think through the steps needed to complete the task, then use the tools to accomplish it.
    """
    
    prompt = PromptTemplate(
        input_variables=["task"],
        template=template
    )
    
    # Initialize the agent
    agent = initialize_agent(
        toolkit.get_tools(),
        llm,
        agent="zero-shot-react-description",
        verbose=True,
        handle_parsing_errors=True
    )
    
    # Example tasks
    tasks = [
        "Find all Python files in the current directory",
        "Search for any functions that contain 'test' in their name",
        "Read the contents of the README.md file",
        "Propose a change to add a new function to a Python file"
    ]
    
    # Run each task
    for task in tasks:
        print(f"\nExecuting task: {task}")
        try:
            result = agent.run(task)
            print(f"Result: {result}")
        except Exception as e:
            print(f"Error: {str(e)}")


if __name__ == "__main__":
    main() 