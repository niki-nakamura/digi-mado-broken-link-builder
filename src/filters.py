import re
from pathlib import Path
from typing import Iterable

def _read_lines(p: Path) -> list[str]:
    if not p.exists():
        return []
    return [x.strip() for x in p.read_text(encoding="utf-8").splitlines() if x.strip() and not x.startswith("#")]

class FilterSuite:
    def __init__(self, base_dir: str = "config/filters"):
        base = Path(base_dir)
        self.competitor_roots = set(_read_lines(base / "competitor_roots.txt"))
        self.competitor_hosts = set(_read_lines(base / "competitor_hosts.txt"))
        self.skip_terms = set(_read_lines(base / "skip_terms_ja.txt"))
        self.soft404_signals = _read_lines(base / "soft404_signals_ja.txt")
        self.allowed_tlds = set(_read_lines(base / "allowed_tlds.txt"))
        patterns = _read_lines(base / "skip_url_patterns.regex")
        self.skip_url_regex = re.compile("|".join(patterns)) if patterns else None

    def build_exclude_site_query(self) -> str:
        # returns like: -site:a.com -site:b.jp ...
        parts = [f"-site:{d}" for d in sorted(self.competitor_roots)]
        return " ".join(parts)

    def is_url_excluded(self, url: str) -> bool:
        if self.skip_url_regex and self.skip_url_regex.search(url or ""):
            return True
        for host in self.competitor_hosts:
            if host and host in (url or ""):
                return True
        return False

    def contains_skip_terms(self, text: str) -> bool:
        t = (text or "").lower()
        return any(s.lower() in t for s in self.skip_terms)

    def detect_soft404(self, html_text: str) -> tuple[bool, str]:
        t = (html_text or "").lower()
        for s in self.soft404_signals:
            if s.lower() in t:
                return True, s
        return False, ""
