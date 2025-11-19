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

# Data directory for storing databases and cached data
DIR_DATA = DIR_ROOT / "data"

# Ensure all required directories exist
for dir in [DIR_DATA]:
    os.makedirs(dir, exist_ok=True)
