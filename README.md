# AI-Native Development Toolkit

A command-line toolkit designed to enhance AI-led software development. This toolkit enables AI systems to build and maintain software more effectively by providing tools that align with AI's cognitive patterns while maintaining human-readable outputs.

## Key Features

- **Knowledge Graph Representation**: Represents code as a connected graph of components and relationships
- **Code Analysis**: Extracts structure and relationships from Python code files
- **Visualization Tools**: Generates human-readable diagrams from the knowledge graph
- **Query Interface**: Provides powerful ways to explore code relationships
- **Multi-Agent System**: Leverages specialized AI agents for code generation and testing tasks

## Installation

The toolkit is designed to be installed directly in your project repository:

```bash
# Install directly using the installation script
curl -sSL https://raw.githubusercontent.com/jackyckma/ai-toolkit/main/scripts/install.sh | bash
```

### Manual Installation

If you prefer manual installation:

```bash
# Clone the repository
git clone https://github.com/jackyckma/ai-toolkit.git .ai-toolkit-temp

# Run the setup script
bash .ai-toolkit-temp/scripts/manual_setup.sh

# Clean up
rm -rf .ai-toolkit-temp
```

This will install the toolkit in the `.ai-toolkit` directory within your project.

## Command Reference

The toolkit provides the following primary commands:

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
ai-toolkit visualize [--component NAME] [--format FORMAT] [--output FILE] [--type TYPE]
```

**What it does:**
- Generates a Mermaid diagram from the knowledge graph
- Can focus on a specific component and its relationships
- Outputs to file or standard output
- Supports different diagram types (component, module, class, dependency, call)

**Options:**
- `--component NAME`: Focus visualization on this component
- `--format FORMAT`: Visualization format (currently only "mermaid", default)
- `--output FILE`: Output file path (outputs to console if not specified)
- `--type TYPE`: Type of diagram to generate (default: "component")

**Examples:**
```bash
# Generate diagram of all components
ai-toolkit visualize

# Focus on a specific component
ai-toolkit visualize --component UserService

# Save diagram to a file
ai-toolkit visualize --output diagram.md

# Generate a dependency diagram
ai-toolkit visualize --type dependency --component DataProcessor
```

### 5. `agent` - Use the Multi-Agent System

Utilizes specialized AI agents to perform code generation and testing tasks.

```bash
ai-toolkit agent --task "TASK_DESCRIPTION" [--direct-mode MODE] [--output FILE]
```

**What it does:**
- Uses a multi-agent system to generate code or tests based on natural language descriptions
- Can work in coordinator mode (delegating to specialized agents) or direct mode (using a single agent)
- Outputs structured results with extracted code blocks

**Options:**
- `--task TEXT`: Task description for the agent system (required)
- `--direct-mode MODE`: Use a single agent directly (`code` or `test`)
- `--output FILE`: Output file path for saving the results
- `--context-file FILE`: JSON file with additional context for the task

**Examples:**
```bash
# Use the coordinator to handle a complex task
ai-toolkit agent --task "Create a Python function that calculates the factorial of a number" --output result.json

# Use the code generation agent directly
ai-toolkit agent --direct-mode code --task "Create a Python function that calculates the factorial of a number" --output result.json

# Use the testing agent directly
ai-toolkit agent --direct-mode test --task "Create tests for a function that calculates the factorial of a number" --output result.json
```

See [agent_system.md](./docs/agent_system.md) for detailed documentation on the multi-agent system.

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

# 5. Generate code using the multi-agent system
ai-toolkit agent --direct-mode code --task "Create a Python function to parse JSON data from a file" --output parser.json
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

### Multi-Agent System Output

When using the `agent` command, you'll get JSON output like:

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

## Troubleshooting

- **"AI-Native Development Toolkit not initialized"**: Run `ai-toolkit init` first
- **No components found**: Make sure you've run `ai-toolkit analyze` on your code
- **Visualization is empty**: Check if components exist using `ai-toolkit query`
- **Agent command fails**: Check your `.env` file for proper API keys

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for development guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

[project.urls]
"Homepage" = "https://github.com/jackyckma/ai-toolkit"
"Bug Tracker" = "https://github.com/jackyckma/ai-toolkit/issues"

## Using with Cursor AI

For the best experience with Cursor AI and to ensure AI assistants can properly utilize this toolkit:

1. Import the included **AI Native Development Rules** as a Project Rule in Cursor AI:
   - In Cursor AI, go to Settings > Project Rules
   - Click "Add Rule" and select the `AI Native Development Rules.md` file from the project root
   - This enables AI assistants to understand how to properly initialize and use the toolkit

2. Ensure the toolkit is installed in your project before asking the AI to use it:
   ```bash
   curl -sSL https://raw.githubusercontent.com/jackyckma/ai-toolkit/main/scripts/install.sh | bash
   ```

Once properly set up, Cursor AI can then help you leverage the toolkit's knowledge graph capabilities without additional prompting. 