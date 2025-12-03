import os
from pathlib import Path
from dotenv import load_dotenv

# Load project-level environment variables from .env at repo root
PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

HOUSE_URL = "https://house.mi.gov/VideoArchive"
SENATE_URL = "https://2kbyogxrg4.execute-api.us-west-2.amazonaws.com/61b3adc8124d7d000891ca5c/home/recent"

TRANSCRIPTION_MODEL = os.getenv("TRANSCRIPTION_MODEL", "gpt-4o-transcribe")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")
DAYS_BACK = int(os.getenv("DAYS_BACK", "60"))
DATA_DIR = "data"
