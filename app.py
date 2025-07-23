# app.py

import streamlit as st
import pandas as pd
import plotly.express as px

# --- Page Configuration ---
st.set_page_config(
    page_title="Gig Work 'True Profit' Dashboard",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Data Loading and Caching ---
@st.cache_data
def load_data(file_path):
    """Loads data from a CSV file and converts date column."""
    df = pd.read_csv(file_path)
    df['date'] = pd.to_datetime(df['date']).dt.date
    return df

# --- Main App ---
def main():
    # Load the data
    try:
        df = load_data('gig_work_data.csv')
    except FileNotFoundError:
        st.error("Error: 'gig_work_data.csv' not found. Please run `generate_data.py` first.")
        return

    # --- Sidebar Filters ---
    st.sidebar.header("Dashboard Filters")
    
    # Date Range Filter
    min_date = df['date'].min()
    max_date = df['date'].max()
    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # Platform Filter
    platforms = df['platform'].unique().tolist()
    selected_platforms = st.sidebar.multiselect(
        "Select Platform(s)",
        options=platforms,
        default=platforms
    )

    # --- Filtering Data Based on User Input ---
    start_date, end_date = date_range
    df_filtered = df[
        (df['date'] >= start_date) &
        (df['date'] <= end_date) &
        (df['platform'].isin(selected_platforms))
    ]

    if df_filtered.empty:
        st.warning("No data available for the selected filters. Please adjust your selection.")
        return

    # --- Main Page Content ---
    st.title("🚗 Gig Work 'True Profit' Dashboard")
    st.markdown("This dashboard moves beyond gross earnings to reveal the **true profitability** of your gig work.")

    # --- Key Performance Indicators (KPIs) ---
    total_gross_fare = df_filtered['gross_fare'].sum()
    total_platform_fees = df_filtered['platform_fees'].sum()
    total_vehicle_costs = df_filtered['vehicle_costs'].sum()
    total_true_profit = df_filtered['true_profit'].sum()
    total_hours_worked = df_filtered['total_time_minutes'].sum() / 60
    
    # Avoid division by zero
    true_hourly_wage = total_true_profit / total_hours_worked if total_hours_worked > 0 else 0

    st.markdown("### High-Level Metrics")
    col1, col2, col3 = st.columns(3)
    col1.metric("True Profit", f"${total_true_profit:,.2f}")
    col2.metric("True Hourly Wage", f"${true_hourly_wage:,.2f}")
    col3.metric("Total Hours Worked", f"{total_hours_worked:,.1f}")

    st.markdown("---")

    # --- Visualizations ---
    st.markdown("### Deep-Dive Analysis")
    
    # Time Series: True Profit Over Time
    profit_over_time = df_filtered.groupby('date')['true_profit'].sum().reset_index()
    fig_line = px.line(
        profit_over_time,
        x='date',
        y='true_profit',
        title='Daily True Profit Over Time',
        labels={'true_profit': 'True Profit ($)', 'date': 'Date'}
    )
    fig_line.update_layout(title_x=0.5)
    st.plotly_chart(fig_line, use_container_width=True)

    # Column Layout for side-by-side charts
    col_viz1, col_viz2 = st.columns(2)

    with col_viz1:
        # Pie Chart: Cost Breakdown
        cost_breakdown_data = {
            'Category': ['True Profit', 'Platform Fees', 'Vehicle Costs'],
            'Amount': [total_true_profit, total_platform_fees, total_vehicle_costs]
        }
        fig_pie = px.pie(
            cost_breakdown_data,
            names='Category',
            values='Amount',
            title='Breakdown of Gross Earnings',
            hole=0.3,
            color_discrete_map={
                'True Profit': 'green',
                'Platform Fees': 'orange',
                'Vehicle Costs': 'red'
            }
        )
        fig_pie.update_layout(title_x=0.5)
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_viz2:
        # Bar Chart: Platform Performance (True Hourly Wage)
        platform_performance = df_filtered.groupby('platform').apply(
            lambda x: (x['true_profit'].sum() / (x['total_time_minutes'].sum() / 60)) if x['total_time_minutes'].sum() > 0 else 0
        ).reset_index(name='true_hourly_wage')
        
        fig_bar = px.bar(
            platform_performance,
            x='platform',
            y='true_hourly_wage',
            title='Platform Comparison by True Hourly Wage',
            labels={'true_hourly_wage': 'Avg. True Hourly Wage ($)', 'platform': 'Platform'},
            color='platform'
        )
        fig_bar.update_layout(title_x=0.5)
        st.plotly_chart(fig_bar, use_container_width=True)

    # --- Raw Data View ---
    with st.expander("View Raw Data for Selected Period"):
        st.dataframe(df_filtered)


if __name__ == "__main__":
    main()