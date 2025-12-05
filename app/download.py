import os
import subprocess
import requests

PREVIEW_MODE = os.getenv("SCRAPER_PREVIEW_MODE", "").lower() == "true"


def download_video(url: str, output_path: str) -> None:
    """
    If PREVIEW_MODE=true, download only the first 60 seconds.
    Otherwise, download the full video.
    """
    if PREVIEW_MODE:
        download_preview(url, output_path)
    else:
        download_full(url, output_path)


def download_preview(url: str, output_path: str, duration: int = 60):
    """
    Stream and save only the first `duration` seconds of the video.
    Works for both MP4 and M3U8.
    """
    print(f"[preview] downloading first {duration}s from {url}")
    cmd = [
        "ffmpeg", "-y",
        "-ss", "0",
        "-i", url,
        "-t", str(duration),
        "-c", "copy",
        output_path
    ]
    subprocess.run(cmd, stdout=subprocess.PIPE,
                   stderr=subprocess.PIPE, check=True)


def download_full(url: str, output_path: str):
    """
    Download entire file to disk.
    """
    print(f"[full] downloading full video from {url}")
    r = requests.get(url, stream=True)
    r.raise_for_status()

    with open(output_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)


def convert_to_mp3(src, dest):
    os.system(f"ffmpeg -i '{src}' -vn -acodec libmp3lame -q:a 4 '{dest}'")
    return dest
