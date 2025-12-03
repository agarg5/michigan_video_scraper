# app/test_single_video.py

import os
from hashlib import sha256
from datetime import datetime
from app.download import download_mp4, convert_to_mp3
from app.transcribe import transcribe
from app.db import SessionLocal, Video, init_db
from app.config import DATA_DIR

# Hardcoded test video
TEST_VIDEO_URL = "https://house.mi.gov/VideoArchivePlayer?video=CORR-030625.mp4"
SOURCE = "house"


def run_test():
    os.makedirs(DATA_DIR, exist_ok=True)
    init_db()

    video_id = sha256(TEST_VIDEO_URL.encode()).hexdigest()
    mp4_path = os.path.join(DATA_DIR, f"{video_id}.mp4")
    mp3_path = os.path.join(DATA_DIR, f"{video_id}.mp3")

    # Download video
    print(f"Downloading {TEST_VIDEO_URL} …")
    download_mp4(TEST_VIDEO_URL, mp4_path)

    # Convert to MP3
    print("Converting to MP3 …")
    convert_to_mp3(mp4_path, mp3_path)

    # Transcribe
    print("Transcribing …")
    transcript_text = transcribe(mp3_path)
    print("Transcript snippet:", transcript_text[:200], "...")

    # Save to DB
    db = SessionLocal()
    video = Video(
        id=video_id,
        source=SOURCE,
        url=TEST_VIDEO_URL,
        date=datetime.utcnow(),
        transcript=transcript_text,
        processed_at=datetime.utcnow(),
    )
    db.add(video)
    db.commit()
    db.close()
    print("Saved to database. Test complete!")


if __name__ == "__main__":
    run_test()
