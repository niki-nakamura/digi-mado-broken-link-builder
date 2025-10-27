# digi-mado-broken-link-builder

Google スプレッドシート「🌐v2.0」の **カタログ** シートの `queries_top10_pipe` を1回の実行につき **1クエリのみ**処理し、
Programmable Search Engine（Custom Search JSON API）で候補URLを収集 → アンカー抽出 → 404/410/ソフト404検知 →
同スプレッドシートの新規シートへ書き込みます。

> 1 run = 1 query（無料枠温存）。GitHub Actions の UI から `Run workflow` で手動実行します。

## 必要な Secrets / Env
- `GCP_SA_KEY`：サービスアカウントJSON（`id-867@sc-api-project.iam.gserviceaccount.com` を編集者登録済みのもの）
- `CSE_API_KEY`：Custom Search JSON API の API キー
- `CSE_CX`：Programmable Search Engine の Search engine ID
- `SHEET_ID`：対象スプレッドシートのID（🌐v2.0）
- 任意：`USER_AGENT`、`LOG_LEVEL`（INFO/DEBUG）

## 主要コマンド（ローカル）
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export GCP_SA_KEY="$(cat service-account.json)"  # またはファイルパスを GOOGLE_APPLICATION_CREDENTIALS に設定
export CSE_API_KEY=xxx CSE_CX=xxx SHEET_ID=xxx SHEET_CATALOG=カタログ
python -m src.scripts.bootstrap_sheets   # 初期ワークシート作成
python -m src.main                       # 1クエリ処理（--catalog-row で行指定も可）
```

## シート作成物
- `SERP_Candidates` / `Anchors_Extracted` / `Suspected_404s` / `Run_Log`（自動作成）

詳細は `docs/` を参照してください。
