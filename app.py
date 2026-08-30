import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st


PRE_YEARS = [2017, 2018, 2019]
POST_YEARS = [2022, 2023, 2024, 2025]


st.set_page_config(page_title="UC Admissions Scouting Report", layout="wide")

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #f8faf6 0%, #eef4e8 45%, #f7f3df 100%);
    }
    [data-testid="stMetric"] {
        background: #ffffffcc;
        border: 1px solid #d7decf;
        border-left: 6px solid #1f6f50;
        padding: 14px 16px;
        border-radius: 8px;
        box-shadow: 0 1px 6px rgba(20, 35, 25, 0.08);
    }
    h1, h2, h3 {
        color: #163b2c;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def load_data():
    df = pd.read_csv("data/bay_area_modeling_table.csv", low_memory=False)
    df = df[df.campus == "Universitywide"].copy()
    return df


def window_summary(df, label, years):
    window = df[df.fall_term.isin(years)]
    schools = (
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
    schools = schools[(schools.applicants > 0) & schools.applicant_gpa.notna()]
    schools["admit_rate"] = schools.admits / schools.applicants
    schools["yield_rate"] = schools.enrollees / schools.admits
    schools["enrollment_rate"] = schools.enrollees / schools.applicants
    schools["window"] = label
    return schools


def weighted_slope(x, y, w):
    mask = x.notna() & y.notna() & w.notna() & (w > 0)
    x = x[mask]
    y = y[mask]
    w = w[mask]
    x_bar = np.average(x, weights=w)
    y_bar = np.average(y, weights=w)
    return np.sum(w * (x - x_bar) * (y - y_bar)) / np.sum(w * (x - x_bar) ** 2)


def weighted_mean(df, col, weight):
    usable = df[df[col].notna() & df[weight].notna() & (df[weight] > 0)]
    if usable.empty:
        return np.nan
    return np.average(usable[col], weights=usable[weight])


df = load_data()
pre = window_summary(df, "Pre-test-blind", PRE_YEARS)
post = window_summary(df, "Post-test-blind", POST_YEARS)

changes = pre.merge(
    post,
    on=["cds_code", "high_school", "city", "county"],
    suffixes=("_pre", "_post"),
)
changes["admit_rate_change"] = changes.admit_rate_post - changes.admit_rate_pre
changes["yield_rate_change"] = changes.yield_rate_post - changes.yield_rate_pre
changes["enrollment_rate_change"] = changes.enrollment_rate_post - changes.enrollment_rate_pre
changes["enrollee_gpa_change"] = changes.enrollee_gpa_post - changes.enrollee_gpa_pre
changes["post_minus_pre_score"] = changes.admit_rate_change * np.sqrt(changes.applicants_post)

st.title("UC Admissions Scouting Report")
st.caption("After UC changed the rules, which Bay Area high schools gained field position?")

left, right = st.columns([1, 3])
with left:
    county = st.multiselect("County", sorted(changes.county.dropna().unique()))
    min_applicants = st.slider("Minimum post-period applicants", 0, 800, 25, step=25)
    selected_school = st.selectbox("School card", sorted(changes.high_school.unique()))

filtered = changes[changes.applicants_post >= min_applicants].copy()
if county:
    filtered = filtered[filtered.county.isin(county)]

pre_rate = pre.admits.sum() / pre.applicants.sum()
post_rate = post.admits.sum() / post.applicants.sum()
pre_slope = weighted_slope(pre.applicant_gpa, pre.admit_rate, pre.applicants)
post_slope = weighted_slope(post.applicant_gpa, post.admit_rate, post.applicants)
enrollee_gpa_change = weighted_mean(changes, "enrollee_gpa_change", "enrollees_post")

with right:
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Before rule change", f"{pre_rate:.1%}")
    m2.metric("After rule change", f"{post_rate:.1%}", f"{post_rate - pre_rate:+.1%}")
    m3.metric("GPA advantage index", f"{post_slope:.3f}", f"{post_slope - pre_slope:+.3f}")
    m4.metric("Enrollee GPA shift", f"{enrollee_gpa_change:+.3f}")

    st.markdown(
        "The post-test-blind period looks like a rule change with real scoreboard movement: admit rates rose, the GPA advantage got weaker, and enrolled-student GPA barely moved. In plain English, chances changed more than the academic profile of students who enrolled."
    )

chart_data = pd.concat([pre, post], ignore_index=True)
if county:
    chart_data = chart_data[chart_data.county.isin(county)]
chart_data = chart_data[chart_data.applicants >= min_applicants]

fig = px.scatter(
    chart_data,
    x="applicant_gpa",
    y="admit_rate",
    color="window",
    size="applicants",
    hover_name="high_school",
    hover_data=["city", "county", "applicants", "admits", "enrollees"],
    trendline="ols",
    labels={
        "applicant_gpa": "Average applicant GPA",
        "admit_rate": "UC admit rate",
        "window": "Time period",
    },
)
fig.update_yaxes(tickformat=".0%")
st.plotly_chart(fig, use_container_width=True)

st.subheader("Scouting card")
card = changes[changes.high_school == selected_school].iloc[0]
c1, c2, c3, c4 = st.columns(4)
c1.metric("Post-policy lift", f"{card.admit_rate_change:+.1%}")
c2.metric("Applicant growth", f"{card.applicants_post - card.applicants_pre:+.0f}")
c3.metric("Yield change", f"{card.yield_rate_change:+.1%}")
c4.metric("Enrollee GPA change", f"{card.enrollee_gpa_change:+.3f}")
st.write(
    f"{card.high_school} in {card.city}, {card.county}: admit rate moved from "
    f"{card.admit_rate_pre:.1%} before test-blind to {card.admit_rate_post:.1%} after test-blind."
)

st.subheader("Biggest risers")
show = filtered.sort_values("post_minus_pre_score", ascending=False)[
    [
        "high_school",
        "city",
        "county",
        "applicants_pre",
        "applicants_post",
        "admit_rate_pre",
        "admit_rate_post",
        "admit_rate_change",
        "yield_rate_change",
        "enrollee_gpa_change",
    ]
].head(25)

st.dataframe(
    show,
    use_container_width=True,
    hide_index=True,
    column_config={
        "admit_rate_pre": st.column_config.NumberColumn("Pre admit rate", format="%.3f"),
        "admit_rate_post": st.column_config.NumberColumn("Post admit rate", format="%.3f"),
        "admit_rate_change": st.column_config.NumberColumn("Admit rate change", format="%.3f"),
        "yield_rate_change": st.column_config.NumberColumn("Yield change", format="%.3f"),
        "enrollee_gpa_change": st.column_config.NumberColumn("Enrollee GPA change", format="%.3f"),
    },
)

st.subheader("Context groups")
group_choice = st.radio("Scouting split", ["Applicant GPA", "FRPM", "a-g completion"], horizontal=True)
metric_labels = {
    "Admit rate change": "admit_rate_change",
    "Yield change": "yield_rate_change",
    "Enrollee GPA change": "enrollee_gpa_change",
}
metric_label = st.selectbox("Compare stat", list(metric_labels))
metric = metric_labels[metric_label]

if group_choice == "Applicant GPA":
    source_col = "applicant_gpa_pre"
elif group_choice == "FRPM":
    source_col = "frpm_pct_pre"
else:
    source_col = "ag_completion_rate_pre"

grouped = filtered.copy()
grouped["group"] = pd.qcut(grouped[source_col], 3, labels=["Low", "Middle", "High"])
group_rows = []
for label, g in grouped.groupby("group", observed=True):
    group_rows.append({"group": label, "schools": len(g), metric: weighted_mean(g, metric, "applicants_post")})
grouped = pd.DataFrame(group_rows)

bar = px.bar(grouped, x="group", y=metric, text=metric)
if "gpa" in metric:
    bar.update_traces(texttemplate="%{text:.3f}", textposition="outside")
else:
    bar.update_traces(texttemplate="%{text:.1%}", textposition="outside")
    bar.update_yaxes(tickformat=".0%")
st.plotly_chart(bar, use_container_width=True)
