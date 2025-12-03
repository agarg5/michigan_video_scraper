import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs

from app.config import HOUSE_URL, DAYS_BACK


def _cutoff() -> datetime:
    return datetime.utcnow() - timedelta(days=DAYS_BACK)


def _normalize_house_url(raw: str) -> str:
    """
    Convert whatever link the House site gives us into a direct MP4 URL.

    Common cases:
      - VideoArchivePlayer?video=CORR-030625.mp4
        -> https://www.house.mi.gov/ArchiveVideoFiles/CORR-030625.mp4
      - Already a direct ArchiveVideoFiles URL: returned unchanged.
    """
    if not raw:
        return raw

    # Already a direct archive URL – return as-is.
    if "ArchiveVideoFiles" in raw and raw.lower().endswith(".mp4"):
        return raw

    parsed = urlparse(raw)
    q = parse_qs(parsed.query)
    video_param = q.get("video", [None])[0]

    if video_param and video_param.lower().endswith(".mp4"):
        return f"https://www.house.mi.gov/ArchiveVideoFiles/{video_param}"

    # Fallback: if it looks like an mp4 filename in the path itself.
    if parsed.path.lower().endswith(".mp4"):
        filename = parsed.path.rsplit("/", 1)[-1]
        return f"https://www.house.mi.gov/ArchiveVideoFiles/{filename}"

    # As a last resort just return the original; downloader may still handle it.
    return raw


def parse_house():
    """
    Scrape the House archive for MP4 video URLs within the last DAYS_BACK days.

    Strategy (based on current site behavior):
    - Load the main archive page (HOUSE_URL).
    - All videos are listed directly in this page's HTML.
    - Find <a href="...mp4"> links.
    - Try to find a nearby date (e.g., in the same row or a preceding
      <span class="date"> element).
    - Filter to videos whose date >= cutoff (DAYS_BACK).
    """
    r = requests.get(HOUSE_URL, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    cutoff = _cutoff()
    items = []
    seen_urls = set()

    # All MP4 links are on the main page.
    for vid in soup.select("a[href*='.mp4']"):
        raw_url = vid.get("href")
        url = _normalize_house_url(raw_url)
        if not url or url in seen_urls:
            continue

        # Default to "now" if we can't parse a date.
        date = datetime.utcnow()

        # Heuristic 1: a preceding span.date
        date_tag = vid.find_previous("span", class_="date")

        # Heuristic 2: a sibling/parent cell with date-like text
        if not date_tag:
            parent_row = vid.find_parent("tr")
            if parent_row:
                # Look for any cell that might contain a date.
                for cell in parent_row.find_all(["td", "th"]):
                    text = cell.get_text(strip=True)
                    if any(ch.isdigit() for ch in text):
                        date_tag = cell
                        break

        if date_tag:
            text = date_tag.get_text(strip=True)
            for fmt in ("%m/%d/%Y", "%Y-%m-%d"):
                try:
                    date = datetime.strptime(text, fmt)
                    break
                except ValueError:
                    continue

        if date >= cutoff:
            items.append({"source": "house", "url": url, "date": date})
            seen_urls.add(url)

    return items
