import tldextract
from urllib.parse import urlparse
import logging # (もし import logging が既にあれば不要)
import os
import argparse
from typing import List
from .utils.logging_setup import setup_logging
from .sheets_client import SheetsClient
from .cse_client import CSEClient
from .filters import FilterSuite
from .anchor_extractor import fetch, extract_anchors, anchor_matches
from .link_checker import check_url_status
from .models.serp_item import SerpItem

def build_query(q_pipe: str, filters: FilterSuite) -> str:
    # 代表語は最初の語、残りは orTerms 的にクエリへ足す。競合除外とURLパターン除外を q へ直接織り込む
    parts = [x.strip() for x in (q_pipe or "").split("|") if x.strip()]
    if not parts:
        return ""
    head = parts[0]
    ors = [p for p in parts[1:] if p != head]
    exclude_sites = filters.build_exclude_site_query()
    # 除外URLパターンは inurl:- を多用すると複雑になるので、まずは結果フィルタで落とす方針
    q = f"{head} ({' OR '.join(ors)}) {exclude_sites} -filetype:pdf -inurl:contact -inurl:news -inurl:press -inurl:pr -inurl:ir -inurl:recruit -inurl:company -inurl:privacy -inurl:terms"
    return q.strip()

def main():
    log = setup_logging()
    log.info("Loading exclusion lists...")
    excluded_domains = set()
    try:
        # competitor_roots.txt の読み込み
        with open("config/filters/competitor_roots.txt", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                # コメント行と空行をスキップ
                if not line or line.startswith("#"):
                    continue
                if domain := line.lstrip('.'):
                    excluded_domains.add(domain)
        
        # competitor_hosts.txt の読み込み
        with open("config/filters/competitor_hosts.txt", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if domain := line.lstrip('.'):
                    excluded_domains.add(domain)
                    
    except FileNotFoundError as e:
        log.warning(f"Could not load filter file: {e}")

    # 自社ドメインもリストに強制追加
    excluded_domains.add("digi-mado.jp")

    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog-row", type=int, default=None, help="1-indexed row in カタログ. If omitted, auto-pick first unprocessed row.")
    args = parser.parse_args()

    sheet_id = os.getenv("SHEET_ID")
    catalog_title = os.getenv("SHEET_CATALOG", "カタログ")
    api_key = os.getenv("CSE_API_KEY")
    cx = os.getenv("CSE_CX")
    ua = os.getenv("USER_AGENT", "digi-mado-broken-link-builder/0.1")

    filters = FilterSuite()
    sc = SheetsClient(sheet_id)
    row = sc.read_catalog_row(catalog_title, args.catalog_row)

    q_pipe = row.get("queries_top10_pipe") or ""
    query = build_query(q_pipe, filters)
    log.info(f"catalog row={row.get('_row')} query={query}")

    cse = CSEClient(api_key, cx)
    
    all_items = []
    total_api_calls = 0
    
    # 3ページ分(1-10, 11-20, 21-30)ループ
    for page in range(3):
        start_index = page * 10 + 1
        try:
            log.info(f"Fetching SERP page {page+1} (start={start_index})...")
            # API call
            resp = cse.search_once(query, lr="lang_ja", num=10, start=start_index) 
            total_api_calls += 1
            
            items_page = resp.get("items", []) or []
            if not items_page:
                log.info(f"No more results found at page {page+1}.")
                break # 30件未満で結果が尽きたら終了
            
            all_items.extend(items_page)
            
        except Exception as e:
            log.error(f"Error fetching SERP page {page+1}: {e}")
            # 1ページでも失敗したら中断
            break

    # --- ▼▼▼ ここから (検索結果の事後フィルタ - 変更なし) ▼▼▼ ---
    filtered_items = []
    # 'all_items' をフィルタリングするように変更 (元の 'items' ではない)
    for item in all_items: 
        url = item.get("link")
        if not url:
            continue

        # .registered_domain は 'note.com' や 'yahoo.co.jp' を返す
        registered_domain = tldextract.extract(url).registered_domain
        # .hostname は 'detail.chiebukuro.yahoo.co.jp' を返す
        hostname = urlparse(url).hostname

        if registered_domain in excluded_domains:
            log.info(f"[POST-FILTER] Excluding {url} (matched root: {registered_domain})")
            continue

        if hostname in excluded_domains:
            log.info(f"[POST-FILTER] Excluding {url} (matched host: {hostname})")
            continue
            
        filtered_items.append(item)
    
    # フィルタ済みのリストで 'items' を上書きする (変更)
    items = filtered_items 
    # --- ▲▲▲ ここまで (検索結果の事後フィルタ) ▲▲▲ ---

    serp_rows = []
    extract_rows = []
    broken_rows = []

    kw_all = [x.strip() for x in q_pipe.split("|") if x.strip()]

    rank = 0
    for it in items:
        rank += 1
        url = it.get("link")
        title = it.get("title", "")
        snippet = it.get("snippet", "")

        if filters.is_url_excluded(url):
            continue

        serp_rows.append([row.get("_row"), q_pipe, query, rank, url, title, snippet, "", ""])

        # Fetch & anchor extract
        try:
            html = fetch(url, ua)
            for text, href, rel in extract_anchors(html):
                if not href or href.startswith(("mailto:", "tel:", "javascript:", "#")):
                    continue
                if not anchor_matches(text, kw_all):
                    continue
                status, final_url, chain = check_url_status(href, ua)
                soft_flag, evidence = filters.detect_soft404(html if status == 200 else "")
                extract_rows.append([url, rank, text, href, "", rel, "", "", "", ""])

                if status in (404, 410) or soft_flag:
                    broken_rows.append([url, rank, text, href, final_url, status, chain, soft_flag, evidence])
        except Exception as e:
            serp_rows.append([row.get("_row"), q_pipe, query, rank, url, title, snippet, "fetch_error", str(e)])

    # Write to Sheets
    # sc.append_rows("SERP_Candidates", [["run_id","catalog_row","query_raw","search_q","rank","url","title","snippet","excluded_by","notes"]])  <-- この行を削除 (または # でコメントアウト)
    for r in serp_rows:
        sc.append_rows("SERP_Candidates", [r])

    # sc.append_rows("Anchors_Extracted", [["run_id","source_url","serp_rank","anchor_text","href","href_domain","rel","context_excerpt","match_keyword","match_score","created_utc"]])  <-- この行を削除
    for r in extract_rows:
        sc.append_rows("Anchors_Extracted", [["", *r, "", "", "", ""]])

    # sc.append_rows("Suspected_404s", [["run_id","source_url","serp_rank","anchor_text","target_url","final_url","status_code","redirect_chain","soft404_flag","evidence","discovered_utc"]])  <-- この行を削除
    for r in broken_rows:
        sc.append_rows("Suspected_404s", [["", *r, ""]])

    log.info(f"API calls={total_api_calls} SERP rows={len(serp_rows)} anchors={len(extract_rows)} broken={len(broken_rows)}")

if __name__ == "__main__":
    main()
