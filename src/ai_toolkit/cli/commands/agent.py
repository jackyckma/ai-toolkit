"""
Agent command for the AI-Native Development Toolkit.

This module implements the 'agent' command, which provides access
to the multi-agent system for coordinated AI assistance.
"""

import sys
import os
import logging
from argparse import Namespace
from pathlib import Path
import json

# Import using absolute imports to avoid path issues
try:
    from ai_toolkit.kb.graph import KnowledgeGraph
    from ai_toolkit.agents import CoordinatorAgent, CodeGenerationAgent, TestingAgent
except ImportError:
    # Fallback for development
    from src.ai_toolkit.kb.graph import KnowledgeGraph
    from src.ai_toolkit.agents import CoordinatorAgent, CodeGenerationAgent, TestingAgent


class AgentCommand:
    """Command handler for the agent CLI command."""
    
    def __init__(self):
        """Initialize the command handler."""
        self.cli = None
    
    def _handle_direct_mode(self, args):
        """Handle direct mode operation with a single agent."""
        print("Executing task in direct mode using the", 
              "code agent" if args.direct_mode == "code" else "testing agent")
        print("Please wait, this may take a few minutes...")
        
        if args.direct_mode == "code":
            # Execute task with code generation agent
            agent = self.cli.agent_system.code_generation_agent
            result = agent.execute(args.task)
        else:
            # Execute task with testing agent
            agent = self.cli.agent_system.testing_agent
            result = agent.execute(args.task)
            
        # Save results to file if provided
        if args.output:
            try:
                with open(args.output, 'w') as f:
                    json.dump(result, f, indent=2)
            except Exception as e:
                print(f"Error saving results to {args.output}: {e}")
        
        # Create summary for console output
        if result["status"] == "success" and "code" in result and result["code"]:
            code_blocks = result["code"]
            print("\nTask completed. Summary:")
            print(f"Status: {result['status']}")
            print("\n--- Solution ---")
            for i, code_block in enumerate(code_blocks):
                if i > 0:
                    print("\n--- Alternative Solution ---")
                print(code_block)
        else:
            print("\nTask completed. Summary:")
            print(f"Status: {result['status']}")
            
            if result["status"] == "error":
                print(f"Error: {result.get('error', 'Unknown error')}")
            
            print("\n--- Solution ---")
            print("No content available")
        
        return result
    
    def __call__(self, args, cli):
        self.cli = cli
        
        try:
            print("Agent system initialized with the following agents:")
            print(f"- Coordinator ({cli.agent_system.coordinator_agent.model})")
            print(f"- Code Generation ({cli.agent_system.code_generation_agent.model})")
            print(f"- Testing ({cli.agent_system.testing_agent.model})")
            print()
            
            # Check if we're in direct mode
            if hasattr(args, 'direct_mode') and args.direct_mode:
                return self._handle_direct_mode(args)
            
            # If not in direct mode, follow the normal coordinator flow
            result = cli.agent_system.execute_task(args.task)
            
            # Create a simpler output format for the console
            print("\nTask completed. Result:")
            if result["status"] == "success":
                print("\nSolution:")
                if "code" in result and result["code"]:
                    for code_block in result["code"]:
                        print(f"\n```python\n{code_block}\n```")
                else:
                    print("No code generated in the solution.")
            else:
                print(f"Status: {result['status']}")
                if "error" in result:
                    print(f"Error: {result['error']}")
            
            # Save result to file if output is specified
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(result, f, indent=2)
                print(f"\nFull result saved to {args.output}")
                
            return 0
            
        except Exception as e:
            print(f"Error executing task: {e}")
            logging.exception("Error in agent command")
            return 1


# For backward compatibility with the legacy main() entry point
def main(args: Namespace) -> int:
    """
    Execute the agent command (legacy entry point).
    
    Args:
        args: Command arguments
        
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    # Check if .ai-toolkit directory exists
    toolkit_dir = Path.cwd() / ".ai-toolkit"
    if not toolkit_dir.exists():
        print("Error: AI-Native Development Toolkit not initialized in this directory")
        print("Run 'ai-toolkit init' first")
        return 1
    
    # Set up logging
    log_level = os.getenv("LOG_LEVEL", "INFO")
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        numeric_level = logging.INFO
    
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(toolkit_dir / "logs" / "agents.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Create logs directory if it doesn't exist
    logs_dir = toolkit_dir / "logs"
    logs_dir.mkdir(exist_ok=True)
    
    # Initialize knowledge graph
    graph = KnowledgeGraph(toolkit_dir)
    
    # Initialize the agent system
    try:
        # Create the agent instances
        coordinator = CoordinatorAgent(graph)
        code_agent = CodeGenerationAgent(graph)
        test_agent = TestingAgent(graph)
        
        print(f"Agent system initialized with the following agents:")
        print(f"- Coordinator ({coordinator.model})")
        print(f"- Code Generation ({code_agent.model})")
        print(f"- Testing ({test_agent.model})")
        
        if args.task:
            # Get context from file if provided
            context = None
            if args.context_file:
                try:
                    with open(args.context_file, "r") as f:
                        context = json.load(f)
                except Exception as e:
                    print(f"Error loading context file: {e}")
                    return 1
            
            # Check if we're using direct mode (single agent)
            if args.direct_mode:
                print(f"\nExecuting task in direct mode using the {args.direct_mode} agent")
                print("Please wait, this may take a few minutes...")
                
                # Select the appropriate agent
                if args.direct_mode == "code":
                    selected_agent = code_agent
                elif args.direct_mode == "test":
                    selected_agent = test_agent
                else:
                    print(f"Error: Unknown agent type '{args.direct_mode}'")
                    return 1
                
                # Execute the task directly with the selected agent
                result = selected_agent.execute(args.task, context)
            else:
                # Execute the task with the coordinator
                print(f"\nExecuting task: {args.task}")
                print("Please wait, this may take a few minutes...")
                
                # Execute the task with the coordinator
                result = coordinator.execute_task(args.task, context)
            
            # Save the result to a file if requested
            if args.output:
                output_file = Path(args.output)
                output_file.parent.mkdir(parents=True, exist_ok=True)
                
                with open(output_file, "w") as f:
                    json.dump(result, f, indent=2)
                
                print(f"\nTask completed. Results saved to {args.output}")
            else:
                # Display a summary of the result
                print("\nTask completed. Summary:")
                print(f"Status: {result.get('status', 'unknown')}")
                
                # Show the integrated solution
                print("\n--- Solution ---")
                print(result.get("content", "No content available"))
            
            return 0
        else:
            print("\nNo task specified. Use --task to provide a task for the agent system.")
            return 1
        
    except Exception as e:
        print(f"Error initializing agent system: {e}")
        logging.exception("Error in agent command")
        return 1 