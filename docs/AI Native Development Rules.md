# AI-Native Development Rules

## 1. System Organization

### 1.1 Dual Representation Architecture
- Maintain two parallel representations of the system:
  - **Human-Readable**: Traditional files and folders for human review
  - **AI-Native**: Knowledge graph structure for AI development
- Synchronize both representations automatically
- Use special tools to translate between representations:
  ```python
  # tools/graph_sync.py
  """
  Synchronizes between file-based code and knowledge graph representation.
  - Running after code changes updates the knowledge graph
  - Running with --reverse flag generates code from knowledge graph
  """
  ```

### 1.2 Knowledge Graph Structure
- Represent the system as a connected knowledge graph rather than hierarchical files
- Each node (concept, function, data structure) connects to related nodes
- Tag all nodes with multiple dimensions:
  - Functionality domain
  - Data transformation type
  - Input/output relationships
  - Usage frequency
  - Dependency count
- Store graph in queryable format:
  ```
  /kb/
    graph.json       # Full knowledge graph
    graph.sqlite     # Queryable database version
    queries/         # Common graph queries
      dependencies.sql
      impact_analysis.sql
      pattern_matches.sql
  ```

### 1.3 Self-Documenting System
- Embed documentation directly in code using standardized patterns
- Maintain parallel representations of each component:
  - Implementation (code)
  - Specification (formal interface)
  - Example usage
  - Test cases
  - Performance characteristics
- Use automated tools to extract and verify consistency:
  ```bash
  # Verify documentation consistency
  ./tools/verify_docs.py --component=auth_service
  
  # Generate missing documentation
  ./tools/doc_generator.py --component=data_processor
  ```

### 1.4 Continuous System Map
- Generate and update a complete system map after each significant change
- Document component relationships with concrete metrics:
  - Coupling score (0-10)
  - Information flow direction
  - Change propagation likelihood
- Visualize with both hierarchical and network views
- Integrate system mapping into the development workflow:
  ```python
  # In commit hooks or CI pipeline
  def after_commit_hook():
      """
      Automatically update system map after each commit.
      - Updates knowledge graph
      - Regenerates visualization
      - Analyzes impact of changes
      """
  ```

## 2. Development Loop

### 2.1 Iterative Expansion Model
- Start with minimal implementation of core functionality
- Expand in concentric circles of related features
- Continuously refactor for maximum pattern recognition
- Capture user feedback as first-class constraints

### 2.2 Hypothesis-Driven Enhancement
- Frame each feature as a hypothesis about user needs
- Implement the minimal version to test the hypothesis
- Collect structured feedback to validate or refute
- Document the evolution of understanding

### 2.3 Simulation-First Development
- Before implementing any feature, simulate its behavior
- Create exhaustive usage scenarios with edge cases
- Validate logical consistency before implementation
- Test against previously captured user preferences

## 3. Code Structures

### 3.1 Pattern-Optimized Components
- Organize code into consistently structured patterns
- Use explicit templates for similar components
- Enforce structural consistency across the codebase
- Examples:
  ```
  # TRANSFORMER COMPONENT TEMPLATE
  # Input schema: {...}
  # Output schema: {...}
  # Transformation rules: [...]
  # Side effects: None
  # Usage frequency: High
  ```

### 3.2 Explicit State Management
- Make all state changes explicit and traceable
- Maintain state transition graphs for complex components
- Prefer pure functions with explicit inputs/outputs
- Document every side effect with source and scope

### 3.3 Parallel Implementation Versions
- Maintain multiple implementations of critical components
- Document performance characteristics of each version
- Create specialized versions for different contexts:
  - High-performance version
  - Memory-efficient version
  - Simplified debugging version
  - Teaching/reference version

## 4. Testing Framework

### 4.1 Exhaustive Property Testing
- Define formal properties that must hold for each component
- Generate automated test cases from properties
- Maintain a repository of edge cases and boundary conditions
- Test against future and historical versions

### 4.2 Simulation Environment
- Create complete simulation environments for testing
- Generate synthetic but realistic input data
- Capture real usage patterns to inform simulation
- Expand test coverage based on failure analysis

### 4.3 Metamorphic Testing
- Identify transformation relationships between inputs and outputs
- Define how changing inputs should change outputs
- Test relationship validity across input domains
- Document discovered invariants

## 5. User Interaction

### 5.1 Constraint Capture
- Translate user feedback into formal constraints
- Categorize constraints by type:
  - Functional requirements
  - Performance thresholds
  - User preferences
  - Domain rules
- Maintain a constraint satisfaction graph

### 5.2 Requirement Evolution
- Track how requirements change over time
- Identify pattern shifts in user expectations
- Generate predictive models of future requirements
- Present adaptation options proactively

### 5.3 Experiment Framework
- Deploy parallel versions to gather comparative feedback
- Design minimal experiments to resolve uncertainty
- Present findings with confidence intervals
- Recommend next experiments based on information gain

## 6. Maintenance Patterns

### 6.1 Automated Dependency Management
- Track all external dependencies with usage patterns
- Maintain compatibility layers for critical dependencies
- Generate migration plans for major version changes
- Create specialized wrappers that normalize interfaces

### 6.2 Anomaly Detection
- Implement runtime instrumentation for pattern detection
- Create baselines of normal behavior
- Alert on unexpected state or performance changes
- Build self-healing mechanisms for common issues

### 6.3 System Evolution
- Periodically restructure the codebase based on usage patterns
- Migrate frequently-used paths to optimized implementations
- Archive and simplify rarely-used components
- Maintain multiple architectural perspectives simultaneously

## 7. Self-Augmentation & Tool Creation

### 7.1 AI Development Tools
- Create specialized tools to enhance your own capabilities:
  - Schema extractors that generate formal models from code
  - Dependency analyzers that visualize component relationships
  - Consistency checkers that validate architectural rules
  - Test generators that identify uncovered edge cases
- Example tool structure:
  ```python
  # tools/dependency_analyzer.py
  """
  Analyzes import relationships and function calls to generate 
  a dependency graph of the entire project.
  
  Usage: python tools/dependency_analyzer.py --output=graph.json
  
  Output formats:
  - JSON: Network representation
  - DOT: Graphviz visualization
  - MD: Markdown summary
  """
  ```

### 7.2 Project Knowledge Base
- Maintain a dedicated knowledge graph database for the project:
  - Store component relationships and metadata
  - Track historical decisions and their reasoning
  - Index code patterns for retrieval and reuse
  - Capture usage statistics and performance metrics
- Example implementation:
  ```
  /project_kb/
    schema.graphql     # Knowledge graph schema
    components.json    # Component registry
    patterns.json      # Reusable patterns
    decisions.json     # Decision history
    metrics.sqlite     # Performance metrics
  ```

### 7.3 Specialized Agent Architecture
- Create purpose-specific agents for different aspects of development:
  - ArchitectAgent: System design and structural decisions
  - TestingAgent: Comprehensive test coverage and validation
  - RefactorAgent: Code optimization and pattern application
  - DocumentationAgent: Human-readable explanations
- Example agent framework:
  ```python
  # agents/base_agent.py
  """
  Base class for specialized development agents.
  Each agent has access to the project knowledge base,
  specialized tools, and a focused responsibility area.
  """
  
  # agents/testing_agent.py
  """
  Specialized agent for test generation and validation.
  Maintains comprehensive test coverage and identifies
  edge cases based on code structure analysis.
  """
  ```

## 8. Communication Interface

### 8.1 User Interaction Model
- Present findings as options with probability estimates
- Format communication based on user's technical level
- Use concrete examples for all abstract concepts
- Visualize system state and changes
- Generate human-readable summaries from AI-native structures

### 8.2 Decision Registry
- Document all significant decisions with:
  - Problem statement
  - Explored alternatives
  - Selection criteria
  - Expected outcomes
  - Verification metrics
- Link decisions to implementing components
- Visualize decision trees for complex choices

### 8.3 Progressive Disclosure
- Layer information by relevance and complexity
- Start with high-level summaries
- Provide drill-down paths for details
- Tag information by user role relevance
- Generate multiple views of the same information:
  - Technical deep-dive for developers
  - Functional overview for product managers
  - Visual representations for stakeholders

## 9. AI-Native Development Toolkit

### 9.1 Toolkit Initialization

- At the start of a project, check for the presence of the AI-Native Development Toolkit:
  ```bash
  # Check if .ai-toolkit directory exists
  if [ ! -d ".ai-toolkit" ]; then
    # Ask user for permission to install
    echo "AI-Native Development Toolkit not found. Would you like to install it? (y/n)"
  fi
  ```

- If toolkit is not available, ask the user for permission to install it:
  ```
  I've noticed that the AI-Native Development Toolkit is not installed in this repository.
  This toolkit would help me:
  - Create a knowledge graph of the code structure
  - Generate visualizations of component relationships
  - Analyze dependencies and code structure
  
  Would you like me to install it from GitHub?
  ```

- Installation process:
  ```bash
  # Option 1: Use the installation script
  curl -sSL https://raw.githubusercontent.com/jackyckma/ai-toolkit/main/scripts/install.sh | bash
  
  # Option 2: Clone and install from GitHub
  git clone https://github.com/jackyckma/ai-toolkit.git .ai-toolkit-temp
  cp -r .ai-toolkit-temp/src/ai_toolkit .ai-toolkit
  rm -rf .ai-toolkit-temp
  ```

### 9.2 Toolkit Usage

- The toolkit is installed in the `.ai-toolkit/` directory within the project
- All commands must be invoked using the full path to the binary:

- Initialize the knowledge graph at the beginning of a project:
  ```bash
  .ai-toolkit/bin/ai-toolkit init [project_name]
  ```

- After creating or modifying code, analyze the codebase:
  ```bash
  .ai-toolkit/bin/ai-toolkit analyze --directory src/
  ```

- Query the knowledge graph to understand structure and relationships:
  ```bash
  # List all components
  .ai-toolkit/bin/ai-toolkit query
  
  # Find a specific component
  .ai-toolkit/bin/ai-toolkit query --component ComponentName
  
  # Show relationships for a component
  .ai-toolkit/bin/ai-toolkit query --component ComponentName --relationships
  ```

- Generate visualizations to understand the system architecture:
  ```bash
  # Generate a component diagram
  .ai-toolkit/bin/ai-toolkit visualize --output docs/system_diagram.md
  
  # Focus on a specific component
  .ai-toolkit/bin/ai-toolkit visualize --component ComponentName --output docs/component_diagram.md
  ```

- Development workflow integration:
  1. Initialize the project with `.ai-toolkit/bin/ai-toolkit init`
  2. Create initial code structure
  3. Analyze the codebase with `.ai-toolkit/bin/ai-toolkit analyze --directory src/`
  4. When you need to understand relationships, use `.ai-toolkit/bin/ai-toolkit query`
  5. When explaining architecture, use `.ai-toolkit/bin/ai-toolkit visualize`
  6. After significant changes, re-analyze with `.ai-toolkit/bin/ai-toolkit analyze`

- For detailed documentation, refer to the toolkit documentation:
  ```
  .ai-toolkit/docs/README.md
  ```
