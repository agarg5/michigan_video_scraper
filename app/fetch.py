import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

def parse_house():
    r = requests.get("https://house.mi.gov/VideoArchive", timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    items = []
    for link in soup.select("a[href*='.mp4']"):
        url = link["href"]
        date = datetime.today()
        items.append({"source": "house", "url": url, "date": date.isoformat()})
    return items

def parse_senate():
    r = requests.get("https://cloud.castus.tv/vod/misenate/?page=ALL", timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    items = []
    for tag in soup.select("a[href*='.mp4']"):
        url = tag["href"]
        date = datetime.today()
        items.append({"source": "senate", "url": url, "date": date.isoformat()})
    return items
