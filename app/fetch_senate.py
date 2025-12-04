import requests
from datetime import datetime, timedelta, timezone
from dateutil import parser as date_parser

from app.config import SENATE_URL, DAYS_BACK


def _cutoff() -> datetime:
    # Return timezone-aware UTC datetime to match parsed dates
    return datetime.now(timezone.utc) - timedelta(days=DAYS_BACK)


def _construct_senate_video_url(video_id: str) -> str:
    """
    Construct the video URL from the video _id.
    Uses CloudFront HLS format: https://dlttx48mxf9m3.cloudfront.net/outputs/{id}/Default/HLS/out.m3u8
    """
    return f"https://dlttx48mxf9m3.cloudfront.net/outputs/{video_id}/Default/HLS/out.m3u8"


def _parse_senate_response(data, cutoff: datetime):
    """
    Parse the Senate API response and extract video items.
    The API returns an array of video objects with _id, date, metadata, etc.
    """
    items = []
    seen_urls = set()

    # The API returns an array directly
    if not isinstance(data, list):
        return items

    for item in data:
        # Extract video ID
        video_id = item.get("_id")
        if not video_id:
            continue

        # Try to get URL from item, or construct it from _id
        url = (
            item.get("url")
            or item.get("video_url")
            or item.get("mp4_url")
            or item.get("videoUrl")
            or _construct_senate_video_url(video_id)
        )

        if url in seen_urls:
            continue

        # Extract date - use original_date if available, otherwise date
        date = datetime.utcnow()  # Default
        date_str = item.get("original_date") or item.get("date")
        if date_str:
            try:
                # dateutil.parser.parse handles ISO format with Z, milliseconds, etc. automatically
                date = date_parser.parse(date_str)
            except (ValueError, TypeError, AttributeError):
                # If parsing fails, keep default (utcnow)
                pass

        # Extract category/name from metadata.filename
        metadata = item.get("metadata", {})
        category = metadata.get("filename") if isinstance(
            metadata, dict) else None
        if not category:
            category = item.get("category") or item.get(
                "committee") or item.get("title")

        # Only include videos within the cutoff window
        if date >= cutoff:
            items.append(
                {
                    "source": "senate",
                    "url": url,
                    "raw_url": url,
                    "category": category,
                    "date": date,
                }
            )
            seen_urls.add(url)

    return items


def parse_senate():
    """
    Fetch Senate video URLs from the API within the last DAYS_BACK days.

    Strategy:
    - Fetch from the Senate API endpoint
    - Parse JSON response
    - Filter to videos whose date >= cutoff (DAYS_BACK)
    """
    cutoff = _cutoff()

    try:
        r = requests.get(SENATE_URL, timeout=30)
        r.raise_for_status()
        data = r.json()

        items = _parse_senate_response(data, cutoff)
        return items

    except Exception as e:
        print(f"Warning: Failed to fetch Senate videos: {e}")
        return []
