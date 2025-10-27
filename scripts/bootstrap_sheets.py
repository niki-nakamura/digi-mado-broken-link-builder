import os
from src.sheets_client import SheetsClient

SHEET_ID = os.getenv("SHEET_ID")
CATALOG = os.getenv("SHEET_CATALOG", "カタログ")

def main():
    sc = SheetsClient(SHEET_ID)
    for title in ["SERP_Candidates", "Anchors_Extracted", "Suspected_404s", "Run_Log"]:
        sc.worksheet(title)  # create if not exists
    print("Worksheets ensured.")

if __name__ == "__main__":
    main()
