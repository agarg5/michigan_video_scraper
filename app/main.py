# app/main.py
import os
from hashlib import sha256
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor

from app.fetch import parse_house
from app.transcribe import transcribe
from app.download import download_mp4, convert_to_mp3
from app.db import SessionLocal, Video, init_db
from app.config import DAYS_BACK, DATA_DIR

FAILED_LOG = os.path.join(DATA_DIR, "failed_videos.csv")
MAX_WORKERS = 4  # adjust based on system/API limits

os.makedirs(DATA_DIR, exist_ok=True)


def log_failure(video_url, error):
    """Append a failed video to CSV for persistence."""
    with open(FAILED_LOG, "a") as f:
        f.write(f"{datetime.utcnow().isoformat()},{video_url},{error}\n")


def process_video(item):
    """Download, convert, transcribe, store; retry once if fails."""
    video_id = sha256(item["url"].encode()).hexdigest()
    mp4_path = os.path.join(DATA_DIR, f"{video_id}.mp4")
    mp3_path = os.path.join(DATA_DIR, f"{video_id}.mp3")
    db = SessionLocal()

    try_count = 0
    while try_count < 2:
        try_count += 1
        try:
            # Skip if already processed
            existing = db.query(Video).filter_by(id=video_id).first()
            if existing:
                return

            # Human-readable name including category and date, e.g.
            # "Judiciary Committee (House 2025-03-06)"
            date = item["date"]
            date_str = date.strftime("%Y-%m-%d")
            category = item.get("category")
            base_label = f"{item['source'].capitalize()} {date_str}"
            name = f"{category} ({base_label})" if category else base_label

            download_mp4(item["url"], mp4_path)
            convert_to_mp3(mp4_path, mp3_path)
            text = transcribe(mp3_path)

            v = Video(
                id=video_id,
                name=name,
                source=item["source"],
                url=item["url"],
                date=date,
                transcript=text,
                processed_at=datetime.utcnow(),
            )
            db.add(v)
            db.commit()

            # Cleanup temp files
            os.remove(mp4_path)
            os.remove(mp3_path)
            return  # success

        except Exception as e:
            db.rollback()
            if try_count >= 2:
                print(f"Failed permanently: {item['url']} - {e}")
                log_failure(item["url"], str(e))
            else:
                print(f"Retrying {item['url']} due to error: {e}")

    db.close()


def run():
    init_db()
    items = parse_house()
    cutoff = datetime.utcnow() - timedelta(days=DAYS_BACK)

    # Filter old videos
    items = [i for i in items if i["date"] >= cutoff]

    # Parallel processing
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        executor.map(process_video, items)


if __name__ == "__main__":
    run()
