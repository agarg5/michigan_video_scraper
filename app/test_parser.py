from app.fetch import parse_house


def summarize(label, items):
    print(f"Found {len(items)} {label} videos")
    if not items:
        return

    dates = sorted(v["date"] for v in items)
    print(f"  Earliest: {dates[0].isoformat()}")
    print(f"  Latest:   {dates[-1].isoformat()}")
    print("  Sample:")
    for v in items[:10]:
        print(f"   - {v['source']} {v['date'].isoformat()} {v['url']}")


if __name__ == "__main__":
    house_videos = parse_house()

    summarize("House", house_videos)
