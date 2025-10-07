import os
from pathlib import Path


# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

# Log directory (allow override via LOG_DIR env, e.g., tests)
LOG_DIR = Path(os.environ.get('LOG_DIR', BASE_DIR / 'logs'))
