# UC Admissions Data Challenge - Mihika Kedia

This repo contains the Question Sprint notebook and early dashboard analysis for the UC Admissions Data Challenge.

Run `question_sprint_answers.ipynb` from the repo root. Each code cell computes one form answer from the provided CSV files in `data/`.

## Dashboard Question

Did UC's test-blind admissions shift make Universitywide admit rates less tied to a Bay Area high school's average applicant GPA?

## AP Stats Style Setup

- Population of interest: Bay Area California public high schools represented in the provided UC admissions data.
- Observational units: one high school summarized across a time window.
- Explanatory variable: average `applicant_gpa`.
- Response variable: Universitywide UC admit rate, computed as total `admits / applicants`.
- Comparison groups: pre-test-blind years `2017-2019` vs post-test-blind years `2022-2025`.
- Null hypothesis: the relationship between school applicant GPA and UC admit rate did not weaken after UC became test-blind.
- Alternative hypothesis: the relationship weakened after UC became test-blind.

The analysis uses `campus == "Universitywide"` because that row counts students admitted to at least one UC, not duplicated campus applications. Rates are computed by summing counts first, then dividing.

Run:

```bash
python dashboard_analysis.py
```

The script writes:

- `dashboard_summary.csv`
- `dashboard_gpa_group_summary.csv`
- `dashboard_school_changes.csv`
