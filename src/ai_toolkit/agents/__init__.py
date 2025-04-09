"""
Agent framework for the AI-Native Development Toolkit.

This module implements a multi-agent system using Microsoft's Autogen
framework to enable specialized agents for different development tasks.
"""

from .base import Agent, AgentRegistry
from .coordinator import CoordinatorAgent
from .code_agent import CodeGenerationAgent
from .test_agent import TestingAgent

# Future agents will be imported here:
# from .architecture_agent import ArchitectureAgent
# from .documentation_agent import DocumentationAgent

__all__ = [
    'Agent',
    'AgentRegistry',
    'CoordinatorAgent',
    'CodeGenerationAgent',
    'TestingAgent',
] 