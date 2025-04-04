#!/bin/bash
#
# AI-Native Development Toolkit Manual Setup Script
# Repository: https://github.com/jackyckma/ai-toolkit
#
# This script sets up the AI-Native Development Toolkit after cloning the repository.
# Usage: bash manual_setup.sh [target_directory]
#

set -e

# Default target directory
TARGET_DIR="${1:-.ai-toolkit}"
echo "Setting up AI-Native Development Toolkit in $TARGET_DIR..."

# Create directory structure
mkdir -p "$TARGET_DIR"/{bin,cache,config,kb/queries}

# Copy toolkit files if we're in the cloned repository
if [ -d "src/ai_toolkit" ]; then
    echo "Copying toolkit files..."
    cp -r src/ai_toolkit/* "$TARGET_DIR"/
fi

# Create default knowledge graph files
echo '{}' > "$TARGET_DIR"/kb/components.json
echo '[]' > "$TARGET_DIR"/kb/relationships.json

# Create config file
cat > "$TARGET_DIR"/config/config.json << EOF
{
    "version": "0.1.0",
    "project_name": "$(basename $(pwd))",
    "installed_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
    "repository": "https://github.com/jackyckma/ai-toolkit"
}
EOF

# Create a simple wrapper script
cat > "$TARGET_DIR"/bin/ai-toolkit << EOF
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

chmod +x "$TARGET_DIR"/bin/ai-toolkit

# Display success message
echo "AI-Native Development Toolkit setup completed!"
echo "You can now use it by running:"
echo "  $TARGET_DIR/bin/ai-toolkit"
echo ""
echo "For example:"
echo "  $TARGET_DIR/bin/ai-toolkit init"
echo "  $TARGET_DIR/bin/ai-toolkit analyze --directory src/" 