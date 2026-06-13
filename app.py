import streamlit as st
import pandas as pd
import plotly.express as px

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title="Lead Follow-Up Survey Dashboard",
    layout="wide"
)

# =========================
# BRAND COLORS
# =========================

RED = "#D32F2F"
DARK_GRAY = "#424242"
MID_GRAY = "#757575"
LIGHT_GRAY = "#F5F5F5"
GREEN = "#2E7D32"

# =========================
# CSS
# =========================

st.markdown(
    f"""
    <style>
    .main {{
        background-color: #FAFAFA;
    }}

    .title {{
        font-size: 38px;
        font-weight: 800;
        color: {DARK_GRAY};
        margin-bottom: 0px;
    }}

    .title span {{
        color: {RED};
    }}

    .subtitle {{
        font-size: 18px;
        color: {MID_GRAY};
        margin-bottom: 30px;
    }}

    .kpi-card {{
        background-color: white;
        padding: 22px 24px;
        border-radius: 18px;
        border: 1px solid #E0E0E0;
        box-shadow: 0px 2px 8px rgba(0,0,0,0.04);
        height: 150px;
    }}

    .kpi-title {{
        font-size: 13px;
        color: {MID_GRAY};
        text-transform: uppercase;
        font-weight: 700;
        letter-spacing: 0.8px;
    }}

    .kpi-value {{
        font-size: 42px;
        color: {RED};
        font-weight: 800;
        margin-top: 8px;
        margin-bottom: 0px;
    }}

    .kpi-subtitle {{
        font-size: 14px;
        color: {MID_GRAY};
        margin-top: 0px;
    }}

    .section-card {{
        background-color: white;
        padding: 22px;
        border-radius: 18px;
        border: 1px solid #E0E0E0;
        box-shadow: 0px 2px 8px rgba(0,0,0,0.04);
        margin-bottom: 20px;
    }}

    .section-title {{
        font-size: 18px;
        color: {DARK_GRAY};
        font-weight: 800;
        text-transform: uppercase;
        margin-bottom: 4px;
    }}

    .section-subtitle {{
        font-size: 14px;
        color: {MID_GRAY};
        margin-bottom: 18px;
    }}

    .insight-box {{
        background-color: #FFF5F5;
        border-left: 6px solid {RED};
        padding: 18px 22px;
        border-radius: 12px;
        color: {DARK_GRAY};
        font-size: 15px;
        margin-top: 16px;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# =========================
# LOAD DATA
# =========================

@st.cache_data
def load_data():
    lead_summary = pd.read_csv("lead_summary.csv")
    survey_detail = pd.read_csv("survey_detail.csv")

    lead_summary["export_date"] = pd.to_datetime(
        lead_summary["export_date"],
        errors="coerce"
    )

    survey_detail["export_date"] = pd.to_datetime(
        survey_detail["export_date"],
        errors="coerce"
    )

    # Remove null country for stakeholder version
    lead_summary = lead_summary[lead_summary["country"].notna()].copy()
    survey_detail = survey_detail[survey_detail["country"].notna()].copy()

    return lead_summary, survey_detail

lead_summary, survey_detail = load_data()

# =========================
# SIDEBAR FILTERS
# =========================

st.sidebar.title("Filters")

countries = sorted(lead_summary["country"].dropna().unique())

selected_countries = st.sidebar.multiselect(
    "Country / Portal",
    options=countries,
    default=countries
)

min_date = lead_summary["export_date"].min()
max_date = lead_summary["export_date"].max()

date_range = st.sidebar.date_input(
    "Export Date",
    value=(min_date, max_date)
)

if len(date_range) == 2:
    start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
else:
    start_date, end_date = min_date, max_date

lead_f = lead_summary[
    (lead_summary["country"].isin(selected_countries)) &
    (lead_summary["export_date"] >= start_date) &
    (lead_summary["export_date"] <= end_date)
].copy()

detail_f = survey_detail[
    (survey_detail["country"].isin(selected_countries)) &
    (survey_detail["export_date"] >= start_date) &
    (survey_detail["export_date"] <= end_date)
].copy()

# =========================
# KPI HELPERS
# =========================

def safe_divide(a, b):
    return a / b if b else 0

def pct(x):
    return f"{x:.1%}"

def kpi_card(title, value, subtitle):
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">{title}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-subtitle">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# =========================
# METRICS
# =========================

surveys_sent = int(lead_f["survey_sent"].sum())
q1_responses = int(lead_f["answered_contact_question"].sum())
contacted = int(lead_f["contacted"].sum())
not_contacted = int(lead_f["not_contacted"].sum())
purchased = int(lead_f["purchased"].sum())
recoverable = int(lead_f["recoverable_lead"].sum())

response_rate = safe_divide(q1_responses, surveys_sent)
contact_rate = safe_divide(contacted, q1_responses)
not_contacted_rate = safe_divide(not_contacted, q1_responses)
purchase_rate = safe_divide(purchased, q1_responses)
recovery_rate = safe_divide(recoverable, q1_responses)

# =========================
# HEADER
# =========================

st.markdown(
    """
    <div class="title">Lead Follow-Up <span>Survey Dashboard</span></div>
    <div class="subtitle">
    Understand seller responsiveness, purchase outcomes and recovery opportunities
    </div>
    """,
    unsafe_allow_html=True
)

# =========================
# KPI ROW
# =========================

c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    kpi_card("Surveys Sent", f"{surveys_sent:,}", "Total users reached")

with c2:
    kpi_card("Response Rate", pct(response_rate), f"{q1_responses:,} of {surveys_sent:,}")

with c3:
    kpi_card("Contact Rate", pct(contact_rate), f"{contacted:,} of {q1_responses:,}")

with c4:
    kpi_card("Purchase Rate", pct(purchase_rate), f"{purchased:,} of {q1_responses:,}")

with c5:
    kpi_card("Recoverable Leads", f"{recoverable:,}", f"{pct(recovery_rate)} of respondents")

st.write("")

# =========================
# ROW 2: FUNNEL + CONTACT + COMPLETION
# =========================

left, middle, right = st.columns([1.2, 1, 1])

with left:
    st.markdown(
        """
        <div class="section-card">
        <div class="section-title">Survey Funnel Overview</div>
        <div class="section-subtitle">From survey sent to recovery opportunity</div>
        """,
        unsafe_allow_html=True
    )

    funnel_df = pd.DataFrame({
        "Step": [
            "Surveys Sent",
            "Q1 Responses",
            "Contacted by Seller",
            "Purchase Outcome Reached",
            "Recoverable Leads"
        ],
        "Leads": [
            surveys_sent,
            q1_responses,
            contacted,
            int(lead_f["answered_purchase_outcome"].sum()),
            recoverable
        ]
    })

    fig = px.funnel(
        funnel_df,
        y="Step",
        x="Leads",
        color_discrete_sequence=[RED]
    )

    fig.update_layout(
        height=380,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(color=DARK_GRAY)
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

with middle:
    st.markdown(
        """
        <div class="section-card">
        <div class="section-title">Contact Status</div>
        <div class="section-subtitle">Among respondents</div>
        """,
        unsafe_allow_html=True
    )

    contact_df = pd.DataFrame({
        "Status": ["Contacted", "Not Contacted"],
        "Leads": [contacted, not_contacted]
    })

    fig = px.pie(
        contact_df,
        values="Leads",
        names="Status",
        hole=0.58,
        color="Status",
        color_discrete_map={
            "Contacted": RED,
            "Not Contacted": DARK_GRAY
        }
    )

    fig.update_traces(
        textinfo="percent+label",
        textfont_size=13
    )

    fig.update_layout(
        height=380,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="white",
        plot_bgcolor="white",
        legend=dict(orientation="h", y=-0.1)
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        f"""
        <div class="insight-box">
        <b>{pct(not_contacted_rate)}</b> of respondents reported they were not contacted by the seller.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown(
        """
        <div class="section-card">
        <div class="section-title">Survey Completion Status</div>
        <div class="section-subtitle">Where leads drop off in the survey</div>
        """,
        unsafe_allow_html=True
    )

    status_df = (
        lead_f
        .groupby("survey_status", dropna=False)
        .agg(leads=("lead_id", "nunique"))
        .reset_index()
        .sort_values("leads", ascending=True)
    )

    fig = px.bar(
        status_df,
        x="leads",
        y="survey_status",
        orientation="h",
        text="leads",
        color_discrete_sequence=[RED]
    )

    fig.update_traces(textposition="outside")

    fig.update_layout(
        height=380,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="white",
        plot_bgcolor="white",
        xaxis_title="Leads",
        yaxis_title=None,
        font=dict(color=DARK_GRAY)
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

# =========================
# ROW 3: OUTCOME + RECOVERY
# =========================

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        """
        <div class="section-card">
        <div class="section-title">Purchase Outcome</div>
        <div class="section-subtitle">Among leads who reached the outcome question</div>
        """,
        unsafe_allow_html=True
    )

    outcome_df = pd.DataFrame({
        "Outcome": [
            "In Progress",
            "Did Not Proceed",
            "Lost Seller Response",
            "Purchased"
        ],
        "Leads": [
            int(lead_f["in_progress"].sum()),
            int(lead_f["did_not_proceed"].sum()),
            int(lead_f["lost_seller_response"].sum()),
            int(lead_f["purchased"].sum())
        ]
    }).sort_values("Leads", ascending=True)

    fig = px.bar(
        outcome_df,
        x="Leads",
        y="Outcome",
        orientation="h",
        text="Leads",
        color_discrete_sequence=[RED]
    )

    fig.update_traces(textposition="outside")

    fig.update_layout(
        height=360,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="white",
        plot_bgcolor="white",
        xaxis_title="Leads",
        yaxis_title=None
    )

    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown(
        """
        <div class="section-card">
        <div class="section-title">Recovery Opportunity Result</div>
        <div class="section-subtitle">Among leads who answered the recovery question</div>
        """,
        unsafe_allow_html=True
    )

    recovery_df = pd.DataFrame({
        "Recovery Outcome": [
            "Interested in Alternatives",
            "Prefer to Wait",
            "Not Interested"
        ],
        "Leads": [
            int(lead_f["recoverable_lead"].sum()),
            int(lead_f["prefer_to_wait"].sum()),
            int(lead_f["not_interested"].sum())
        ]
    }).sort_values("Leads", ascending=True)

    fig = px.bar(
        recovery_df,
        x="Leads",
        y="Recovery Outcome",
        orientation="h",
        text="Leads",
        color_discrete_sequence=[RED]
    )

    fig.update_traces(textposition="outside")

    fig.update_layout(
        height=360,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="white",
        plot_bgcolor="white",
        xaxis_title="Leads",
        yaxis_title=None
    )

    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col3:
    st.markdown(
        """
        <div class="section-card">
        <div class="section-title">Recovery by Origin</div>
        <div class="section-subtitle">Where recoverable leads come from</div>
        """,
        unsafe_allow_html=True
    )

    recovery_origin = (
        detail_f[
            (detail_f["business_outcome"] == "Recoverable Lead")
            & (detail_f["block"].str.contains("Recovery", na=False))
        ]
        .groupby("block", dropna=False)
        .agg(leads=("lead_id", "nunique"))
        .reset_index()
        .sort_values("leads", ascending=True)
    )

    recovery_origin["block"] = recovery_origin["block"].str.replace("Recovery - ", "", regex=False)

    fig = px.bar(
        recovery_origin,
        x="leads",
        y="block",
        orientation="h",
        text="leads",
        color_discrete_sequence=[RED]
    )

    fig.update_traces(textposition="outside")

    fig.update_layout(
        height=360,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="white",
        plot_bgcolor="white",
        xaxis_title="Recoverable Leads",
        yaxis_title=None
    )

    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# =========================
# COUNTRY COMPARISON
# =========================

st.markdown(
    """
    <div class="section-card">
    <div class="section-title">Country Comparison</div>
    <div class="section-subtitle">Key rates by country / portal</div>
    """,
    unsafe_allow_html=True
)

country_summary = (
    lead_f
    .groupby("country", dropna=False)
    .agg(
        surveys_sent=("survey_sent", "sum"),
        q1_responses=("answered_contact_question", "sum"),
        contacted=("contacted", "sum"),
        not_contacted=("not_contacted", "sum"),
        purchased=("purchased", "sum"),
        recoverable=("recoverable_lead", "sum")
    )
    .reset_index()
)

country_summary["Response Rate"] = country_summary["q1_responses"] / country_summary["surveys_sent"]
country_summary["Contact Rate"] = country_summary["contacted"] / country_summary["q1_responses"]
country_summary["Not Contacted Rate"] = country_summary["not_contacted"] / country_summary["q1_responses"]
country_summary["Purchase Rate"] = country_summary["purchased"] / country_summary["q1_responses"]
country_summary["Recovery Opportunity Rate"] = country_summary["recoverable"] / country_summary["q1_responses"]

rate_long = country_summary.melt(
    id_vars="country",
    value_vars=[
        "Response Rate",
        "Contact Rate",
        "Not Contacted Rate",
        "Purchase Rate",
        "Recovery Opportunity Rate"
    ],
    var_name="Metric",
    value_name="Rate"
)

fig = px.bar(
    rate_long,
    x="Rate",
    y="Metric",
    color="country",
    orientation="h",
    barmode="group",
    text=rate_long["Rate"].apply(lambda x: f"{x:.1%}"),
    color_discrete_sequence=[RED, DARK_GRAY, MID_GRAY]
)

fig.update_layout(
    height=420,
    margin=dict(l=10, r=10, t=10, b=10),
    paper_bgcolor="white",
    plot_bgcolor="white",
    xaxis_tickformat=".0%",
    xaxis_title="Rate",
    yaxis_title=None,
    legend_title=None
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)

# =========================
# KEY TAKEAWAYS
# =========================

st.markdown(
    f"""
    <div class="section-card">
    <div class="section-title">Key Takeaways</div>
    <div class="section-subtitle">Executive reading of the survey results</div>

    <ul style="font-size:16px; color:{DARK_GRAY}; line-height:1.8;">
        <li><b>Seller contact is the main bottleneck:</b> {pct(not_contacted_rate)} of respondents reported no seller contact.</li>
        <li><b>Recovery opportunity is significant:</b> {recoverable:,} leads are open to receiving alternative vehicle options.</li>
        <li><b>Purchase completion is still low:</b> only {pct(purchase_rate)} of respondents reported completing a purchase.</li>
        <li><b>Use country filters</b> to identify where seller follow-up and recovery programs should be prioritized.</li>
    </ul>
    </div>
    """,
    unsafe_allow_html=True
)