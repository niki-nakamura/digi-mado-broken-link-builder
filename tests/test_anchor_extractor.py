from src.anchor_extractor import anchor_matches

def test_anchor_matches():
    assert anchor_matches("これは棲み分けの例", ["棲み分け", "住み分け"])
    assert not anchor_matches("これは別の話", ["棲み分け", "住み分け"])
