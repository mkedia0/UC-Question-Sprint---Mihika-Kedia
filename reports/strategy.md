# Best Strategy To Win

## Positioning

Do not submit a generic admissions dashboard. The data is strongest when used to answer a policy/action question:

> Where can UC increase Bay Area access most efficiently, and what kind of outreach should each school receive?

Judges will likely reward work that is accurate, grounded in the data warnings, and useful to a real decision-maker.

## Recommended Product

Create an "UC Opportunity Map" with three deliverables:

1. Ranked target schools for UC outreach.
2. Segments that explain why each school is a target.
3. Campus or systemwide recommendations tied to the segment.

## Segments

- **Hidden Eligible Pool**: high a-g completion, low UC applicant conversion.
- **High Need, High Potential**: high FRPM, meaningful a-g completion, below-peer UC application volume.
- **Conversion Problem**: plenty of applicants but admits/enrollees lag expected baselines.
- **Yield Problem**: admits are strong, but enrollees are weak.
- **Campus Mismatch**: students apply to very selective campuses while better-fit UC campuses have more room.

## Analysis Sequence

1. Use `dashboard_data.csv`, `campus == "Universitywide"`, Fall 2025 for the first ranked school list.
2. Backtest the same school rankings over 2022-2025 to avoid one-year noise.
3. Add county-level views for Alameda, Contra Costa, San Francisco, San Mateo, Santa Clara, Solano, Sonoma, Marin, and Napa.
4. Use the ethnicity summary file only for system/campus-level equity trends.
5. Use discipline and transfer files as a final "what students should know" sidebar, not the main analysis.

## Charts To Build

- Scatter: a-g completers vs UC applicants, colored by FRPM, labeled for biggest gaps.
- Slope chart: Universitywide admit rate before vs after test-blind admissions, 2019 to 2025.
- Bar chart: top 15 outreach opportunity schools.
- Map: Bay Area high schools by opportunity score.
- Funnel: graduates -> a-g completers -> UC applicants -> admits -> enrollees.

## What To Avoid

- Do not average admit rates across schools.
- Do not sum campus rows to create systemwide totals.
- Do not fill redacted blanks with zero.
- Do not make claims about individual student odds.
- Do not build a race analysis from redacted school-level race columns.

## Submission Narrative

Lead with this:

"The bottleneck is not only admissions selectivity. At many Bay Area schools, the bigger opportunity is earlier in the pipeline: students complete the courses that make UC possible, but too few become UC applicants or enrollees. This project identifies where UC outreach could convert existing eligibility into real access."

Then show the ranked list and three example school stories.
