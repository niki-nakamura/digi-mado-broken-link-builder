import unicodedata
import re

def normalize_text(s: str) -> str:
    if s is None:
        return ""
    # NFKCで全角→半角・互換分解、余計な空白折りたたみ、小文字化
    s = unicodedata.normalize("NFKC", s)
    s = re.sub(r"\s+", " ", s).strip().lower()
    return s
