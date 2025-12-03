# Michigan Legislature Video Scraper

This service:
- Detects newly published House and Senate hearing videos.
- Downloads recent videos (last 60 days).
- Transcribes audio using OpenAI Whisper or another provider.
- Avoids reprocessing by tracking processed IDs.
- Runs safely on Railway on a periodic schedule.

See source code in `app/` and environment variable definitions in `.env.example`.
