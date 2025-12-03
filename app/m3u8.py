import subprocess
import tempfile
import os


def m3u8_to_wav(m3u8_url: str) -> str:
    """
    Downloads and converts an HLS (.m3u8) stream to a temporary WAV file.
    Returns the path to the WAV file.
    Caller is responsible for deleting the file afterwards.
    """

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    tmp_path = tmp.name
    tmp.close()  # ffmpeg will write to it

    cmd = [
        "ffmpeg",
        "-i", m3u8_url,
        "-vn",
        "-acodec", "pcm_s16le",
        "-ar", "16000",
        "-ac", "1",
        tmp_path,
        "-y"
    ]

    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode != 0:
        os.unlink(tmp_path)
        raise RuntimeError(f"ffmpeg conversion failed: {proc.stderr.decode()}")

    return tmp_path
