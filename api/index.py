import sys
from pathlib import Path

# Add project root to Python module path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

# Import your Flask app instance
from app import app