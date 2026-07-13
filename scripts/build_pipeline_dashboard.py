#!/usr/bin/env python3
"""
AI 신약 파이프라인 경쟁사 트래킹 대시보드 빌드 스크립트.

source_data/ai_drug_pipeline_candidates.csv (경쟁사 파이프라인, 메인)
source_data/drug_candidates_master.csv (화합물 벤치마크, 보조)
를 읽어 정규화/집계한 뒤 scripts/index_template.html의
__DATA_JSON__ 자리표시자를 채워 index.html을 생성한다.

표준 라이브러리만 사용 (csv, json, collections, pathlib) - pip install 불필요.
"""
import csv
import json
import statistics
from collections import Counter, OrderedDict, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "source_data"
TEMPLATE_PATH = ROOT / "scripts" / "index_template.html"
OUTPUT_HTML = ROOT / "index.html"
OUTPUT_JSON = ROOT / "data" / "pipeline_data.json"

PIPELINE_CSV = DATA_DIR / "ai_drug_pipeline_candidates.csv"
MASTER_CSV = DATA_DIR / "drug_candidates_master.csv"

# 개발단계 원문 -> (그룹, 퍼널 순서). 중단은 퍼널과 별도 취급(order=None).
STAGE_GROUP_MAP = [
    (lambda s: "중단" in s or "Discontinued" in s, "중단", None),
    (lambda s: "Phase III" in s, "Phase III", 4),
    (lambda s: "Phase I/II" in s or "Phase I/IIa" in s or "Early clinical" in s, "Phase I/II", 3),
    (lambda s: "Phase I/Ib" in s, "Phase I/Ib", 2),
    (lambda s: "Phase I" in s, "Phase I", 2),
    (lambda s: "전임상" in s or "IND" in s, "전임상/IND 준비", 1),
]

STAGE_ORDER_LABELS = OrderedDict([
    (1, "전임상/IND 준비"),
    (2, "Phase I"),
    (3, "Phase I/II"),
    (4, "Phase III"),
    (5, "상용화(승인)"),
])


def classify_stage(raw_stage: str):
    for pred, group, order in STAGE_GROUP_MAP:
        if pred(raw_stage):
            return group, order
    return raw_stage, None


def load_pipeline():
    rows = []
    with open(PIPELINE_CSV, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for r in reader:
            group, order = classify_stage(r["current_stage"])
            rows.append({
                "company": r["company"].strip(),
                "candidate_name": r["candidate_name"].strip(),
                "target_mechanism": r["target_mechanism"].strip(),
                "indication": r["indication"].strip(),
                "ai_discovery_approach": r["ai_discovery_approach"].strip(),
                "current_stage": r["current_stage"].strip(),
                "stage_group": group,
                "stage_order": order,  # None = 중단 (퍼널 밖)
                "commercialized": r["commercialized"].strip(),
                "key_milestone_note": r["key_milestone_note"].strip(),
                "source_url": r["source_url"].strip(),
                "as_of_date": r["as_of_date"].strip(),
            })
    return rows


def build_company_summary(pipeline_rows):
    by_company = defaultdict(list)
    for r in pipeline_rows:
        by_company[r["company"]].append(r)

    summary = []
    for company, rows in by_company.items():
        staged = [r for r in rows if r["stage_order"] is not None]
        if staged:
            best = max(staged, key=lambda r: r["stage_order"])
            best_stage_label = best["current_stage"]
            best_stage_order = best["stage_order"]
        else:
            best_stage_label = "중단"
            best_stage_order = 0
        platforms = sorted(set(r["ai_discovery_approach"] for r in rows))
        discontinued_count = sum(1 for r in rows if r["stage_order"] is None)
        summary.append({
            "company": company,
            "candidate_count": len(rows),
            "best_stage_label": best_stage_label,
            "best_stage_order": best_stage_order,
            "discontinued_count": discontinued_count,
            "platforms": platforms,
            "candidates": [r["candidate_name"] for r in rows],
        })
    summary.sort(key=lambda s: (-s["best_stage_order"], -s["candidate_count"]))
    return summary


def build_funnel(pipeline_rows):
    counts = Counter()
    for r in pipeline_rows:
        if r["stage_order"] is not None:
            counts[r["stage_order"]] += 1
    funnel = []
    for order, label in STAGE_ORDER_LABELS.items():
        funnel.append({"order": order, "label": label, "count": counts.get(order, 0)})
    discontinued = sum(1 for r in pipeline_rows if r["stage_order"] is None)
    return funnel, discontinued


def to_float(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def load_master():
    rows = []
    with open(MASTER_CSV, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for r in reader:
            fda = r["fda_approved"].strip()
            if fda == "1":
                fda_cat = "approved"
            elif fda == "0":
                fda_cat = "failed_toxicity"
            else:
                fda_cat = "unclassified"

            tox_assays = [a for a in r["toxicity_assay"].split(";") if a] if r["toxicity_assay"] else []
            rows.append({
                "compound_id": r["compound_id"],
                "source_dataset": r["source_dataset"],
                "mw": to_float(r["mw"]),
                "logp": to_float(r["logp"]),
                "hbd": to_float(r["hbd"]),
                "hba": to_float(r["hba"]),
                "tpsa": to_float(r["tpsa"]),
                "rotatable_bonds": to_float(r["rotatable_bonds"]),
                "qed_druglikeness": to_float(r["qed_druglikeness"]),
                "lipinski_violations": to_float(r["lipinski_violations"]),
                "toxicity_flag": r["toxicity_flag"].strip(),
                "toxicity_assays": tox_assays,
                "fda_category": fda_cat,
                "efficacy_assay": r["efficacy_assay"].strip(),
                "efficacy_value": r["efficacy_value"].strip(),
                "efficacy_active_flag": r["efficacy_active_flag"].strip(),
            })
    return rows


NUMERIC_FIELDS = ["mw", "logp", "hbd", "hba", "tpsa", "rotatable_bonds", "qed_druglikeness", "lipinski_violations"]


def group_stats(rows):
    stats = {}
    for field in NUMERIC_FIELDS:
        vals = [r[field] for r in rows if r[field] is not None]
        if vals:
            stats[field] = {
                "min": round(min(vals), 3),
                "mean": round(statistics.mean(vals), 3),
                "max": round(max(vals), 3),
                "n": len(vals),
            }
        else:
            stats[field] = None
    return stats


def build_benchmark(master_rows):
    dataset_counts = Counter(r["source_dataset"] for r in master_rows)

    fda_groups = defaultdict(list)
    for r in master_rows:
        fda_groups[r["fda_category"]].append(r)
    fda_group_stats = {cat: group_stats(rows) for cat, rows in fda_groups.items()}
    fda_group_counts = {cat: len(rows) for cat, rows in fda_groups.items()}

    tox_valid = [r for r in master_rows if r["toxicity_flag"] != ""]
    tox_positive = [r for r in tox_valid if r["toxicity_flag"] == "1"]

    efficacy_by_dataset = defaultdict(lambda: {"n": 0, "active": 0, "assay": None})
    for r in master_rows:
        if r["efficacy_active_flag"] != "":
            d = efficacy_by_dataset[r["source_dataset"]]
            d["n"] += 1
            d["assay"] = r["efficacy_assay"]
            if r["efficacy_active_flag"] == "1":
                d["active"] += 1

    tox21_assay_counts = Counter()
    for r in master_rows:
        if r["source_dataset"] == "Tox21":
            for a in r["toxicity_assays"]:
                tox21_assay_counts[a] += 1

    return {
        "total_compounds": len(master_rows),
        "dataset_counts": dict(dataset_counts),
        "fda_group_counts": fda_group_counts,
        "fda_group_stats": fda_group_stats,
        "toxicity_valid_n": len(tox_valid),
        "toxicity_positive_n": len(tox_positive),
        "efficacy_by_dataset": dict(efficacy_by_dataset),
        "tox21_assay_counts": dict(tox21_assay_counts.most_common()),
    }


def main():
    pipeline_rows = load_pipeline()
    company_summary = build_company_summary(pipeline_rows)
    funnel, discontinued = build_funnel(pipeline_rows)
    master_rows = load_master()
    benchmark = build_benchmark(master_rows)

    as_of_prefixes = sorted({r["as_of_date"][:7] for r in pipeline_rows})
    milestones = sorted(pipeline_rows, key=lambda r: r["as_of_date"], reverse=True)

    data = {
        "meta": {
            "generated_note": "정적 스냅샷 (as_of_date는 행마다 상이, 기사/보도자료 발표 시점 기준)",
            "total_candidates": len(pipeline_rows),
            "total_companies": len(company_summary),
            "commercialized_count": sum(1 for r in pipeline_rows if r["commercialized"].lower() == "yes"),
            "as_of_date_range": [as_of_prefixes[0], as_of_prefixes[-1]] if as_of_prefixes else None,
        },
        "pipeline": pipeline_rows,
        "company_summary": company_summary,
        "funnel": funnel,
        "discontinued_count": discontinued,
        "milestones": milestones,
        "benchmark": benchmark,
    }

    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    data_json_str = json.dumps(data, ensure_ascii=False)
    final_html = template.replace("__DATA_JSON__", data_json_str)
    OUTPUT_HTML.write_text(final_html, encoding="utf-8")

    print(f"OK: {OUTPUT_JSON} ({OUTPUT_JSON.stat().st_size} bytes)")
    print(f"OK: {OUTPUT_HTML} ({OUTPUT_HTML.stat().st_size} bytes)")
    print(f"총 후보물질 {len(pipeline_rows)}건 / 기업 {len(company_summary)}개 / 벤치마크 화합물 {len(master_rows)}건")


if __name__ == "__main__":
    main()
