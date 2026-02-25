# Agentic Frameworks

This directory explores various Agentic Frameworks and their implementations. Agentic frameworks provide the scaffolding and tools necessary to build AI agents that can reason, plan, and execute tasks autonomously. These frameworks abstract away the complexities of managing LLM interactions, state, and tool usage, allowing developers to focus on defining agent behaviors and workflows.

## Prerequisites First!

Before diving into specific agent frameworks, it's highly recommended to understand the fundamental concepts in the `Prerequisites` directory:

### 1. Asynchronous Programming
Located in `Prerequisites/Async/`:
- `1. basics.ipynb`: Foundation of async programming in Python
- `2. sync_vs_async.ipynb`: Comparison between synchronous and asynchronous approaches

Understanding async programming is crucial as most modern AI agent frameworks utilize asynchronous operations for efficient communication and task handling.

### 2. Data Validation with Pydantic
Located in `Prerequisites/Pydantic/`:
- `main.ipynb`: Introduction to Pydantic for data validation and settings management

Pydantic is extensively used in agent frameworks for configuration management and data validation.

## Frameworks Overview

### Current Implementations

1. **AutoGen** (Microsoft)
   - Location: `/Autogen`
   - A framework for building multi-agent systems with LLMs
   - Includes examples of basic usage, customization, and advanced features

2. **Langchain** 
   - Location: `/Langchain`
   - A framework for developing applications powered by large language models (LLMs)
   - Includes examples covering core concepts like model integration, message handling, tools, and structured output

3. **LangGraph**
   - Location: `/LangGraph`
   - A library for building stateful, multi-actor applications with LLMs
   - Focuses on creating cyclical graphs for agent workflows, enabling complex patterns like loops and branching

### Coming Soon
This directory will be expanded to include other popular agent frameworks such as:
- CrewAI
- SmolAgents
- Langflow
- And more...

## Getting Started

1. Start with the prerequisites:
   - Complete the async programming tutorials
   - Work through the Pydantic examples
   - These foundations will make it easier to understand and work with any agent framework

2. Choose a framework:
   - Each framework will have its own directory with examples and documentation
   - Follow the specific setup instructions in each framework's directory


## Note

Each agent framework has its own strengths and ideal use cases. As you explore different frameworks, you'll discover which ones are best suited for your specific needs. The prerequisites covered in this directory will help you better understand and work with any of these frameworks.

## Additional Resources

- Each framework directory contains specific `requirements.txt` files for easy setup
- Notebooks are designed to be run sequentially to build understanding progressively
- Check individual notebook files for detailed explanations and code examples

Feel free to start with any framework after completing the prerequisites.
