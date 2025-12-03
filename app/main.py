import os
from datetime import datetime, timedelta
from app.fetch import parse_house, parse_senate
from app.storage import load_processed, save_processed
from app.download import download_mp4, convert_to_mp3
from app.transcribe import transcribe
from app.config import DATA_DIR, DAYS_BACK

def run():
    processed = load_processed()
    os.makedirs(DATA_DIR, exist_ok=True)

    items = parse_house() + parse_senate()
    cutoff = datetime.utcnow() - timedelta(days=DAYS_BACK)

    for item in items:
        video_id = item["url"]
        if video_id in processed:
            continue

        # If upstream pages ever expose real timestamps, compare to cutoff.
        mp4_path = os.path.join(DATA_DIR, f"{hash(video_id)}.mp4")
        mp3_path = mp4_path.replace(".mp4", ".mp3")
        txt_path = mp4_path.replace(".mp4", ".txt")

        try:
            download_mp4(item["url"], mp4_path)
            convert_to_mp3(mp4_path, mp3_path)
            text = transcribe(mp3_path)
            with open(txt_path, "w") as f:
                f.write(text)

            processed.add(video_id)
            save_processed(processed)

        except Exception as e:
            print("Error:", e)
            continue

if __name__ == "__main__":
    run()
