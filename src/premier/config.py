"""Configuration management for premier participants."""

from pathlib import Path
from typing import Optional

try:
    import tomllib
except ImportError:
    # Python < 3.11
    import tomli as tomllib


def load_config(config_path: str) -> dict:
    """Load TOML configuration file.
    
    Args:
        config_path: Path to TOML config file
        
    Returns:
        Dictionary containing config data
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If config file is invalid
    """
    path = Path(config_path)
    
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(path, "rb") as f:
        try:
            return tomllib.load(f)
        except Exception as e:
            raise ValueError(f"Invalid TOML config file: {e}")


def get_participants(config: dict) -> dict[int, str]:
    """Extract participants from config.
    
    Args:
        config: Configuration dictionary from load_config()
        
    Returns:
        Dictionary mapping entry_id (int) to name (str)
    """
    participants = config.get("participants", {})
    
    # Convert string keys to integers
    return {int(k): v for k, v in participants.items()}


def get_export_defaults(config: dict) -> dict:
    """Extract export defaults from config.
    
    Args:
        config: Configuration dictionary from load_config()
        
    Returns:
        Dictionary with gw_start and gw_end
    """
    export = config.get("export", {})
    return {
        "gw_start": export.get("gw_start", 1),
        "gw_end": export.get("gw_end", 5),
    }


def get_entry_id_to_name(config: dict) -> dict[int, str]:
    """Extract entry ID to participant name mapping from config.
    
    Args:
        config: Configuration dictionary from load_config()
        
    Returns:
        Dictionary mapping entry_id (int) to name (str)
    """
    participants = config.get("participants", {})
    return {int(k): v for k, v in participants.items()}
