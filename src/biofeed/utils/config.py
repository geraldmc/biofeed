"""Configuration management for BioFeed."""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

# Default configuration values
DEFAULT_CONFIG = {
    "cache_duration": 3600,  # 1 hour in seconds
    "default_feeds": {
        "nature_bioinformatics": {
            "name": "Nature Bioinformatics",
            "url": "https://www.nature.com/subjects/bioinformatics.atom",
            "category": "bioinformatics"
        }
    }
}

def get_config_dir() -> Path:
    """Get the configuration directory for BioFeed."""
    # Use XDG_CONFIG_HOME if available, otherwise use ~/.config
    config_home = os.environ.get("XDG_CONFIG_HOME")
    if config_home:
        config_dir = Path(config_home) / "biofeed"
    else:
        config_dir = Path.home() / ".config" / "biofeed"
    
    # Create the directory if it doesn't exist
    config_dir.mkdir(parents=True, exist_ok=True)
    
    return config_dir

def get_config_file(filename: str) -> Path:
    """Get a configuration file path."""
    return get_config_dir() / filename

def load_config(filename: str, default: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Load a configuration file, creating it with default values if it doesn't exist."""
    config_file = get_config_file(filename)
    
    if not config_file.exists():
        # Create the file with default values
        config_data = default or {}
        with open(config_file, "w") as f:
            json.dump(config_data, f, indent=2)
        return config_data
    
    try:
        with open(config_file, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        # If the file is corrupted, create a new one with default values
        config_data = default or {}
        with open(config_file, "w") as f:
            json.dump(config_data, f, indent=2)
        return config_data

def save_config(filename: str, config_data: Dict[str, Any]) -> None:
    """Save configuration to a file."""
    config_file = get_config_file(filename)
    
    with open(config_file, "w") as f:
        json.dump(config_data, f, indent=2)