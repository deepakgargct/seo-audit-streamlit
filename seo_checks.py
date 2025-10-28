from bs4 import BeautifulSoup
from collections import Counter
import textstat

def extract_title(soup):
    if not soup: return "", 0
    title = soup.title.string.strip() if soup.title else ""
    return title, len(title)

def extract_meta_description(soup):
    if not soup: return "", 0
    md = (soup.find("meta", {"name": "description"}) or {}).get("content", "")
    return md, len(md)

def extract_canonical(soup):
    if not soup: return ""
    return (soup.find("link", {"rel": "canonical"}) or {}).get("href", "")

def extract_robots_meta(soup):
    if not soup: return ""
    return (soup.find("meta", {"name": "robots"}) or {}).get("content", "")

def extract_headings(soup):
    headings = {}
    for i in range(1,7):
        tags = soup.find_all(f"h{i}")
        headings[f"h{i}"] = [t.get_text(strip=True) for t in tags]
    issues = []
    if len(headings["h1"]) != 1:
        issues.append("Invalid H1 count")
    return headings, issues

def extract_word_count(soup):
    if not soup: return 0
    text = soup.get_text(" ", strip=True)
    return len(text.split())

def extract_images_missing_alt(soup):
    if not soup: return 0
    imgs = soup.find_all("img")
    no_alt = len([i for i in imgs if not i.get("alt")])
    return no_alt

def extract_structured_data(soup):
    return len(soup.find_all("script", {"type":"application/ld+json"}))

def get_keywords(soup, top_n=10):
    text = soup.get_text(" ", strip=True)
    words = [w.lower() for w in text.split()]
    counts = Counter(words)
    return dict(counts.most_common(top_n))

def readability_score(soup):
    text = soup.get_text(" ", strip=True)
    try:
        return textstat.flesch_reading_ease(text)
    except:
        return None
