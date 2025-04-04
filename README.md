# AI-Native Development Toolkit

A command-line toolkit designed to enhance AI-led software development. This toolkit enables AI systems to build and maintain software more effectively by providing tools that align with AI's cognitive patterns while maintaining human-readable outputs.

## Key Features

- **Knowledge Graph Representation**: Represents code as a connected graph of components and relationships
- **Code Analysis**: Extracts structure and relationships from Python code files
- **Visualization Tools**: Generates human-readable diagrams from the knowledge graph
- **Query Interface**: Provides powerful ways to explore code relationships

## Installation

```bash
# Install directly using the installation script
curl -sSL https://raw.githubusercontent.com/jackyckma/ai-toolkit/main/scripts/install.sh | bash
```

Or for development:

```bash
# Clone the repository
git clone https://github.com/jackyckma/ai-toolkit.git
cd ai-toolkit

# Install in development mode
pip install -e .
```

## Command Reference

The toolkit provides four primary commands:

### 1. `init` - Initialize a Project

Creates a `.ai-toolkit` directory in your project with the necessary knowledge graph structure.

```bash
ai-toolkit init [project_name]
```

**What it does:**
- Creates `.ai-toolkit/` directory with kb, config, and cache subdirectories
- Initializes empty knowledge graph files (components.json, relationships.json)
- Sets up project metadata in config.json

**Options:**
- `project_name`: Optional name for the project (defaults to directory name)
- `--directory PATH`: Specify a different directory to initialize

**Example:**
```bash
ai-toolkit init my-awesome-project
```

### 2. `analyze` - Analyze Code

Analyzes your code and updates the knowledge graph with components and relationships.

```bash
ai-toolkit analyze --directory PATH
```

**What it does:**
- Scans Python files in the specified directory (recursively)
- Extracts components (modules, classes, functions, methods)
- Identifies relationships (imports, contains, inherits)
- Updates the knowledge graph with this information

**Options:**
- `--directory PATH`: Directory containing code to analyze (required)
- `--language LANG`: Programming language to analyze (currently only "python", default)

**Example:**
```bash
ai-toolkit analyze --directory src/
```

### 3. `query` - Query the Knowledge Graph

Queries the knowledge graph for components and their relationships.

```bash
ai-toolkit query [--component NAME] [--relationships] [--format FORMAT]
```

**What it does:**
- Searches the knowledge graph for components matching the query
- Displays information about components and their relationships
- Formats output as text or JSON

**Options:**
- `--component NAME`: Name of the component to query
- `--relationships`: Also show relationships for the component
- `--format FORMAT`: Output format ("text" or "json", default: "text")

**Examples:**
```bash
# List all components
ai-toolkit query

# Find a specific component
ai-toolkit query --component UserService

# Show relationships for a component
ai-toolkit query --component UserService --relationships

# Get output in JSON format
ai-toolkit query --component UserService --relationships --format json
```

### 4. `visualize` - Generate Visualizations

Creates visual diagrams from the knowledge graph.

```bash
ai-toolkit visualize [--component NAME] [--format FORMAT] [--output FILE]
```

**What it does:**
- Generates a Mermaid diagram from the knowledge graph
- Can focus on a specific component and its relationships
- Outputs to file or standard output

**Options:**
- `--component NAME`: Focus visualization on this component
- `--format FORMAT`: Visualization format (currently only "mermaid", default)
- `--output FILE`: Output file path (outputs to console if not specified)

**Examples:**
```bash
# Generate diagram of all components
ai-toolkit visualize

# Focus on a specific component
ai-toolkit visualize --component UserService

# Save diagram to a file
ai-toolkit visualize --output diagram.md
```

## Example Workflow

A typical workflow using the toolkit might look like:

```bash
# 1. Initialize the project
ai-toolkit init my-project

# 2. Analyze the codebase
ai-toolkit analyze --directory src/

# 3. Query to understand the structure
ai-toolkit query --component MainController --relationships

# 4. Generate a visualization
ai-toolkit visualize --component MainController --output system-diagram.md
```

## Output Examples

### Knowledge Graph Structure

The toolkit creates the following structure in your project:

```
.ai-toolkit/
├── kb/                  # Knowledge graph storage
│   ├── components.json  # All components
│   └── relationships.json # Relationships between components
├── config/              # Configuration files
└── cache/               # Analysis cache
```

### Mermaid Visualization Output

When using the `visualize` command, you'll get Mermaid markdown like:

```mermaid
graph TD
    module1[main.py] --> module2[utils.py]
    module1 ==> class1[Class<br/>UserController]
    class1 ==> method1[handle_request()]
    class1 ==> method2[process_data()]
```

## Troubleshooting

- **"AI-Native Development Toolkit not initialized"**: Run `ai-toolkit init` first
- **No components found**: Make sure you've run `ai-toolkit analyze` on your code
- **Visualization is empty**: Check if components exist using `ai-toolkit query`

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for development guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

[project.urls]
"Homepage" = "https://github.com/jackyckma/ai-toolkit"
"Bug Tracker" = "https://github.com/jackyckma/ai-toolkit/issues" 