import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque
import time

def crawl_site(start_url, max_pages=500):
    allowed_domain = urlparse(start_url).netloc
    visited = {}
    queue = deque([(start_url, 0)])   # (url, depth)

    while queue and len(visited) < max_pages:
        url, depth = queue.popleft()
        if url in visited:
            continue

        try:
            start_t = time.time()
            r = requests.get(url, timeout=10)
            load_time = round(time.time() - start_t, 3)
            soup = BeautifulSoup(r.text, "html.parser")

            visited[url] = {
                "status": r.status_code,
                "load_time": load_time,
                "html": r.text,
                "soup": soup,
                "depth": depth
            }

            for a in soup.find_all("a", href=True):
                href = urljoin(url, a["href"])
                if urlparse(href).netloc == allowed_domain:
                    if href not in visited:
                        queue.append((href, depth + 1))

        except:
            visited[url] = {
                "status": "error",
                "load_time": None,
                "html": "",
                "soup": None,
                "depth": depth
            }

    return visited
