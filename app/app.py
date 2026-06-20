import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import os

# ── Page config ───────────────────────────────────────────────────
st.set_page_config(
    page_title="European Bank Churn Analytics",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #F8F7F4; }
    .stMetric { background: white; border-radius: 10px; padding: 12px; border: 1px solid #E8E6E1; }
    .stMetric label { font-size: 12px !important; color: #888780 !important; text-transform: uppercase; letter-spacing: 0.05em; }
    .block-container { padding-top: 1.5rem; }
    h1 { color: #0f2744; font-size: 1.8rem !important; }
    h2 { color: #0f2744; font-size: 1.2rem !important; }
    h3 { color: #0f2744; font-size: 1rem !important; }
    .insight-box { background: #FCEBEB; border-left: 4px solid #E24B4A;
                   padding: 12px 16px; border-radius: 6px; margin: 8px 0; }
    .insight-box-amber { background: #FAEEDA; border-left: 4px solid #BA7517;
                         padding: 12px 16px; border-radius: 6px; margin: 8px 0; }
    .insight-box-green { background: #EAF3DE; border-left: 4px solid #3B6D11;
                         padding: 12px 16px; border-radius: 6px; margin: 8px 0; }
</style>
""", unsafe_allow_html=True)

# ── Load data ─────────────────────────────────────────────────────
@st.cache_data
def load_data():
    base = os.path.dirname(os.path.abspath(__file__))
    csv  = os.path.join(base, "..", "data", "european_bank_churn.csv")
    df   = pd.read_csv(csv)
    df['AgeGroup']    = pd.cut(df['Age'],    bins=[0,30,45,60,200], labels=['<30','30-45','46-60','60+'])
    df['TenureGroup'] = pd.cut(df['Tenure'], bins=[-1,2,5,10],      labels=['New (0-2yr)','Mid (3-5yr)','Long (6-10yr)'])
    df['BalanceSeg']  = pd.cut(df['Balance'],bins=[-1,1,50000,200000],labels=['Zero Balance','Low (1-50k)','High (50k+)'])
    df['CreditBand']  = pd.cut(df['CreditScore'],
                               bins=[0,579,669,739,799,850],
                               labels=['Very Poor (<580)','Fair (580-669)','Good (670-739)',
                                       'Very Good (740-799)','Exceptional (800+)'])
    return df

df = load_data()

PALETTE = {'Churned':'#E24B4A','Retained':'#378ADD'}
NAVY, RED, GREEN, AMBER = '#0f2744','#E24B4A','#3B6D11','#BA7517'

# ── Sidebar filters ───────────────────────────────────────────────
st.sidebar.image("https://img.icons8.com/color/96/bank-building.png", width=60)
st.sidebar.title("🔍 Filters")
st.sidebar.markdown("---")

geo_opts = ['All'] + sorted(df['Geography'].unique())
sel_geo  = st.sidebar.multiselect("Geography", geo_opts[1:], default=geo_opts[1:])

gender_opts = ['All'] + sorted(df['Gender'].unique())
sel_gender  = st.sidebar.multiselect("Gender", gender_opts[1:], default=gender_opts[1:])

age_opts = ['<30','30-45','46-60','60+']
sel_age  = st.sidebar.multiselect("Age Group", age_opts, default=age_opts)

st.sidebar.markdown("---")
st.sidebar.markdown("**Balance range (EUR)**")
bal_min, bal_max = st.sidebar.slider("", 0, 250000, (0, 250000), step=5000)

st.sidebar.markdown("---")
st.sidebar.info("📊 **Dataset:** 9,783 customers\n\n🌍 France · Germany · Spain\n\n📅 Fiscal Year 2025\n\n🏛 European Central Bank")

# ── Apply filters ─────────────────────────────────────────────────
mask = (
    df['Geography'].isin(sel_geo if sel_geo else df['Geography'].unique()) &
    df['Gender'].isin(sel_gender if sel_gender else df['Gender'].unique()) &
    df['AgeGroup'].isin(sel_age  if sel_age  else df['AgeGroup'].unique()) &
    df['Balance'].between(bal_min, bal_max)
)
dff = df[mask].copy()

total    = len(dff)
churned  = int(dff['Exited'].sum())
retained = total - churned
churn_r  = churned/total*100 if total else 0

# ═══════════════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════════════
st.markdown("""
<div style="background:linear-gradient(135deg,#0f2744,#1a3a5c);
            padding:20px 28px;border-radius:12px;margin-bottom:20px">
  <h1 style="color:white;margin:0;font-size:1.6rem">
    🏦 European Bank — Customer Churn Pattern Analytics
  </h1>
  <p style="color:#CBD5E0;margin:6px 0 0;font-size:0.9rem">
    Customer Segmentation & Churn Intelligence Dashboard &nbsp;·&nbsp;
    Finance Analytics Division &nbsp;·&nbsp; FY 2025
  </p>
</div>
""", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Overview", "🌍 Geography", "👥 Demographics", "💰 Financial Profile", "📋 KPI Dashboard"
])

# ═══════════════════════════════════════════════════════════════════
# TAB 1 — OVERVIEW
# ═══════════════════════════════════════════════════════════════════
with tab1:
    c1,c2,c3,c4,c5,c6 = st.columns(6)
    c1.metric("Total Customers",  f"{total:,}")
    c2.metric("Churned",          f"{churned:,}",          delta=f"{churn_r:.1f}% rate",  delta_color="inverse")
    c3.metric("Retained",         f"{retained:,}",         delta=f"{100-churn_r:.1f}%",   delta_color="normal")
    hv = dff[dff['Balance']>100000]
    c4.metric("High-Value Churn", f"{hv['Exited'].mean()*100:.1f}%", delta="balance>100k",delta_color="inverse")
    c5.metric("Avg Balance (Churned)", f"€{dff[dff['Exited']==1]['Balance'].mean():,.0f}")
    c6.metric("Avg Age (Churned)",     f"{dff[dff['Exited']==1]['Age'].mean():.1f} yrs")

    st.markdown("---")
    col1, col2 = st.columns([1.3, 1])

    with col1:
        st.subheader("Churn by Geography & Gender")
        gg = dff.groupby(['Geography','Gender']).agg(
            Total=('Exited','count'), Churned=('Exited','sum')).reset_index()
        gg['ChurnRate'] = gg['Churned']/gg['Total']*100
        fig = px.bar(gg, x='Geography', y='ChurnRate', color='Gender',
                     barmode='group', text=gg['ChurnRate'].round(1).astype(str)+'%',
                     color_discrete_map={'Female':'#D4537E','Male':'#378ADD'},
                     labels={'ChurnRate':'Churn Rate %'})
        fig.update_layout(plot_bgcolor='white', paper_bgcolor='white',
                          font_color=NAVY, height=320, legend_title='')
        fig.update_traces(textposition='outside')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Overall Churn Split")
        pie_df = pd.DataFrame({'Status':['Churned','Retained'],'Count':[churned,retained]})
        fig2 = px.pie(pie_df, names='Status', values='Count', hole=0.55,
                      color='Status', color_discrete_map=PALETTE)
        fig2.update_layout(plot_bgcolor='white', paper_bgcolor='white',
                           font_color=NAVY, height=320,
                           annotations=[dict(text=f'<b>{churn_r:.1f}%</b><br>churn',
                                             x=0.5,y=0.5,font_size=16,showarrow=False,
                                             font_color=RED)])
        st.plotly_chart(fig2, use_container_width=True)

    # Age churn combo
    st.subheader("Age Group — Volume vs Churn Rate")
    ag = dff.groupby('AgeGroup', observed=True).agg(
        Total=('Exited','count'), Churned=('Exited','sum')).reset_index()
    ag['ChurnRate'] = ag['Churned']/ag['Total']*100

    fig3 = make_subplots(specs=[[{"secondary_y":True}]])
    fig3.add_trace(go.Bar(x=ag['AgeGroup'].astype(str), y=ag['Total'],
                          name='Customers', marker_color='#B5D4F4'), secondary_y=False)
    fig3.add_trace(go.Scatter(x=ag['AgeGroup'].astype(str), y=ag['ChurnRate'],
                              name='Churn Rate %', line=dict(color=RED,width=3),
                              mode='lines+markers+text',
                              text=ag['ChurnRate'].round(1).astype(str)+'%',
                              textposition='top center',
                              marker=dict(size=8, color=RED)), secondary_y=True)
    fig3.update_layout(plot_bgcolor='white', paper_bgcolor='white',
                       font_color=NAVY, height=320, legend=dict(orientation='h',y=1.12))
    fig3.update_yaxes(title_text="Customers", secondary_y=False)
    fig3.update_yaxes(title_text="Churn Rate %", secondary_y=True,
                      ticksuffix='%', range=[0,65])
    st.plotly_chart(fig3, use_container_width=True)

    # Insight callouts
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("""<div class="insight-box">
        <b>🚨 Revenue-at-risk:</b> Churned customers hold <b>€18,399 more</b> in average balance
        than retained ones. The 1,179 high-value churners represent <b>€107M+ in lost AUM</b>.
        </div>""", unsafe_allow_html=True)
    with col_b:
        st.markdown("""<div class="insight-box-amber">
        <b>⚠️ Age insight:</b> Churners are <b>7.5 years older</b> on average (44.9 vs 37.4).
        Mid-career life transitions are driving exits — a wealth advisory product gap exists.
        </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# TAB 2 — GEOGRAPHY
# ═══════════════════════════════════════════════════════════════════
with tab2:
    st.subheader("Geographic Risk Index")

    geo = dff.groupby('Geography').agg(
        Total=('Exited','count'), Churned=('Exited','sum')).reset_index()
    geo['Retained']  = geo['Total'] - geo['Churned']
    geo['ChurnRate'] = geo['Churned']/geo['Total']*100

    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(geo, x='Geography', y=['Retained','Churned'],
                     barmode='stack', color_discrete_map=PALETTE,
                     labels={'value':'Customers','variable':'Status'},
                     text_auto=True)
        fig.update_layout(plot_bgcolor='white', paper_bgcolor='white',
                          font_color=NAVY, height=350)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = px.bar(geo, x='Geography', y='ChurnRate',
                      color='ChurnRate',
                      color_continuous_scale=['#3B6D11','#BA7517','#E24B4A'],
                      text=geo['ChurnRate'].round(2).astype(str)+'%',
                      labels={'ChurnRate':'Churn Rate %'})
        fig2.update_traces(textposition='outside')
        fig2.update_layout(plot_bgcolor='white', paper_bgcolor='white',
                           font_color=NAVY, height=350, showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Country-Level Detail Table")
    geo['Risk Level'] = geo['ChurnRate'].apply(
        lambda x: '🔴 CRITICAL' if x>25 else ('🟡 WATCH' if x>15 else '🟢 SAFE'))
    geo_disp = geo[['Geography','Total','Churned','Retained','ChurnRate','Risk Level']].copy()
    geo_disp['ChurnRate'] = geo_disp['ChurnRate'].round(2).astype(str) + '%'
    geo_disp.columns = ['Country','Total','Churned','Retained','Churn Rate','Risk Level']
    st.dataframe(geo_disp.set_index('Country'), use_container_width=True)

    st.subheader("Geography × Tenure Churn Heatmap")
    ht = dff.groupby(['Geography','TenureGroup'], observed=True)['Exited'].mean().reset_index()
    ht['ChurnRate'] = ht['Exited']*100
    pivot = ht.pivot(index='TenureGroup', columns='Geography', values='ChurnRate')
    fig3 = px.imshow(pivot, text_auto='.1f', color_continuous_scale='RdYlGn_r',
                     labels={'color':'Churn %'}, aspect='auto')
    fig3.update_layout(plot_bgcolor='white', paper_bgcolor='white',
                       font_color=NAVY, height=300)
    st.plotly_chart(fig3, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════
# TAB 3 — DEMOGRAPHICS
# ═══════════════════════════════════════════════════════════════════
with tab3:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Gender Churn Comparison")
        gen = dff.groupby('Gender').agg(
            Total=('Exited','count'), Churned=('Exited','sum')).reset_index()
        gen['ChurnRate'] = gen['Churned']/gen['Total']*100
        fig = px.bar(gen, x='Gender', y='ChurnRate',
                     color='Gender', text=gen['ChurnRate'].round(1).astype(str)+'%',
                     color_discrete_map={'Female':'#D4537E','Male':'#378ADD'},
                     labels={'ChurnRate':'Churn Rate %'})
        fig.update_traces(textposition='outside')
        fig.update_layout(plot_bgcolor='white', paper_bgcolor='white',
                          font_color=NAVY, height=320, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Products Held vs Churn Rate")
        prod = dff.groupby('NumOfProducts').agg(
            Total=('Exited','count'), Churned=('Exited','sum')).reset_index()
        prod['ChurnRate'] = prod['Churned']/prod['Total']*100
        colors = ['#BA7517' if r<25 else '#E24B4A' for r in prod['ChurnRate']]
        fig2 = px.bar(prod, x='NumOfProducts', y='ChurnRate',
                      text=prod['ChurnRate'].round(1).astype(str)+'%',
                      labels={'NumOfProducts':'# Products','ChurnRate':'Churn Rate %'},
                      color='ChurnRate',
                      color_continuous_scale=['#3B6D11','#BA7517','#E24B4A'])
        fig2.update_traces(textposition='outside')
        fig2.update_layout(plot_bgcolor='white', paper_bgcolor='white',
                           font_color=NAVY, height=320, showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Active Membership Impact")
    act = dff.groupby('IsActiveMember').agg(
        Total=('Exited','count'), Churned=('Exited','sum')).reset_index()
    act['Label'] = act['IsActiveMember'].map({0:'Inactive',1:'Active'})
    act['ChurnRate'] = act['Churned']/act['Total']*100

    col3, col4 = st.columns(2)
    with col3:
        fig3 = px.bar(act, x='Label', y='ChurnRate',
                      color='Label', text=act['ChurnRate'].round(1).astype(str)+'%',
                      color_discrete_map={'Active':'#3B6D11','Inactive':'#E24B4A'},
                      labels={'ChurnRate':'Churn Rate %','Label':'Status'})
        fig3.update_traces(textposition='outside')
        fig3.update_layout(plot_bgcolor='white', paper_bgcolor='white',
                           font_color=NAVY, height=300, showlegend=False)
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""<div class="insight-box">
        <b>1.85× churn multiplier:</b> Inactive members churn at <b>26.68%</b> vs
        just <b>14.39%</b> for active members. Re-engagement programmes have the
        highest ROI of any retention lever.
        </div>""", unsafe_allow_html=True)
        st.markdown("""<div class="insight-box-green">
        <b>✅ Optimal strategy:</b> Customers with <b>2 products</b> churn at only
        <b>7.62%</b>. Avoid over-bundling — 3+ products cause catastrophic churn.
        </div>""", unsafe_allow_html=True)

    st.subheader("Tenure Group Analysis")
    ten = dff.groupby('TenureGroup', observed=True).agg(
        Total=('Exited','count'), Churned=('Exited','sum')).reset_index()
    ten['Retained']  = ten['Total'] - ten['Churned']
    ten['ChurnRate'] = ten['Churned']/ten['Total']*100
    fig4 = px.bar(ten, x='TenureGroup', y=['Retained','Churned'],
                  barmode='stack', color_discrete_map=PALETTE,
                  text_auto=True,
                  labels={'value':'Customers','TenureGroup':'Tenure'})
    fig4.update_layout(plot_bgcolor='white', paper_bgcolor='white',
                       font_color=NAVY, height=300)
    st.plotly_chart(fig4, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════
# TAB 4 — FINANCIAL PROFILE
# ═══════════════════════════════════════════════════════════════════
with tab4:
    st.subheader("Churned vs Retained — Financial Comparison")

    churn_df   = dff[dff['Exited']==1]
    retain_df  = dff[dff['Exited']==0]

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Avg Balance — Churned",   f"€{churn_df['Balance'].mean():,.0f}")
    c2.metric("Avg Balance — Retained",  f"€{retain_df['Balance'].mean():,.0f}",
              delta=f"-€{churn_df['Balance'].mean()-retain_df['Balance'].mean():,.0f}",
              delta_color="inverse")
    c3.metric("Avg Salary — Churned",    f"€{churn_df['EstimatedSalary'].mean():,.0f}")
    c4.metric("Avg Age — Churned",       f"{churn_df['Age'].mean():.1f} yrs",
              delta=f"+{churn_df['Age'].mean()-retain_df['Age'].mean():.1f} yrs",
              delta_color="inverse")

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Balance Segment Churn")
        bal = dff.groupby('BalanceSeg', observed=True).agg(
            Total=('Exited','count'), Churned=('Exited','sum')).reset_index()
        bal['ChurnRate'] = bal['Churned']/bal['Total']*100
        fig = px.bar(bal, x='BalanceSeg', y='ChurnRate',
                     text=bal['ChurnRate'].round(1).astype(str)+'%',
                     color='ChurnRate', color_continuous_scale=['#3B6D11','#BA7517','#E24B4A'],
                     labels={'BalanceSeg':'Balance Segment','ChurnRate':'Churn Rate %'})
        fig.update_traces(textposition='outside')
        fig.update_layout(plot_bgcolor='white', paper_bgcolor='white',
                          font_color=NAVY, height=320, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Credit Score Band Churn")
        cr = dff.groupby('CreditBand', observed=True).agg(
            Total=('Exited','count'), Churned=('Exited','sum')).reset_index()
        cr['ChurnRate'] = cr['Churned']/cr['Total']*100
        fig2 = px.bar(cr, x='CreditBand', y='ChurnRate',
                      text=cr['ChurnRate'].round(1).astype(str)+'%',
                      color='ChurnRate', color_continuous_scale='Blues',
                      labels={'CreditBand':'Credit Band','ChurnRate':'Churn Rate %'})
        fig2.update_traces(textposition='outside')
        fig2.update_layout(plot_bgcolor='white', paper_bgcolor='white',
                           font_color=NAVY, height=320, showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Balance Distribution — Churned vs Retained")
    fig3 = go.Figure()
    fig3.add_trace(go.Histogram(x=retain_df['Balance'], name='Retained',
                                 opacity=0.7, marker_color='#378ADD',
                                 nbinsx=40, histnorm='percent'))
    fig3.add_trace(go.Histogram(x=churn_df['Balance'], name='Churned',
                                 opacity=0.7, marker_color='#E24B4A',
                                 nbinsx=40, histnorm='percent'))
    fig3.update_layout(barmode='overlay', plot_bgcolor='white', paper_bgcolor='white',
                       font_color=NAVY, height=320,
                       xaxis_title='Balance (EUR)', yaxis_title='% of group',
                       legend=dict(orientation='h', y=1.05))
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("""<div class="insight-box">
    <b>💡 Key finding — Credit score does NOT predict churn:</b> Churn rates vary only between
    18.6% and 21.9% across all five credit score bands. Creditworthiness screening cannot substitute
    for behavioural retention modelling.
    </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# TAB 5 — KPI DASHBOARD
# ═══════════════════════════════════════════════════════════════════
with tab5:
    st.subheader("Full KPI Summary — FY 2025")

    kpis = [
        ("Overall churn rate",            f"{churn_r:.2f}%",  "< 15%",  "AT RISK"  if churn_r>15  else "MET"),
        ("Germany churn rate",            "32.35%",            "< 20%",  "CRITICAL"),
        ("France churn rate",             "16.16%",            "< 15%",  "WATCH"),
        ("Spain churn rate",              "16.66%",            "< 15%",  "WATCH"),
        ("Female churn rate",             "25.10%",            "< 18%",  "AT RISK"),
        ("Male churn rate",               "16.36%",            "< 15%",  "WATCH"),
        ("High-value customer churn",     "25.16%",            "< 15%",  "CRITICAL"),
        ("Age 46-60 churn rate",          "51.05%",            "< 25%",  "CRITICAL"),
        ("Inactive member churn",         "26.68%",            "< 18%",  "AT RISK"),
        ("Active member churn",           "14.39%",            "< 12%",  "WATCH"),
        ("2-product holder churn",        "7.62%",             "< 10%",  "MET"),
        ("3-product holder churn",        "82.24%",            "< 25%",  "CRITICAL"),
        ("4-product holder churn",        "100.0%",            "< 25%",  "CRITICAL"),
        ("Avg balance delta (C vs R)",    "€18,399 higher",    "< €5k",  "CRITICAL"),
    ]

    status_emoji = {'CRITICAL':'🔴','AT RISK':'🟠','WATCH':'🟡','MET':'🟢'}
    kpi_df = pd.DataFrame(kpis, columns=['KPI','Value','Target','Status'])
    kpi_df['Status'] = kpi_df['Status'].map(lambda s: f"{status_emoji.get(s,'')} {s}")

    def highlight(row):
        if 'CRITICAL' in row['Status']: bg = '#FCEBEB'
        elif 'AT RISK' in row['Status']: bg = '#FAEEDA'
        elif 'WATCH'   in row['Status']: bg = '#FFFBEB'
        else: bg = '#EAF3DE'
        return ['','',f'background-color:{bg}',f'background-color:{bg}']

    st.dataframe(
        kpi_df.style.apply(highlight, axis=1).set_properties(**{'font-size':'13px'}),
        use_container_width=True, height=530
    )

    st.markdown("---")
    st.subheader("Strategic Recommendations Summary")
    recs = [
        ("🔴 R1 — CRITICAL", "Germany Market Intervention",
         "Deploy retention task force. Target: reduce Germany churn from 32.35% → sub-20% in 12 months."),
        ("🔴 R2 — CRITICAL", "Age 46-60 Wealth Retention",
         "Launch wealth advisory tier for mid-career customers. Address life transition trigger points."),
        ("🟠 R3 — HIGH",     "Product Bundling Audit",
         "Audit 3- & 4-product holders. Optimise cross-sell for the 2-product sweet spot (7.62% churn)."),
        ("🟠 R4 — HIGH",     "Inactive Re-engagement",
         "4,731 inactive members = €25M+ opportunity. Implement tiered 30/60/90-day re-engagement."),
        ("🟡 R5 — MODERATE", "Gender-Differentiated Products",
         "Investigate 8.7pp female-male churn gap. Develop targeted products for female customers."),
        ("🟡 R6 — MODERATE", "Behavioural Churn Model",
         "Replace credit-score-based models with behavioural signals: login recency, transaction patterns."),
    ]
    for badge, title, desc in recs:
        with st.expander(f"{badge} — {title}"):
            st.write(desc)

    st.markdown("---")
    st.caption("**Data source:** European Central Bank Customer Database · FY 2025 · "
               "9,783 customers · France, Germany, Spain · "
               "Finance Analytics Division · Unified Mentor Internship Project")
