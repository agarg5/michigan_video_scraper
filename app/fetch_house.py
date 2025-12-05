import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse, parse_qs

from app.config import HOUSE_URL, DAYS_BACK


def _cutoff() -> datetime:
    return datetime.now(timezone.utc) - timedelta(days=DAYS_BACK)


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

        date_tag = vid

        category = raw_url[-16:-11]

        if date_tag:
            text = date_tag.next.strip()  # example 'Thursday, February 20, 2025'
            fmt = "%A, %B %d, %Y"
            try:
                # Parse as naive datetime, then make it timezone-aware (UTC)
                date = datetime.strptime(
                    text, fmt).replace(tzinfo=timezone.utc)
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
