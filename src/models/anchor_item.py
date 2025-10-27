from dataclasses import dataclass

@dataclass
class AnchorItem:
    source_url: str
    serp_rank: int
    anchor_text: str
    href: str
    rel: str = ""
    context_excerpt: str = ""
    match_keyword: str = ""
    match_score: float = 0.0
