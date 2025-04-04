"""
Configuration module for the AI-Native Development Toolkit.

This module provides access to configuration settings for the toolkit.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any

def get_config() -> Dict[str, Any]:
    """
    Get the toolkit configuration.
    
    Returns:
        Dictionary containing the configuration
    """
    config_path = Path(__file__).parent / "config.json"
    if not config_path.exists():
        return {
            "version": "0.1.0",
            "name": "AI-Native Development Toolkit",
            "description": "A toolkit for AI-native development with knowledge graph and visualization capabilities",
            "repository": "https://github.com/jackyckma/ai-toolkit"
        }
    
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_version() -> str:
    """
    Get the toolkit version.
    
    Returns:
        Version string
    """
    return get_config().get("version", "0.1.0") 