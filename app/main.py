# app/main.py
import os
from hashlib import sha256
from datetime import datetime, timedelta, timezone
from concurrent.futures import ThreadPoolExecutor

from app.fetch_house import parse_house
from app.fetch_senate import parse_senate
from app.transcribe import transcribe
from app.download import download_mp4, convert_to_mp3
from app.m3u8 import m3u8_to_wav
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

            # Handle m3u8 files (Senate) vs mp4 files (House)
            is_m3u8 = item["url"].endswith(".m3u8")

            if is_m3u8:
                # Convert m3u8 to wav, then transcribe
                wav_path = m3u8_to_wav(item["url"])
                try:
                    text = transcribe(wav_path)
                finally:
                    # Cleanup wav file
                    if os.path.exists(wav_path):
                        os.remove(wav_path)
            else:
                # Download mp4, convert to mp3, then transcribe
                mp4_path = os.path.join(DATA_DIR, f"{video_id}.mp4")
                mp3_path = os.path.join(DATA_DIR, f"{video_id}.mp3")
                try:
                    download_mp4(item["url"], mp4_path)
                    convert_to_mp3(mp4_path, mp3_path)
                    text = transcribe(mp3_path)
                finally:
                    # Cleanup temp files
                    if os.path.exists(mp4_path):
                        os.remove(mp4_path)
                    if os.path.exists(mp3_path):
                        os.remove(mp3_path)

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
    cutoff = datetime.now(timezone.utc) - timedelta(days=DAYS_BACK)

    # Fetch videos from both House and Senate
    house_items = parse_house()
    senate_items = parse_senate()

    # Combine and filter old videos
    all_items = house_items + senate_items
    items = [i for i in all_items if i["date"] >= cutoff]

    # Parallel processing
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        executor.map(process_video, items)


if __name__ == "__main__":
    run()
