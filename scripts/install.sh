#!/bin/bash
#
# AI-Native Development Toolkit Installation Script
# Repository: https://github.com/jackyckma/ai-toolkit
#

set -e

# Check if this is an update or a fresh installation
if [ -d ".ai-toolkit" ]; then
    echo "Updating AI-Native Development Toolkit..."
    
    # Create a backup of existing data
    echo "Creating backup of existing data..."
    backup_dir=".ai-toolkit/backups/$(date +"%Y%m%d_%H%M%S")"
    mkdir -p "$backup_dir"
    
    # Backup knowledge graph data
    if [ -f ".ai-toolkit/kb/components.json" ]; then
        cp ".ai-toolkit/kb/components.json" "$backup_dir/"
    fi
    if [ -f ".ai-toolkit/kb/relationships.json" ]; then
        cp ".ai-toolkit/kb/relationships.json" "$backup_dir/"
    fi
    
    # Backup config
    if [ -f ".ai-toolkit/config/config.json" ]; then
        cp ".ai-toolkit/config/config.json" "$backup_dir/"
    fi
    
    # Backup cache
    if [ -d ".ai-toolkit/cache" ]; then
        cp -r ".ai-toolkit/cache" "$backup_dir/"
    fi
    
    echo "Existing data backed up to $backup_dir"
    
    # Get current version before update
    old_version=$(grep '"version":' .ai-toolkit/config/config.json | cut -d'"' -f4 || echo "unknown")
    echo "Current version: $old_version"
    
    # Download latest code
    echo "Downloading latest toolkit files from GitHub..."
    git clone --depth 1 https://github.com/jackyckma/ai-toolkit.git .ai-toolkit-temp
    
    # Get new version
    new_version=$(grep '"version":' .ai-toolkit-temp/src/ai_toolkit/config/config.json | cut -d'"' -f4 || echo "$old_version")
    
    # Save existing bin directory temporarily if it exists and has custom scripts
    if [ -d ".ai-toolkit/bin" ]; then
        if [ "$(find .ai-toolkit/bin -type f -not -name 'ai-toolkit' | wc -l)" -gt 0 ]; then
            echo "Preserving custom scripts in bin directory..."
            cp -r ".ai-toolkit/bin" "$backup_dir/"
        fi
    fi
    
    # Update toolkit code
    echo "Updating toolkit code..."
    # Copy the migrations script first so we can use it after updating
    cp .ai-toolkit-temp/scripts/migrations.sh "$backup_dir/"
    
    # Update all code
    cp -r .ai-toolkit-temp/src/ai_toolkit/* .ai-toolkit/
    
    # Restore knowledge graph data
    echo "Restoring knowledge graph data..."
    if [ -f "$backup_dir/components.json" ]; then
        cp "$backup_dir/components.json" ".ai-toolkit/kb/"
    fi
    if [ -f "$backup_dir/relationships.json" ]; then
        cp "$backup_dir/relationships.json" ".ai-toolkit/kb/"
    fi
    
    # Restore config but update version
    if [ -f "$backup_dir/config.json" ]; then
        # Create temporary config with updated version
        jq ".version = \"$new_version\" | .updated_at = \"$(date -u +"%Y-%m-%dT%H:%M:%SZ")\"" \
           "$backup_dir/config.json" > ".ai-toolkit/config/config.json" 2>/dev/null || \
        # Fallback if jq is not available
        cp "$backup_dir/config.json" ".ai-toolkit/config/config.json"
    fi
    
    # Restore cache
    if [ -d "$backup_dir/cache" ]; then
        cp -r "$backup_dir/cache"/* ".ai-toolkit/cache/" 2>/dev/null || true
    fi
    
    # Run data migrations if version has changed
    if [ "$old_version" != "$new_version" ] && [ -f "$backup_dir/migrations.sh" ]; then
        echo "Running data migrations..."
        bash "$backup_dir/migrations.sh" "$old_version" "$new_version" ".ai-toolkit"
    fi
    
    # Ensure the wrapper script is executable
    chmod +x .ai-toolkit/bin/ai-toolkit
    
    # Clean up temp files
    rm -rf .ai-toolkit-temp
    
    # Display update success message
    echo "AI-Native Development Toolkit updated successfully!"
    echo "Version: $old_version -> $new_version"
    echo "Your existing data has been preserved."
    
else
    echo "Installing AI-Native Development Toolkit..."

    # Create .ai-toolkit directory
    mkdir -p .ai-toolkit/{bin,kb,config,cache,backups}
    mkdir -p .ai-toolkit/kb/{queries}

    # Clone the repository
    echo "Downloading toolkit files from GitHub..."
    git clone --depth 1 https://github.com/jackyckma/ai-toolkit.git .ai-toolkit-temp
    cp -r .ai-toolkit-temp/src/ai_toolkit/* .ai-toolkit/
    
    # Create necessary script directories and copy scripts
    mkdir -p .ai-toolkit/scripts
    cp .ai-toolkit-temp/scripts/migrations.sh .ai-toolkit/scripts/
    chmod +x .ai-toolkit/scripts/migrations.sh

    # Create default knowledge graph files
    echo '{}' > .ai-toolkit/kb/components.json
    echo '[]' > .ai-toolkit/kb/relationships.json

    # Get version from code
    version=$(grep '"version":' .ai-toolkit-temp/src/ai_toolkit/config/config.json | cut -d'"' -f4 || echo "0.1.0")
    
    # Create config file
    cat > .ai-toolkit/config/config.json << EOF
{
    "version": "$version",
    "project_name": "$(basename $(pwd))",
    "installed_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
    "repository": "https://github.com/jackyckma/ai-toolkit"
}
EOF

    # Create a wrapper script
    cat > .ai-toolkit/bin/ai-toolkit << EOF
#!/bin/bash
# AI-Native Development Toolkit Wrapper
# Repository: https://github.com/jackyckma/ai-toolkit

echo "AI-Native Development Toolkit v$version"
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
    update)
        echo "Updating AI-Native Development Toolkit..."
        curl -sSL https://raw.githubusercontent.com/jackyckma/ai-toolkit/main/scripts/install.sh | bash
        ;;
    version)
        echo "AI-Native Development Toolkit version $version"
        echo "Installed at: $(grep '"installed_at":' .ai-toolkit/config/config.json | cut -d'"' -f4)"
        ;;
    *)
        echo "Usage: ai-toolkit [command]"
        echo "Available commands: init, analyze, query, visualize, update, version"
        ;;
esac
EOF

    chmod +x .ai-toolkit/bin/ai-toolkit
    
    # Clean up temp files
    rm -rf .ai-toolkit-temp

    # Display success message
    echo "AI-Native Development Toolkit installed successfully!"
    echo "Version: $version"
    echo "You can now use it by running:"
    echo "  .ai-toolkit/bin/ai-toolkit"
    echo ""
    echo "For example:"
    echo "  .ai-toolkit/bin/ai-toolkit init"
    echo "  .ai-toolkit/bin/ai-toolkit analyze --directory src/"
    echo "  .ai-toolkit/bin/ai-toolkit update    # To update the toolkit"
    echo "  .ai-toolkit/bin/ai-toolkit version   # To check version info"
fi
