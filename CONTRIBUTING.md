# Contributing to AI-Native Development Toolkit

Thank you for your interest in contributing to the AI-Native Development Toolkit! This document provides guidelines and instructions for contributing to the project.

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ai-toolkit.git
   cd ai-toolkit
   ```

2. Set up a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install development dependencies:
   ```bash
   pip install -e .
   ```

4. Verify setup:
   ```bash
   python test_project_structure.py
   ```

## Project Structure

The project follows the structure outlined below:

```
ai-toolkit/
├── src/
│   ├── ai_toolkit/          # Main package
│   │   ├── cli/             # Command line interface
│   │   ├── kb/              # Knowledge graph
│   │   ├── parser/          # Code parsers
│   │   └── viz/             # Visualization
│   └── bin/
│       └── ai-toolkit       # Command-line entry point
├── tests/                   # Test suite
├── docs/                    # Documentation
├── scripts/
│   └── install.sh           # Installation script
├── pyproject.toml           # Package configuration
└── README.md                # Project documentation
```

## Development Workflow

1. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and ensure they follow the coding style

3. Test your changes
   ```bash
   # Run the basic structure test
   python test_project_structure.py
   
   # Test the CLI functionality
   python -m ai_toolkit.cli.main --help
   ```

4. Commit and push your changes:
   ```bash
   git commit -m "Description of your changes"
   git push origin feature/your-feature-name
   ```

5. Open a pull request

## Adding New Features

### Adding a New Command

To add a new command to the CLI:

1. Create a new command file in `src/ai_toolkit/cli/commands/`
2. Implement the `main(args)` function
3. Add the command parser to `create_parser()` in `src/ai_toolkit/cli/main.py`

### Adding a New Visualization Format

To add a new visualization format:

1. Create a new generator class in `src/ai_toolkit/viz/`
2. Implement the `DiagramGenerator` interface
3. Update the `visualize` command to use the new format

### Adding a New Language Parser

To add support for a new programming language:

1. Create a new parser in `src/ai_toolkit/parser/`
2. Implement the language-specific parsing logic
3. Update the `analyze` command to use the new parser

## Coding Guidelines

- Follow PEP 8 style guide for Python code
- Use type hints for function parameters and return values
- Write docstrings for all modules, classes, and functions
- Keep functions small and focused on a single responsibility
- Use meaningful variable and function names

## Documentation

- Update documentation when adding or changing features
- Include examples of how to use new features
- Document any command-line arguments or options

## License

By contributing to the AI-Native Development Toolkit, you agree that your contributions will be licensed under the project's MIT license. 