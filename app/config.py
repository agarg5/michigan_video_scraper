import os

HOUSE_URL = "https://house.mi.gov/VideoArchive"
SENATE_URL = "https://cloud.castus.tv/vod/misenate/?page=ALL"

TRANSCRIPTION_MODEL = os.getenv("TRANSCRIPTION_MODEL", "gpt-4o-transcribe")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")
DAYS_BACK = int(os.getenv("DAYS_BACK", "60"))
DATA_DIR = "data"
