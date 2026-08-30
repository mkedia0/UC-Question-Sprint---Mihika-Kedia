# UC Admissions Data Challenge

Analysis workspace for the UC Admissions Data Challenge.

## Core Thesis

The strongest path is to frame UC access as a pipeline problem:

1. Which Bay Area high schools produce many UC-eligible graduates but fewer UC applicants than expected?
2. Which schools outperform peer baselines once applicant pool size, a-g completion, poverty, and academic context are considered?
3. Where would outreach create the most new UC admits or enrollments?

That story is more useful than a leaderboard-style admit-rate model because it points to specific schools, counties, and intervention levers.

## Repo Layout

- `data/`: original challenge CSV files and data README.
- `src/profile_data.py`: dependency-free data profiler.
- `src/opportunity_index.py`: starter scoring model for outreach opportunities.
- `reports/`: generated Markdown outputs.
- `notebooks/`: optional exploratory notebooks.

## Quick Start

```bash
python3 src/profile_data.py
python3 src/opportunity_index.py
```

## Important Data Rules

- Use `campus == "Universitywide"` for systemwide school outcomes. Do not sum campuses for systemwide counts.
- Blank counts are redacted, not zero.
- Compare pre-2021 and post-2021 admissions carefully because UC stopped using SAT/ACT for Fall 2021 onward.
- For race/ethnicity, use `uc_admissions_summary_by_ethnicity.csv`, not school-level redacted fields.
- Aggregate rates by summing counts first, then dividing.

## Current Winning Direction

Build an "UC Opportunity Map" that identifies high schools where the UC pipeline is under-converting:

- Many graduates or a-g completers.
- Relatively low UC application volume.
- Lower-than-peer admit or enrollment conversion.
- High socioeconomic need.
- Clear campus-specific or county-specific recommendation.

The final submission should include:

- A 1-page executive brief.
- A ranked table of target schools.
- 3-5 charts/maps.
- A simple, defensible scoring method.
- One concrete outreach recommendation per segment.
