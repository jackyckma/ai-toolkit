# AI-Native Development Toolkit

## Project Overview

Create a command-line toolkit designed to enhance AI-led software development. This toolkit will enable AI systems (like Cursor AI) to build and maintain software more effectively by providing tools that align with AI's cognitive patterns while maintaining human-readable outputs.

The toolkit will be designed for direct use by AI assistants through shell commands, making it easy for systems like Cursor AI to integrate these tools into their development workflow. The primary goal is to help AIs build and maintain a knowledge graph of the project alongside traditional code files.

## Core Objectives

1. **Command-Line Interface**: Create a unified CLI with multiple subcommands
2. **Knowledge Representation**: Build a simple system for representing software as connected knowledge graphs
3. **Code Analysis**: Develop tools to extract semantic information from Python code files
4. **Visualization**: Generate human-readable visualizations of project structure
5. **Easy Deployment**: Create simple installation mechanisms for AI assistants to use

## MVP Components

### 1. Command-Line Interface

Create a unified `ai-toolkit` command with subcommands:

```bash
ai-toolkit init       # Initialize a new project
ai-toolkit analyze    # Analyze code and update knowledge graph
ai-toolkit query      # Query the knowledge graph
ai-toolkit visualize  # Generate visualizations
```

Each command should have clear help documentation and examples.

### 2. Knowledge Graph Engine

Implement a simple system for tracking software components and relationships:

- Basic component registry (modules, classes, functions)
- Simple relationship tracking (dependencies, calls)
- JSON-based storage in `.ai-toolkit/kb/` directory
- Query capabilities to find components and their relationships

### 3. Code Analysis Tool

Create a basic Python code analyzer:

- Parse Python files using AST
- Extract components (modules, classes, functions)
- Detect dependencies between components
- Update the knowledge graph with findings

### 4. Visualization Generator

Implement a tool to visualize the knowledge graph:

- Generate Mermaid diagrams of component relationships
- Create simple dependency graphs
- Produce hierarchical views of the project structure

### 5. Installation System

Develop an easy installation mechanism:

- Create an `install.sh` script for downloading and setting up the toolkit
- Generate a `.ai-toolkit/` directory structure in the target project
- Include version tracking for future updates

## Technical Requirements

- Implement in Python 3.9+
- Minimize external dependencies for the core functionality
- Create clear, documented command-line interfaces
- Store all data in the `.ai-toolkit/` directory
- Provide detailed help text for all commands

## Deliverables

1. **Command-Line Application**: The `ai-toolkit` command and its subcommands
2. **Knowledge Graph Implementation**: Core system for tracking components
3. **Code Analyzer**: Basic Python code analysis tool
4. **Visualization Generator**: Tool for creating Mermaid diagrams
5. **Installation Script**: Easy deployment mechanism
6. **Documentation**: Usage guide and examples
7. **Sample Integration**: Example of integration with Cursor AI Rules

## Installation & Usage

The toolkit will be installed into a `.ai-toolkit/` directory within a project:

```bash
# Installation
curl -sSL https://raw.githubusercontent.com/username/ai-toolkit/main/scripts/install.sh | bash

# Initialize a project
ai-toolkit init my_project

# Analyze existing code
ai-toolkit analyze --directory src/

# Generate a visualization
ai-toolkit visualize --format mermaid --output docs/system.md

# Query the knowledge graph
ai-toolkit query --component UserService --relationships
```

## Directory Structure

```
.ai-toolkit/              # Toolkit directory in user projects
├── bin/                  # Command-line tools
├── kb/                   # Knowledge graph storage
│   ├── components.json   # Component registry
│   └── relationships.json# Relationship mapping
├── config/               # Configuration files
└── cache/                # Analysis cache
```

## Integration with Cursor AI Rules

The toolkit is designed to be used by AI assistants like Cursor AI. A sample rule for Cursor AI might look like:

```
## AI-Native Development

If the `.ai-toolkit/` directory doesn't exist:
1. Download and install the toolkit:
   ```bash
   curl -sSL https://raw.githubusercontent.com/username/ai-toolkit/main/scripts/install.sh | bash
   ```

When developing new features:
1. First analyze the existing codebase:
   ```bash
   ai-toolkit analyze --directory src/
   ```
2. Generate a system diagram:
   ```bash
   ai-toolkit visualize --format mermaid
   ```
3. Query related components:
   ```bash
   ai-toolkit query --related-to UserService
   ```
```

## Future Extensions

After the MVP is successfully implemented and validated, consider these extensions:

1. **Synchronization Engine**: Tools to update code based on knowledge graph changes
2. **Additional Language Support**: Add analyzers for JavaScript, TypeScript, etc.
3. **Advanced Visualization**: Interactive diagrams and more complex views
4. **Pattern Recognition**: Identify and document common code patterns
5. **Multiple Graph Views**: Domain-specific views of the same codebase
