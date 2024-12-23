import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configure page layout
st.set_page_config(page_title="Production Dashboard", layout="wide", initial_sidebar_state="expanded")

# Load and preprocess data
@st.cache_data
def load_data():
    df_actual_time = pd.read_csv('data-actual-time-work-2023.csv')

    # Convert date columns to datetime
    df_actual_time['Posting Date'] = pd.to_datetime(df_actual_time['Posting Date'], errors='coerce')

    # Add calculated columns
    df_actual_time['Total Cost'] = df_actual_time['Direct \nCost'] + df_actual_time['Overhead \nCost']

    return df_actual_time

df_actual_time = load_data()

# Sidebar filters
with st.sidebar:
    st.header("Filters")
    date_range = st.date_input(
        "Date Range", [df_actual_time['Posting Date'].min(), df_actual_time['Posting Date'].max()]
    )
    departments = st.multiselect("Departments", df_actual_time['Department'].unique())

# Apply filters
filtered_data = df_actual_time[
    (df_actual_time['Posting Date'] >= pd.to_datetime(date_range[0])) &
    (df_actual_time['Posting Date'] <= pd.to_datetime(date_range[1]))
]
if departments:
    filtered_data = filtered_data[filtered_data['Department'].isin(departments)]

# Dashboard Title
st.title("📊 Wood Production Dashboard")

# First Row: Metrics and Insights
col1, col2, col3, col4, col5 = st.columns(5)

# Column 1: Key Metrics
with col1:
    st.markdown("### Key Metrics")
    st.metric("Total Orders", len(filtered_data['Order No.'].unique()))
    st.metric("Avg. Time (hrs)", round(filtered_data['Time'].mean(), 2))
    st.metric("Total Quantity", int(filtered_data['Quantity'].sum()))
    st.metric("Total Cost", f"${filtered_data['Total Cost'].sum():,.2f}")

# Column 2: Distribution of Time Taken
with col2:
    fig_hist = px.histogram(filtered_data, x='Time', nbins=30, title="Distribution of Time Taken")
    st.plotly_chart(fig_hist, use_container_width=True)

# Column 3: Correlation Between Time and Quantity
with col3:
    fig_scatter = px.scatter(filtered_data, x='Time', y='Quantity', title="Correlation: Time vs Quantity")
    st.plotly_chart(fig_scatter, use_container_width=True)

# Column 4: Quantity Trends Over Time by Department
with col4:
    time_dept_summary = filtered_data.groupby(['Posting Date', 'Department'])['Quantity'].sum().reset_index()
    fig_line_dept = px.line(
        time_dept_summary,
        x='Posting Date',
        y='Quantity',
        color='Department',
        title="Quantity Trends Over Time by Department"
    )
    st.plotly_chart(fig_line_dept, use_container_width=True)

# Column 5: Orders by Department (Pie Chart)
with col5:
    dept_order_summary = filtered_data['Department'].value_counts().reset_index()
    dept_order_summary.columns = ['Department', 'Count']
    fig_pie = px.pie(dept_order_summary, names='Department', values='Count', title="Orders by Department")
    st.plotly_chart(fig_pie, use_container_width=True)

col6, col7, col8, col9, col10 = st.columns(5)

# Column 6: Heatmap for Efficiency (Item Type vs Department)
with col6:
    heatmap_data = filtered_data.groupby(['Item', 'Department'])['Time'].mean().reset_index()
    heatmap_fig = px.density_heatmap(
        heatmap_data, x='Department', y='Item', z='Time',
        color_continuous_scale='Viridis', title="Efficiency Heatmap (Avg Time): Item vs Department"
    )
    st.plotly_chart(heatmap_fig, use_container_width=True)

# Column 7: Largest Quantities by Sales Orders
with col7:
    sales_order_summary = filtered_data.groupby('Sales order')['Quantity'].sum().reset_index()
    sales_order_summary = sales_order_summary.sort_values('Quantity', ascending=False).head(10)
    fig_sales_bar = px.bar(
        sales_order_summary, x='Sales order', y='Quantity', title="Top Sales Orders by Quantity"
    )
    st.plotly_chart(fig_sales_bar, use_container_width=True)

# Column 8: Cost Breakdown by Department
with col8:
    cost_summary = filtered_data.groupby('Department')[['Direct \nCost', 'Overhead \nCost']].sum().reset_index()
    cost_fig = go.Figure(data=[
        go.Bar(name='Direct Cost', x=cost_summary['Department'], y=cost_summary['Direct \nCost']),
        go.Bar(name='Overhead Cost', x=cost_summary['Department'], y=cost_summary['Overhead \nCost'])
    ])
    cost_fig.update_layout(
        barmode='stack', title="Cost Breakdown by Department (Direct vs Overhead)"
    )
    st.plotly_chart(cost_fig, use_container_width=True)

# Column 9: Consistently Produced Items
with col9:
    item_summary = filtered_data.groupby('Item')['Quantity'].sum().reset_index()
    item_summary = item_summary.sort_values('Quantity', ascending=False).head(10)
    fig_item_bar = px.bar(
        item_summary, x='Item', y='Quantity', title="Top 10 Consistently Produced Items"
    )
    st.plotly_chart(fig_item_bar, use_container_width=True)

# Column 10: Quantity vs Average Cost Per Unit
with col10:
    filtered_data['Avg Cost Per Unit'] = filtered_data['Total Cost'] / filtered_data['Quantity']
    quantity_cost_summary = filtered_data.groupby('Quantity')['Avg Cost Per Unit'].mean().reset_index()
    fig_quantity_cost = px.scatter(
        quantity_cost_summary, x='Quantity', y='Avg Cost Per Unit',
        title="Quantity vs Avg Cost Per Unit"
    )
    st.plotly_chart(fig_quantity_cost, use_container_width=True)
