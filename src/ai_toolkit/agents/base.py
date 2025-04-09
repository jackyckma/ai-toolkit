"""
Base agent implementations for the AI-Native Development Toolkit.

This module defines the base Agent class and AgentRegistry that all
specialized agents will inherit from and register with.
"""

import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Type, Union, Set
import json
from uuid import uuid4

import autogen
from dotenv import load_dotenv

from ai_toolkit.kb.graph import KnowledgeGraph

# Load environment variables
load_dotenv()


class Agent:
    """Base class for all agents in the toolkit."""
    
    def __init__(
        self,
        name: str,
        knowledge_graph: KnowledgeGraph,
        model: Optional[str] = None,
        system_message: Optional[str] = None,
    ):
        """
        Initialize a base agent.
        
        Args:
            name: The name of the agent
            knowledge_graph: The knowledge graph to use for context
            model: The model to use for this agent
            system_message: The system message to use for this agent
        """
        self.name = name
        self.id = str(uuid4())
        self.knowledge_graph = knowledge_graph
        self.logger = logging.getLogger(f"ai_toolkit.agents.{name}")
        
        # Set up model configuration
        self.model = model or os.getenv(f"{name.upper()}_MODEL", "gpt-4-turbo")
        self.max_tokens = int(os.getenv("MAX_TOKENS", "4096"))
        self.temperature = float(os.getenv("TEMPERATURE", "0.1"))
        
        # Set up the default system message
        self.system_message = system_message or (
            f"You are the {name} agent in the AI-Native Development Toolkit. "
            f"Your responsibility is to assist with development tasks related to {name}."
        )
        
        # Initialize Autogen agent
        self._setup_autogen_agent()
        
        # Register the agent
        AgentRegistry.register(self)
    
    def _setup_autogen_agent(self):
        """Set up the Autogen agent for this agent."""
        # Configure Autogen
        config_list = [
            {
                "model": self.model,
                "api_key": os.getenv("OPENAI_API_KEY"),
            }
        ]
        
        # Set up cache directory
        cache_dir = os.getenv("CACHE_DIR", ".ai-toolkit/cache/agents")
        Path(cache_dir).mkdir(parents=True, exist_ok=True)
        
        # Create Autogen agent - updated for compatibility with newer autogen versions
        self.agent = autogen.AssistantAgent(
            name=self.name,
            llm_config={
                "config_list": config_list,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
            },
            system_message=self.system_message,
        )
    
    def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a task using this agent.
        
        Args:
            task: The task to execute
            context: Additional context for the task
            
        Returns:
            The result of the task execution
        """
        self.logger.info(f"Executing task: {task}")
        
        # Create a custom termination function to prevent loops
        def is_termination_msg(message):
            """Check if the conversation should terminate."""
            if message.get("content") is None or message.get("content").strip() == "":
                # Don't terminate on empty messages
                return False
                
            if message.get("role") == "user" and (
                "TERMINATE" in message.get("content", "") or 
                "terminate" in message.get("content", "").lower()
            ):
                return True
                
            return False
        
        # Create a user proxy for this interaction with custom configuration
        user_proxy = autogen.UserProxyAgent(
            name="user_proxy",
            human_input_mode="NEVER",
            code_execution_config={"work_dir": "ai_toolkit_workspace", "use_docker": False},
            is_termination_msg=is_termination_msg,
            max_consecutive_auto_reply=2,  # Limit consecutive auto-replies
        )
        
        # Register a custom reply function to prevent empty message loops
        def custom_auto_reply(self, messages=None, sender=None, config=None):
            """Custom reply function that prevents empty message loops."""
            if messages and len(messages) > 0:
                last_message = messages[-1]
                if last_message.get("content", "").strip() == "":
                    # Don't respond to empty messages
                    return False, "TERMINATE"
                    
                # Check for repeated identical messages
                if len(messages) >= 3:
                    if (messages[-1].get("content") == messages[-2].get("content") and
                        messages[-2].get("content") == messages[-3].get("content")):
                        # Detected a loop of identical messages, terminate
                        return False, "TERMINATE"
            
            # Default behavior - don't auto reply
            return False, None
            
        # Override the auto_reply method
        user_proxy.auto_reply = lambda messages, sender, config: custom_auto_reply(user_proxy, messages, sender, config)
        
        # Prepare the message with context from the knowledge graph
        message = self._prepare_message_with_context(task, context)
        
        # DEBUG logging
        self.logger.info("Initiated agent execution with the following configuration:")
        self.logger.info(f"Agent model: {self.model}")
        self.logger.info(f"Task: {task[:50]}...")  # Log first 50 chars
        
        # IMPORTANT: Redirect stdout to capture terminal output
        import io
        import sys
        original_stdout = sys.stdout
        captured_output = io.StringIO()
        
        # Very basic initialization of chat tracking
        captured_messages = []
        assistant_messages = []
        
        # Initiate the conversation with a timeout and capture the chat history
        try:
            # Redirect stdout to capture output
            sys.stdout = captured_output
            
            # Start the conversation
            self.logger.info("Starting conversation with agent...")
            user_proxy.initiate_chat(
                self.agent, 
                message=message,
                max_turns=10  # Maximum number of turns to prevent infinite loops
            )
            
            # Restore stdout
            sys.stdout = original_stdout
            
            # Get the captured output
            terminal_output = captured_output.getvalue()
            self.logger.info(f"Captured {len(terminal_output)} bytes of terminal output")
            
            # Create a synthetic message for the output
            if terminal_output:
                assistant_messages.append({
                    "role": "assistant",
                    "content": terminal_output
                })
            
            # After chat completes, get the conversation history if available
            if hasattr(self.agent, 'chat_messages') and user_proxy.name in self.agent.chat_messages:
                chat_history = self.agent.chat_messages[user_proxy.name]
                
                # Debug: Log the complete chat history
                self.logger.info(f"Chat completed. Found {len(chat_history)} total messages.")
                
                # Filter only for assistant messages with content
                assistant_messages_from_chat = [
                    msg for msg in chat_history 
                    if msg.get("role") == "assistant" and msg.get("content")
                ]
                
                # Merge with terminal output if needed
                if assistant_messages_from_chat:
                    assistant_messages.extend(assistant_messages_from_chat)
                
                # Debug: Print the captured messages
                self.logger.info(f"Captured {len(assistant_messages)} total assistant messages")
                        
        except Exception as e:
            # Restore stdout
            sys.stdout = original_stdout
            
            self.logger.error(f"Error during chat: {e}")
            self.logger.exception("Exception details:")
            
            # Get the captured output
            terminal_output = captured_output.getvalue()
            if terminal_output:
                assistant_messages.append({
                    "role": "assistant",
                    "content": terminal_output
                })
                
            # Try to recover if we have any chat history
            if hasattr(self.agent, 'chat_messages') and user_proxy.name in self.agent.chat_messages:
                chat_history = self.agent.chat_messages[user_proxy.name]
                
                # Debug: Log the chat history after error
                self.logger.info(f"After error. Found {len(chat_history)} total messages in chat history.")
                
                # Filter only for assistant messages with content
                assistant_messages_from_chat = [
                    msg for msg in chat_history 
                    if msg.get("role") == "assistant" and msg.get("content")
                ]
                
                # Merge with terminal output
                for msg in assistant_messages_from_chat:
                    if msg not in assistant_messages:
                        assistant_messages.append(msg)
                
                self.logger.info(f"Recovered {len(assistant_messages)} total messages after error")
        
        # Process the results if we have any messages
        if assistant_messages:
            self.logger.info("Processing captured messages...")
            result = self._process_result(assistant_messages)
            self.logger.info(f"Processing complete. Result status: {result.get('status')}")
            return result
        
        # If we couldn't get any messages, return an error
        self.logger.error("No messages captured from agent conversation.")
        return {
            "status": "error",
            "error": "No response from agent",
            "agent": self.name,
            "agent_id": self.id,
        }
    
    def _prepare_message_with_context(self, task: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Prepare a message with context from the knowledge graph.
        
        Args:
            task: The task to execute
            context: Additional context for the task
            
        Returns:
            The prepared message with context
        """
        message_parts = [f"# Task\n{task}\n"]
        
        # Add context if provided
        if context:
            message_parts.append("# Additional Context\n")
            for key, value in context.items():
                if isinstance(value, (dict, list)):
                    message_parts.append(f"## {key}\n```json\n{json.dumps(value, indent=2)}\n```\n")
                else:
                    message_parts.append(f"## {key}\n{value}\n")
        
        # Add knowledge graph context
        # TODO: Add relevant information from the knowledge graph based on the task
        
        return "\n".join(message_parts)
    
    def _process_result(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process the result from the Autogen agent.
        
        Args:
            messages: The messages from the Autogen agent
            
        Returns:
            The processed result
        """
        # Extract the last message content
        if not messages:
            return {"status": "error", "error": "No response from agent"}
        
        # Get the last non-empty message from the agent
        last_message = None
        for message in reversed(messages):
            if (message.get("role") == "assistant" and 
                message.get("content") and 
                message.get("content").strip()):
                last_message = message["content"]
                break
        
        if not last_message:
            return {"status": "error", "error": "No substantive response from agent"}
        
        # Parse the message for structured data
        # TODO: Implement more sophisticated parsing based on agent type
        
        return {
            "status": "success",
            "content": last_message,
            "agent": self.name,
            "agent_id": self.id,
        }


class AgentRegistry:
    """Registry for all agents in the toolkit."""
    
    _agents: Dict[str, Agent] = {}
    
    @classmethod
    def register(cls, agent: Agent) -> None:
        """
        Register an agent with the registry.
        
        Args:
            agent: The agent to register
        """
        cls._agents[agent.id] = agent
    
    @classmethod
    def get_agent(cls, agent_id: str) -> Optional[Agent]:
        """
        Get an agent by ID.
        
        Args:
            agent_id: The ID of the agent to get
            
        Returns:
            The agent with the given ID, or None if not found
        """
        return cls._agents.get(agent_id)
    
    @classmethod
    def get_agent_by_name(cls, name: str) -> Optional[Agent]:
        """
        Get an agent by name.
        
        Args:
            name: The name of the agent to get
            
        Returns:
            The first agent with the given name, or None if not found
        """
        for agent in cls._agents.values():
            if agent.name.lower() == name.lower():
                return agent
        return None
    
    @classmethod
    def list_agents(cls) -> List[Agent]:
        """
        List all registered agents.
        
        Returns:
            A list of all registered agents
        """
        return list(cls._agents.values()) 