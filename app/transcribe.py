import openai

from app.config import OPENAI_API_KEY


client = openai.OpenAI(api_key=OPENAI_API_KEY)


def transcribe(audio_path: str) -> str:
    with open(audio_path, "rb") as f:
        resp = client.audio.transcriptions.create(
            model="whisper-1",
            file=f,
        )
    return resp.text
