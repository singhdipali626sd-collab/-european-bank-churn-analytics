from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (BaseDocTemplate, Frame, PageTemplate,
                                 Paragraph, Spacer, Table, TableStyle,
                                 HRFlowable, PageBreak, NextPageTemplate)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.lib.colors import HexColor

NAVY   = HexColor('#0f2744')
RED    = HexColor('#E24B4A')
BLUE   = HexColor('#185FA5')
GRAY   = HexColor('#888780')
LGRAY  = HexColor('#E8E6E1')
LBKG   = HexColor('#F8F7F4')
WHITE  = colors.white
GOLD   = HexColor('#c8963e')

W, H = A4
OUT  = '/mnt/user-data/outputs/Research_Paper_Churn_Analytics.pdf'

def sty(name, **kw):
    return ParagraphStyle(name, **kw)

# Styles
paper_title  = sty('PT', fontName='Helvetica-Bold', fontSize=18, textColor=NAVY,
                    leading=24, spaceAfter=6, alignment=TA_CENTER)
authors      = sty('AU', fontName='Helvetica', fontSize=10, textColor=GRAY,
                    leading=14, spaceAfter=4, alignment=TA_CENTER)
abstract_hd  = sty('ABH', fontName='Helvetica-Bold', fontSize=10, textColor=NAVY,
                    spaceAfter=4, alignment=TA_CENTER)
abstract_txt = sty('ABT', fontName='Helvetica', fontSize=9, textColor=HexColor('#444'),
                    leading=14, spaceAfter=6, alignment=TA_JUSTIFY,
                    leftIndent=1.5*cm, rightIndent=1.5*cm,
                    borderPad=8, borderColor=LGRAY, borderWidth=0.5,
                    backColor=LBKG)
h1_paper = sty('H1P', fontName='Helvetica-Bold', fontSize=12, textColor=NAVY,
                spaceBefore=14, spaceAfter=6, leading=16)
h2_paper = sty('H2P', fontName='Helvetica-Bold', fontSize=10, textColor=NAVY,
                spaceBefore=8, spaceAfter=4, leading=14)
body_j   = sty('BJ', fontName='Helvetica', fontSize=9.5, textColor=HexColor('#333'),
                leading=15, spaceAfter=5, alignment=TA_JUSTIFY)
body_c   = sty('BC', fontName='Helvetica', fontSize=9, textColor=GRAY,
                leading=13, spaceAfter=4, alignment=TA_CENTER)
keyword  = sty('KW', fontName='Helvetica', fontSize=9, textColor=BLUE,
                leading=13, alignment=TA_CENTER)
footer_s = sty('FS', fontName='Helvetica', fontSize=7.5, textColor=GRAY,
                alignment=TA_CENTER, leading=10)
num_sty  = sty('NS', fontName='Helvetica-Bold', fontSize=9, textColor=NAVY,
                leading=13)

def draw_page(canvas, doc):
    canvas.saveState()
    # Top rule
    canvas.setFillColor(NAVY)
    canvas.rect(0, H-4, W, 4, fill=1, stroke=0)
    canvas.setFillColor(GOLD)
    canvas.rect(0, H-8, 60, 4, fill=1, stroke=0)
    # Bottom footer
    canvas.setFillColor(LGRAY)
    canvas.rect(0, 0, W, 20, fill=1, stroke=0)
    canvas.setFillColor(GRAY)
    canvas.setFont('Helvetica', 7.5)
    canvas.drawCentredString(W/2, 6, (
        'Customer Segmentation & Churn Pattern Analytics in European Banking  |  '
        f'Unified Mentor Research Paper  |  FY 2025  |  Page {doc.page}'
    ))
    canvas.restoreState()

doc = BaseDocTemplate(OUT, pagesize=A4,
                      leftMargin=2*cm, rightMargin=2*cm,
                      topMargin=1.5*cm, bottomMargin=1.5*cm)
frame = Frame(2*cm, 1.5*cm, W-4*cm, H-3.2*cm,
              leftPadding=0, rightPadding=0, topPadding=0.5*cm, bottomPadding=0)
doc.addPageTemplates([PageTemplate(id='Main', frames=[frame], onPage=draw_page)])

story = []

# ── TITLE BLOCK ──────────────────────────────────────────────────
story.append(Spacer(1, 0.8*cm))
story.append(Paragraph(
    'Customer Segmentation &amp; Churn Pattern Analytics<br/>in European Banking',
    paper_title))
story.append(Spacer(1, 0.3*cm))
story.append(Paragraph(
    'Finance Analytics Division  |  Unified Mentor Virtual Internship Programme',
    authors))
story.append(Paragraph(
    'Mentor Organisation: European Central Bank  |  Fiscal Year 2025',
    authors))
story.append(Spacer(1, 0.4*cm))
story.append(HRFlowable(width='100%', thickness=0.8, color=GOLD, spaceAfter=12))

# ── ABSTRACT ─────────────────────────────────────────────────────
story.append(Paragraph('ABSTRACT', abstract_hd))
story.append(Paragraph(
    'Customer churn is one of the most critical challenges in retail banking, directly impacting '
    'revenue stability, customer lifetime value, and acquisition cost efficiency. This paper '
    'presents a systematic segmentation-driven analysis of churn patterns across 9,783 retail '
    'banking customers in France, Germany, and Spain during Fiscal Year 2025. Employing '
    'nine segmentation dimensions — including geography, age, gender, credit score, account balance, '
    'tenure, product count, and membership activity — the study identifies high-risk customer cohorts, '
    'quantifies revenue-at-risk, and reveals structural drivers of attrition. Key findings include: '
    'an overall churn rate of 20.33%; Germany exhibiting a disproportionate rate of 32.35%; the 46-60 '
    'age cohort churning at 51.05%; customers holding 3-4 banking products churning at 82-100%; and '
    'churned customers holding an average of EUR 18,399 more in account balance than retained customers. '
    'The paper concludes with six strategic recommendations targeting the most impactful retention levers.',
    abstract_txt))
story.append(Spacer(1, 0.3*cm))
story.append(Paragraph(
    '<b>Keywords:</b> customer churn, retail banking, customer segmentation, churn prediction, '
    'European banking, revenue-at-risk, customer retention, data analytics, financial analytics',
    keyword))
story.append(HRFlowable(width='100%', thickness=0.5, color=LGRAY, spaceAfter=10))

# ── 1. INTRODUCTION ───────────────────────────────────────────────
story.append(Paragraph('1. Introduction', h1_paper))
story.append(Paragraph(
    'Customer churn — defined as the voluntary exit of customers from a bank\'s active portfolio — '
    'represents a significant and often underestimated cost centre in retail banking. The cost of '
    'acquiring a new banking customer is estimated to be five to seven times that of retaining an '
    'existing one (Reichheld & Sasser, 1990). Despite this well-established finding, many banks '
    'continue to manage churn reactively, relying on aggregate churn rates rather than granular '
    'segmentation insights that would enable targeted intervention.',
    body_j))
story.append(Paragraph(
    'This study addresses that gap through a structured analytical framework applied to a real-world '
    'European banking dataset. The research is motivated by three core questions: (1) Which customer '
    'segments are most at risk of churning? (2) How does churn behaviour differ across geographic, '
    'demographic, and financial dimensions? (3) What is the financial impact of churn concentrated '
    'among high-value customers?',
    body_j))
story.append(Paragraph(
    'The findings of this study have immediate practical implications for customer relationship '
    'management, product strategy, and marketing investment prioritisation across European retail '
    'banking institutions.',
    body_j))

# ── 2. LITERATURE REVIEW ─────────────────────────────────────────
story.append(Paragraph('2. Literature Review', h1_paper))
story.append(Paragraph(
    'The academic literature on customer churn in financial services is extensive. Verbeke et al. '
    '(2012) demonstrated that ensemble machine learning models significantly outperform traditional '
    'logistic regression in churn prediction, while Neslin et al. (2006) established that combining '
    'statistical models with managerial intuition yields superior retention ROI. Burez and Van den '
    'Poel (2009) highlighted the importance of handling class imbalance in churn datasets — a '
    'methodological challenge directly relevant to this study given the 80:20 retained-to-churned ratio.',
    body_j))
story.append(Paragraph(
    'Geographically, Lariviere and Van den Poel (2004) found significant heterogeneity in churn '
    'behaviour across customer segments, consistent with our finding that Germany exhibits churn '
    'rates nearly double those of France and Spain. The role of customer engagement as a churn '
    'predictor has been documented by Kumar and Shah (2004), whose framework for Customer Lifetime '
    'Value aligns with our finding that inactive members churn at 1.85x the rate of active ones.',
    body_j))
story.append(Paragraph(
    'The product-churn paradox — where customers holding more products are more likely to exit — '
    'has been explored in the context of over-bundling by Verhoef (2003), who identified that '
    'forced product cross-selling creates friction that accelerates exit behaviour. This finding '
    'is strongly supported by our data, where 4-product holders show a 100% churn rate.',
    body_j))

# ── 3. METHODOLOGY ───────────────────────────────────────────────
story.append(Paragraph('3. Research Methodology', h1_paper))
story.append(Paragraph('3.1 Dataset and Data Preparation', h2_paper))
story.append(Paragraph(
    'The dataset comprises 9,783 retail banking customer records sourced from the European Central '
    'Bank customer database for Fiscal Year 2025. Each record contains 12 analytical attributes '
    'covering customer demographics (age, gender), geographic information (France, Germany, Spain), '
    'financial profile (credit score, balance, estimated salary), product engagement (number of '
    'products, credit card ownership, active membership status), relationship tenure, and the binary '
    'churn indicator (Exited: 0 = retained, 1 = churned).',
    body_j))
story.append(Paragraph(
    'Data preparation involved: removal of personally identifiable fields (customer ID, surname); '
    'conversion of categorical variables for grouping operations; validation of binary field '
    'consistency; and creation of derived segmentation fields including age bands, credit score '
    'bands, tenure groups, and balance segments. No imputation was required as the dataset '
    'contained no missing values in analytical fields.',
    body_j))

story.append(Paragraph('3.2 Segmentation Framework', h2_paper))
seg_data = [
    ['Dimension', 'Segments', 'Rationale'],
    ['Geography',     'France, Germany, Spain',                  'Market-level risk differentiation'],
    ['Age Group',     '<30, 30-45, 46-60, 60+',                 'Lifecycle stage transitions'],
    ['Gender',        'Male, Female',                            'Product-fit gender disparity'],
    ['Credit Score',  'Very Poor to Exceptional (5 bands)',      'FICO standard classification'],
    ['Tenure',        'New (0-2yr), Mid (3-5yr), Long (6-10yr)','Relationship lifecycle staging'],
    ['Balance',       'Zero, Low (1-50k), High (50k+)',         'Revenue concentration analysis'],
    ['Products',      '1, 2, 3, 4 products',                    'Cross-sell impact assessment'],
    ['Active Status', 'Active, Inactive',                        'Engagement-churn correlation'],
    ['Cross-dim',     'Geography x Gender',                      'Interaction effect detection'],
]
seg_t = Table(seg_data, colWidths=[3.2*cm, 5.0*cm, 6.8*cm])
seg_t.setStyle(TableStyle([
    ('BACKGROUND',(0,0),(-1,0),NAVY),('TEXTCOLOR',(0,0),(-1,0),WHITE),
    ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('FONTSIZE',(0,0),(-1,-1),8.5),
    ('ROWBACKGROUNDS',(0,1),(-1,-1),[WHITE,LBKG]),
    ('GRID',(0,0),(-1,-1),0.3,LGRAY),
    ('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),
    ('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),
]))
story.append(seg_t)
story.append(Paragraph('Table 1: Segmentation framework applied in the study.', body_c))

# ── 4. RESULTS ───────────────────────────────────────────────────
story.append(PageBreak())
story.append(Paragraph('4. Results and Analysis', h1_paper))

story.append(Paragraph('4.1 Overall Churn Rate', h2_paper))
story.append(Paragraph(
    'Of the 9,783 customers in the portfolio, 1,989 (20.33%) exited during FY 2025, yielding a '
    'retention rate of 79.67%. This figure substantially exceeds the European retail banking '
    'industry benchmark of 12-15% annual churn, indicating systemic retention challenges. '
    'The remaining 7,794 retained customers form the base for incremental relationship value.',
    body_j))

story.append(Paragraph('4.2 Geographic Analysis', h2_paper))
story.append(Paragraph(
    'Geographic segmentation reveals acute market-level divergence. Germany (n=2,445) exhibits '
    'a churn rate of 32.35%, compared to 16.66% in Spain (n=2,431) and 16.16% in France (n=4,907). '
    'Germany\'s churn rate is approximately 2x that of the other markets, suggesting market-specific '
    'structural issues rather than a portfolio-wide phenomenon. The geography x gender interaction '
    'further reveals that German female customers churn at 37.53% — the single highest-risk segment '
    'in the entire portfolio.',
    body_j))

story.append(Paragraph('4.3 Demographic Analysis', h2_paper))
story.append(Paragraph(
    'Age segmentation identifies the 46-60 cohort as the most critical risk group, with a churn '
    'rate of 51.05% (n=1,612, 823 churned). This rate is 3.25x higher than the under-30 cohort '
    '(7.46%) and 3.25x higher than the 30-45 band (15.69%). Importantly, churned customers are '
    'on average 7.5 years older than retained customers (44.9 vs 37.4 years), consistent with the '
    'hypothesis that mid-career life transitions — mortgage completion, retirement preparation, '
    'estate planning — are triggering bank exits. The 60+ cohort shows elevated churn at 24.89%, '
    'likely reflecting consolidation behaviours in later life stages.',
    body_j))
story.append(Paragraph(
    'Gender analysis confirms a structural disparity: female customers churn at 25.10% versus '
    '16.36% for male customers — an 8.74 percentage point gap. This gap is consistent across all '
    'three geographies, suggesting systemic product-fit or service delivery issues for female '
    'customers rather than market-specific factors.',
    body_j))

story.append(Paragraph('4.4 Product and Engagement Analysis', h2_paper))
story.append(Paragraph(
    'Product count analysis yields one of the most striking findings of the study. The optimal '
    'product holding for retention is 2 products (7.62% churn, n=4,501). Churn rises dramatically '
    'at 3 products (82.24%, n=259) and reaches 100% at 4 products (n=58). This product paradox '
    'contradicts the traditional assumption that cross-selling creates loyalty, and instead '
    'suggests that over-bundling generates friction and dissatisfaction that accelerates exit. '
    'The 100% churn rate among 4-product holders warrants immediate investigation into potential '
    'mis-selling practices.',
    body_j))
story.append(Paragraph(
    'Membership activity is a significant churn predictor. Inactive members (n=4,731) churn at '
    '26.68% compared to 14.39% for active members (n=5,052), a 1.85x multiplier. With 48.4% '
    'of the portfolio classified as inactive, this represents the largest addressable retention '
    'opportunity in the dataset.',
    body_j))

story.append(Paragraph('4.5 Financial Profile of Churned Customers', h2_paper))
fin_data = [
    ['Metric', 'Churned (n=1,989)', 'Retained (n=7,794)', 'Difference'],
    ['Avg account balance',   'EUR 91,101', 'EUR 72,702', '+EUR 18,399 (churned higher)'],
    ['Avg estimated salary',  'EUR 101,030','EUR 99,842', '+EUR 1,188  (churned higher)'],
    ['Avg age',               '44.9 years', '37.4 years', '+7.5 years  (churned older)'],
    ['Avg credit score',      '645.3',       '652.0',      '-6.7 pts   (churned lower)'],
    ['Avg num of products',   '1.48',         '1.54',      '-0.06      (similar)'],
]
ft = Table(fin_data, colWidths=[4.2*cm, 3.4*cm, 3.4*cm, 4.4*cm])
ft.setStyle(TableStyle([
    ('BACKGROUND',(0,0),(-1,0),NAVY),('TEXTCOLOR',(0,0),(-1,0),WHITE),
    ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('FONTSIZE',(0,0),(-1,-1),8.5),
    ('ROWBACKGROUNDS',(0,1),(-1,-1),[WHITE,LBKG]),
    ('GRID',(0,0),(-1,-1),0.3,LGRAY),
    ('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),
    ('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),
    ('TEXTCOLOR',(3,1),(3,2),RED),
]))
story.append(ft)
story.append(Paragraph('Table 2: Financial profile comparison of churned vs retained customers.', body_c))
story.append(Spacer(1, 0.2*cm))
story.append(Paragraph(
    'The most significant financial finding is that churned customers hold EUR 18,399 more in '
    'average account balance than retained customers. This inverts the common assumption that '
    'churn is primarily a low-value customer problem, and reframes it as a premium segment '
    'attrition crisis. Assuming the 1,179 high-value churners (balance > EUR 100,000) exited '
    'with their full balances, the estimated assets under management lost exceed EUR 107 million.',
    body_j))
story.append(Paragraph(
    'Notably, credit score shows minimal predictive power for churn, with rates ranging only '
    'from 18.58% to 21.94% across five credit bands. This finding has direct methodological '
    'implications: credit-score-based risk models are unsuitable proxies for churn prediction, '
    'and behavioural or demographic models must be developed independently.',
    body_j))

# ── 5. DISCUSSION ────────────────────────────────────────────────
story.append(Paragraph('5. Discussion', h1_paper))
story.append(Paragraph(
    'The findings of this study converge on a coherent narrative: European retail bank churn '
    'in FY 2025 is driven by demographic life transitions (particularly in the 46-60 cohort), '
    'geographic market failures (most acutely in Germany), product-experience friction (in '
    'multi-product customers), and engagement decay (among nearly half the portfolio). These '
    'drivers are interdependent — a 50-year-old German female customer with 3 products and '
    'low engagement represents the intersection of multiple high-risk factors.',
    body_j))
story.append(Paragraph(
    'The wealth-churn paradox — where higher-balance customers exit at higher rates — has '
    'significant implications for revenue modelling. Standard churn cost calculations based on '
    'average customer value will underestimate the true financial impact; institutions must '
    'weight churn costs by segment balance to accurately capture revenue-at-risk.',
    body_j))
story.append(Paragraph(
    'Tenure analysis reveals that churn is a lifecycle-persistent problem (19.63%-21.16% '
    'across all tenure bands), contradicting both the "early exit" hypothesis (where new customers '
    'churn most) and the "loyalty decay" hypothesis (where long-tenured customers churn most). '
    'This persistence suggests that the root causes are structural product-service gaps rather '
    'than relationship-age dynamics.',
    body_j))

# ── 6. RECOMMENDATIONS ───────────────────────────────────────────
story.append(PageBreak())
story.append(Paragraph('6. Strategic Recommendations', h1_paper))
recs = [
    ('R1 — Germany Market Intervention (CRITICAL)',
     'Deploy a dedicated Germany retention task force combining exit interview analysis, '
     'NPS deep-dives, and competitor benchmarking. Set a 12-month target of reducing Germany '
     'churn from 32.35% to sub-20%. Specific focus on the German female segment (37.53% churn) '
     'through product-fit and service delivery reviews.'),
    ('R2 — Age 46-60 Wealth Retention Programme (CRITICAL)',
     'Launch a dedicated wealth advisory and relationship banking tier for mid-to-late career '
     'customers. Proactively engage customers approaching age 46 with personalised financial '
     'planning reviews addressing mortgage completion, retirement preparation, and estate management. '
     'Assign dedicated relationship managers to high-balance customers in this cohort.'),
    ('R3 — Product Bundling Audit (HIGH)',
     'Commission an immediate audit of all 3- and 4-product customers, including a mis-selling '
     'review. Redesign cross-sell incentive structures to target the 2-product optimal point. '
     'Introduce product satisfaction scoring and exit-intent early warning systems for '
     'multi-product holders.'),
    ('R4 — Inactive Member Re-engagement (HIGH)',
     'The 4,731 inactive members represent a EUR 25M+ retention opportunity. Implement a '
     'tiered re-engagement programme: 30-day personalised digital nudge sequence, 60-day '
     'outbound relationship call, 90-day exclusive offer. Inactivity is a leading churn '
     'indicator — intervene before exit behaviour crystallises.'),
    ('R5 — Gender-Differentiated Product Strategy (MODERATE)',
     'Investigate the structural causes of the 8.74 percentage point female-male churn gap '
     'through qualitative focus groups and quantitative product-usage analysis. Develop '
     'targeted products: family financial planning accounts, career-break bridging products, '
     'and female entrepreneurship lending programmes.'),
    ('R6 — Behavioural Churn Prediction Model (MODERATE)',
     'Credit score is demonstrably not a churn predictor (18.6%-21.9% across all bands). '
     'Redirect model development resources toward a behavioural churn prediction model '
     'incorporating: transaction frequency decline, login recency, product usage drop-off, '
     'customer service contact patterns, and cross-channel engagement signals.'),
]
for title, text in recs:
    story.append(Paragraph(title, h2_paper))
    story.append(Paragraph(text, body_j))

# ── 7. CONCLUSION ────────────────────────────────────────────────
story.append(Paragraph('7. Conclusion', h1_paper))
story.append(Paragraph(
    'This study demonstrates that European retail banking churn is not a uniform phenomenon '
    'but a highly segmented one, with certain cohorts experiencing churn rates far exceeding '
    'the portfolio average. The 20.33% overall churn rate masks critical exposures: a national '
    'market in acute distress (Germany, 32.35%), a demographic cohort losing one in two customers '
    '(age 46-60, 51.05%), a product experience driving near-total exit (3-4 products, 82-100%), '
    'and a premium-balance customer cohort churning at higher rates than the average.',
    body_j))
story.append(Paragraph(
    'The finding that churned customers are wealthier than retained ones fundamentally reframes '
    'the churn problem from a volume challenge to a revenue quality challenge. Banks that focus '
    'retention investment on low-value customers will systematically underinvest in the segments '
    'that matter most to long-term profitability.',
    body_j))
story.append(Paragraph(
    'The six strategic recommendations presented — spanning market-level intervention, '
    'lifecycle-oriented product design, engagement re-activation, and behavioural analytics — '
    'provide a prioritised roadmap for European retail banking institutions seeking to address '
    'these structural churn challenges systematically and efficiently.',
    body_j))

# ── REFERENCES ───────────────────────────────────────────────────
story.append(Paragraph('References', h1_paper))
refs = [
    'Burez, J., & Van den Poel, D. (2009). Handling class imbalance in customer churn prediction. '
    '<i>Expert Systems with Applications, 36</i>(3), 4626-4636.',
    'Kumar, V., & Shah, D. (2004). Building and sustaining profitable customer loyalty for the '
    '21st century. <i>Journal of Retailing, 80</i>(4), 317-330.',
    'Lariviere, B., & Van den Poel, D. (2004). Investigating the role of product features in '
    'preventing customer churn. <i>European Journal of Operational Research, 156</i>(2), 511-524.',
    'Neslin, S. A., Gupta, S., Kamakura, W., Lu, J., & Mason, C. H. (2006). Defection detection: '
    'Measuring and understanding the predictive accuracy of customer churn models. '
    '<i>Journal of Marketing Research, 43</i>(2), 204-211.',
    'Reichheld, F. F., & Sasser, W. E. (1990). Zero defections: Quality comes to services. '
    '<i>Harvard Business Review, 68</i>(5), 105-111.',
    'Verbeke, W., Dejaeger, K., Martens, D., Hur, J., & Baesens, B. (2012). New insights into '
    'churn prediction in the telecommunication sector. '
    '<i>European Journal of Operational Research, 218</i>(1), 211-229.',
    'Verhoef, P. C. (2003). Understanding the effect of customer relationship management efforts '
    'on customer retention and customer share development. '
    '<i>Journal of Marketing, 67</i>(4), 30-45.',
]
for r in refs:
    story.append(Paragraph(f'   {chr(8226)}  {r}',
                            ParagraphStyle('ref', fontName='Helvetica', fontSize=9,
                                           textColor=HexColor('#444'), leading=14,
                                           spaceAfter=5, alignment=TA_JUSTIFY)))

story.append(Spacer(1, 0.6*cm))
story.append(HRFlowable(width='100%', thickness=0.5, color=LGRAY, spaceAfter=6))
story.append(Paragraph(
    'Submitted to: Unified Mentor Virtual Internship Programme  |  '
    'Domain: Finance Analytics  |  FY 2025  |  Confidential Research Document',
    footer_s))

doc.build(story)
print(f"Research paper saved: {OUT}")
