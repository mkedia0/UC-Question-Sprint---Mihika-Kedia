import numpy as np
import pandas as pd
import statsmodels.api as sm
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "given_materials" / "data" / "bay_area_modeling_table.csv"
OUTPUTS = Path(__file__).resolve().parent / "analysis_outputs"
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
            admit_gpa=("admit_gpa", "mean"),
            enrollee_gpa=("enrollee_gpa", "mean"),
            frpm_pct=("frpm_pct", "mean"),
            ag_completion_rate=("ag_completion_rate", "mean"),
        )
        .reset_index()
    )
    by_school = by_school[(by_school.applicants > 0) & by_school.applicant_gpa.notna()]
    by_school["admit_rate"] = by_school.admits / by_school.applicants
    by_school["yield_rate"] = by_school.enrollees / by_school.admits
    by_school["enrollment_rate"] = by_school.enrollees / by_school.applicants
    by_school["enrollee_applicant_gpa_gap"] = by_school.enrollee_gpa - by_school.applicant_gpa
    by_school["enrollee_admit_gpa_gap"] = by_school.enrollee_gpa - by_school.admit_gpa
    by_school["window"] = label
    return by_school


def weighted_mean(df, col, weight="applicants"):
    usable = df[df[col].notna() & df[weight].notna() & (df[weight] > 0)]
    return np.average(usable[col], weights=usable[weight])


def slope_change_test(pre, post):
    pre = pre.copy()
    post = post.copy()
    pre["post_period"] = 0
    post["post_period"] = 1
    combined = pd.concat([pre, post], ignore_index=True)
    combined = combined.dropna(subset=["applicant_gpa", "admit_rate", "applicants"])
    combined["gpa_post_interaction"] = combined.applicant_gpa * combined.post_period

    x = sm.add_constant(combined[["applicant_gpa", "post_period", "gpa_post_interaction"]])
    model = sm.WLS(combined.admit_rate, x, weights=combined.applicants).fit()
    return pd.DataFrame(
        [
            {
                "test": "Weighted regression interaction: applicant_gpa x post_test_blind",
                "interaction_coefficient": model.params["gpa_post_interaction"],
                "p_value": model.pvalues["gpa_post_interaction"],
                "alpha": 0.05,
                "significant_at_0_05": model.pvalues["gpa_post_interaction"] < 0.05,
            }
        ]
    )


def context_slope_tests(school_change):
    predictors = {
        "applicant_gpa_pre": "Pre-period applicant GPA",
        "frpm_pct_pre": "Pre-period FRPM share",
        "ag_completion_rate_pre": "Pre-period a-g completion rate",
    }
    outcomes = {
        "admit_rate_change": ("Admit rate change", "applicants_post"),
        "yield_rate_change": ("Yield change", "admits_post"),
        "enrollee_gpa_change": ("Enrollee GPA change", "enrollees_post"),
    }

    rows = []
    for predictor, predictor_label in predictors.items():
        for outcome, (outcome_label, weight_col) in outcomes.items():
            usable = school_change.dropna(subset=[predictor, outcome, weight_col])
            usable = usable[usable[weight_col] > 0]
            x = sm.add_constant(usable[[predictor]])
            model = sm.WLS(usable[outcome], x, weights=usable[weight_col]).fit()
            rows.append(
                {
                    "predictor": predictor_label,
                    "outcome": outcome_label,
                    "slope": model.params[predictor],
                    "p_value": model.pvalues[predictor],
                    "alpha": 0.05,
                    "significant_at_0_05": model.pvalues[predictor] < 0.05,
                }
            )
    return pd.DataFrame(rows)


def compare_groups(school_change, labels):
    rows = []
    for label, group_index in labels.items():
        g = school_change.loc[group_index]
        rows.append(
            {
                "group": label,
                "schools": len(g),
                "pre_admit_rate": weighted_mean(g, "admit_rate_pre", "applicants_pre"),
                "post_admit_rate": weighted_mean(g, "admit_rate_post", "applicants_post"),
                "admit_rate_change": weighted_mean(g, "admit_rate_change", "applicants_post"),
                "applicant_change": g.applicants_post.sum() - g.applicants_pre.sum(),
                "yield_rate_change": weighted_mean(g, "yield_rate_change", "admits_post"),
                "applicant_gpa_change": weighted_mean(g, "applicant_gpa_change", "applicants_post"),
                "admit_gpa_change": weighted_mean(g, "admit_gpa_change", "admits_post"),
                "enrollee_gpa_change": weighted_mean(g, "enrollee_gpa_change", "enrollees_post"),
                "enrollee_applicant_gpa_gap_change": weighted_mean(
                    g, "enrollee_applicant_gpa_gap_change", "enrollees_post"
                ),
                "enrollee_admit_gpa_gap_change": weighted_mean(
                    g, "enrollee_admit_gpa_gap_change", "enrollees_post"
                ),
            }
        )
    return pd.DataFrame(rows)


def main():
    OUTPUTS.mkdir(exist_ok=True)
    df = pd.read_csv(DATA, low_memory=False)
    df = df[df.campus == "Universitywide"].copy()

    pre = summarize_window(df, "Pre-test-blind (2017-2019)", PRE_YEARS)
    post = summarize_window(df, "Post-test-blind (2022-2025)", POST_YEARS)
    combined = pd.concat([pre, post], ignore_index=True)
    significance = slope_change_test(pre, post)

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
                "avg_admit_gpa": weighted_mean(g, "admit_gpa", "admits"),
                "avg_enrollee_gpa": weighted_mean(g, "enrollee_gpa", "enrollees"),
                "enrollee_applicant_gpa_gap": weighted_mean(g, "enrollee_applicant_gpa_gap", "enrollees"),
                "enrollee_admit_gpa_gap": weighted_mean(g, "enrollee_admit_gpa_gap", "enrollees"),
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
    school_change["admit_gpa_change"] = school_change.admit_gpa_post - school_change.admit_gpa_pre
    school_change["enrollee_gpa_change"] = school_change.enrollee_gpa_post - school_change.enrollee_gpa_pre
    school_change["enrollee_applicant_gpa_gap_change"] = (
        school_change.enrollee_applicant_gpa_gap_post - school_change.enrollee_applicant_gpa_gap_pre
    )
    school_change["enrollee_admit_gpa_gap_change"] = (
        school_change.enrollee_admit_gpa_gap_post - school_change.enrollee_admit_gpa_gap_pre
    )
    school_change["yield_rate_change"] = school_change.yield_rate_post - school_change.yield_rate_pre
    school_change["post_minus_pre_score"] = (
        school_change.admit_rate_change * np.sqrt(school_change.applicants_post)
    )
    context_tests = context_slope_tests(school_change)

    low_gpa = school_change[school_change.applicant_gpa_pre <= school_change.applicant_gpa_pre.quantile(0.33)]
    mid_gpa = school_change[
        school_change.applicant_gpa_pre.between(
            school_change.applicant_gpa_pre.quantile(0.33),
            school_change.applicant_gpa_pre.quantile(0.67),
            inclusive="neither",
        )
    ]
    high_gpa = school_change[school_change.applicant_gpa_pre >= school_change.applicant_gpa_pre.quantile(0.67)]

    low_frpm = school_change[school_change.frpm_pct_pre <= school_change.frpm_pct_pre.quantile(0.33)]
    mid_frpm = school_change[
        school_change.frpm_pct_pre.between(
            school_change.frpm_pct_pre.quantile(0.33),
            school_change.frpm_pct_pre.quantile(0.67),
            inclusive="neither",
        )
    ]
    high_frpm = school_change[school_change.frpm_pct_pre >= school_change.frpm_pct_pre.quantile(0.67)]

    low_ag = school_change[school_change.ag_completion_rate_pre <= school_change.ag_completion_rate_pre.quantile(0.33)]
    mid_ag = school_change[
        school_change.ag_completion_rate_pre.between(
            school_change.ag_completion_rate_pre.quantile(0.33),
            school_change.ag_completion_rate_pre.quantile(0.67),
            inclusive="neither",
        )
    ]
    high_ag = school_change[school_change.ag_completion_rate_pre >= school_change.ag_completion_rate_pre.quantile(0.67)]

    gpa_summary = compare_groups(
        school_change,
        {
            "Lower applicant GPA": low_gpa.index,
            "Middle applicant GPA": mid_gpa.index,
            "Higher applicant GPA": high_gpa.index,
        },
    )
    frpm_summary = compare_groups(
        school_change,
        {
            "Lower FRPM": low_frpm.index,
            "Middle FRPM": mid_frpm.index,
            "Higher FRPM": high_frpm.index,
        },
    )
    ag_summary = compare_groups(
        school_change,
        {
            "Lower a-g completion": low_ag.index,
            "Middle a-g completion": mid_ag.index,
            "Higher a-g completion": high_ag.index,
        },
    )

    summary.to_csv(OUTPUTS / "test_blind_overall_summary.csv", index=False)
    significance.to_csv(OUTPUTS / "gpa_slope_significance_test.csv", index=False)
    context_tests.to_csv(OUTPUTS / "context_slope_significance_tests.csv", index=False)
    gpa_summary.to_csv(OUTPUTS / "applicant_gpa_group_changes.csv", index=False)
    frpm_summary.to_csv(OUTPUTS / "frpm_group_changes.csv", index=False)
    ag_summary.to_csv(OUTPUTS / "ag_completion_group_changes.csv", index=False)
    school_change.sort_values("post_minus_pre_score", ascending=False).to_csv(
        OUTPUTS / "school_level_pre_post_changes.csv", index=False
    )

    print("Main hypothesis:")
    print("H0: The GPA-admit-rate relationship did not weaken after UC became test-blind.")
    print("HA: The GPA-admit-rate relationship weakened after UC became test-blind.")
    print()
    print(summary.round(4).to_string(index=False))
    print()
    print("Regression significance test:")
    print(significance.round(4).to_string(index=False))
    print()
    print("Context slope significance tests:")
    print(context_tests.round(4).to_string(index=False))
    print()
    print("By applicant GPA group:")
    print(gpa_summary.round(4).to_string(index=False))
    print()
    print("By FRPM group:")
    print(frpm_summary.round(4).to_string(index=False))
    print()
    print("By a-g completion group:")
    print(ag_summary.round(4).to_string(index=False))
    print()
    print("Top post-test-blind admit-rate gainers:")
    cols = ["high_school", "city", "county", "admit_rate_pre", "admit_rate_post", "admit_rate_change"]
    print(school_change.sort_values("post_minus_pre_score", ascending=False)[cols].head(10).round(4).to_string(index=False))


if __name__ == "__main__":
    main()
