# UC Question Sprint - Mihika Kedia

This repository computes the numeric answers for the UC Admissions Data Challenge Question Sprint.

## Methodology

All answers are computed from the provided CSV datasets. I used count-weighted calculations for admit rates, meaning I summed admits and applicants first, then divided. I used `campus == "Universitywide"` when the question asks about unique UC applicants rather than campus-level applications, because the Universitywide row counts people once while campus rows count applications to individual campuses. For race/ethnicity questions, I used `uc_admissions_summary_by_ethnicity.csv` rather than redacted school-level race columns.

Run:

```bash
python3 src/question_sprint_answers.py
```

Primary output:

- `reports/question_sprint_answers.md`

## Answers

1. `5.74`
2. `0.0818`
3. `Davis`
4. `0.09`
5. `9`
6. `Hispanic/Latino(a)`
7. `0.3364`
8. `0.9906`
9. `248`
10. `MISSION SENIOR HIGH SCHOOL`
