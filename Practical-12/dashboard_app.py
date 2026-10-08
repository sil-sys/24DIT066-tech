"""
========================================================================================
Interactive Customer Sales Dashboard (Streamlit + Plotly)
BDA Practical 12: Customer Sales Dashboard Using Interactive Analytics
Author: Sil Shah (24DIT066)
Run with: streamlit run dashboard_app.py
========================================================================================
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

st.set_page_config(
    page_title="RetailEdge - Customer Sales Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load data
@st.cache_data
def load_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, "superstore_sales.csv")
    df = pd.read_csv(csv_path)
    df['Order Date'] = pd.to_datetime(df['Order Date'])
    df['Ship Date'] = pd.to_datetime(df['Ship Date'])
    df['Year'] = df['Order Date'].dt.year
    df['Quarter'] = df['Order Date'].dt.to_period('Q').astype(str)
    df['YearMonth'] = df['Order Date'].dt.to_period('M').astype(str)
    return df

df = load_data()

# ----------------- SIDEBAR CONTROLS & FILTERS -----------------
st.sidebar.title("🎛️ Dashboard Controls")
st.sidebar.markdown("**Interactive Filters for Visual Exploration**")

# Region Filter
regions = ["All Regions"] + sorted(list(df['Region'].unique()))
selected_region = st.sidebar.selectbox("Select Geographic Region:", regions)

# Category Filter
categories = ["All Categories"] + sorted(list(df['Category'].unique()))
selected_category = st.sidebar.selectbox("Select Product Category:", categories)

# Customer Segment Filter
segments = ["All Segments"] + sorted(list(df['Segment'].unique()))
selected_segment = st.sidebar.selectbox("Select Customer Segment:", segments)

# Year Filter
years = sorted(list(df['Year'].unique()))
selected_years = st.sidebar.multiselect("Select Years:", years, default=years)

# Apply filters
filtered_df = df.copy()
if selected_region != "All Regions":
    filtered_df = filtered_df[filtered_df['Region'] == selected_region]
if selected_category != "All Categories":
    filtered_df = filtered_df[filtered_df['Category'] == selected_category]
if selected_segment != "All Segments":
    filtered_df = filtered_df[filtered_df['Segment'] == selected_segment]
if selected_years:
    filtered_df = filtered_df[filtered_df['Year'].isin(selected_years)]

# ----------------- MAIN DASHBOARD HEADER -----------------
st.title("📊 RetailEdge Executive Sales & Profitability Dashboard")
st.markdown(
    """
    **Interactive Business Intelligence & Decision-Support System**  
    *Student ID: 24DIT066 | Course: CSUE301 Big Data Analytics | DEPSTAR (CHARUSAT)*
    """
)
st.markdown("---")

# ----------------- TOP KPI SUMMARY METRICS -----------------
total_sales = filtered_df['Sales'].sum()
total_profit = filtered_df['Profit'].sum()
margin = (total_profit / total_sales * 100) if total_sales > 0 else 0
orders = filtered_df['Order ID'].nunique()
aov = total_sales / orders if orders > 0 else 0

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("💰 Total Sales", f"${total_sales:,.0f}")
col2.metric("📈 Net Profit", f"${total_profit:,.0f}")
col3.metric("🎯 Profit Margin", f"{margin:.2f}%")
col4.metric("📦 Total Orders", f"{orders:,}")
col5.metric("🛒 Avg Order Value", f"${aov:,.0f}")

st.markdown("---")

# ----------------- CHARTS ROW 1: TRENDS & CATEGORY SHARE -----------------
r1_col1, r1_col2 = st.columns([2, 1])

with r1_col1:
    st.subheader("📅 Monthly Sales & Profit Trajectory")
    monthly_trend = filtered_df.groupby('YearMonth').agg({'Sales': 'sum', 'Profit': 'sum'}).reset_index().sort_values('YearMonth')
    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(x=monthly_trend['YearMonth'], y=monthly_trend['Sales'], mode='lines+markers', name='Sales ($)', line=dict(color='#0D47A1', width=3)))
    fig_trend.add_trace(go.Scatter(x=monthly_trend['YearMonth'], y=monthly_trend['Profit'], mode='lines+markers', name='Profit ($)', line=dict(color='#2E7D32', width=2.5)))
    fig_trend.update_layout(xaxis_title="Month", yaxis_title="Amount ($)", hovermode="x unified", height=380, margin=dict(l=20, r=20, t=30, b=20))
    st.plotly_chart(fig_trend, use_container_width=True)

with r1_col2:
    st.subheader("🍩 Category Revenue Share")
    cat_dist = filtered_df.groupby('Category')['Sales'].sum().reset_index()
    fig_pie = px.pie(cat_dist, names='Category', values='Sales', hole=0.45, color_discrete_sequence=['#1E88E5', '#00ACC1', '#5E35B1'])
    fig_pie.update_layout(height=380, margin=dict(l=10, r=10, t=30, b=20))
    st.plotly_chart(fig_pie, use_container_width=True)

# ----------------- CHARTS ROW 2: DRILL-DOWN & REGIONS -----------------
r2_col1, r2_col2 = st.columns(2)

with r2_col1:
    st.subheader("🔍 Sub-Category Profitability Drill-Down")
    subcat_p = filtered_df.groupby('Sub-Category').agg({'Sales': 'sum', 'Profit': 'sum'}).reset_index()
    subcat_p['Profit Margin %'] = (subcat_p['Profit'] / subcat_p['Sales'] * 100).round(2)
    subcat_p['Color'] = subcat_p['Profit'].apply(lambda x: '#2E7D32' if x >= 0 else '#C62828')
    fig_subcat = px.bar(
        subcat_p.sort_values('Sales', ascending=False),
        x='Sub-Category', y='Sales', color='Profit',
        color_continuous_scale=['#C62828', '#FFF9C4', '#2E7D32'],
        title="Sub-Category Sales Colored by Net Profit/Loss"
    )
    fig_subcat.update_layout(height=380, margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig_subcat, use_container_width=True)

with r2_col2:
    st.subheader("🗺️ Regional Sales & Profit Comparison")
    reg_p = filtered_df.groupby('Region').agg({'Sales': 'sum', 'Profit': 'sum'}).reset_index()
    fig_reg = go.Figure(data=[
        go.Bar(name='Sales ($)', x=reg_p['Region'], y=reg_p['Sales'], marker_color='#0277BD'),
        go.Bar(name='Profit ($)', x=reg_p['Region'], y=reg_p['Profit'], marker_color='#43A047')
    ])
    fig_reg.update_layout(barmode='group', height=380, margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig_reg, use_container_width=True)

# ----------------- DRILL-THROUGH DATA EXPLORER -----------------
st.markdown("---")
st.subheader("📋 Granular Order Level Drill-Through Table")
with st.expander("Explore Filtered Order Records (Top 100 Rows)"):
    display_cols = ['Order ID', 'Order Date', 'Customer Name', 'Segment', 'Region', 'State', 'Category', 'Sub-Category', 'Sales', 'Discount', 'Profit']
    st.dataframe(filtered_df[display_cols].head(100), use_container_width=True)

st.info("💡 **Executive Takeaway**: Technology products (Copiers & Phones) drive major corporate profitability, while deep discounting in Furniture (Tables & Bookcases) creates bottom-line friction. Strategic discount thresholds should be enforced.")
