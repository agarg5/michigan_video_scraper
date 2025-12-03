from app.fetch import parse_house


def summarize(label, items):
    print(f"Found {len(items)} {label} videos")
    if not items:
        return

    dates = sorted(v["date"] for v in items)
    print(f"  Earliest: {dates[0].isoformat()}")
    print(f"  Latest:   {dates[-1].isoformat()}")
    print("  First 10 (source, date, raw_url -> normalized_url):")
    for v in items[:10]:
        raw = v.get("raw_url", v["url"])
        norm = v["url"]
        print(f"   - {v['source']} {v['date'].isoformat()} {raw}  ->  {norm}")


if __name__ == "__main__":
    house_videos = parse_house()

    summarize("House", house_videos)
    print("\nFull House URL list (raw -> normalized):")
    for i, v in enumerate(house_videos, start=1):
        raw = v.get("raw_url", v["url"])
        norm = v["url"]
        print(f"{i:3}: {raw}  ->  {norm}")
