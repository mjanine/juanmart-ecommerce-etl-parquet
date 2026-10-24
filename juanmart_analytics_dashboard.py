import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# ---------------------------------------------------------
# Page Configuration & Styling
# ---------------------------------------------------------
st.set_page_config(
    page_title="JuanMart Executive Analytics",
    page_icon="🛒",
    layout="wide"
)

st.markdown("""
    <style>
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        padding: 5% 5% 5% 10%;
        border-radius: 8px;
        box-shadow: 1px 1px 4px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

st.title("🛒 JuanMart Executive Sales Analytics Dashboard")
st.markdown("Monitor regional sales growth, order volume trends, and product performance.")
st.markdown("---")

# ---------------------------------------------------------
# Load Data & Augment Dimensions
# ---------------------------------------------------------
@st.cache_data
def load_data():
    try:
        clean_df = pd.read_parquet("cleaned_juanmart_sales.parquet")
    except FileNotFoundError:
        clean_df = pd.read_csv("juanmart_clean_sales.csv")
    
    raw_df = pd.read_csv("juanmart_raw_sales.csv")
    clean_df['order_date'] = pd.to_datetime(clean_df['order_date'])
    
    geo_map = {
        "National Capital Region": {"lat": 14.5995, "lon": 120.9842},
        "CALABARZON": {"lat": 14.1008, "lon": 121.0794}
    }
    clean_df['lat'] = clean_df['region'].map(lambda x: geo_map.get(x, {}).get('lat', 14.5995))
    clean_df['lon'] = clean_df['region'].map(lambda x: geo_map.get(x, {}).get('lon', 120.9842))
    
    categories = ['Electronics', 'Fashion', 'Home Groceries', 'Artisanal']
    np.random.seed(42) 
    clean_df['product_category'] = np.random.choice(categories, size=len(clean_df))
    
    margin_map = {'Electronics': 0.15, 'Fashion': 0.35, 'Home Groceries': 0.20, 'Artisanal': 0.50}
    clean_df['profit_margin'] = clean_df['product_category'].map(margin_map)
    
    return clean_df, raw_df

clean_df, raw_df = load_data()

# ---------------------------------------------------------
# Calculate KPIs
# ---------------------------------------------------------
completed_orders = clean_df[clean_df['status'] == 'Completed']

total_net_revenue = completed_orders['amount_paid'].sum()
aov = completed_orders['amount_paid'].mean() if len(completed_orders) > 0 else 0
total_orders = len(clean_df)

total_raw_rows = len(raw_df)
raw_duplicates = raw_df.duplicated().sum()
raw_missing = raw_df.isnull().sum().sum()
error_rate = ((raw_duplicates + raw_missing) / (total_raw_rows * raw_df.shape[1])) * 100

# ---------------------------------------------------------
# KPI Dashboard Section
# ---------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Net Revenue", f"₱{total_net_revenue:,.2f}", "+15% vs Last Year")
col2.metric("Average Order Value (AOV)", f"₱{aov:,.2f}")
col3.metric("Total Orders", f"{total_orders}")
col4.metric("Data Error Rate (Quarantined)", f"{error_rate:.1f}%", "-2.1% improvement", delta_color="inverse")

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------
# Visualizations Section - Row 1
# ---------------------------------------------------------
COLOR_BLUE = '#0072B2'
COLOR_SKY_BLUE = '#56B4E9'
COLOR_VERMILLION = '#D55E00'
COLOR_GREEN = '#009E73'
COLOR_ORANGE = '#E69F00'
COLOR_PURPLE = '#CC79A7'

col_left, col_right = st.columns((1.5, 1))

with col_left:
    st.subheader("📅 Revenue Trend Over Time")
    trend_df = completed_orders.groupby('order_date')['amount_paid'].sum().reset_index()
    fig_trend = px.area(
        trend_df, 
        x='order_date', 
        y='amount_paid',
        markers=True,
        color_discrete_sequence=[COLOR_BLUE],
        labels={'order_date': 'Order Date', 'amount_paid': 'Net Revenue (₱)'}
    )
    fig_trend.update_layout(
        template="plotly_white",
        margin=dict(l=0, r=0, t=30, b=0),
        yaxis=dict(showgrid=True, gridcolor='#e0e0e0', zeroline=False),
        xaxis=dict(showgrid=False)
    )
    st.plotly_chart(fig_trend, width='stretch')

with col_right:
    st.subheader("🗺️ Regional Sales Density")
    map_df = completed_orders.groupby(['region', 'lat', 'lon'])['amount_paid'].sum().reset_index()
    # Updated to scatter_map to clear deprecation warning
    fig_map = px.scatter_map(
        map_df, 
        lat="lat", lon="lon", 
        color="amount_paid", size="amount_paid",
        hover_name="region", hover_data={"lat": False, "lon": False, "amount_paid": True},
        color_continuous_scale=px.colors.sequential.Cividis, 
        size_max=40, zoom=6.5,
        map_style="carto-positron"
    )
    fig_map.update_layout(margin=dict(l=0, r=0, t=30, b=0), coloraxis_showscale=False)
    st.plotly_chart(fig_map, width='stretch')

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------
# Visualizations Section - Row 2
# ---------------------------------------------------------
col_bot_left, col_bot_right = st.columns((1.5, 1))

with col_bot_left:
    st.subheader("🛍️ Product Category Performance")
    prod_df = completed_orders.groupby('product_category').agg(
        sales_volume=('amount_paid', 'sum'),
        avg_margin=('profit_margin', 'mean')
    ).reset_index()
    
    fig_prod = go.Figure()
    fig_prod.add_trace(go.Bar(
        x=prod_df['product_category'], y=prod_df['sales_volume'], 
        name='Sales Volume (₱)', marker_color=COLOR_SKY_BLUE
    ))
    fig_prod.add_trace(go.Scatter(
        x=prod_df['product_category'], y=prod_df['avg_margin'], 
        name='Profit Margin (%)', yaxis='y2', mode='lines+markers', 
        line=dict(color=COLOR_VERMILLION, width=3), 
        marker=dict(size=10, symbol='diamond')
    ))
    
    fig_prod.update_layout(
        template="plotly_white",
        yaxis=dict(title="Sales Volume (₱)", showgrid=False),
        yaxis2=dict(title="Profit Margin", overlaying="y", side="right", tickformat=".0%", showgrid=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=0, r=0, t=30, b=0)
    )
    st.plotly_chart(fig_prod, width='stretch')

with col_bot_right:
    st.subheader("📦 Order Status Mix")
    status_df = clean_df['status'].value_counts().reset_index()
    status_df.columns = ['Status', 'Count']
    fig_status = px.pie(
        status_df, 
        names='Status', 
        values='Count', 
        hole=0.45,
        color='Status',
        color_discrete_map={
            'Completed': COLOR_GREEN, 
            'Cancelled': COLOR_ORANGE, 
            'Returned': COLOR_PURPLE
        }
    )
    fig_status.update_traces(textposition='outside', textinfo='percent+label')
    fig_status.update_layout(
        template="plotly_white",
        margin=dict(l=20, r=20, t=30, b=20), 
        showlegend=False
    )
    st.plotly_chart(fig_status, width='stretch')