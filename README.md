# UC Admissions Data Challenge - Mihika Kedia

This repo contains the Question Sprint notebook and a Streamlit dashboard for the UC Admissions Data Challenge.

Run `question_sprint_answers.ipynb` from the repo root. Each code cell computes one form answer from the provided CSV files in `data/`.

Run the dashboard with:

```bash
streamlit run app.py
```

## Dashboard Question

How did UC's test-blind admissions shift affect applicants' chances of admission from Bay Area public high schools, and which kinds of schools saw the biggest change?

## Study Design

- Population of interest: Bay Area California public high schools represented in the provided UC admissions data.
- Observational units: one high school summarized across a time window.
- Explanatory variables: school applicant GPA, free/reduced-price meal share (`frpm_pct`), and a-g completion rate.
- Response variables: Universitywide UC admit rate (`admits / applicants`), applicant volume, yield rate (`enrollees / admits`), enrollment rate (`enrollees / applicants`), and the GPA profile of applicants, admits, and enrollees.
- Comparison groups: pre-test-blind years `2017-2019` vs post-test-blind years `2022-2025`.
- Null hypothesis: test-blind admissions did not meaningfully change UC admission chances across Bay Area public high schools.
- Alternative hypothesis: test-blind admissions changed UC admission chances, with different effects by school context.

The analysis uses `campus == "Universitywide"` because that row counts students admitted to at least one UC, not duplicated campus applications. Rates are computed by summing counts first, then dividing. All dashboard metrics come from the provided challenge CSV files in `data/`; no outside data is used in the analysis.

## Methodology

This is an observational study, not a randomized experiment. The explanatory condition is whether the admissions cycle happened before or after UC became test-blind. Because other changes happened over time too, the dashboard describes association rather than proving causation.

The main test is a comparison of two least-squares regression relationships:

```text
x = average applicant GPA at a high school
y = Universitywide UC admit rate from that high school
```

If the post-test-blind regression slope is smaller than the pre-test-blind slope, that is evidence that admit rate became less strongly associated with the GPA profile of a school's applicants.

The dashboard also compares conditional group means across thirds of schools by applicant GPA, FRPM share, and a-g completion rate. This checks whether the pre/post change looks different across subgroups instead of only reporting one systemwide average.

Preliminary result: the post-test-blind period had a higher overall admit rate, and the relationship between school applicant GPA and admit rate became much weaker. Higher-FRPM schools saw the largest admit-rate increase, but their yield fell, suggesting admission chances improved more than actual enrollment. The GPA gap metrics compare `enrollee_gpa` to `applicant_gpa` and `admit_gpa` to test whether the enrolled class shifted along with admit chances.

Run:

```bash
python dashboard_analysis.py
```

The script writes:

- `analysis_outputs/test_blind_overall_summary.csv`
- `analysis_outputs/applicant_gpa_group_changes.csv`
- `analysis_outputs/frpm_group_changes.csv`
- `analysis_outputs/ag_completion_group_changes.csv`
- `analysis_outputs/school_level_pre_post_changes.csv`
