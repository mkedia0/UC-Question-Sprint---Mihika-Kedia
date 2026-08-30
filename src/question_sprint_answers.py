#!/usr/bin/env python3
"""Compute UC Admissions Data Challenge question sprint answers."""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
REPORTS = ROOT / "reports"


def f(value: str) -> float:
    return float(value) if value != "" else 0.0


def load(name: str) -> list[dict[str, str]]:
    with (DATA / name).open(newline="", encoding="utf-8-sig") as fp:
        return list(csv.DictReader(fp))


def weighted_rate(rows: list[dict[str, str]]) -> float:
    applicants = sum(f(r["applicants"]) for r in rows)
    admits = sum(f(r["admits"]) for r in rows)
    return admits / applicants


def main() -> None:
    REPORTS.mkdir(exist_ok=True)
    bay = load("bay_area_modeling_table.csv")
    dash = load("dashboard_data.csv")
    eth = load("uc_admissions_summary_by_ethnicity.csv")
    disc = load("uc_freshman_admission_by_discipline.csv")

    answers: list[tuple[str, str, str]] = []

    # 1. Average campuses per applicant = total campus applications / unique systemwide applicants.
    fall_2025 = [r for r in bay if r["fall_term"] == "2025"]
    campus_apps = sum(f(r["applicants"]) for r in fall_2025 if r["campus"] != "Universitywide")
    unique_apps = sum(f(r["applicants"]) for r in fall_2025 if r["campus"] == "Universitywide")
    answers.append(("Average campuses per applicant, fall 2025", f"{campus_apps / unique_apps:.2f}", f"{campus_apps:g} / {unique_apps:g}"))

    # 2. UCLA admit rate from California public high schools in this table, count-weighted.
    ucla_2025 = [r for r in fall_2025 if r["campus"] == "Los Angeles"]
    answers.append(("Fall 2025 UCLA admit rate", f"{weighted_rate(ucla_2025):.4f}", "admits / applicants"))

    # 3. Campus where CS costs the most admit rate vs all-disciplines rate.
    overall_by_campus = {}
    cs_by_campus = {}
    for r in disc:
        if r["fall_term"] != "2025":
            continue
        if r["broad_discipline"] == "All disciplines":
            overall_by_campus[r["campus"]] = f(r["admit_rate"])
        if r["broad_discipline"] == "Computer Science":
            cs_by_campus[r["campus"]] = f(r["admit_rate"])
    gaps = {
        campus: overall_by_campus[campus] - cs_rate
        for campus, cs_rate in cs_by_campus.items()
        if campus in overall_by_campus
    }
    campus, gap = max(gaps.items(), key=lambda item: item[1])
    answers.append(("Biggest CS admit-rate cost", campus, f"gap={gap:.4f}, overall={overall_by_campus[campus]:.4f}, cs={cs_by_campus[campus]:.4f}"))

    # 4. Berkeley CS admit GPA IQR.
    berkeley_cs = next(r for r in disc if r["campus"] == "Berkeley" and r["broad_discipline"] == "Computer Science")
    iqr = f(berkeley_cs["admit_gpa_p75"]) - f(berkeley_cs["admit_gpa_p25"])
    answers.append(("Berkeley CS admit GPA IQR", f"{iqr:.2f}", f"{berkeley_cs['admit_gpa_p75']} - {berkeley_cs['admit_gpa_p25']}"))

    # 5 and 6. Ethnicity admit rates from official summary file.
    by_key: dict[tuple[str, str], dict[str, float]] = defaultdict(dict)
    for r in eth:
        if r["entrant_level"] == "freshman" and r["fall_term"] == "2025" and r["ethnicity"] in {"White", "Hispanic/Latino(a)"}:
            by_key[(r["campus"], r["ethnicity"])][r["count_type"]] = f(r["n"])
    higher_white = 0
    campus_checks = []
    for campus in sorted({c for c, _ in by_key if c != "Systemwide"}):
        white = by_key[(campus, "White")]["Adm"] / by_key[(campus, "White")]["App"]
        hisp = by_key[(campus, "Hispanic/Latino(a)")]["Adm"] / by_key[(campus, "Hispanic/Latino(a)")]["App"]
        campus_checks.append((campus, white, hisp))
        higher_white += white > hisp
    answers.append(("Campuses where White admit rate > Hispanic/Latino(a)", str(higher_white), "; ".join(f"{c}: W {w:.3f}, H {h:.3f}" for c, w, h in campus_checks)))
    white_sys = by_key[("Systemwide", "White")]["Adm"] / by_key[("Systemwide", "White")]["App"]
    hisp_sys = by_key[("Systemwide", "Hispanic/Latino(a)")]["Adm"] / by_key[("Systemwide", "Hispanic/Latino(a)")]["App"]
    answers.append(("Systemwide higher admit-rate group", "White" if white_sys > hisp_sys else "Hispanic/Latino(a)", f"White={white_sys:.4f}, Hispanic/Latino(a)={hisp_sys:.4f}"))

    # 7. Class of 2023 Bay Area graduates enrolled at CCC within 12 months.
    uni_2023 = [r for r in bay if r["fall_term"] == "2023" and r["campus"] == "Universitywide"]
    ccc = sum(f(r["enrolled_ccc"]) for r in uni_2023)
    hs_completers = sum(f(r["hs_completers"]) for r in uni_2023)
    answers.append(("Class of 2023 share enrolled at CCC", f"{ccc / hs_completers:.4f}", f"{ccc:g} / {hs_completers:g}"))

    # 8. Mission San Jose 2023 Universitywide applicants / a-g completers.
    mission = [
        r for r in bay
        if r["fall_term"] == "2023"
        and r["campus"] == "Universitywide"
        and r["high_school"] == "MISSION SAN JOSE HIGH SCHOOL"
    ][0]
    mission_share = f(mission["applicants"]) / f(mission["ag_completers"])
    answers.append(("Mission San Jose 2023 UC applicants / a-g completers", f"{mission_share:.4f}", f"{mission['applicants']} / {mission['ag_completers']}"))

    # 9. Distinct schools with at least one freshman applicant to UC in fall 2025.
    schools = {
        r["cds_code"] or f"{r['high_school']}|{r['city']}|{r['county']}"
        for r in fall_2025
        if r["campus"] == "Universitywide" and f(r["applicants"]) >= 1
    }
    answers.append(("Distinct CA public high schools with >=1 UC applicant, fall 2025", str(len(schools)), "Universitywide rows"))

    # 10. Listed schools, Berkeley 2022-2025 weighted residual.
    listed = {
        "HERCULES HIGH SCHOOL",
        "MISSION SENIOR HIGH SCHOOL",
        "MONTEREY TRAIL HIGH SCHOOL",
        "PHILLIP & SALA BURTON ACAD HS",
        "RANCHO SAN JUAN HIGH SCHOOL",
    }
    residuals = {}
    details = []
    for school in sorted(listed):
        rows = [
            r for r in dash
            if r["campus"] == "Berkeley"
            and r["fall_term"] in {"2022", "2023", "2024", "2025"}
            and r["high_school"] == school
            and r["admit_rate_residual"] != ""
            and r["applicants"] != ""
        ]
        numerator = sum(f(r["admit_rate_residual"]) * f(r["applicants"]) for r in rows)
        denominator = sum(f(r["applicants"]) for r in rows)
        if denominator:
            residuals[school] = numerator / denominator
            details.append(f"{school}: {residuals[school]:.4f}")
        else:
            details.append(f"{school}: not present in Bay Area table")
    best = max(residuals.items(), key=lambda item: item[1])[0]
    answers.append(("Berkeley 2022-2025 biggest positive residual", best, "; ".join(details)))

    out = REPORTS / "question_sprint_answers.md"
    lines = ["# Question Sprint Answers", ""]
    for idx, (question, answer, note) in enumerate(answers, start=1):
        lines += [f"## {idx}. {question}", "", f"Answer: `{answer}`", "", f"Check: {note}", ""]
    out.write_text("\n".join(lines), encoding="utf-8")
    print(out)
    for idx, (_, answer, note) in enumerate(answers, start=1):
        print(f"{idx}. {answer} ({note})")


if __name__ == "__main__":
    main()
