import os
import json
import gspread
from typing import List, Dict

def _client_from_env():
    # Prefer JSON in GCP_SA_KEY; fallback to GOOGLE_APPLICATION_CREDENTIALS
    sa_json = os.getenv("GCP_SA_KEY")
    if sa_json:
        creds_dict = json.loads(sa_json)
        return gspread.service_account_from_dict(creds_dict)
    cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if cred_path and os.path.exists(cred_path):
        return gspread.service_account(filename=cred_path)
    # As a last resort, try default creds (if running in ADC-enabled env)
    return gspread.client.Client(None)

class SheetsClient:
    def __init__(self, sheet_id: str):
        self.gc = _client_from_env()
        self.sheet = self.gc.open_by_key(sheet_id)

    def worksheet(self, title: str):
        try:
            return self.sheet.worksheet(title)
        except gspread.WorksheetNotFound:
            return self.sheet.add_worksheet(title=title, rows=1000, cols=20)

    def read_catalog_row(self, catalog_title: str, row_index: int | None) -> Dict:
        ws = self.worksheet(catalog_title)
        records = ws.get_all_records()
        if row_index is None:
            # find first row with empty "processed_flag"
            for i, r in enumerate(records, start=2):  # header = row 1
                if not r.get("processed_flag"):
                    r["_row"] = i
                    return r
            raise RuntimeError("No unprocessed rows found.")
        else:
            r = records[row_index - 2]
            r["_row"] = row_index
            return r

    def append_rows(self, title: str, rows: List[List]):
        ws = self.worksheet(title)
        if ws.row_count < 2:
            # add header if empty sheet
            pass
        ws.append_rows(rows)

    def update_cell(self, title: str, row: int, col: int, value):
        ws = self.worksheet(title)
        ws.update_cell(row, col, value)
