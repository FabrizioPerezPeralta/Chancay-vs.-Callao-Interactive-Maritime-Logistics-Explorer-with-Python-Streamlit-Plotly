"""Enterprise Business Intelligence & Operations Analytics Explorer.

An interactive executive dashboard built with Python, Streamlit, Plotly,
and Seaborn for dynamic cross-filtering, financial analytics, and scenario modeling.
"""

import json
import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import streamlit as st

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="Enterprise BI Explorer | Executive Operations Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# Custom Styling for Executive Analytics
# ---------------------------------------------------------
st.markdown("""
<style>
    /* Metric Cards Styling */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.9) 100%);
        border: 1px solid rgba(14, 165, 233, 0.25);
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.35);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        border-color: rgba(14, 165, 233, 0.6);
    }
    div[data-testid="stMetricLabel"] {
        color: #94A3B8 !important;
        font-size: 0.85rem !important;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    div[data-testid="stMetricValue"] {
        color: #F8FAFC !important;
        font-size: 1.85rem !important;
        font-weight: 700;
    }

    /* Hero Banner */
    .hero-banner {
        background: linear-gradient(90deg, rgba(14, 165, 233, 0.15) 0%, rgba(56, 189, 248, 0.05) 100%);
        border-left: 4px solid #0EA5E9;
        border-radius: 8px;
        padding: 18px 24px;
        margin-bottom: 24px;
    }
    .hero-title {
        font-size: 1.95rem;
        font-weight: 800;
        color: #F8FAFC;
        margin-bottom: 6px;
    }
    .hero-subtitle {
        color: #94A3B8;
        font-size: 0.95rem;
        line-height: 1.5;
    }

    /* Tag Pills */
    .pill {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 6px;
        margin-top: 6px;
    }
    .pill-blue {
        background: rgba(14, 165, 233, 0.2);
        color: #38BDF8;
        border: 1px solid rgba(14, 165, 233, 0.4);
    }
    .pill-green {
        background: rgba(34, 197, 94, 0.2);
        color: #4ADE80;
        border: 1px solid rgba(34, 197, 94, 0.4);
    }
    .pill-amber {
        background: rgba(245, 158, 11, 0.2);
        color: #FBBF24;
        border: 1px solid rgba(245, 158, 11, 0.4);
    }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# Data Ingestion & High-Performance Caching
# ---------------------------------------------------------
@st.cache_data(ttl=3600)
def load_dataset() -> pd.DataFrame:
    """Load, cleanse, and augment the operations dataset with caching."""
    csv_file = os.path.join(os.path.dirname(__file__), "data", "dataset.csv")
    if not os.path.exists(csv_file):
        return pd.DataFrame()

    df = pd.read_csv(csv_file)
    df["Order_Date"] = pd.to_datetime(df["Order_Date"])
    df["Ship_Date"] = pd.to_datetime(df["Ship_Date"])
    df["Year"] = df["Order_Date"].dt.year
    df["Month"] = df["Order_Date"].dt.month
    df["Month_Name"] = df["Order_Date"].dt.strftime("%b")
    df["Year_Month"] = df["Order_Date"].dt.to_period("M").astype(str)
    df["Fulfillment_Days"] = (df["Ship_Date"] - df["Order_Date"]).dt.days
    df["Profit_Margin"] = np.where(
        df["Sales"] > 0,
        (df["Profit"] / df["Sales"]) * 100,
        0.0
    )

    season_map = {
        12: "Winter", 1: "Winter", 2: "Winter",
        3: "Spring", 4: "Spring", 5: "Spring",
        6: "Summer", 7: "Summer", 8: "Summer",
        9: "Autumn", 10: "Autumn", 11: "Autumn"
    }
    df["Season"] = df["Month"].map(season_map)
    return df


@st.cache_data
def load_metadata() -> dict:
    """Load metadata describing dataset coordinates and schema."""
    meta_file = os.path.join(os.path.dirname(__file__), "data", "metadata.json")
    if os.path.exists(meta_file):
        with open(meta_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


# ---------------------------------------------------------
# Interactive Sidebar Filters
# ---------------------------------------------------------
def render_sidebar(df: pd.DataFrame):
    """Render sidebar filters and return the user-filtered subset."""
    st.sidebar.image(
        "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=400&auto=format&fit=crop&q=80",
        use_container_width=True
    )
    st.sidebar.title("🎛️ Executive Filters")

    if df.empty:
        return df

    min_date = df["Order_Date"].min().date()
    max_date = df["Order_Date"].max().date()

    date_range = st.sidebar.date_input(
        "📅 Observation Period",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    regions = sorted(df["Region"].unique())
    selected_regions = st.sidebar.multiselect("🌍 Macro Region", regions, default=regions)

    categories = sorted(df["Category"].unique())
    selected_categories = st.sidebar.multiselect("📦 Product Category", categories, default=categories)

    segments = sorted(df["Segment"].unique())
    selected_segments = st.sidebar.multiselect("👥 Customer Segment", segments, default=segments)

    priorities = sorted(df["Order_Priority"].unique())
    selected_priorities = st.sidebar.multiselect("⚡ Fulfillment Priority", priorities, default=priorities)

    # Date handling
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
    active_pct = (len(filtered) / len(df) * 100) if len(df) > 0 else 0
    st.sidebar.markdown(f"**Filtered Cohort:** `{len(filtered):,}` / `{len(df):,}` rows ({active_pct:.1f}%)")
    st.sidebar.progress(active_pct / 100)

    return filtered


# ---------------------------------------------------------
# KPI Metric Scorecard
# ---------------------------------------------------------
def render_kpis(filtered: pd.DataFrame, full_df: pd.DataFrame):
    """Render executive scorecard with baseline comparisons."""
    tot_sales = filtered["Sales"].sum()
    tot_profit = filtered["Profit"].sum()
    margin = (tot_profit / tot_sales * 100) if tot_sales > 0 else 0
    orders = filtered["Order_ID"].nunique()
    aov = (tot_sales / orders) if orders > 0 else 0
    units = filtered["Quantity"].sum()

    bench_margin = (
        (full_df["Profit"].sum() / full_df["Sales"].sum() * 100)
        if not full_df.empty and full_df["Sales"].sum() > 0
        else 0
    )
    delta_margin = margin - bench_margin

    cols = st.columns(6)
    cols[0].metric("Gross Revenue", f"${tot_sales:,.2f}")
    cols[1].metric("Net Profit", f"${tot_profit:,.2f}")
    cols[2].metric("Profit Margin", f"{margin:.1f}%", f"{delta_margin:+.1f}% vs Bench")
    cols[3].metric("Order Volume", f"{orders:,}")
    cols[4].metric("Average Order Value", f"${aov:,.2f}")
    cols[5].metric("Units Delivered", f"{units:,}")


# ---------------------------------------------------------
# Tab 1: Temporal Trends & Rolling Dynamics
# ---------------------------------------------------------
def render_tab_trends(filtered: pd.DataFrame):
    """Render dual-axis rolling time series and seasonality distributions."""
    st.markdown("#### 📈 Temporal Dynamics & Rolling Moving Averages")
    st.caption("Tracking commercial revenue trajectories and net profit margins across time.")

    daily = (
        filtered.groupby("Order_Date")[["Sales", "Profit"]]
        .sum()
        .reset_index()
        .sort_values("Order_Date")
    )
    daily["Sales_Smooth_14D"] = daily["Sales"].rolling(14, min_periods=1).mean()
    daily["Profit_Smooth_14D"] = daily["Profit"].rolling(14, min_periods=1).mean()

    fig_ts = go.Figure()
    fig_ts.add_trace(go.Scatter(
        x=daily["Order_Date"],
        y=daily["Sales"],
        name="Daily Gross Revenue",
        mode="lines",
        line=dict(color="rgba(14, 165, 233, 0.25)", width=1),
        hoverinfo="skip"
    ))
    fig_ts.add_trace(go.Scatter(
        x=daily["Order_Date"],
        y=daily["Sales_Smooth_14D"],
        name="Revenue 14-Day Trend",
        mode="lines",
        line=dict(color="#0EA5E9", width=2.8),
        yaxis="y1"
    ))
    fig_ts.add_trace(go.Scatter(
        x=daily["Order_Date"],
        y=daily["Profit_Smooth_14D"],
        name="Net Profit 14-Day Trend",
        mode="lines",
        line=dict(color="#10B981", width=2.5, dash="dot"),
        yaxis="y2"
    ))
    fig_ts.update_layout(
        template="plotly_dark",
        height=420,
        margin=dict(l=40, r=40, t=30, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(title="Transaction Date", showgrid=True, gridcolor="#1E293B"),
        yaxis=dict(title="Gross Revenue ($USD)", title_font=dict(color="#0EA5E9"), tickfont=dict(color="#0EA5E9")),
        yaxis2=dict(
            title="Net Operating Profit ($USD)",
            title_font=dict(color="#10B981"),
            tickfont=dict(color="#10B981"),
            overlaying="y",
            side="right",
            showgrid=False
        ),
        hovermode="x unified"
    )
    st.plotly_chart(fig_ts, use_container_width=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("##### 🗓️ Monthly Revenue Distribution by Season")
        fig_box = px.box(
            filtered,
            x="Month_Name",
            y="Sales",
            color="Season",
            category_orders={"Month_Name": [
                "Jan", "Feb", "Mar", "Apr", "May", "Jun",
                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
            ]},
            color_discrete_map={"Winter": "#3B82F6", "Spring": "#10B981", "Summer": "#EF4444", "Autumn": "#F59E0B"},
            template="plotly_dark",
            height=340
        )
        fig_box.update_layout(margin=dict(l=30, r=20, t=20, b=30), xaxis_title="Month", yaxis_title="Sales ($USD)")
        st.plotly_chart(fig_box, use_container_width=True)

    with col_b:
        st.markdown("##### 📦 Sub-Category Revenue Ranking")
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
            hover_data=["Profit"],
            template="plotly_dark",
            height=340,
            color_discrete_sequence=px.colors.qualitative.Prism
        )
        fig_bar.update_layout(margin=dict(l=20, r=20, t=20, b=20), xaxis_title="Sales ($USD)", yaxis_title="")
        st.plotly_chart(fig_bar, use_container_width=True)


# ---------------------------------------------------------
# Tab 2: Geospatial & Segment Operations
# ---------------------------------------------------------
def render_tab_geospatial(filtered: pd.DataFrame):
    """Render US state choropleth map and customer segment breakdowns."""
    st.markdown("#### 🗺️ Geospatial Territory & Market Segment Footprint")
    col1, col2 = st.columns([1.3, 1.0])

    with col1:
        st.markdown("##### 🇺🇸 State-Level Sales Penetration")
        state_data = (
            filtered.groupby("State")[["Sales", "Profit", "Quantity"]]
            .sum()
            .reset_index()
        )
        fig_map = px.choropleth(
            state_data,
            locations="State",
            locationmode="USA-states",
            color="Sales",
            scope="usa",
            color_continuous_scale="Viridis",
            hover_data=["Profit", "Quantity"],
            template="plotly_dark",
            height=400
        )
        fig_map.update_layout(margin=dict(l=0, r=0, t=20, b=0))
        st.plotly_chart(fig_map, use_container_width=True)

    with col2:
        st.markdown("##### 👥 Segment Revenue Share & Prioritization")
        seg_data = filtered.groupby("Segment")["Sales"].sum().reset_index()
        fig_pie = px.pie(
            seg_data,
            values="Sales",
            names="Segment",
            hole=0.45,
            template="plotly_dark",
            height=400,
            color_discrete_sequence=px.colors.sequential.Tealgrn
        )
        fig_pie.update_traces(textposition="inside", textinfo="percent+label")
        fig_pie.update_layout(margin=dict(l=10, r=10, t=20, b=10))
        st.plotly_chart(fig_pie, use_container_width=True)


# ---------------------------------------------------------
# Tab 3: Deep Dive: Pricing, Elasticity & Seaborn
# ---------------------------------------------------------
def render_tab_deep_dive(filtered: pd.DataFrame):
    """Render scatter elasticity and statistical distribution with Seaborn."""
    st.markdown("#### 🔬 Pricing Elasticity, Discount Impact & Statistical Modeling")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("##### 🏷️ Promotional Discount vs Operating Margin")
        fig_scatter = px.scatter(
            filtered,
            x="Discount",
            y="Profit_Margin",
            color="Category",
            size="Quantity",
            hover_data=["Sub_Category", "Sales", "Profit"],
            trendline="ols",
            template="plotly_dark",
            height=400
        )
        fig_scatter.update_layout(
            margin=dict(l=30, r=20, t=20, b=30),
            xaxis_title="Promotional Discount Rate",
            yaxis_title="Profit Margin (%)"
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    with col2:
        st.markdown("##### 📊 Statistical Margin Distributions (Seaborn)")
        fig_sns, ax = plt.subplots(figsize=(6, 4.4))
        fig_sns.patch.set_facecolor("#0e1117")
        ax.set_facecolor("#161b22")

        sns.boxplot(
            data=filtered,
            x="Category",
            y="Profit_Margin",
            palette="mako",
            ax=ax,
            boxprops=dict(alpha=0.85)
        )
        ax.set_title("Profit Margin Variance across Categories", color="white", fontsize=11)
        ax.set_xlabel("Category", color="#94A3B8")
        ax.set_ylabel("Profit Margin (%)", color="#94A3B8")
        ax.tick_params(colors="#CBD5E1")
        for spine in ax.spines.values():
            spine.set_color("#30363D")
        plt.tight_layout()
        st.pyplot(fig_sns)
        plt.close(fig_sns)


# ---------------------------------------------------------
# Tab 4: Interactive What-If Scenario Simulator
# ---------------------------------------------------------
def render_tab_simulator(filtered: pd.DataFrame):
    """Render interactive scenario engine to project sales & margin adjustments."""
    st.markdown("#### 🔮 Executive What-If Scenario & Financial Simulator")
    st.info(
        "Simulate strategic operational adjustments in price markup, discount policies, "
        "and logistics efficiency to project revenue and profitability impact in real-time."
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        price_adj = st.slider("📈 Price Adjustment (%)", min_value=-20, max_value=30, value=5, step=1)
    with c2:
        discount_adj = st.slider("🏷️ Discount Modification (%)", min_value=-15, max_value=15, value=-3, step=1)
    with c3:
        shipping_eff = st.slider("🚚 Logistics Optimization (%)", min_value=-30, max_value=20, value=-10, step=2)

    # Simulation engine
    sim_df = filtered.copy()
    base_sales = sim_df["Sales"].sum()
    base_profit = sim_df["Profit"].sum()
    base_shipping = sim_df["Shipping_Cost"].sum()
    base_margin = (base_profit / base_sales * 100) if base_sales > 0 else 0

    # Apply adjustments
    sim_sales = base_sales * (1 + price_adj / 100) * (1 - discount_adj / 100)
    sim_shipping = base_shipping * (1 + shipping_eff / 100)
    shipping_savings = base_shipping - sim_shipping
    revenue_delta = sim_sales - base_sales
    sim_profit = base_profit + (revenue_delta * 0.45) + shipping_savings
    sim_margin = (sim_profit / sim_sales * 100) if sim_sales > 0 else 0
    profit_delta = sim_profit - base_profit

    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Projected Revenue", f"${sim_sales:,.2f}", f"{sim_sales - base_sales:+,.2f}")
    s2.metric("Projected Profit", f"${sim_profit:,.2f}", f"{profit_delta:+,.2f}")
    s3.metric("Projected Margin", f"{sim_margin:.1f}%", f"{sim_margin - base_margin:+.1f}%")
    s4.metric("Logistics Variance", f"${sim_shipping:,.2f}", f"{-shipping_savings:+,.2f}")

    # Comparative visualization
    comparison_data = pd.DataFrame({
        "Metric": ["Revenue ($)", "Operating Profit ($)", "Shipping Cost ($)"],
        "Baseline": [base_sales, base_profit, base_shipping],
        "Simulated": [sim_sales, sim_profit, sim_shipping]
    })
    fig_comp = px.bar(
        comparison_data,
        x="Metric",
        y=["Baseline", "Simulated"],
        barmode="group",
        title="Baseline vs Simulated Scenario Forecast",
        template="plotly_dark",
        color_discrete_sequence=["#64748B", "#0EA5E9"],
        height=360
    )
    fig_comp.update_layout(margin=dict(l=30, r=20, t=40, b=20), yaxis_title="Amount ($USD)")
    st.plotly_chart(fig_comp, use_container_width=True)


# ---------------------------------------------------------
# Tab 5: Data Explorer & Metadata Inspector
# ---------------------------------------------------------
def render_tab_data(filtered: pd.DataFrame, meta: dict):
    """Render granular tabular inspection, metadata viewer, and CSV exporter."""
    st.markdown("#### 📋 Granular Dataset Explorer & Metadata Catalog")

    with st.expander("ℹ️ Inspect Dataset Metadata Schema", expanded=False):
        if meta:
            st.json(meta)
        else:
            st.info("No metadata.json file found in data/ directory.")

    cols_to_view = st.multiselect(
        "Select Visible Columns",
        options=list(filtered.columns),
        default=[
            "Order_ID", "Order_Date", "Customer_Name", "Segment",
            "State", "Region", "Category", "Sub_Category",
            "Sales", "Discount", "Profit"
        ]
    )

    st.dataframe(filtered[cols_to_view], use_container_width=True, height=360)

    csv_payload = filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Export Filtered Records (CSV)",
        data=csv_payload,
        file_name="bi_filtered_dataset.csv",
        mime="text/csv"
    )


# ---------------------------------------------------------
# Main Execution Orchestrator
# ---------------------------------------------------------
def main():
    """Main dashboard entrypoint."""
    df = load_dataset()
    meta = load_metadata()

    if df.empty:
        st.error("⚠️ Dataset not located. Please verify `data/dataset.csv` exists.")
        return

    filtered_df = render_sidebar(df)

    # Hero Banner
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-title">📊 Enterprise Business Intelligence Explorer</div>
        <div class="hero-subtitle">
            Executive operations, supply chain performance, and strategic profitability analytics
            powered by Python, Streamlit, Plotly, and Seaborn.
        </div>
        <div>
            <span class="pill pill-blue">Enterprise BI</span>
            <span class="pill pill-green">Sub-Second Caching (@st.cache_data)</span>
            <span class="pill pill-amber">Plotly + Seaborn</span>
            <span class="pill pill-blue">Interactive What-If Engine</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Top-Level KPIs
    render_kpis(filtered_df, df)
    st.markdown("<br>", unsafe_allow_html=True)

    # Analytical Tabs
    t1, t2, t3, t4, t5 = st.tabs([
        "📈 Temporal & Trends",
        "🗺️ Geography & Segments",
        "🔬 Pricing & Elasticity",
        "🔮 What-If Simulator",
        "📋 Data & Metadata"
    ])

    with t1:
        render_tab_trends(filtered_df)
    with t2:
        render_tab_geospatial(filtered_df)
    with t3:
        render_tab_deep_dive(filtered_df)
    with t4:
        render_tab_simulator(filtered_df)
    with t5:
        render_tab_data(filtered_df, meta)


if __name__ == "__main__":
    main()
