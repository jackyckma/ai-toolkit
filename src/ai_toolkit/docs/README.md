# AI-Native Development Toolkit Documentation

## Overview

The AI-Native Development Toolkit provides tools for AI-led software development, enabling AI systems to build and maintain a knowledge graph representation of code alongside traditional file-based representations.

## Installation

The toolkit is typically installed in the `.ai-toolkit/` directory of your project. There are two main installation methods:

### Installation Script
```bash
curl -sSL https://raw.githubusercontent.com/yourusername/ai-toolkit/main/scripts/install.sh | bash
```

### Manual Installation from GitHub
```bash
git clone https://github.com/yourusername/ai-toolkit.git .ai-toolkit-temp
cp -r .ai-toolkit-temp/src/ai_toolkit .ai-toolkit
rm -rf .ai-toolkit-temp
```

## Command Invocation

After installation, the toolkit commands should be invoked using the full path to the binary:

```bash
# Using the full path to the command
.ai-toolkit/bin/ai-toolkit [command] [options]
```

## Command Reference

### 1. Initialize a Project

```bash
.ai-toolkit/bin/ai-toolkit init [project_name]
```

**Options:**
- `project_name`: Optional name for the project (defaults to directory name)
- `--directory PATH`: Specify a different directory to initialize

### 2. Analyze Code

```bash
.ai-toolkit/bin/ai-toolkit analyze --directory PATH
```

**Options:**
- `--directory PATH`: Directory containing code to analyze (required)
- `--language LANG`: Programming language to analyze (currently only "python", default)

### 3. Query the Knowledge Graph

```bash
.ai-toolkit/bin/ai-toolkit query [--component NAME] [--relationships] [--format FORMAT]
```

**Options:**
- `--component NAME`: Name of the component to query
- `--relationships`: Also show relationships for the component
- `--format FORMAT`: Output format ("text" or "json", default: "text")

### 4. Generate Visualizations

```bash
.ai-toolkit/bin/ai-toolkit visualize [--component NAME] [--format FORMAT] [--output FILE]
```

**Options:**
- `--component NAME`: Focus visualization on this component
- `--format FORMAT`: Visualization format (currently only "mermaid", default)
- `--output FILE`: Output file path (outputs to console if not specified)

## Knowledge Graph Structure

The toolkit creates the following structure in your project:

```
.ai-toolkit/
├── kb/                  # Knowledge graph storage
│   ├── components.json  # All components
│   └── relationships.json # Relationships between components
├── config/              # Configuration files
└── cache/               # Analysis cache
```

## Development Workflow Integration

1. Initialize the project with `.ai-toolkit/bin/ai-toolkit init`
2. Create initial code structure
3. Analyze the codebase with `.ai-toolkit/bin/ai-toolkit analyze --directory src/`
4. When you need to understand relationships, use `.ai-toolkit/bin/ai-toolkit query`
5. When explaining architecture, use `.ai-toolkit/bin/ai-toolkit visualize`
6. After significant changes, re-analyze with `.ai-toolkit/bin/ai-toolkit analyze`

## Known Limitations

- Currently only supports Python code analysis
- Visualization is limited to Mermaid diagrams
- Large codebases may result in complex visualizations 