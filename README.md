# Brick by Brick: Rebuilding UC Access

This repository contains my UC Admissions Data Challenge submission. The main project is a Streamlit dashboard that studies how UC's test-blind admissions shift was associated with Bay Area public high school admission patterns.

**Theme:** when UC removed the test-score brick, did GPA become load-bearing, or did access shift?

## Repository Structure

- `app.py`: small Streamlit launcher for deployment from the repo root.
- `dashboard/`: dashboard app, analysis script, and generated results.
- `question_sprint/`: notebook for the Question Sprint answers.
- `given_materials/data/`: challenge-provided CSV files and data README.

## Dashboard Question

How did UC's test-blind admissions shift affect applicants' chances of admission from Bay Area public high schools, and which kinds of schools saw the biggest change?

## Study Design

- Population of interest: Bay Area California public high schools represented in the provided UC admissions data.
- Observational units: one high school summarized across a time window.
- Main response variable: Universitywide UC admit rate, calculated as `admits / applicants`.
- Main explanatory variables: school applicant GPA, post-test-blind period, and their interaction.
- Context variables: free/reduced-price meal share (`frpm_pct`) and a-g completion rate.
- Comparison groups: pre-test-blind years `2017-2019` vs post-test-blind years `2022-2025`.
- Null hypothesis: the GPA/admit-rate relationship did not meaningfully change after UC became test-blind.
- Alternative hypothesis: the GPA/admit-rate relationship changed after UC became test-blind.

This is an observational study, not a randomized experiment. The dashboard describes association rather than proving that test-blind admissions was the only cause of the observed changes.

## Methodology

The analysis uses `campus == "Universitywide"` because that row counts each student once if they were admitted to at least one UC. Rates are computed by summing counts first, then dividing. All metrics come from the provided challenge CSV files; no outside data is used.

The main significance check uses a weighted regression interaction model with applicant count as the weight:

```text
admit_rate = applicant_gpa + post_test_blind + applicant_gpa * post_test_blind
```

The interaction term tests whether the GPA/admit-rate slope changed significantly after the policy shift.

The dashboard also compares weighted subgroup means across thirds of schools by applicant GPA, FRPM share, and a-g completion rate. The grouped lines are visual summaries; the p-values underneath come from continuous weighted regressions using the original school context variables.

## Key Finding

The post-test-blind period had a higher overall admit rate, and the relationship between school applicant GPA and admit rate became much weaker. The GPA/admit-rate slope dropped from `0.214` to `0.050`, with an interaction p-value of `0.027`, so the slope change is statistically significant at `alpha = 0.05`.

Higher-FRPM schools saw the largest admit-rate increase, but their yield fell, suggesting admission access improved more than enrollment conversion.

## Run Locally

Install requirements, then run the dashboard from the repo root:

```bash
pip install -r requirements.txt
streamlit run app.py
```

Run the analysis script:

```bash
python dashboard/dashboard_analysis.py
```

The script writes generated results to `dashboard/analysis_outputs/`.
