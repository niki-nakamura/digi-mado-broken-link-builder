from dataclasses import dataclass

@dataclass
class SerpItem:
    rank: int
    url: str
    title: str = ""
    snippet: str = ""
