import openai
from app.config import OPENAI_API_KEY, TRANSCRIPTION_MODEL

openai.api_key = OPENAI_API_KEY

def transcribe(audio_path):
    with open(audio_path, "rb") as f:
        result = openai.audio.transcriptions.create(
            file=f,
            model=TRANSCRIPTION_MODEL
        )
    return result.text
