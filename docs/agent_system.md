# AI-Native Development Toolkit: Multi-Agent System

The AI-Native Development Toolkit includes a powerful multi-agent system that leverages specialized AI agents to perform different development tasks. This document explains how to use the agent system effectively.

## Overview

The multi-agent system is designed with a coordinator-based architecture:

- **Coordinator Agent**: Manages the overall task execution, breaks down complex tasks into subtasks, and delegates to specialized agents
- **Code Generation Agent**: Specializes in writing high-quality, maintainable code based on specifications
- **Testing Agent**: Focuses on creating comprehensive tests and identifying edge cases

## Usage

### Basic Usage (Coordinator Mode)

To use the multi-agent system with the coordinator:

```bash
ai-toolkit agent --task "Create a Python function that calculates the factorial of a number" --output result.json
```

In this mode, the coordinator will:
1. Break down the task into subtasks
2. Delegate each subtask to the appropriate specialized agent
3. Integrate the results into a cohesive solution

### Direct Mode

For simpler tasks or when you want to use a specific agent directly, you can use direct mode:

```bash
# Use the code generation agent directly
ai-toolkit agent --direct-mode code --task "Create a Python function that calculates the factorial of a number" --output result.json

# Use the testing agent directly
ai-toolkit agent --direct-mode test --task "Create tests for a function that calculates the factorial of a number" --output result.json
```

Direct mode bypasses the coordinator and sends your task directly to the specified agent.

## Command Options

The following options are available for the `agent` command:

- `--task`: The task description for the agent system (required)
- `--direct-mode`: Use a single agent directly (`code` or `test`)
- `--output`: Output file path for saving the results
- `--context-file`: JSON file with additional context for the task

## Output Format

The agent system generates a structured output in JSON format:

```json
{
  "status": "success",
  "message": "The full message from the agent",
  "code": [
    "def factorial(n):\n    if n == 0 or n == 1:\n        return 1\n    else:\n        return n * factorial(n-1)"
  ],
  "agent": "codegenerationagent",
  "agent_id": "37c1dfd1-2f51-4306-a6c2-a19798675a2f"
}
```

### Output Fields

- `status`: The status of the task execution (`success` or `error`)
- `message`: The full message from the agent
- `code`: Array of extracted code blocks (when available)
- `agent`: The name of the agent that generated the response
- `agent_id`: The unique ID of the agent

In case of errors, the output will include an `error` field with a description of the error.

## Environment Variables

The agent system behavior can be customized using the following environment variables:

- `COORDINATOR_MODEL`: The model to use for the coordinator agent (default: `gpt-4o`)
- `CODE_AGENT_MODEL`: The model to use for the code generation agent (default: `gpt-4-turbo`)
- `TESTING_AGENT_MODEL`: The model to use for the testing agent (default: `gpt-4-turbo`)
- `MAX_TOKENS`: Maximum number of tokens for agent responses (default: `4096`)
- `TEMPERATURE`: Temperature setting for generation (default: `0.1`)

These variables can be set in a `.env` file in your project root or directly in your environment.

## Workflow Integration

The agent system can be integrated into your development workflow:

1. Use the coordinator for complex tasks that require multiple specialized agents
2. Use direct mode for quick code generation or testing tasks
3. Save the results to files for further processing or integration
4. Use the generated code in your project after review

## Examples

### Generate a Sum of Factors Function

```bash
ai-toolkit agent --direct-mode code --task "Create a Python function that calculates the sum of all factors of a given number n (i.e., all numbers that divide n evenly). Make the function efficient and include test cases." --output factors.json
```

### Generate a Binary Search Implementation

```bash
ai-toolkit agent --direct-mode code --task "Create a Python function that implements a binary search algorithm for finding an element in a sorted list. Include proper documentation and test cases." --output binary_search.json
``` 