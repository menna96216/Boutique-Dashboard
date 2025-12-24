# -----------------------------
# 1. Import Libraries
# -----------------------------
import pandas as pd
import plotly.express as px
import streamlit as st

# -----------------------------
# 2. Load Data
# -----------------------------
df = pd.read_csv("Data - Sheet1.csv")  # عدلي لو Excel
df.drop_duplicates(inplace=True)
df['profit'] = (df['unit_price'] - df['cost']) * df['units_sold']
df['margin'] = (df['unit_price'] - df['cost']) / df['unit_price']
df['date'] = pd.to_datetime(df['date'])
df['month'] = df['date'].dt.to_period('M').astype(str)

# -----------------------------
# 3. Page Config
# -----------------------------
st.set_page_config(page_title="Boutique Dashboard", layout="wide")
st.title("Boutique Sales Dashboard")

# -----------------------------
# 4. Sidebar Filters
# -----------------------------
st.sidebar.header("Filters")
channel = st.sidebar.selectbox("Select Channel", options=['All'] + list(df['channel'].unique()))
style = st.sidebar.selectbox("Select Style", options=['All'] + list(df['style'].unique()))
segment = st.sidebar.selectbox("Select Customer Segment", options=['All'] + list(df['customer_segment'].unique()))
product = st.sidebar.selectbox("Select Product Type", options=['All'] + list(df['product_type'].unique()))

# -----------------------------
# 5. Filter Data
# -----------------------------
dff = df.copy()
if channel != 'All': dff = dff[dff['channel']==channel]
if style != 'All': dff = dff[dff['style']==style]
if segment != 'All': dff = dff[dff['customer_segment']==segment]
if product != 'All': dff = dff[dff['product_type']==product]

# -----------------------------
# 6. KPIs
# -----------------------------
total_profit = dff['profit'].sum()
avg_margin = dff['margin'].mean()
total_units = dff['units_sold'].sum()
total_ad = dff['ad_spend'].sum()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Profit", f"${total_profit:,.2f}")
col2.metric("Average Margin", f"{avg_margin:.2%}")
col3.metric("Total Units Sold", f"{total_units}")
col4.metric("Total Ad Spend", f"${total_ad:,.2f}")

# -----------------------------
# 7. Profit per Channel
# -----------------------------
channel_fig = px.bar(dff.groupby('channel')['profit'].sum().reset_index(),
                     x='channel', y='profit', color='channel',
                     title="Total Profit by Channel")
st.plotly_chart(channel_fig, use_container_width=True)

# -----------------------------
# 8. Average Profit per Style
# -----------------------------
style_fig = px.bar(dff.groupby('style')['profit'].mean().reset_index(),
                   x='style', y='profit', color='style',
                   title="Average Profit by Style")
st.plotly_chart(style_fig, use_container_width=True)

# -----------------------------
# 9. Stacked Bar: Profit by Product Type & Customer Segment
# -----------------------------
stacked_data = dff.groupby(['product_type','customer_segment'])['profit'].sum().reset_index()
stacked_fig = px.bar(stacked_data, x='product_type', y='profit', color='customer_segment',
                     title="Profit by Product Type and Customer Segment")
st.plotly_chart(stacked_fig, use_container_width=True)

# -----------------------------
# 10. Scatter: Profit vs Ad Spend
# -----------------------------
scatter_fig = px.scatter(dff, x='ad_spend', y='profit', color='channel', hover_data=['product_type'],
                         title="Profit vs Ad Spend")
st.plotly_chart(scatter_fig, use_container_width=True)

# -----------------------------
# 11. Monthly Trend
# -----------------------------
monthly = dff.groupby('month')[['profit','margin']].mean().reset_index()
monthly_fig = px.line(monthly, x='month', y=['profit','margin'], markers=True,
                      title="Monthly Profit & Margin Trend")
st.plotly_chart(monthly_fig, use_container_width=True)

# -----------------------------
# 12. Heatmap: Margin by Product Type & Style
# -----------------------------
pivot = dff.pivot_table(values='margin', index='product_type', columns='style', aggfunc='mean')
heatmap_fig = px.imshow(pivot, text_auto=".2f", color_continuous_scale='YlGnBu',
                        labels={'x':'Style','y':'Product Type','color':'Margin'},
                        title="Margin by Product Type and Style")
st.plotly_chart(heatmap_fig, use_container_width=True)

# -----------------------------
# 13. Heatmap: Margin by Style × Channel
# -----------------------------
pivot_style_channel = dff.pivot_table(values='margin', index='style', columns='channel', aggfunc='mean')
heatmap_style_channel_fig = px.imshow(pivot_style_channel, text_auto=".2f", color_continuous_scale='Viridis',
                                      labels={'x':'Channel','y':'Style','color':'Margin'},
                                      title="Margin by Style and Channel")
st.plotly_chart(heatmap_style_channel_fig, use_container_width=True)

# -----------------------------
# 14. Top Performers Table
# -----------------------------
top_table = dff.groupby('product_type')[['profit','margin','units_sold']].sum().reset_index()
top_table = top_table.sort_values(by='profit', ascending=False).head(5)
st.subheader("Top 5 Products by Profit")
st.table(top_table)
