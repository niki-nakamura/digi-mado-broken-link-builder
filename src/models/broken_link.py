from dataclasses import dataclass

@dataclass
class BrokenLink:
    source_url: str
    serp_rank: int
    anchor_text: str
    target_url: str
    final_url: str
    status_code: int
    redirect_chain: str
    soft404_flag: bool
    evidence: str
