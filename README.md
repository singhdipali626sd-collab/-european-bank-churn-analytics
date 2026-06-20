# 🏦 European Bank — Customer Segmentation & Churn Pattern Analytics

> **Unified Mentor Internship Project** | Finance Analytics Domain | FY 2025

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-link.streamlit.app)

---

## 📌 Project Overview

This project performs comprehensive **customer churn analysis** across a European banking portfolio covering **9,783 customers** in France, Germany, and Spain. It identifies high-risk customer segments, quantifies revenue-at-risk from churn, and provides data-driven strategic recommendations.

**Mentor:** European Central Bank (Unified Mentor Programme)

---

## 🎯 Objectives

- Measure and benchmark the overall churn rate
- Identify churn distribution across customer segments
- Compare churn behaviour across European regions
- Understand churn among high-value customers
- Evaluate engagement and tenure patterns
- Support strategic retention planning

---

## 📊 Dataset

| Column | Description |
|--------|-------------|
| CreditScore | Customer creditworthiness score |
| Geography | Country (France / Spain / Germany) |
| Gender | Male / Female |
| Age | Customer age |
| Tenure | Years with the bank |
| Balance | Account balance (EUR) |
| NumOfProducts | Number of bank products held |
| HasCrCard | Credit card ownership (0/1) |
| IsActiveMember | Activity indicator (0/1) |
| EstimatedSalary | Annual estimated salary (EUR) |
| Exited | **Churn indicator — target variable** (0/1) |

**Source:** European Central Bank Customer Database, FY 2025

---

## 🔍 Key Findings

| Finding | Insight |
|---------|---------|
| 🔴 Overall Churn Rate | **20.33%** — 1,989 of 9,783 customers exited |
| 🔴 Germany Crisis | **32.35%** churn — nearly 2× France & Spain |
| 🔴 Age 46–60 | **51.05%** churn rate — critical cohort |
| 🔴 Product Paradox | 3-product holders: **82%**, 4-product: **100%** churn |
| 🔴 Wealth Loss | Churners hold **€18,399 more** in avg balance than retained |
| 🟡 Gender Gap | Female: **25.1%** vs Male: **16.4%** churn |
| 🟡 Engagement | Inactive members churn at **1.85×** the rate of active members |
| 🟢 Sweet Spot | 2-product holders churn at only **7.62%** |

---

## 🛠️ Tech Stack

- **Python 3.12** — core analytics
- **Pandas** — data wrangling and segmentation
- **Plotly** — interactive visualisations
- **Streamlit** — web app deployment
- **ReportLab + Matplotlib** — PDF report generation

---

## 📁 Project Structure

```
churn_project/
├── app/
│   └── app.py                  # Streamlit dashboard
├── data/
│   └── european_bank_churn.csv # Cleaned dataset (9,783 rows)
├── notebooks/
│   └── churn_analysis.ipynb    # Full EDA notebook
├── assets/
│   └── European_Bank_Churn_Analytics.pdf  # Final report
├── requirements.txt
└── README.md
```

---

## 🚀 Run Locally

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/european-bank-churn-analytics.git
cd european-bank-churn-analytics

# Install dependencies
pip install -r requirements.txt

# Launch the Streamlit app
streamlit run app/app.py
```

---

## 📈 Segmentation Dimensions

- **Geographic:** France · Germany · Spain
- **Age Bands:** <30 · 30–45 · 46–60 · 60+
- **Credit Score:** Very Poor → Exceptional (5 bands)
- **Tenure:** New (0–2yr) · Mid (3–5yr) · Long (6–10yr)
- **Balance:** Zero · Low (€1–50k) · High (€50k+)
- **Products:** 1 · 2 · 3 · 4 products
- **Engagement:** Active vs Inactive members
- **Cross-dimension:** Geography × Gender interaction

---

## 🏆 KPI Summary

| KPI | Value | Target | Status |
|-----|-------|--------|--------|
| Overall churn rate | 20.33% | <15% | 🔴 AT RISK |
| Germany churn | 32.35% | <20% | 🔴 CRITICAL |
| High-value churn | 25.16% | <15% | 🔴 CRITICAL |
| Age 46–60 churn | 51.05% | <25% | 🔴 CRITICAL |
| Inactive member churn | 26.68% | <18% | 🟠 AT RISK |
| 2-product churn | 7.62% | <10% | 🟢 MET |

---

## 📋 Strategic Recommendations

1. **🔴 Germany Market Intervention** — Dedicated retention task force; target <20% in 12 months
2. **🔴 Age 46–60 Wealth Programme** — Wealth advisory tier addressing life-transition triggers
3. **🟠 Product Bundling Audit** — Review 3- & 4-product holders; optimise cross-sell strategy
4. **🟠 Inactive Re-engagement** — 30/60/90-day tiered programme for 4,731 inactive members
5. **🟡 Gender-Differentiated Products** — Targeted products addressing 8.7pp gender churn gap
6. **🟡 Behavioural Churn Model** — Replace credit scoring with behavioural prediction signals

---

## 👤 Author

**Finance Analytics Intern**
Unified Mentor Virtual Internship Programme — FY 2025
Domain: Data Analytics / Finance
Mentor Organisation: European Central Bank

---

*This project is submitted as part of the Unified Mentor Skill + Project Based Virtual Internship Program.*
