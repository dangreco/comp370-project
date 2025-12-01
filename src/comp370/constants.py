"""
Project-wide constants and directory setup.

This module defines the root directory structure and ensures that
required directories exist.
"""

import os
from pathlib import Path
from importlib.resources import files

# Root directory of the project
DIR_ROOT = Path(files(__package__)).parent.parent

# Data directory for storing databases
DIR_DATA = DIR_ROOT / "data"

# Cache directory for storing cached data
DIR_CACHE = DIR_ROOT / "cache"

# Ensure all required directories exist
for dir in [DIR_DATA, DIR_CACHE]:
    os.makedirs(dir, exist_ok=True)
