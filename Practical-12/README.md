# Practical 12: Customer Sales Dashboard Using Interactive Analytics

## Student Information
- **Student ID:** 24DIT066
- **Student Name:** Sil Shah
- **Course:** CSUE301 : Big Data Analytics
- **Institute:** Devang Patel Institute of Advance Technology and Research (DEPSTAR)
- **University:** Charotar University of Science and Technology (CHARUSAT)
- **CO / PO Mapping:** CO6, PO1, PO2, PO4, PO5, PO10, PO12

---

## Aim
To design, implement, and publish an interactive Customer Sales Dashboard using Business Intelligence tools and Interactive Analytics for executive decision-making.

---

## Problem Definition & Scenario
You are working as a Data Visualization Analyst at a retail analytics company. Management wants to monitor sales performance across products, regions, and customer segments through an interactive dashboard. Static reports are insufficient for decision-making. Your task is to design an interactive dashboard that allows management to explore sales data and identify key business trends.

---

## Files Included
- `practical12.py`: Complete Python script for dataset validation, temporal feature engineering, multi-dimensional KPI calculation, and generation of all high-resolution dashboard visuals.
- `generate_sales_dataset.py`: Realistic multi-year Superstore Sales dataset generator.
- `superstore_sales.csv`: Ingested dataset containing 5,000 multi-category, multi-region sales orders.
- `dashboard_app.py`: Full interactive Streamlit + Plotly web dashboard with real-time cross-filtering, metric cards, and drill-through explorer.
  - Run locally: `streamlit run dashboard_app.py`
- `Practical_12_Customer_Sales_Dashboard.docx`: Comprehensive Word document matching institutional format with cover page, methodology, KPI formulations, high-res figures, tables, answers to Q1-Q5, supplementary problems, post-lab work, and viva rubrics.
- `sales_dashboard_report.txt`: Automated executive KPI and business performance summary report.
- `kpi_summary_dashboard.png`: Executive dashboard overview with KPI summary cards, monthly trend, category donut, and regional comparison.
- `category_drilldown_analysis.png`: Sub-category profitability drill-down highlighting high-margin Technology vs loss-making Furniture.
- `regional_performance_map.png`: Regional and state-level sales and profitability distribution.
- `monthly_quarterly_trend.png`: Quarterly sales and profit performance with QoQ growth rate.
- `customer_segmentation_analysis.png`: Customer segment distribution and profit efficiency.
- `create_word_doc.py`: Automated generator script for compiling the Word document.

---

## Key Business Insights & Findings
- **Total Gross Sales:** $8,885,748.66
- **Total Net Profit:** $683,907.28 (Overall Profit Margin: 7.70%)
- **Top Performing Category:** Technology accounts for 65.49% of revenue ($5.82M) and yields a 14.23% profit margin ($827.8k profit), driven by Copiers (24.81% margin) and Phones.
- **Critical Risk Area:** Furniture recorded a net loss (-$217,559.55, -8.86% margin) due to deep discounting (>= 24%) on bulky Tables (-$189.4k loss) and Bookcases (-$71.3k loss).
- **Segment Leadership:** Consumer segment represents ~52% of transaction volume, while the Home Office segment produces the highest margin efficiency (9.35%) and Average Order Value ($1,861.88).
