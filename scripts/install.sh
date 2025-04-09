#!/bin/bash
#
# AI-Native Development Toolkit Installation Script
# Repository: https://github.com/jackyckma/ai-toolkit
#
# This script downloads and installs the AI-Native Development Toolkit.
# Usage: curl -sSL https://raw.githubusercontent.com/jackyckma/ai-toolkit/main/scripts/install.sh | bash
#

set -e

echo "Installing AI-Native Development Toolkit..."

# Create a temporary directory for the download
TEMP_DIR=$(mktemp -d)
REPO_URL="https://github.com/jackyckma/ai-toolkit.git"
TARGET_DIR=".ai-toolkit"

# Clean up temp directory on exit
trap 'rm -rf "$TEMP_DIR"' EXIT

# Clone the repository to the temporary directory
echo "Downloading toolkit from $REPO_URL..."
git clone --depth 1 "$REPO_URL" "$TEMP_DIR"

# Run the manual setup script
echo "Setting up the toolkit..."
bash "$TEMP_DIR/scripts/manual_setup.sh" "$TARGET_DIR"

# Display success message
echo ""
echo "AI-Native Development Toolkit installation completed!"
echo "You can now use it by running:"
echo "  $TARGET_DIR/bin/ai-toolkit"
echo ""
echo "For example:"
echo "  $TARGET_DIR/bin/ai-toolkit init"
echo "  $TARGET_DIR/bin/ai-toolkit analyze --directory src/"
echo "  $TARGET_DIR/bin/ai-toolkit agent --direct-mode code --task \"Create a function\""
echo ""
echo "Documentation: $TARGET_DIR/docs/"
echo "Repository: $REPO_URL"
