from googleapiclient.discovery import build
from typing import List, Dict

class CSEClient:
    def __init__(self, api_key: str, cx: str):
        self.api_key = api_key
        self.cx = cx
        self.service = build("customsearch", "v1", developerKey=api_key, cache_discovery=False)

    def search_once(self, q: str, **kwargs) -> Dict:
        # A single API call per run
        kwargs.setdefault("num", 10)
        return self.service.cse().list(q=q, cx=self.cx, **kwargs).execute()
