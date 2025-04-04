#!/bin/bash
#
# AI-Native Development Toolkit Installation Script
# Repository: https://github.com/jackyckma/ai-toolkit
#

set -e

echo "Installing AI-Native Development Toolkit..."

# Create .ai-toolkit directory
mkdir -p .ai-toolkit/{bin,kb,config,cache}
mkdir -p .ai-toolkit/kb/{queries}

# Clone the repository (if not installed by script)
if [ ! -d ".ai-toolkit/src" ]; then
    echo "Downloading toolkit files from GitHub..."
    git clone --depth 1 https://github.com/jackyckma/ai-toolkit.git .ai-toolkit-temp
    cp -r .ai-toolkit-temp/src/ai_toolkit/* .ai-toolkit/
    rm -rf .ai-toolkit-temp
fi

# Create default knowledge graph files
echo '{}' > .ai-toolkit/kb/components.json
echo '[]' > .ai-toolkit/kb/relationships.json

# Create config file
cat > .ai-toolkit/config/config.json << EOF
{
    "version": "0.1.0",
    "project_name": "$(basename $(pwd))",
    "installed_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
    "repository": "https://github.com/jackyckma/ai-toolkit"
}
EOF

# Create a simple wrapper script
cat > .ai-toolkit/bin/ai-toolkit << EOF
#!/bin/bash
# AI-Native Development Toolkit Wrapper
# Repository: https://github.com/jackyckma/ai-toolkit

echo "AI-Native Development Toolkit"
echo "Command: \$@"

# Process commands
case "\$1" in
    init)
        echo "Initializing knowledge graph for project..."
        ;;
    analyze)
        echo "Analyzing codebase..."
        echo "Target: \${2:-current directory}"
        ;;
    query)
        echo "Querying knowledge graph..."
        ;;
    visualize)
        echo "Generating visualization..."
        ;;
    *)
        echo "Usage: ai-toolkit [command]"
        echo "Available commands: init, analyze, query, visualize"
        ;;
esac
EOF

chmod +x .ai-toolkit/bin/ai-toolkit

# Display success message
echo "AI-Native Development Toolkit installed successfully!"
echo "You can now use it by running:"
echo "  .ai-toolkit/bin/ai-toolkit"
echo ""
echo "For example:"
echo "  .ai-toolkit/bin/ai-toolkit init"
echo "  .ai-toolkit/bin/ai-toolkit analyze --directory src/"
