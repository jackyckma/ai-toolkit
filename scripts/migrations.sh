#!/bin/bash
#
# AI-Native Development Toolkit Migration Script
# Repository: https://github.com/jackyckma/ai-toolkit
#
# This script handles migrations between different versions of the toolkit

set -e

# Source and destination versions
SOURCE_VERSION=$1
TARGET_VERSION=$2
TOOLKIT_DIR=$3

if [ -z "$SOURCE_VERSION" ] || [ -z "$TARGET_VERSION" ] || [ -z "$TOOLKIT_DIR" ]; then
    echo "Usage: $0 <source_version> <target_version> <toolkit_directory>"
    exit 1
fi

echo "Migrating from version $SOURCE_VERSION to $TARGET_VERSION..."

# Compare versions
version_lt() {
    [ "$1" = "$2" ] && return 1 || [  "$1" = "$(echo -e "$1\n$2" | sort -V | head -n1)" ]
}

# Function to run specific migration based on version
run_migration() {
    local from=$1
    local to=$2
    
    echo "Applying migration from $from to $to..."
    
    # These are placeholder migrations. Add real migrations as needed.
    case "$from-$to" in
        "0.1.0-0.2.0")
            echo "Migrating from 0.1.0 to 0.2.0..."
            # Example: Update component schema to include new fields
            # jq '.[].new_field = ""' "$TOOLKIT_DIR/kb/components.json" > temp.json && mv temp.json "$TOOLKIT_DIR/kb/components.json"
            ;;
            
        "0.2.0-0.3.0")
            echo "Migrating from 0.2.0 to 0.3.0..."
            # Example: Update relationship schema
            ;;
            
        "0.3.0-0.4.0")
            echo "Migrating from 0.3.0 to 0.4.0..."
            # Example: Restructure cache format
            ;;
            
        *)
            echo "No specific migration needed from $from to $to"
            ;;
    esac
}

# Check if we're skipping multiple versions and need to run multiple migrations
if version_lt "$SOURCE_VERSION" "$TARGET_VERSION"; then
    # Define all versions in sequence
    VERSIONS=("0.1.0" "0.2.0" "0.3.0" "0.4.0" "0.5.0")
    
    # Find indices of source and target versions
    SOURCE_INDEX=-1
    TARGET_INDEX=-1
    
    for i in "${!VERSIONS[@]}"; do
        if [ "${VERSIONS[$i]}" = "$SOURCE_VERSION" ]; then
            SOURCE_INDEX=$i
        fi
        if [ "${VERSIONS[$i]}" = "$TARGET_VERSION" ]; then
            TARGET_INDEX=$i
        fi
    done
    
    # Run migrations sequentially
    if [ $SOURCE_INDEX -ge 0 ] && [ $TARGET_INDEX -gt $SOURCE_INDEX ]; then
        for ((i=SOURCE_INDEX; i<TARGET_INDEX; i++)); do
            from="${VERSIONS[$i]}"
            to="${VERSIONS[$i+1]}"
            run_migration "$from" "$to"
        done
    else
        echo "Warning: Cannot determine migration path from $SOURCE_VERSION to $TARGET_VERSION"
        echo "Attempting direct migration..."
        run_migration "$SOURCE_VERSION" "$TARGET_VERSION"
    fi
else
    echo "No migration needed - source version is not older than target version"
fi

echo "Migration completed successfully!" 