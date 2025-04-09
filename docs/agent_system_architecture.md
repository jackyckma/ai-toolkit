# AI-Native Development Toolkit: Agent System Architecture

This document describes the technical architecture and implementation details of the multi-agent system in the AI-Native Development Toolkit.

## System Overview

The multi-agent system follows a coordinator-based architecture where specialized agents handle different aspects of development tasks:

```
┌─────────────────┐      ┌───────────────────────┐
│                 │      │                       │
│     User CLI    │─────▶│    Coordinator Agent  │
│                 │      │                       │
└─────────────────┘      └───────────┬───────────┘
                                     │
                                     ▼
                     ┌───────────────┴───────────────┐
                     │                               │
          ┌──────────▼──────────┐      ┌─────────────▼────────────┐
          │                     │      │                          │
          │ Code Generation     │      │ Testing                  │
          │ Agent               │      │ Agent                    │
          │                     │      │                          │
          └─────────────────────┘      └──────────────────────────┘
```

## Key Components

### 1. Base Agent Implementation (`src/ai_toolkit/agents/base.py`)

The `Agent` base class provides core functionality for all specialized agents:

- **Initialization**: Sets up agent parameters, knowledge graph connection, and logging
- **Message Handling**: Captures and processes messages from agent conversations
- **Result Processing**: Extracts structured information from agent outputs
- **Context Management**: Prepares task context from knowledge graph data

The `AgentRegistry` provides a central registry of all agent instances for easy access.

### 2. Coordinator Agent (`src/ai_toolkit/agents/coordinator.py`)

The `CoordinatorAgent` manages complex tasks by:

1. Breaking down tasks into subtasks using `_parse_decomposition()`
2. Delegating subtasks to appropriate specialist agents
3. Integrating results from multiple agents into a cohesive solution
4. Handling errors and providing fallbacks when decomposition fails

### 3. Code Generation Agent (`src/ai_toolkit/agents/code_agent.py`)

The `CodeGenerationAgent` specializes in writing high-quality code:

- Processes prompts with an emphasis on code structure and patterns
- Extracts code blocks from responses using regex pattern matching
- Returns structured results with separated code blocks and explanations

### 4. Testing Agent (similar structure to Code Generation Agent)

The `TestingAgent` focuses on creating comprehensive tests.

## Message Flow

The message flow in the system follows this pattern:

1. **Task Reception**: The CLI receives a task from the user
2. **Agent Selection**: 
   - In coordinator mode: Task is sent to the coordinator for decomposition
   - In direct mode: Task is sent directly to a specialized agent
3. **Agent Execution**:
   - Agent retrieves relevant context from the knowledge graph
   - Agent processes the task using the appropriate LLM
   - Messages are captured using stdout redirection and chat history access
4. **Result Processing**:
   - Agent extracts structured information from messages
   - Code blocks are identified and separated from explanatory text
5. **Response Delivery**:
   - Structured JSON output is returned to the CLI
   - Results are displayed to the user and/or saved to a file

## Direct Mode Implementation

The direct mode allows bypassing the coordinator and using a specialized agent directly:

```
┌─────────────────┐      ┌───────────────────────┐
│                 │      │                       │
│     User CLI    │─────▶│    Specialized Agent  │
│                 │      │                       │
└─────────────────┘      └───────────────────────┘
```

This mode is implemented in the CLI using the `--direct-mode` parameter and is handled by the `_handle_direct_mode()` method in the `AgentCommand` class.

## Result Format

The agent system returns results in a consistent JSON format:

```json
{
  "status": "success",
  "message": "The full message content",
  "code": ["extracted_code_block_1", "extracted_code_block_2"],
  "agent": "agent_name",
  "agent_id": "unique_agent_id"
}
```

In case of errors:

```json
{
  "status": "error",
  "error": "Error description",
  "agent": "agent_name",
  "agent_id": "unique_agent_id"
}
```

## Advanced Message Handling

To ensure robust message capture from the LLM, the system implements multiple fallback strategies:

1. **Terminal Output Capture**: Redirects stdout during agent execution to capture all outputs
2. **Chat History Access**: Extracts messages from the agent's internal chat history
3. **Reversed Message Processing**: Processes messages in reverse order to prioritize the latest outputs
4. **Multiple Fallbacks**: Falls back to different message sources if primary methods fail

This approach ensures that the agent responses are reliably captured and processed, even in cases where the standard chat history might not be available.

## Environment and Configuration

The agent system uses environment variables for configuration, loaded via the `dotenv` package:

- Model selection for each agent type
- Temperature and max token settings
- API credentials
- Optional debugging flags

## Integration with Knowledge Graph

The agent system is integrated with the toolkit's knowledge graph:

- Agents have access to the knowledge graph for context
- Relevant components and relationships can be included in prompts
- Future enhancements will use the graph to generate more informed responses

## Extensibility

The system is designed for extensibility:

1. **New Agent Types**: Add new specialized agents by inheriting from the `Agent` base class
2. **Message Processing**: Customize how messages are processed for different agent types
3. **Context Enhancement**: Extend context preparation to include more knowledge graph data
4. **Result Format**: Add new fields to the result format for specialized agent outputs

## Future Enhancements

Planned enhancements to the agent system include:

- **Architecture Agent**: Specialized agent for system design decisions
- **Documentation Agent**: Agent focused on generating comprehensive documentation
- **Agent Collaboration**: Enhanced collaboration between agents for complex tasks
- **Learning from History**: Agents that learn from past executions and improve over time
- **Knowledge Graph Integration**: Deeper integration with the code analysis features 