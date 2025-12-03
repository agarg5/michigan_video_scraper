import requests
import os

def download_mp4(url, dest):
    r = requests.get(url, stream=True, timeout=60)
    r.raise_for_status()
    with open(dest, "wb") as f:
        for chunk in r.iter_content(1024*1024):
            f.write(chunk)
    return dest

def convert_to_mp3(src, dest):
    # Use ffmpeg. Railway supports it by default.
    os.system(f"ffmpeg -i '{src}' -vn -acodec libmp3lame -q:a 4 '{dest}'")
    return dest
