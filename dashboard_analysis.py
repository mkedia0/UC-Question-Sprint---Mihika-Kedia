import numpy as np
import pandas as pd


DATA = "data/bay_area_modeling_table.csv"
PRE_YEARS = [2017, 2018, 2019]
POST_YEARS = [2022, 2023, 2024, 2025]


def weighted_slope(x, y, w):
    mask = x.notna() & y.notna() & w.notna() & (w > 0)
    x = x[mask].astype(float)
    y = y[mask].astype(float)
    w = w[mask].astype(float)
    x_bar = np.average(x, weights=w)
    y_bar = np.average(y, weights=w)
    return np.sum(w * (x - x_bar) * (y - y_bar)) / np.sum(w * (x - x_bar) ** 2)


def weighted_corr(x, y, w):
    mask = x.notna() & y.notna() & w.notna() & (w > 0)
    x = x[mask].astype(float)
    y = y[mask].astype(float)
    w = w[mask].astype(float)
    x_bar = np.average(x, weights=w)
    y_bar = np.average(y, weights=w)
    cov = np.sum(w * (x - x_bar) * (y - y_bar))
    x_var = np.sum(w * (x - x_bar) ** 2)
    y_var = np.sum(w * (y - y_bar) ** 2)
    return cov / np.sqrt(x_var * y_var)


def summarize_window(df, label, years):
    window = df[df.fall_term.isin(years)].copy()
    by_school = (
        window.groupby(["cds_code", "high_school", "city", "county"], dropna=False)
        .agg(
            applicants=("applicants", "sum"),
            admits=("admits", "sum"),
            enrollees=("enrollees", "sum"),
            applicant_gpa=("applicant_gpa", "mean"),
            frpm_pct=("frpm_pct", "mean"),
            ag_completion_rate=("ag_completion_rate", "mean"),
        )
        .reset_index()
    )
    by_school = by_school[(by_school.applicants > 0) & by_school.applicant_gpa.notna()]
    by_school["admit_rate"] = by_school.admits / by_school.applicants
    by_school["yield_rate"] = by_school.enrollees / by_school.admits
    by_school["window"] = label
    return by_school


def main():
    df = pd.read_csv(DATA, low_memory=False)
    df = df[df.campus == "Universitywide"].copy()

    pre = summarize_window(df, "Pre-test-blind (2017-2019)", PRE_YEARS)
    post = summarize_window(df, "Post-test-blind (2022-2025)", POST_YEARS)
    combined = pd.concat([pre, post], ignore_index=True)

    summary_rows = []
    for label, g in combined.groupby("window"):
        summary_rows.append(
            {
                "window": label,
                "schools": len(g),
                "applicants": int(g.applicants.sum()),
                "admits": int(g.admits.sum()),
                "weighted_admit_rate": g.admits.sum() / g.applicants.sum(),
                "gpa_admit_slope": weighted_slope(g.applicant_gpa, g.admit_rate, g.applicants),
                "gpa_admit_corr": weighted_corr(g.applicant_gpa, g.admit_rate, g.applicants),
                "avg_applicant_gpa": np.average(g.applicant_gpa, weights=g.applicants),
            }
        )

    summary = pd.DataFrame(summary_rows)

    school_change = pre.merge(
        post,
        on=["cds_code", "high_school", "city", "county"],
        suffixes=("_pre", "_post"),
    )
    school_change["admit_rate_change"] = school_change.admit_rate_post - school_change.admit_rate_pre
    school_change["applicant_gpa_change"] = school_change.applicant_gpa_post - school_change.applicant_gpa_pre
    school_change["yield_rate_change"] = school_change.yield_rate_post - school_change.yield_rate_pre
    school_change["post_minus_pre_score"] = (
        school_change.admit_rate_change * np.sqrt(school_change.applicants_post)
    )

    low_gpa = school_change[school_change.applicant_gpa_pre <= school_change.applicant_gpa_pre.quantile(0.33)]
    high_gpa = school_change[school_change.applicant_gpa_pre >= school_change.applicant_gpa_pre.quantile(0.67)]

    group_summary = pd.DataFrame(
        [
            {
                "group": "Lower-GPA applicant pools",
                "schools": len(low_gpa),
                "avg_admit_rate_change": np.average(low_gpa.admit_rate_change, weights=low_gpa.applicants_post),
            },
            {
                "group": "Higher-GPA applicant pools",
                "schools": len(high_gpa),
                "avg_admit_rate_change": np.average(high_gpa.admit_rate_change, weights=high_gpa.applicants_post),
            },
        ]
    )

    summary.to_csv("dashboard_summary.csv", index=False)
    group_summary.to_csv("dashboard_gpa_group_summary.csv", index=False)
    school_change.sort_values("post_minus_pre_score", ascending=False).to_csv(
        "dashboard_school_changes.csv", index=False
    )

    print("Main hypothesis:")
    print("H0: The GPA-admit-rate relationship did not weaken after UC became test-blind.")
    print("HA: The GPA-admit-rate relationship weakened after UC became test-blind.")
    print()
    print(summary.round(4).to_string(index=False))
    print()
    print(group_summary.round(4).to_string(index=False))
    print()
    print("Top post-test-blind admit-rate gainers:")
    cols = ["high_school", "city", "county", "admit_rate_pre", "admit_rate_post", "admit_rate_change"]
    print(school_change.sort_values("post_minus_pre_score", ascending=False)[cols].head(10).round(4).to_string(index=False))


if __name__ == "__main__":
    main()
