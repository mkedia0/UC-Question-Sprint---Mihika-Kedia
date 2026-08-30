#!/usr/bin/env python3
"""Rank Bay Area high schools by UC outreach opportunity."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
REPORTS = ROOT / "reports"


def to_float(value: str) -> float | None:
    if value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def score(row: dict[str, str]) -> float | None:
    graduates = to_float(row["graduates"])
    ag_rate = to_float(row["ag_completion_rate"])
    applicants = to_float(row["applicants"])
    admits = to_float(row["admits"])
    frpm = to_float(row["frpm_pct"])
    residual = to_float(row.get("admit_rate_residual", ""))

    if not graduates or not ag_rate or applicants is None:
        return None

    ag_completers = graduates * ag_rate
    applicant_gap = max(ag_completers - applicants, 0)
    need_multiplier = 1 + (frpm or 0)
    underperformance = max(-(residual or 0), 0) + 0.05
    admit_signal = 1 + ((admits or 0) / max(applicants, 1))

    return applicant_gap * need_multiplier * underperformance * admit_signal


def main() -> None:
    REPORTS.mkdir(exist_ok=True)
    source = DATA / "dashboard_data.csv"
    rows: list[dict[str, str]] = []

    with source.open(newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            if row["campus"] != "Universitywide" or row["fall_term"] != "2025":
                continue
            opportunity = score(row)
            if opportunity is None:
                continue
            row["opportunity_score"] = f"{opportunity:.2f}"
            rows.append(row)

    rows.sort(key=lambda r: float(r["opportunity_score"]), reverse=True)

    fields = [
        "high_school",
        "city",
        "county",
        "graduates",
        "ag_completion_rate",
        "applicants",
        "admits",
        "admit_rate",
        "frpm_pct",
        "expected_admit_rate",
        "admit_rate_residual",
        "opportunity_score",
    ]

    out_csv = REPORTS / "opportunity_index_2025.csv"
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in fields} for row in rows)

    md = ["# 2025 UC Outreach Opportunity Index", ""]
    md.append("This starter index ranks schools with large a-g-to-UC applicant gaps, higher socioeconomic need, and below-baseline admit-rate residuals.")
    md += ["", "| Rank | High School | City | County | Applicants | Admits | Score |", "|---:|---|---|---|---:|---:|---:|"]
    for i, row in enumerate(rows[:25], start=1):
        md.append(
            f"| {i} | {row['high_school']} | {row['city']} | {row['county']} | "
            f"{row['applicants']} | {row['admits']} | {row['opportunity_score']} |"
        )

    out_md = REPORTS / "opportunity_index_2025.md"
    out_md.write_text("\n".join(md), encoding="utf-8")
    print(f"Wrote {out_csv}")
    print(f"Wrote {out_md}")


if __name__ == "__main__":
    main()
