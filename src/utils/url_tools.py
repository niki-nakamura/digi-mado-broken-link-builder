import tldextract

def domain(url: str) -> str:
    ext = tldextract.extract(url or "")
    if not ext.domain:
        return ""
    root = f"{ext.domain}.{ext.suffix}" if ext.suffix else ext.domain
    return root
