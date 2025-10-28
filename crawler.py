import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque
import time

# -------------------------------------------------------------------
# ✅ Global Session w/ Browser Headers
# -------------------------------------------------------------------
session = requests.Session()
session.headers.update({
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/121.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Connection": "keep-alive"
})


def safe_request(url, timeout=10):
    """
    Safely perform GET request with retry fallback
    """
    try:
        r = session.get(url, timeout=timeout)
        if r.status_code == 403:
            # Retry with different UA
            alt_headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/119.0.0.0 Safari/537.36"
                )
            }
            r = session.get(url, timeout=timeout, headers=alt_headers)
        return r
    except:
        return None


def crawl_site(start_url, max_pages=500, delay=0.3):
    """
    Crawl site using BFS, track depth, store HTML + soup
    """
    allowed_domain = urlparse(start_url).netloc
    visited = {}
    queue = deque([(start_url, 0)])   # (url, depth)

    while queue and len(visited) < max_pages:
        url, depth = queue.popleft()

        if url in visited:
            continue

        # Delay to avoid blocking
        time.sleep(delay)

        try:
            start_t = time.time()
            r = safe_request(url)

            if not r:
                visited[url] = {
                    "status": "error",
                    "load_time": None,
                    "html": "",
                    "soup": None,
                    "depth": depth
                }
                continue

            load_time = round(time.time() - start_t, 3)
            status = r.status_code

            soup = None
            if status == 200:
                soup = BeautifulSoup(r.text, "html.parser")

            visited[url] = {
                "status": status,
                "load_time": load_time,
                "html": r.text,
                "soup": soup,
                "depth": depth
            }

            # If 403 & no soup → skip link parsing
            if not soup:
                continue

            # Link discovery
            for a in soup.find_all("a", href=True):
                href = urljoin(url, a["href"])
                if urlparse(href).netloc == allowed_domain:
                    if href not in visited:
                        queue.append((href, depth + 1))

        except Exception as e:
            visited[url] = {
                "status": "error",
                "load_time": None,
                "html": "",
                "soup": None,
                "depth": depth
            }

    return visited
