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


def _parse_house_page(url: str, cutoff: datetime):
    """
    Parse a single House archive page and extract video items.
    Returns a list of video items found on that page.
    """
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    items = []
    seen_urls = set()

    # All MP4 links are on the page.
    for vid in soup.select("a[href*='.mp4']"):
        raw_url = vid.get("href")
        url_normalized = _normalize_house_url(raw_url)
        if not url_normalized or url_normalized in seen_urls:
            continue

        # Default to "now" if we can't parse a date.
        date = datetime.utcnow()

        # Heuristic 1: a preceding span.date
        date_tag = vid.find_previous("span", class_="date")

        category = None

        # Heuristic 2: a sibling/parent cell with date-like text
        if not date_tag:
            parent_row = vid.find_parent("tr")
            if parent_row:
                cells = parent_row.find_all(["td", "th"])
                # Look for any cell that might contain a date.
                for cell in cells:
                    text = cell.get_text(strip=True)
                    if any(ch.isdigit() for ch in text):
                        date_tag = cell
                        break
                # Use the first non-empty, non-date cell as a simple "category"
                for cell in cells:
                    text = cell.get_text(strip=True)
                    if text and cell is not date_tag:
                        category = text
                        break

        if date_tag:
            text = date_tag.get_text(strip=True)
            for fmt in ("%m/%d/%Y", "%Y-%m-%d"):
                try:
                    date = datetime.strptime(text, fmt)
                    break
                except ValueError:
                    continue

        # Only include videos within the cutoff window
        if date >= cutoff:
            items.append(
                {
                    "source": "house",
                    "url": url_normalized,
                    "raw_url": raw_url,
                    "category": category,
                    "date": date,
                }
            )
            seen_urls.add(url_normalized)

    return items


def parse_house():
    """
    Scrape the House archive for MP4 video URLs within the last DAYS_BACK days.

    Strategy:
    - The page by default only shows videos from the current year.
    - If DAYS_BACK spans into previous years, we fetch multiple years using
      the &Year=YYYY query parameter.
    - Parse each year's page and combine results.
    - Filter to videos whose date >= cutoff (DAYS_BACK).
    """
    cutoff = _cutoff()
    cutoff_year = cutoff.year
    current_year = datetime.utcnow().year

    # Determine which years we need to fetch
    years_to_fetch = list(range(cutoff_year, current_year + 1))

    all_items = []
    seen_urls = set()

    # Fetch each year's page
    for year in years_to_fetch:
        # Build URL with Year parameter
        if "?" in HOUSE_URL:
            year_url = f"{HOUSE_URL}&Year={year}"
        else:
            year_url = f"{HOUSE_URL}?Year={year}"

        try:
            year_items = _parse_house_page(year_url, cutoff)
            # Deduplicate across years (same video might appear in multiple years)
            for item in year_items:
                if item["url"] not in seen_urls:
                    all_items.append(item)
                    seen_urls.add(item["url"])
        except Exception as e:
            # Log but continue with other years
            print(f"Warning: Failed to fetch year {year}: {e}")

    return all_items

