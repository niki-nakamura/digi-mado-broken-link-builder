from src.filters import FilterSuite

def test_build_exclude_query():
    fs = FilterSuite()
    q = fs.build_exclude_site_query()
    assert "-site:" in q
