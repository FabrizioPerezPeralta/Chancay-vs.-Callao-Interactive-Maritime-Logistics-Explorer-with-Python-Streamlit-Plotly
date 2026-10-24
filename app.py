"""Interactive Business Intelligence Dashboard.

Built with Streamlit, Pandas, Plotly, and Seaborn to provide dynamic
analytics, cross-filtering, and executive insights.
"""

import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import streamlit as st

# Configure page settings
st.set_page_config(
    page_title="Executive BI Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling for premium analytics aesthetics
CUSTOM_CSS = """
<style>
    .metric-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    }
    .metric-title {
        color: #94a3b8;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-value {
        color: #f8fafc;
        font-size: 1.75rem;
        font-weight: 700;
        margin-top: 4px;
    }
    .metric-delta {
        font-size: 0.85rem;
        font-weight: 500;
        margin-top: 2px;
    }
    .delta-positive { color: #10b981; }
    .delta-negative { color: #ef4444; }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 16px;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


@st.cache_data
def load_data(filepath: str) -> pd.DataFrame:
    """Load and preprocess the dataset with high-performance caching."""
    if not os.path.exists(filepath):
        # Fallback empty dataframe with required schema
        return pd.DataFrame()

    df = pd.read_csv(filepath)
    df["Order_Date"] = pd.to_datetime(df["Order_Date"])
    df["Ship_Date"] = pd.to_datetime(df["Ship_Date"])
    df["Year"] = df["Order_Date"].dt.year
    df["Year_Month"] = df["Order_Date"].dt.to_period("M").astype(str)
    df["Profit_Margin"] = np.where(
        df["Sales"] > 0,
        (df["Profit"] / df["Sales"]) * 100,
        0.0
    )
    return df


def render_sidebar(df: pd.DataFrame):
    """Render interactive sidebar filters and return the filtered dataset."""
    st.sidebar.image(
        "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=300&auto=format&fit=crop&q=60",
        use_container_width=True
    )
    st.sidebar.title("🎛️ Filter Controls")

    if df.empty:
        return df

    min_date = df["Order_Date"].min().date()
    max_date = df["Order_Date"].max().date()

    date_range = st.sidebar.date_input(
        "📅 Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    regions = sorted(df["Region"].unique())
    selected_regions = st.sidebar.multiselect(
        "🌍 Region",
        options=regions,
        default=regions
    )

    categories = sorted(df["Category"].unique())
    selected_categories = st.sidebar.multiselect(
        "📦 Category",
        options=categories,
        default=categories
    )

    segments = sorted(df["Segment"].unique())
    selected_segments = st.sidebar.multiselect(
        "👥 Customer Segment",
        options=segments,
        default=segments
    )

    priorities = sorted(df["Order_Priority"].unique())
    selected_priorities = st.sidebar.multiselect(
        "⚡ Order Priority",
        options=priorities,
        default=priorities
    )

    # Apply date filters
    if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
        start_d, end_d = date_range
    else:
        start_d, end_d = min_date, max_date

    mask = (
        (df["Order_Date"].dt.date >= start_d) &
        (df["Order_Date"].dt.date <= end_d) &
        (df["Region"].isin(selected_regions)) &
        (df["Category"].isin(selected_categories)) &
        (df["Segment"].isin(selected_segments)) &
        (df["Order_Priority"].isin(selected_priorities))
    )

    filtered = df[mask]

    st.sidebar.divider()
    st.sidebar.markdown(f"**Records Selected:** `{len(filtered):,}` / `{len(df):,}`")
    pct_active = (len(filtered) / len(df) * 100) if len(df) > 0 else 0
    st.sidebar.progress(pct_active / 100)

    return filtered


def render_kpi_cards(filtered: pd.DataFrame, full_df: pd.DataFrame):
    """Display top-level executive KPI metrics."""
    tot_sales = filtered["Sales"].sum()
    tot_profit = filtered["Profit"].sum()
    margin = (tot_profit / tot_sales * 100) if tot_sales > 0 else 0
    orders_cnt = filtered["Order_ID"].nunique()
    aov = (tot_sales / orders_cnt) if orders_cnt > 0 else 0
    units_sold = filtered["Quantity"].sum()

    benchmark_margin = (
        (full_df["Profit"].sum() / full_df["Sales"].sum() * 100)
        if not full_df.empty and full_df["Sales"].sum() > 0
        else 0
    )
    margin_diff = margin - benchmark_margin

    cols = st.columns(6)
    cols[0].metric("Total Sales", f"${tot_sales:,.2f}")
    cols[1].metric("Total Profit", f"${tot_profit:,.2f}")
    cols[2].metric("Profit Margin", f"{margin:.1f}%", f"{margin_diff:+.1f}% vs Avg")
    cols[3].metric("Total Orders", f"{orders_cnt:,}")
    cols[4].metric("Avg Order Value", f"${aov:,.2f}")
    cols[5].metric("Units Sold", f"{units_sold:,}")


def render_revenue_tab(filtered: pd.DataFrame):
    """Render time series and category breakdown."""
    st.subheader("📈 Revenue & Profit Trends")
    col1, col2 = st.columns([7, 5])

    with col1:
        monthly = (
            filtered.groupby("Year_Month")[["Sales", "Profit"]]
            .sum()
            .reset_index()
            .sort_values("Year_Month")
        )
        fig_trend = go.Figure()
        fig_trend.add_trace(
            go.Scatter(
                x=monthly["Year_Month"],
                y=monthly["Sales"],
                mode="lines+markers",
                name="Sales ($)",
                line=dict(color="#3b82f6", width=3),
                fill="tozeroy",
                fillcolor="rgba(59, 130, 246, 0.1)"
            )
        )
        fig_trend.add_trace(
            go.Scatter(
                x=monthly["Year_Month"],
                y=monthly["Profit"],
                mode="lines+markers",
                name="Profit ($)",
                line=dict(color="#10b981", width=3)
            )
        )
        fig_trend.update_layout(
            title="Monthly Sales vs Profit Performance",
            xaxis_title="Month",
            yaxis_title="Amount ($USD)",
            template="plotly_dark",
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_trend, use_container_width=True)

    with col2:
        subcat = (
            filtered.groupby(["Category", "Sub_Category"])[["Sales", "Profit"]]
            .sum()
            .reset_index()
            .sort_values("Sales", ascending=True)
        )
        fig_bar = px.bar(
            subcat,
            x="Sales",
            y="Sub_Category",
            color="Category",
            orientation="h",
            title="Sales by Sub-Category",
            hover_data=["Profit"],
            template="plotly_dark",
            color_discrete_sequence=px.colors.qualitative.Prism
        )
        fig_bar.update_layout(margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_bar, use_container_width=True)


def render_regional_tab(filtered: pd.DataFrame):
    """Render geographical and customer segment analytics."""
    st.subheader("🗺️ Regional & Segmentation Analytics")
    col1, col2 = st.columns(2)

    with col1:
        state_sales = (
            filtered.groupby("State")[["Sales", "Profit"]]
            .sum()
            .reset_index()
        )
        fig_map = px.choropleth(
            state_sales,
            locations="State",
            locationmode="USA-states",
            color="Sales",
            scope="usa",
            title="Sales Distribution Across US States",
            color_continuous_scale="Viridis",
            hover_data=["Profit"],
            template="plotly_dark"
        )
        fig_map.update_layout(margin=dict(l=0, r=0, t=40, b=0))
        st.plotly_chart(fig_map, use_container_width=True)

    with col2:
        seg_data = (
            filtered.groupby("Segment")[["Sales", "Profit"]]
            .sum()
            .reset_index()
        )
        fig_pie = px.pie(
            seg_data,
            values="Sales",
            names="Segment",
            hole=0.45,
            title="Sales Share by Customer Segment",
            template="plotly_dark",
            color_discrete_sequence=px.colors.sequential.Tealgrn
        )
        fig_pie.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(fig_pie, use_container_width=True)


def render_deep_dive_tab(filtered: pd.DataFrame):
    """Render correlation and distribution analysis."""
    st.subheader("🔬 Correlation & Distribution Deep Dive")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Discount vs Profit Margin Impact (Plotly)**")
        fig_scatter = px.scatter(
            filtered,
            x="Discount",
            y="Profit_Margin",
            color="Category",
            size="Quantity",
            hover_data=["Sub_Category", "Sales", "Profit"],
            trendline="ols",
            title="Discount vs Profit Margin by Product Category",
            template="plotly_dark"
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    with col2:
        st.markdown("**Profit Margin Distribution by Category (Seaborn)**")
        fig_sns, ax = plt.subplots(figsize=(6, 4.2))
        fig_sns.patch.set_facecolor("#0e1117")
        ax.set_facecolor("#161b22")

        sns.boxplot(
            data=filtered,
            x="Category",
            y="Profit_Margin",
            palette="mako",
            ax=ax,
            boxprops=dict(alpha=0.8)
        )
        ax.set_title("Profit Margin Variation", color="white", fontsize=12)
        ax.set_xlabel("Category", color="white")
        ax.set_ylabel("Profit Margin (%)", color="white")
        ax.tick_params(colors="white")
        for spine in ax.spines.values():
            spine.set_color("#30363d")
        plt.tight_layout()
        st.pyplot(fig_sns)
        plt.close(fig_sns)


def render_data_explorer(filtered: pd.DataFrame):
    """Render interactive data explorer and CSV export."""
    st.subheader("📋 Dataset Explorer & Export")
    st.markdown("Inspect granular records and export filtered subsets.")

    cols_to_show = st.multiselect(
        "Select Columns to Display",
        options=list(filtered.columns),
        default=[
            "Order_ID", "Order_Date", "Customer_Name", "Segment",
            "State", "Category", "Sub_Category", "Sales", "Discount", "Profit"
        ]
    )

    st.dataframe(filtered[cols_to_show], use_container_width=True, height=350)

    csv_data = filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Filtered Data (CSV)",
        data=csv_data,
        file_name="filtered_dataset.csv",
        mime="text/csv"
    )


def main():
    """Main dashboard application orchestration."""
    data_path = os.path.join(os.path.dirname(__file__), "data", "dataset.csv")
    df = load_data(data_path)

    if df.empty:
        st.error("⚠️ Dataset not found. Please ensure `data/dataset.csv` exists.")
        return

    filtered_df = render_sidebar(df)

    # Dashboard Header
    st.title("📊 Enterprise Business Intelligence Dashboard")
    st.caption(
        "Interactive analytics and decision-support system • "
        "Streamlit & Plotly Data App"
    )
    st.divider()

    # KPI Metrics
    render_kpi_cards(filtered_df, df)
    st.markdown("<br>", unsafe_allow_html=True)

    # Interactive Analytical Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Revenue & Profit",
        "🗺️ Geography & Segments",
        "🔬 Deep Dive & Distributions",
        "📋 Data Explorer"
    ])

    with tab1:
        render_revenue_tab(filtered_df)

    with tab2:
        render_regional_tab(filtered_df)

    with tab3:
        render_deep_dive_tab(filtered_df)

    with tab4:
        render_data_explorer(filtered_df)


if __name__ == "__main__":
    main()
