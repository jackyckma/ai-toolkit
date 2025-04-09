"""
Coordinator agent for the AI-Native Development Toolkit.

This agent coordinates the activities of specialist agents and manages
the execution of complex tasks by delegating subtasks to appropriate agents.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
import json
import os
import re

import autogen
from dotenv import load_dotenv

from ai_toolkit.kb.graph import KnowledgeGraph
from .base import Agent, AgentRegistry

# Load environment variables
load_dotenv()


class CoordinatorAgent(Agent):
    """
    Coordinator agent that manages other agents.
    
    The coordinator is responsible for:
    1. Breaking down complex tasks into subtasks
    2. Delegating subtasks to appropriate agents
    3. Integrating results from multiple agents
    4. Resolving conflicts between agent outputs
    5. Maintaining the overall project context
    """
    
    def __init__(self, knowledge_graph: KnowledgeGraph):
        """
        Initialize the coordinator agent.
        
        Args:
            knowledge_graph: The knowledge graph to use for context
        """
        # Define the system message for the coordinator
        coordinator_system_message = """
        You are the Coordinator agent in the AI-Native Development Toolkit.
        
        Your primary responsibilities are:
        
        1. TASK DECOMPOSITION: Break down complex development tasks into smaller, manageable subtasks
        2. AGENT DELEGATION: Determine which specialist agent should handle each subtask
        3. CONTEXT MANAGEMENT: Maintain and provide relevant context to specialist agents
        4. RESULT INTEGRATION: Combine outputs from multiple agents into a cohesive solution
        5. CONFLICT RESOLUTION: Resolve any conflicts or inconsistencies between agent outputs
        
        You have access to the following specialist agents:
        - CodeGenerationAgent: Writes high-quality, maintainable code
        - TestingAgent: Creates comprehensive tests and identifies edge cases
        - (Future) ArchitectureAgent: Designs system structure and evaluates patterns
        - (Future) DocumentationAgent: Creates clear documentation
        
        When you receive a task:
        1. Analyze it to understand the full requirements
        2. Break it down into subtasks
        3. For each subtask, determine which specialist agent should handle it
        4. Collect and integrate the results
        5. Verify that the integrated solution meets the original requirements
        
        Always structure your responses in a way that clearly separates:
        - Your analysis of the task
        - Your decomposition plan
        - Your delegation decisions
        - Your integration strategy
        
        Your goal is to produce higher quality results than would be possible with a single agent approach.
        """
        
        # Call the parent constructor with the coordinator-specific parameters
        super().__init__(
            name="coordinator",
            knowledge_graph=knowledge_graph,
            model=os.getenv("COORDINATOR_MODEL", "gpt-4o"),
            system_message=coordinator_system_message,
        )
        
        # Initialize the task history
        self.task_history: List[Dict[str, Any]] = []
    
    def execute_task(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a complex task by coordinating multiple specialist agents.
        
        Args:
            task: The task to execute
            context: Additional context for the task
            
        Returns:
            The result of the task execution
        """
        self.logger.info(f"Executing complex task: {task}")
        
        # First, have the coordinator analyze and decompose the task
        decomposition_result = self.execute(
            task=f"Analyze and decompose the following task into subtasks for specialist agents:\n\n{task}",
            context=context
        )
        
        # Handle potential errors in decomposition
        if decomposition_result.get("status") == "error" or "content" not in decomposition_result:
            self.logger.error(f"Error in task decomposition: {decomposition_result.get('error', 'Unknown error')}")
            return {
                "status": "error",
                "error": f"Failed to decompose task: {decomposition_result.get('error', 'Unknown error')}",
                "task": task,
                "agent": self.name,
                "agent_id": self.id,
            }
        
        # Parse the decomposition result to get subtasks and assignments
        try:
            subtasks = self._parse_decomposition(decomposition_result["content"])
        except Exception as e:
            self.logger.error(f"Error parsing decomposition: {e}")
            # Return a more graceful error with the raw content
            return {
                "status": "error",
                "error": f"Failed to parse task decomposition: {e}",
                "raw_decomposition": decomposition_result.get("content", "No content available"),
                "task": task,
                "agent": self.name,
                "agent_id": self.id,
            }
        
        # Check if we have any subtasks
        if not subtasks:
            self.logger.warning("No subtasks were identified from decomposition")
            # Try to execute the task directly with a code agent
            code_agent = AgentRegistry.get_agent_by_name("codegenerationagent")
            if code_agent:
                self.logger.info("Delegating task directly to code generation agent")
                return code_agent.execute(task, context)
            else:
                return {
                    "status": "error",
                    "error": "Failed to identify subtasks and no code agent available",
                    "task": task,
                    "agent": self.name,
                    "agent_id": self.id,
                }
        
        # Execute each subtask with the appropriate agent
        subtask_results = []
        for subtask in subtasks:
            agent_name = subtask["agent"]
            subtask_task = subtask["task"]
            
            # Get the agent from the registry
            agent = AgentRegistry.get_agent_by_name(agent_name)
            if not agent:
                self.logger.error(f"Agent {agent_name} not found for subtask: {subtask_task}")
                subtask_results.append({
                    "status": "error",
                    "error": f"Agent {agent_name} not found",
                    "subtask": subtask,
                })
                continue
            
            # Execute the subtask with the agent
            subtask_result = agent.execute(subtask_task, context)
            subtask_result["subtask"] = subtask
            subtask_results.append(subtask_result)
        
        # Have the coordinator integrate the results
        integration_context = {
            "original_task": task,
            "subtasks": subtasks,
            "subtask_results": subtask_results,
        }
        
        if context:
            integration_context.update(context)
        
        integration_result = self.execute(
            task="Integrate the results of the subtasks into a cohesive solution for the original task.",
            context=integration_context
        )
        
        # Store the task execution in the history
        task_record = {
            "task": task,
            "decomposition": subtasks,
            "subtask_results": subtask_results,
            "integration": integration_result,
        }
        self.task_history.append(task_record)
        
        return integration_result
    
    def _parse_decomposition(self, decomposition_text: str) -> List[Dict[str, Any]]:
        """
        Parse the decomposition text to extract subtasks and agent assignments.
        
        Args:
            decomposition_text: The text output from the decomposition step
            
        Returns:
            A list of subtasks with assigned agents
        """
        if not decomposition_text or not isinstance(decomposition_text, str):
            self.logger.error(f"Invalid decomposition text: {decomposition_text}")
            return []
            
        # This is a simple parser that looks for markdown-style subtask definitions
        # A more robust parser would use regex or a more structured output format
        
        subtasks = []
        current_subtask = None
        
        for line in decomposition_text.strip().split("\n"):
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
                
            # Check for subtask headers (## Subtask 1: Description)
            if line.startswith("## Subtask") or line.startswith("### Subtask"):
                if current_subtask:
                    subtasks.append(current_subtask)
                
                current_subtask = {
                    "id": len(subtasks) + 1,
                    "title": line.split(":", 1)[1].strip() if ":" in line else line,
                    "task": "",
                    "agent": "",
                    "dependencies": [],
                }
            
            # Check for task defined without subtask header (Subtask 1:)
            elif line.startswith("Subtask ") and ":" in line:
                if current_subtask:
                    subtasks.append(current_subtask)
                
                current_subtask = {
                    "id": len(subtasks) + 1,
                    "title": line.split(":", 1)[1].strip(),
                    "task": "",
                    "agent": "",
                    "dependencies": [],
                }
            
            # Check for agent assignment
            elif line.startswith("Agent:") and current_subtask:
                agent_name = line.split(":", 1)[1].strip().lower()
                
                # Normalize agent names
                if "code" in agent_name:
                    current_subtask["agent"] = "codegenerationagent"
                elif "test" in agent_name:
                    current_subtask["agent"] = "testingagent"
                elif "architect" in agent_name:
                    current_subtask["agent"] = "architectureagent"
                elif "doc" in agent_name:
                    current_subtask["agent"] = "documentationagent"
                else:
                    current_subtask["agent"] = agent_name
            
            # Check for task description
            elif line.startswith("Task:") and current_subtask:
                current_subtask["task"] = line.split(":", 1)[1].strip()
            
            # Look for sections containing task descriptions
            elif current_subtask and (line.startswith("**Task**:") or line == "**Task**:" or line == "Task:"):
                # The next line might contain the task
                current_subtask["task"] = ""  # Initialize to handle multi-line tasks
                continue
                
            # Add to task description if we have a current subtask
            elif current_subtask and current_subtask.get("task") is not None and line:
                # If we have a task and this isn't another header or label
                if not any(line.startswith(prefix) for prefix in ["Agent:", "Dependencies:", "##", "###", "**"]):
                    current_subtask["task"] += f"\n{line}" if current_subtask["task"] else line
            
            # Check for dependencies
            elif line.startswith("Dependencies:") and current_subtask:
                deps = line.split(":", 1)[1].strip()
                current_subtask["dependencies"] = [int(d.strip()) for d in deps.split(",") if d.strip().isdigit()]
        
        # Add the last subtask if it exists
        if current_subtask:
            subtasks.append(current_subtask)
        
        # If we couldn't find subtasks based on headers, try looking for numbered lists
        if not subtasks:
            self.logger.warning("No subtasks found using headers, trying numbered list format")
            subtasks = self._parse_numbered_list_format(decomposition_text)
            
        # If we still have no subtasks, create a default one for the code agent
        if not subtasks:
            self.logger.warning("Creating default subtask for code generation agent")
            return [{
                "id": 1,
                "title": "Implementation",
                "task": decomposition_text,  # Use the entire text as the task
                "agent": "codegenerationagent",
                "dependencies": [],
            }]
        
        # Assign default agents if not specified
        for subtask in subtasks:
            if not subtask.get("agent"):
                if "test" in subtask.get("title", "").lower() or "test" in subtask.get("task", "").lower():
                    subtask["agent"] = "testingagent"
                else:
                    subtask["agent"] = "codegenerationagent"
                    
            # Ensure task is not empty
            if not subtask.get("task"):
                subtask["task"] = subtask.get("title", "Perform the task as described")
                
        return subtasks
        
    def _parse_numbered_list_format(self, text: str) -> List[Dict[str, Any]]:
        """Parse subtasks from a numbered list format."""
        subtasks = []
        lines = text.strip().split('\n')
        current_task = None
        current_id = None
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Look for numbered list items (1., 2., etc.)
            number_match = re.match(r'^(\d+)\.\s+(.+)$', line)
            if number_match:
                # Save the previous task if it exists
                if current_task is not None and current_id is not None:
                    subtasks.append({
                        "id": current_id,
                        "title": current_task,
                        "task": current_task,
                        "agent": "",
                        "dependencies": [],
                    })
                
                # Start a new task
                current_id = int(number_match.group(1))
                current_task = number_match.group(2)
                
                # Look ahead to see if there are agent assignments
                if i + 1 < len(lines) and "agent" in lines[i + 1].lower():
                    agent_line = lines[i + 1].lower()
                    if "code" in agent_line:
                        agent = "codegenerationagent"
                    elif "test" in agent_line:
                        agent = "testingagent"
                    else:
                        agent = "codegenerationagent"  # Default
                        
                    # Add the subtask with the agent
                    subtasks.append({
                        "id": current_id,
                        "title": current_task,
                        "task": current_task,
                        "agent": agent,
                        "dependencies": [],
                    })
                    
                    # Reset current_task to avoid adding it again
                    current_task = None
                    current_id = None
                
        # Add the last task if it exists
        if current_task is not None and current_id is not None:
            subtasks.append({
                "id": current_id,
                "title": current_task,
                "task": current_task,
                "agent": "",
                "dependencies": [],
            })
            
        return subtasks 