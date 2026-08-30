#!/usr/bin/env python3
"""Profile the challenge CSVs without third-party dependencies."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
REPORTS = ROOT / "reports"


def iter_rows(path: Path):
    with path.open(newline="", encoding="utf-8-sig") as f:
        yield from csv.DictReader(f)


def count_rows(path: Path) -> tuple[int, list[str], dict[str, int]]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames or []
        missing = Counter()
        n = 0
        for row in reader:
            n += 1
            for field in fields:
                if row.get(field, "") == "":
                    missing[field] += 1
    return n, fields, dict(missing)


def main() -> None:
    REPORTS.mkdir(exist_ok=True)
    lines = ["# Data Profile", ""]

    for path in sorted(DATA.glob("*.csv")):
        n, fields, missing = count_rows(path)
        lines += [
            f"## {path.name}",
            "",
            f"- Rows: {n:,}",
            f"- Columns: {len(fields):,}",
            f"- First columns: {', '.join(fields[:10])}",
            "",
            "| Column | Missing | Missing % |",
            "|---|---:|---:|",
        ]
        ranked = sorted(missing.items(), key=lambda item: item[1], reverse=True)[:15]
        for field, count in ranked:
            lines.append(f"| `{field}` | {count:,} | {count / n:.1%} |")
        lines.append("")

    out = REPORTS / "data_profile.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
