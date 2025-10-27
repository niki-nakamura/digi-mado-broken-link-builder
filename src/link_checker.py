import requests

def check_url_status(url: str, user_agent: str | None = None, timeout: int = 8):
    headers = {"User-Agent": user_agent or "digi-mado-broken-link-builder/0.1"}
    history = []
    try:
        r = requests.head(url, headers=headers, timeout=timeout, allow_redirects=True)
        final = r
        for h in r.history:
            history.append(f"{h.status_code}:{h.url}")
        # Some servers don't support HEAD -> fallback to GET if 405/403/400 etc.
        if r.status_code >= 400 and r.status_code not in (404, 410):
            g = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
            final = g
            for h in g.history:
                history.append(f"{h.status_code}:{h.url}")
        return final.status_code, final.url, " -> ".join(history)
    except Exception as e:
        return -1, url, f"error:{e}"
