# Simple dry-run: read first catalog row, build query, print only (no API call)
import os
from src.sheets_client import SheetsClient
from src.filters import FilterSuite
from src.main import build_query

SHEET_ID = os.getenv("SHEET_ID")
CATALOG = os.getenv("SHEET_CATALOG", "カタログ")

sc = SheetsClient(SHEET_ID)
row = sc.read_catalog_row(CATALOG, None)
fs = FilterSuite()
q = build_query(row.get("queries_top10_pipe",""), fs)
print("row:", row.get("_row"), "query:", q)
