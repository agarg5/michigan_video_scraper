import openai
from app.config import OPENAI_API_KEY, TRANSCRIPTION_MODEL
import subprocess
import os

openai.api_key = OPENAI_API_KEY

def transcribe(audio_path):
    # For large videos, we assume conversion to WAV or MP3 is performed before this call.
    with open(audio_path, "rb") as f:
        result = openai.audio.transcriptions.create(
            file=f,
            model=TRANSCRIPTION_MODEL
        )
    return result.text
