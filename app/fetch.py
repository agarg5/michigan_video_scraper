import requests
from bs4 import BeautifulSoup
from datetime import datetime

def parse_house():
    r = requests.get("https://house.mi.gov/VideoArchive", timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    items = []
    for link in soup.select("a[href*='.mp4']"):
        url = link["href"]
        items.append({"source": "house", "url": url, "date": datetime.utcnow()})
    return items

def parse_senate():
    r = requests.get("https://cloud.castus.tv/vod/misenate/?page=ALL", timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    items = []
    for tag in soup.select("a[href*='.mp4']"):
        url = tag["href"]
        items.append({"source": "senate", "url": url, "date": datetime.utcnow()})
    return items
