from src.link_checker import check_url_status

def test_link_checker_handles_error():
    status, final, chain = check_url_status("https://nonexistent.example.com/404/test")
    assert isinstance(status, int)
