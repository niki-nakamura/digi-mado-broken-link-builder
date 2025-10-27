import requests
from bs4 import BeautifulSoup
from typing import Iterable, List
from .utils.normalizer import normalize_text

def fetch(url: str, user_agent: str | None = None, timeout: int = 10) -> str:
    headers = {"User-Agent": user_agent or "digi-mado-broken-link-builder/0.1"}
    r = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
    r.raise_for_status()
    return r.text

def extract_anchors(html: str) -> List[tuple[str, str, str]]:
    soup = BeautifulSoup(html, "lxml")
    out = []
    for a in soup.select("a[href]"):
        href = a.get("href", "")
        text = (a.get_text(strip=True) or "")[:200]
        rel = (a.get("rel") or [])
        rel = " ".join(rel) if isinstance(rel, list) else str(rel)
        out.append((text, href, rel))
    return out

def anchor_matches(text: str, keywords: Iterable[str]) -> bool:
    t = normalize_text(text)
    for kw in keywords:
        if normalize_text(kw) in t:
            return True
    return False
