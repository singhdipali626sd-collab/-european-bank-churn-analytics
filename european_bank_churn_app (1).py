import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="European Bank | Churn Analytics",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* Header */
.main-header {
    background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
    padding: 2rem 2.5rem;
    border-radius: 16px;
    margin-bottom: 1.5rem;
    color: white;
}
.main-header h1 { font-size: 2rem; font-weight: 700; margin: 0; letter-spacing: -0.5px; }
.main-header p  { font-size: 0.95rem; opacity: 0.75; margin: 0.4rem 0 0; }

/* KPI Cards */
.kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-bottom: 1.5rem; }
.kpi-card {
    background: white;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    border-left: 4px solid var(--accent);
    box-shadow: 0 2px 8px rgba(0,0,0,0.07);
}
.kpi-card .label { font-size: 0.75rem; font-weight: 600; color: #6b7280; text-transform: uppercase; letter-spacing: 0.05em; }
.kpi-card .value { font-size: 1.9rem; font-weight: 700; color: #111827; line-height: 1.2; margin-top: 0.3rem; }
.kpi-card .delta { font-size: 0.8rem; margin-top: 0.2rem; }
.kpi-card.red   { --accent: #ef4444; }
.kpi-card.amber { --accent: #f59e0b; }
.kpi-card.blue  { --accent: #3b82f6; }
.kpi-card.green { --accent: #10b981; }

/* Section headers */
.section-title {
    font-size: 1.1rem; font-weight: 600; color: #111827;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid #f3f4f6;
    margin-bottom: 1rem;
}

/* Sidebar */
[data-testid="stSidebar"] { background: #0f2027 !important; }
[data-testid="stSidebar"] * { color: #e5e7eb !important; }
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stMultiSelect label { color: #9ca3af !important; font-size: 0.8rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }
[data-testid="stSidebar"] h2 { color: white !important; font-size: 1rem !important; }
[data-testid="stSidebar"] .stSlider label { color: #9ca3af !important; }

/* Chart containers */
.chart-container {
    background: white; border-radius: 12px;
    padding: 1.25rem; box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    margin-bottom: 1rem;
}

/* Tables */
.dataframe { border-radius: 8px !important; overflow: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Data generation ───────────────────────────────────────────────────────────
@st.cache_data
def generate_data(n=10000, seed=42):
    rng = np.random.default_rng(seed)
    countries  = rng.choice(["France", "Germany", "Spain"], n, p=[0.50, 0.25, 0.25])
    genders    = rng.choice(["Male", "Female"], n, p=[0.545, 0.455])
    ages       = np.clip(rng.normal(38, 12, n).astype(int), 18, 92)
    tenures    = rng.integers(0, 11, n)
    credit_scores = np.clip(rng.normal(650, 97, n).astype(int), 350, 850)
    salaries   = np.clip(rng.normal(100000, 50000, n), 11_500, 199_999)
    n_products = rng.choice([1, 2, 3, 4], n, p=[0.50, 0.46, 0.03, 0.01])
    has_cc     = rng.choice([0, 1], n, p=[0.29, 0.71])
    is_active  = rng.choice([0, 1], n, p=[0.49, 0.51])

    # Balance: ~30% zero-balance
    zero_mask  = rng.random(n) < 0.30
    balance    = np.where(zero_mask, 0.0, np.clip(rng.normal(76000, 62000, n), 0, 250000))

    # Churn probability (logistic-ish)
    logit = (
        -1.5
        + 0.4  * (countries == "Germany").astype(float)
        - 0.2  * (countries == "Spain").astype(float)
        + 0.03 * np.clip((ages - 40) / 10, -3, 3)
        - 0.25 * is_active
        + 0.35 * (n_products > 2).astype(float)
        - 0.1  * has_cc
        + 0.3  * (genders == "Female").astype(float)
        + rng.normal(0, 0.4, n)
    )
    prob_churn = 1 / (1 + np.exp(-logit))
    exited     = (rng.random(n) < prob_churn).astype(int)

    df = pd.DataFrame({
        "CustomerId":      np.arange(15634602, 15634602 + n),
        "CreditScore":     credit_scores,
        "Geography":       countries,
        "Gender":          genders,
        "Age":             ages,
        "Tenure":          tenures,
        "Balance":         balance.round(2),
        "NumOfProducts":   n_products,
        "HasCrCard":       has_cc,
        "IsActiveMember":  is_active,
        "EstimatedSalary": salaries.round(2),
        "Exited":          exited,
    })

    # Derived segments
    df["AgeGroup"]     = pd.cut(df["Age"],    bins=[0, 29, 45, 60, 200],
                                labels=["<30", "30–45", "46–60", "60+"])
    df["CreditBand"]   = pd.cut(df["CreditScore"], bins=[0, 579, 719, 850],
                                labels=["Low (<580)", "Medium (580–719)", "High (720+)"])
    df["TenureGroup"]  = pd.cut(df["Tenure"],  bins=[-1, 2, 6, 10],
                                labels=["New (0–2y)", "Mid-term (3–6y)", "Long-term (7+y)"])
    df["BalanceSegment"] = pd.cut(df["Balance"], bins=[-1, 0, 50000, 1e9],
                                  labels=["Zero Balance", "Low Balance", "High Balance"])
    df["HighValue"]    = (df["Balance"] > df["Balance"].quantile(0.75)).astype(int)
    return df

df_full = generate_data()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏦 Churn Analytics")
    st.markdown("---")
    st.markdown("### Segment Filters")

    geo_opts = st.multiselect("Geography", ["France", "Germany", "Spain"],
                               default=["France", "Germany", "Spain"])
    gender_opts = st.multiselect("Gender", ["Male", "Female"], default=["Male", "Female"])
    age_opts = st.multiselect("Age Group", ["<30", "30–45", "46–60", "60+"],
                               default=["<30", "30–45", "46–60", "60+"])
    credit_opts = st.multiselect("Credit Band",
                                  ["Low (<580)", "Medium (580–719)", "High (720+)"],
                                  default=["Low (<580)", "Medium (580–719)", "High (720+)"])
    balance_opts = st.multiselect("Balance Segment",
                                   ["Zero Balance", "Low Balance", "High Balance"],
                                   default=["Zero Balance", "Low Balance", "High Balance"])
    tenure_opts = st.multiselect("Tenure Group",
                                  ["New (0–2y)", "Mid-term (3–6y)", "Long-term (7+y)"],
                                  default=["New (0–2y)", "Mid-term (3–6y)", "Long-term (7+y)"])
    active_filter = st.selectbox("Membership Status", ["All", "Active Only", "Inactive Only"])

    st.markdown("---")
    st.markdown("### Display")
    show_pct = st.toggle("Show as Percentages", value=True)

# ── Apply filters ─────────────────────────────────────────────────────────────
df = df_full.copy()
if geo_opts:     df = df[df["Geography"].isin(geo_opts)]
if gender_opts:  df = df[df["Gender"].isin(gender_opts)]
if age_opts:     df = df[df["AgeGroup"].isin(age_opts)]
if credit_opts:  df = df[df["CreditBand"].isin(credit_opts)]
if balance_opts: df = df[df["BalanceSegment"].isin(balance_opts)]
if tenure_opts:  df = df[df["TenureGroup"].isin(tenure_opts)]
if active_filter == "Active Only":   df = df[df["IsActiveMember"] == 1]
elif active_filter == "Inactive Only": df = df[df["IsActiveMember"] == 0]

# ── Colour palette ────────────────────────────────────────────────────────────
PALETTE   = {"Churned": "#ef4444", "Retained": "#3b82f6"}
GEO_COLORS = {"France": "#3b82f6", "Germany": "#ef4444", "Spain": "#f59e0b"}

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🏦 Customer Churn Pattern Analytics</h1>
    <p>European Banking — Segmentation-Driven Churn Intelligence Dashboard</p>
</div>
""", unsafe_allow_html=True)

# ── Navigation ────────────────────────────────────────────────────────────────
tabs = st.tabs(["📊 Overview", "🌍 Geography", "👥 Demographics", "💰 High-Value Customers", "🔍 Segment Deep-Dive"])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — OVERVIEW
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[0]:
    total        = len(df)
    churned      = df["Exited"].sum()
    retained     = total - churned
    churn_rate   = churned / total * 100 if total else 0
    hv_churn     = df[df["HighValue"] == 1]["Exited"].mean() * 100 if len(df[df["HighValue"]==1]) else 0
    inactive_churn = df[df["IsActiveMember"]==0]["Exited"].mean() * 100 if len(df[df["IsActiveMember"]==0]) else 0
    avg_balance_churned = df[df["Exited"]==1]["Balance"].mean()

    # KPI row
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Overall Churn Rate", f"{churn_rate:.1f}%",
                  delta=f"{churn_rate - 20.4:.1f}pp vs baseline", delta_color="inverse")
    with c2:
        st.metric("Churned Customers", f"{churned:,}", delta=f"of {total:,} total")
    with c3:
        st.metric("High-Value Churn Rate", f"{hv_churn:.1f}%",
                  delta="Top-quartile balance", delta_color="inverse")
    with c4:
        st.metric("Inactive Member Churn", f"{inactive_churn:.1f}%",
                  delta="Engagement risk", delta_color="inverse")

    st.markdown("")
    col_a, col_b = st.columns([1, 2])

    with col_a:
        st.markdown('<div class="section-title">Churn vs Retention Split</div>', unsafe_allow_html=True)
        fig_donut = go.Figure(go.Pie(
            labels=["Retained", "Churned"],
            values=[retained, churned],
            hole=0.62,
            marker_colors=["#3b82f6", "#ef4444"],
            textinfo="label+percent",
            textfont_size=13,
        ))
        fig_donut.add_annotation(
            text=f"<b>{churn_rate:.1f}%</b><br>Churn",
            x=0.5, y=0.5, showarrow=False, font_size=18, align="center"
        )
        fig_donut.update_layout(
            showlegend=False, height=320, margin=dict(t=10, b=10, l=10, r=10),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    with col_b:
        st.markdown('<div class="section-title">Churn Rate by Key Dimensions</div>', unsafe_allow_html=True)
        dims = {
            "Geography":      "Geography",
            "Age Group":      "AgeGroup",
            "Credit Band":    "CreditBand",
            "Tenure Group":   "TenureGroup",
            "Balance Seg.":   "BalanceSegment",
        }
        rows = []
        for label, col in dims.items():
            grp = df.groupby(col, observed=True)["Exited"].agg(["mean","sum","count"]).reset_index()
            grp.columns = [col, "ChurnRate", "Churned", "Total"]
            grp["Dimension"] = label
            grp.rename(columns={col: "Segment"}, inplace=True)
            rows.append(grp)
        bar_df = pd.concat(rows)
        bar_df["ChurnPct"] = (bar_df["ChurnRate"] * 100).round(1)
        bar_df["Segment"] = bar_df["Segment"].astype(str)

        fig_bar = px.bar(
            bar_df, x="ChurnPct", y="Segment", color="Dimension",
            orientation="h", text="ChurnPct",
            color_discrete_sequence=px.colors.qualitative.Bold,
        )
        fig_bar.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig_bar.update_layout(
            height=370, showlegend=True, xaxis_title="Churn Rate (%)",
            yaxis_title="", margin=dict(t=10, b=10, l=0, r=60),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(gridcolor="#f3f4f6"),
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # Financial summary
    st.markdown('<div class="section-title">Financial Profile — Churned vs Retained</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        fin_df = df.groupby("Exited").agg(
            AvgBalance=("Balance", "mean"),
            AvgSalary=("EstimatedSalary", "mean"),
            AvgCreditScore=("CreditScore", "mean"),
            AvgAge=("Age", "mean"),
        ).reset_index()
        fin_df["Status"] = fin_df["Exited"].map({0: "Retained", 1: "Churned"})

        fig_fin = go.Figure()
        metrics = ["AvgBalance", "AvgSalary"]
        for m in metrics:
            fig_fin.add_trace(go.Bar(
                x=fin_df["Status"], y=fin_df[m],
                name=m.replace("Avg","Avg "),
                marker_color=["#3b82f6","#ef4444"] if m == metrics[0] else ["#60a5fa","#f87171"],
            ))
        fig_fin.update_layout(
            barmode="group", height=300, title="Avg Balance & Salary",
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(gridcolor="#f3f4f6"), margin=dict(t=40,b=10,l=0,r=0),
        )
        st.plotly_chart(fig_fin, use_container_width=True)

    with col2:
        fig_credit = go.Figure()
        for status, color in [("Churned", "#ef4444"), ("Retained", "#3b82f6")]:
            sub = df[df["Exited"] == (1 if status=="Churned" else 0)]
            fig_credit.add_trace(go.Histogram(
                x=sub["CreditScore"], name=status, opacity=0.72,
                marker_color=color, nbinsx=30,
            ))
        fig_credit.update_layout(
            barmode="overlay", height=300, title="Credit Score Distribution",
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(gridcolor="#f3f4f6"), xaxis_title="Credit Score",
            margin=dict(t=40,b=10,l=0,r=0),
        )
        st.plotly_chart(fig_credit, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — GEOGRAPHY
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[1]:
    st.markdown('<div class="section-title">Geographic Churn Risk Analysis</div>', unsafe_allow_html=True)

    geo_df = df.groupby("Geography")["Exited"].agg(
        ChurnRate="mean", Churned="sum", Total="count"
    ).reset_index()
    geo_df["ChurnPct"] = (geo_df["ChurnRate"] * 100).round(2)
    geo_df["RetainedPct"] = (100 - geo_df["ChurnPct"]).round(2)
    geo_df["Color"] = geo_df["Geography"].map(GEO_COLORS)

    c1, c2, c3 = st.columns(3)
    for col, country in zip([c1, c2, c3], ["France", "Germany", "Spain"]):
        row = geo_df[geo_df["Geography"] == country]
        if len(row):
            r = row.iloc[0]
            col.metric(f"🏳️ {country}", f"{r['ChurnPct']:.1f}%",
                       delta=f"{r['Churned']:,} churned of {r['Total']:,}")

    st.markdown("")
    col_left, col_right = st.columns(2)

    with col_left:
        fig_geo = go.Figure()
        fig_geo.add_trace(go.Bar(
            x=geo_df["Geography"], y=geo_df["RetainedPct"],
            name="Retained", marker_color="#3b82f6",
        ))
        fig_geo.add_trace(go.Bar(
            x=geo_df["Geography"], y=geo_df["ChurnPct"],
            name="Churned", marker_color="#ef4444",
        ))
        fig_geo.update_layout(
            barmode="stack", height=380, title="Churn vs Retention by Country (%)",
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(gridcolor="#f3f4f6", title="Share (%)"),
            margin=dict(t=50, b=10, l=0, r=0),
        )
        st.plotly_chart(fig_geo, use_container_width=True)

    with col_right:
        # Age × Geography heatmap
        hm_df = df.groupby(["Geography", "AgeGroup"], observed=True)["Exited"].mean().reset_index()
        hm_df.columns = ["Geography", "AgeGroup", "ChurnRate"]
        hm_df["ChurnPct"] = (hm_df["ChurnRate"] * 100).round(1)
        pivot = hm_df.pivot(index="Geography", columns="AgeGroup", values="ChurnPct").fillna(0)

        fig_hm = px.imshow(
            pivot,
            color_continuous_scale=["#dbeafe", "#3b82f6", "#1d4ed8", "#ef4444"],
            title="Churn Rate Heatmap: Geography × Age Group (%)",
            text_auto=".1f",
            aspect="auto",
        )
        fig_hm.update_layout(
            height=380, paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(t=50, b=10, l=0, r=0),
            coloraxis_colorbar=dict(title="Churn %"),
        )
        st.plotly_chart(fig_hm, use_container_width=True)

    # Products by geography
    st.markdown('<div class="section-title">Product Adoption & Churn by Country</div>', unsafe_allow_html=True)
    prod_geo = df.groupby(["Geography", "NumOfProducts"])["Exited"].agg(
        ChurnRate="mean", Count="count"
    ).reset_index()
    prod_geo["ChurnPct"] = (prod_geo["ChurnRate"] * 100).round(1)
    prod_geo["NumOfProducts"] = prod_geo["NumOfProducts"].astype(str) + " product(s)"

    fig_prod = px.bar(
        prod_geo, x="NumOfProducts", y="ChurnPct", color="Geography",
        barmode="group", text="ChurnPct",
        color_discrete_map=GEO_COLORS,
        title="Churn Rate by Number of Products per Geography",
    )
    fig_prod.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig_prod.update_layout(
        height=350, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(gridcolor="#f3f4f6", title="Churn Rate (%)"),
        margin=dict(t=50, b=10, l=0, r=0),
    )
    st.plotly_chart(fig_prod, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — DEMOGRAPHICS
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[2]:
    st.markdown('<div class="section-title">Demographic Churn Analysis</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        # Gender
        gen_df = df.groupby("Gender")["Exited"].agg(
            ChurnRate="mean", Churned="sum", Total="count"
        ).reset_index()
        gen_df["ChurnPct"] = (gen_df["ChurnRate"] * 100).round(1)

        fig_gen = px.bar(
            gen_df, x="Gender", y="ChurnPct", color="Gender",
            text="ChurnPct", color_discrete_map={"Male": "#3b82f6", "Female": "#ec4899"},
            title="Churn Rate by Gender",
        )
        fig_gen.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig_gen.update_layout(
            showlegend=False, height=320,
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(gridcolor="#f3f4f6", title="Churn Rate (%)"),
            margin=dict(t=50, b=10, l=0, r=0),
        )
        st.plotly_chart(fig_gen, use_container_width=True)

    with col2:
        # Active member
        act_df = df.groupby("IsActiveMember")["Exited"].agg(
            ChurnRate="mean", Count="count"
        ).reset_index()
        act_df["IsActiveMember"] = act_df["IsActiveMember"].map({0: "Inactive", 1: "Active"})
        act_df["ChurnPct"] = (act_df["ChurnRate"] * 100).round(1)

        fig_act = px.bar(
            act_df, x="IsActiveMember", y="ChurnPct", color="IsActiveMember",
            text="ChurnPct", color_discrete_map={"Active": "#10b981", "Inactive": "#f59e0b"},
            title="Churn Rate by Membership Activity",
        )
        fig_act.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig_act.update_layout(
            showlegend=False, height=320,
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(gridcolor="#f3f4f6", title="Churn Rate (%)"),
            margin=dict(t=50, b=10, l=0, r=0),
        )
        st.plotly_chart(fig_act, use_container_width=True)

    # Age group churn with size context
    st.markdown('<div class="section-title">Age Group Churn — Rate & Volume</div>', unsafe_allow_html=True)
    age_df = df.groupby("AgeGroup", observed=True)["Exited"].agg(
        ChurnRate="mean", Churned="sum", Total="count"
    ).reset_index()
    age_df["ChurnPct"] = (age_df["ChurnRate"] * 100).round(1)
    age_df["Retained"] = age_df["Total"] - age_df["Churned"]
    age_df["AgeGroup"] = age_df["AgeGroup"].astype(str)

    fig_age = make_subplots(specs=[[{"secondary_y": True}]])
    fig_age.add_trace(go.Bar(
        x=age_df["AgeGroup"], y=age_df["Retained"],
        name="Retained", marker_color="#3b82f6", opacity=0.85,
    ), secondary_y=False)
    fig_age.add_trace(go.Bar(
        x=age_df["AgeGroup"], y=age_df["Churned"],
        name="Churned", marker_color="#ef4444", opacity=0.85,
    ), secondary_y=False)
    fig_age.add_trace(go.Scatter(
        x=age_df["AgeGroup"], y=age_df["ChurnPct"],
        mode="lines+markers+text", name="Churn Rate",
        line=dict(color="#f59e0b", width=3),
        marker=dict(size=10, color="#f59e0b"),
        text=age_df["ChurnPct"].apply(lambda x: f"{x:.1f}%"),
        textposition="top center",
    ), secondary_y=True)
    fig_age.update_layout(
        barmode="stack", height=380,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(gridcolor="#f3f4f6", title="Customer Count"),
        yaxis2=dict(title="Churn Rate (%)", range=[0, max(age_df["ChurnPct"])*1.4]),
        margin=dict(t=10, b=10, l=0, r=60),
        legend=dict(orientation="h", y=1.05),
    )
    st.plotly_chart(fig_age, use_container_width=True)

    # Tenure churn
    st.markdown('<div class="section-title">Tenure vs Churn — Engagement Lifecycle</div>', unsafe_allow_html=True)
    ten_df = df.groupby("Tenure")["Exited"].agg(
        ChurnRate="mean", Count="count"
    ).reset_index()
    ten_df["ChurnPct"] = (ten_df["ChurnRate"] * 100).round(1)

    fig_ten = px.area(
        ten_df, x="Tenure", y="ChurnPct",
        line_shape="spline",
        title="Churn Rate Across Customer Tenure (Years)",
        color_discrete_sequence=["#3b82f6"],
    )
    fig_ten.update_traces(fillcolor="rgba(59,130,246,0.15)", line_color="#3b82f6", line_width=3)
    fig_ten.update_layout(
        height=300, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(gridcolor="#f3f4f6", title="Churn Rate (%)"),
        xaxis=dict(title="Years with Bank", dtick=1),
        margin=dict(t=50, b=10, l=0, r=0),
    )
    st.plotly_chart(fig_ten, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 — HIGH-VALUE CUSTOMERS
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[3]:
    st.markdown('<div class="section-title">High-Value Customer Churn Intelligence</div>', unsafe_allow_html=True)

    hv_df    = df[df["HighValue"] == 1]
    hv_total = len(hv_df)
    hv_churn_n = hv_df["Exited"].sum()
    hv_churn_r = hv_churn_n / hv_total * 100 if hv_total else 0
    revenue_at_risk = hv_df[hv_df["Exited"]==1]["Balance"].sum()
    avg_hv_balance  = hv_df["Balance"].mean()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("High-Value Customers", f"{hv_total:,}", "Top-quartile balance")
    c2.metric("HV Churn Rate", f"{hv_churn_r:.1f}%", delta=f"{hv_churn_n:,} churned", delta_color="inverse")
    c3.metric("Balance at Risk", f"€{revenue_at_risk/1e6:.1f}M", "Churned HV balance")
    c4.metric("Avg HV Balance", f"€{avg_hv_balance:,.0f}")

    st.markdown("")
    col_a, col_b = st.columns(2)

    with col_a:
        hv_geo = hv_df.groupby("Geography")["Exited"].agg(
            ChurnRate="mean", Churned="sum", Total="count"
        ).reset_index()
        hv_geo["ChurnPct"] = (hv_geo["ChurnRate"] * 100).round(1)
        hv_geo["RiskScore"] = (hv_geo["ChurnPct"] * hv_geo["Total"] / hv_total).round(1)

        fig_hv_geo = px.bar(
            hv_geo, x="Geography", y="ChurnPct",
            color="Geography", text="ChurnPct",
            color_discrete_map=GEO_COLORS,
            title="High-Value Churn Rate by Country",
        )
        fig_hv_geo.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig_hv_geo.update_layout(
            showlegend=False, height=340,
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(gridcolor="#f3f4f6", title="Churn Rate (%)"),
            margin=dict(t=50, b=10, l=0, r=0),
        )
        st.plotly_chart(fig_hv_geo, use_container_width=True)

    with col_b:
        # Balance vs salary scatter for churned HV
        sample = hv_df.sample(min(800, len(hv_df)), random_state=42)
        fig_scatter = px.scatter(
            sample, x="EstimatedSalary", y="Balance",
            color=sample["Exited"].map({0: "Retained", 1: "Churned"}),
            color_discrete_map=PALETTE,
            opacity=0.65, size_max=8,
            title="Balance vs Salary (High-Value Customers)",
            labels={"EstimatedSalary": "Estimated Salary (€)", "Balance": "Balance (€)"},
        )
        fig_scatter.update_layout(
            height=340, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(gridcolor="#f3f4f6"),
            xaxis=dict(gridcolor="#f3f4f6"),
            margin=dict(t=50, b=10, l=0, r=0),
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    # Balance distribution
    col1, col2 = st.columns(2)
    with col1:
        fig_bal = go.Figure()
        for status, color in [("Churned", "#ef4444"), ("Retained", "#3b82f6")]:
            sub = hv_df[hv_df["Exited"] == (1 if status=="Churned" else 0)]
            fig_bal.add_trace(go.Histogram(
                x=sub["Balance"], name=status,
                marker_color=color, opacity=0.7, nbinsx=30,
            ))
        fig_bal.update_layout(
            barmode="overlay", height=310,
            title="Balance Distribution — Churned vs Retained (HV)",
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(gridcolor="#f3f4f6"), xaxis_title="Balance (€)",
            margin=dict(t=50, b=10, l=0, r=0),
        )
        st.plotly_chart(fig_bal, use_container_width=True)

    with col2:
        hv_age = hv_df.groupby("AgeGroup", observed=True)["Exited"].agg(
            ChurnRate="mean", Churned="sum"
        ).reset_index()
        hv_age["ChurnPct"] = (hv_age["ChurnRate"]*100).round(1)
        hv_age["AgeGroup"] = hv_age["AgeGroup"].astype(str)

        fig_hv_age = px.funnel(
            hv_age.sort_values("ChurnPct", ascending=False),
            x="Churned", y="AgeGroup", color="ChurnPct",
            color_continuous_scale=["#dbeafe","#3b82f6","#ef4444"],
            title="HV Churn Volume by Age Group",
        )
        fig_hv_age.update_layout(
            height=310, paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(t=50, b=10, l=0, r=0),
        )
        st.plotly_chart(fig_hv_age, use_container_width=True)

    # HV summary table
    st.markdown('<div class="section-title">High-Value Segment Summary Table</div>', unsafe_allow_html=True)
    tbl = hv_df.groupby(["Geography","Gender","AgeGroup"], observed=True).agg(
        Customers=("Exited","count"),
        Churned=("Exited","sum"),
        AvgBalance=("Balance","mean"),
        AvgSalary=("EstimatedSalary","mean"),
    ).reset_index()
    tbl["ChurnRate"] = (tbl["Churned"]/tbl["Customers"]*100).round(1).astype(str) + "%"
    tbl["AvgBalance"] = tbl["AvgBalance"].apply(lambda x: f"€{x:,.0f}")
    tbl["AvgSalary"]  = tbl["AvgSalary"].apply(lambda x: f"€{x:,.0f}")
    tbl["AgeGroup"]   = tbl["AgeGroup"].astype(str)
    tbl = tbl.sort_values("Churned", ascending=False).head(20)
    st.dataframe(tbl, use_container_width=True, hide_index=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 5 — SEGMENT DEEP-DIVE
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[4]:
    st.markdown('<div class="section-title">Segment Deep-Dive & Cross-Analysis</div>', unsafe_allow_html=True)

    d_col1, d_col2 = st.columns(2)
    dim_x = d_col1.selectbox("Primary Dimension (X)", 
        ["Geography","AgeGroup","Gender","TenureGroup","CreditBand","BalanceSegment"])
    dim_y = d_col2.selectbox("Secondary Dimension (Split by)",
        ["Gender","Geography","AgeGroup","TenureGroup","CreditBand","BalanceSegment"])

    cross = df.groupby([dim_x, dim_y], observed=True)["Exited"].agg(
        ChurnRate="mean", Churned="sum", Total="count"
    ).reset_index()
    cross["ChurnPct"]   = (cross["ChurnRate"] * 100).round(1)
    cross[dim_x] = cross[dim_x].astype(str)
    cross[dim_y] = cross[dim_y].astype(str)

    fig_cross = px.bar(
        cross, x=dim_x, y="ChurnPct", color=dim_y,
        barmode="group", text="ChurnPct",
        color_discrete_sequence=px.colors.qualitative.Bold,
        title=f"Churn Rate: {dim_x} × {dim_y}",
    )
    fig_cross.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig_cross.update_layout(
        height=400, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(gridcolor="#f3f4f6", title="Churn Rate (%)"),
        margin=dict(t=50, b=10, l=0, r=0),
    )
    st.plotly_chart(fig_cross, use_container_width=True)

    # Products deep-dive
    st.markdown('<div class="section-title">Product Portfolio & Churn Risk</div>', unsafe_allow_html=True)
    prod_df = df.groupby(["NumOfProducts","IsActiveMember"])["Exited"].agg(
        ChurnRate="mean", Count="count"
    ).reset_index()
    prod_df["Activity"] = prod_df["IsActiveMember"].map({0:"Inactive",1:"Active"})
    prod_df["ChurnPct"] = (prod_df["ChurnRate"]*100).round(1)
    prod_df["Label"] = prod_df["NumOfProducts"].astype(str) + " Product(s)"

    fig_prod2 = px.bar(
        prod_df, x="Label", y="ChurnPct", color="Activity",
        barmode="group", text="ChurnPct",
        color_discrete_map={"Active":"#10b981","Inactive":"#f59e0b"},
        title="Churn Rate by Product Count & Membership Activity",
    )
    fig_prod2.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig_prod2.update_layout(
        height=340, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(gridcolor="#f3f4f6", title="Churn Rate (%)"),
        margin=dict(t=50, b=10, l=0, r=0),
    )
    st.plotly_chart(fig_prod2, use_container_width=True)

    # Full filtered data
    st.markdown('<div class="section-title">Filtered Dataset Export View</div>', unsafe_allow_html=True)
    show_cols = ["Geography","Gender","Age","AgeGroup","Tenure","TenureGroup",
                 "Balance","BalanceSegment","CreditScore","CreditBand",
                 "NumOfProducts","IsActiveMember","HasCrCard","EstimatedSalary",
                 "HighValue","Exited"]
    disp = df[show_cols].copy()
    disp["Exited"] = disp["Exited"].map({0:"Retained",1:"Churned"})
    disp["IsActiveMember"] = disp["IsActiveMember"].map({0:"Inactive",1:"Active"})
    disp["HasCrCard"] = disp["HasCrCard"].map({0:"No",1:"Yes"})
    disp["HighValue"] = disp["HighValue"].map({0:"No",1:"Yes"})
    disp["AgeGroup"] = disp["AgeGroup"].astype(str)
    disp["TenureGroup"] = disp["TenureGroup"].astype(str)
    disp["CreditBand"] = disp["CreditBand"].astype(str)
    disp["BalanceSegment"] = disp["BalanceSegment"].astype(str)
    st.dataframe(disp.head(500), use_container_width=True, hide_index=True)
    st.caption(f"Showing first 500 of {len(df):,} filtered records.")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<center style='color:#9ca3af;font-size:0.8rem;'>"
    "European Bank Customer Churn Analytics · Data: Simulated · "
    "European Central Bank — Strategic Analytics Division"
    "</center>",
    unsafe_allow_html=True
)
