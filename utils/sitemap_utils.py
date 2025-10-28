import requests

def get_sitemap_urls(start_url):
    guess = start_url.rstrip("/") + "/sitemap.xml"
    urls = set()

    try:
        r = requests.get(guess, timeout=10)
        if r.status_code == 200:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(r.text, "xml")
            locs = soup.find_all("loc")
            urls = set([l.get_text(strip=True) for l in locs])
    except:
        pass
    return urls
