#!/usr/bin/env python3
"""
source_data/*.csv -> Supabase Postgres 테이블 upsert.

SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY 환경변수가 필요하다. service role key는 RLS를 우회하는
쓰기 권한을 가지므로 GitHub Actions secret 등 서버 측에만 보관하고 index.html(브라우저)에는 절대 넣지 않는다.

표준 라이브러리만 사용 (csv, json, os, urllib.request) - pip install 불필요.
"""
import csv
import json
import os
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "source_data"

SUPABASE_URL = os.environ["SUPABASE_URL"].rstrip("/")
SERVICE_ROLE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

NUMERIC_FIELDS = {"mw", "logp", "hbd", "hba", "tpsa", "rotatable_bonds", "qed_druglikeness", "lipinski_violations"}


def blank_to_none(value):
    value = value.strip()
    return value if value != "" else None


def load_csv(path):
    rows = []
    with open(path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for r in reader:
            row = {}
            for k, v in r.items():
                v = blank_to_none(v)
                row[k] = float(v) if (k in NUMERIC_FIELDS and v is not None) else v
            rows.append(row)
    return rows


def upsert(table, rows, on_conflict):
    if not rows:
        return
    url = f"{SUPABASE_URL}/rest/v1/{table}?on_conflict={on_conflict}"
    body = json.dumps(rows).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST", headers={
        "apikey": SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SERVICE_ROLE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates,return=minimal",
    })
    try:
        with urllib.request.urlopen(req) as resp:
            resp.read()
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"{table} upsert 실패 ({e.code}): {e.read().decode('utf-8', 'replace')}") from e


def main():
    pipeline_rows = load_csv(DATA_DIR / "ai_drug_pipeline_candidates.csv")
    benchmark_rows = load_csv(DATA_DIR / "drug_candidates_master.csv")

    upsert("pipeline_candidates", pipeline_rows, "company,candidate_name")
    upsert("benchmark_compounds", benchmark_rows, "compound_id")

    print(f"OK: pipeline_candidates {len(pipeline_rows)}행, benchmark_compounds {len(benchmark_rows)}행 upsert 완료")


if __name__ == "__main__":
    main()
