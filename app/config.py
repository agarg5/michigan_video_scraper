import os

HOUSE_URL = "https://house.mi.gov/VideoArchive"
SENATE_URL = "https://cloud.castus.tv/vod/misenate/?page=ALL"
DATA_DIR = "data"
PROCESSED_FILE = os.path.join(DATA_DIR, "processed.json")

TRANSCRIPTION_MODEL = os.getenv("TRANSCRIPTION_MODEL", "gpt-4o-transcribe")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DAYS_BACK = int(os.getenv("DAYS_BACK", "60"))
