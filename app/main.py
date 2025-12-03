import os
from hashlib import sha256
from datetime import datetime, timedelta
from app.fetch import parse_house, parse_senate
from app.transcribe import transcribe
from app.download import download_mp4, convert_to_mp3
from app.db import SessionLocal, Video, init_db
from app.config import DAYS_BACK, DATA_DIR


def run():
    init_db()
    os.makedirs(DATA_DIR, exist_ok=True)

    items = parse_house() + parse_senate()
    cutoff = datetime.utcnow() - timedelta(days=DAYS_BACK)

    db = SessionLocal()

    for item in items:
        video_id = sha256(item["url"].encode()).hexdigest()

        existing = db.query(Video).filter_by(id=video_id).first()
        if existing:
            continue

        mp4_path = os.path.join(DATA_DIR, f"{video_id}.mp4")
        mp3_path = os.path.join(DATA_DIR, f"{video_id}.mp3")

        try:
            download_mp4(item["url"], mp4_path)
            convert_to_mp3(mp4_path, mp3_path)
            text = transcribe(mp3_path)

            v = Video(
                id=video_id,
                source=item["source"],
                url=item["url"],
                date=item["date"],
                transcript=text,
                processed_at=datetime.utcnow(),
            )
            db.add(v)
            db.commit()

        except Exception as e:
            print("Error:", e)
            db.rollback()

    db.close()


if __name__ == "__main__":
    run()
