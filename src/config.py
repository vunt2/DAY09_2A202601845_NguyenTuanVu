import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env if present
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=BASE_DIR / ".env")

# Workspace paths
DATA_DIR = BASE_DIR / "data"
INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"
LOGGING_DIR = BASE_DIR / "logging"
TRACE_FILE = BASE_DIR / "trace.jsonl"
METADATA_FILE = BASE_DIR / "metadata.json"

# Model & System Config
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "your_openrouter_api_key_here")
MODEL_NAME = os.getenv("MODEL_NAME", "openai/gpt-4o-mini")
POLICY_VERSION = os.getenv("POLICY_VERSION", "EC_POLICY_V1")

# Model parameter limit enforcement (<= 10B)
MAX_PARAMETER_SIZE = "8B"
FRAMEWORK = "Python Native Multi-Agent Pipeline"

def ensure_directories():
    """Ensure output and logging directories exist."""
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    LOGGING_DIR.mkdir(parents=True, exist_ok=True)

ensure_directories()
