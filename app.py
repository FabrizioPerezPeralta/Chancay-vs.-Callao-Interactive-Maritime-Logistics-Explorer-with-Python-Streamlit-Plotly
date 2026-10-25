"""Megapuerto de Chancay vs. Puerto del Callao: Maritime Logistics & Freight Explorer.

Interactive Business Intelligence application built with Python, Streamlit, Plotly,
and Seaborn to analyze trans-Pacific container shipping, transit times, demurrage costs,
carbon emissions, and scenario planning between Peru and Asia.
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
    page_title="Chancay vs. Callao | Maritime Logistics Explorer",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# Custom Styling for Maritime Executive Analytics
# ---------------------------------------------------------
st.markdown("""
<style>
    /* Metric Cards Styling */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.85) 0%, rgba(30, 41, 59, 0.70) 100%);
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
        font-size: 0.82rem !important;
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
        background: linear-gradient(90deg, rgba(14, 165, 233, 0.18) 0%, rgba(2, 132, 199, 0.06) 100%);
        border-left: 4px solid #0EA5E9;
        border-radius: 8px;
        padding: 20px 24px;
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
    """Load, cleanse, and augment the maritime logistics dataset with caching."""
    csv_file = os.path.join(os.path.dirname(__file__), "data", "dataset.csv")
    if not os.path.exists(csv_file):
        return pd.DataFrame()

    df = pd.read_csv(csv_file)
    df["Booking_Date"] = pd.to_datetime(df["Booking_Date"])
    df["Year"] = df["Booking_Date"].dt.year
    df["Month"] = df["Booking_Date"].dt.month
    df["Month_Name"] = df["Booking_Date"].dt.strftime("%b")
    df["Year_Month"] = df["Booking_Date"].dt.to_period("M").astype(str)

    # Unit cost and delay derivations
    df["Total_Cost_Per_TEU"] = np.where(
        df["Container_TEUs"] > 0,
        df["Total_Logistics_Cost_USD"] / df["Container_TEUs"],
        0.0
    )
    df["CO2_Per_TEU"] = np.where(
        df["Container_TEUs"] > 0,
        df["CO2_Emissions_Tons"] / df["Container_TEUs"],
        0.0
    )
    return df


@st.cache_data
def load_metadata() -> dict:
    """Load metadata describing study terminals and maritime schema."""
    meta_file = os.path.join(os.path.dirname(__file__), "data", "metadata.json")
    if os.path.exists(meta_file):
        with open(meta_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


# ---------------------------------------------------------
# Interactive Sidebar Filters
# ---------------------------------------------------------
def render_sidebar(df: pd.DataFrame):
    """Render sidebar filters and return the user-filtered maritime cohort."""
    st.sidebar.image(
        "https://images.unsplash.com/photo-1578575437130-527eed3abbec?w=400&auto=format&fit=crop&q=80",
        use_container_width=True
    )
    st.sidebar.title("🎛️ Maritime Filters")

    if df.empty:
        return df

    min_date = df["Booking_Date"].min().date()
    max_date = df["Booking_Date"].max().date()

    date_range = st.sidebar.date_input(
        "📅 Departure Date Window",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    ports = sorted(df["Origin_Port"].unique())
    selected_ports = st.sidebar.multiselect("⚓ Origin Port", ports, default=ports)

    destinations = sorted(df["Destination_Port"].unique())
    selected_destinations = st.sidebar.multiselect("🌏 Asian Gateway Hub", destinations, default=destinations)

    cargos = sorted(df["Cargo_Type"].unique())
    selected_cargos = st.sidebar.multiselect("📦 Cargo Category", cargos, default=cargos)

    carriers = sorted(df["Shipping_Line"].unique())
    selected_carriers = st.sidebar.multiselect("🚢 Ocean Carrier", carriers, default=carriers)

    # Date handling
    if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
        start_d, end_d = date_range
    else:
        start_d, end_d = min_date, max_date

    mask = (
        (df["Booking_Date"].dt.date >= start_d) &
        (df["Booking_Date"].dt.date <= end_d) &
        (df["Origin_Port"].isin(selected_ports)) &
        (df["Destination_Port"].isin(selected_destinations)) &
        (df["Cargo_Type"].isin(selected_cargos)) &
        (df["Shipping_Line"].isin(selected_carriers))
    )

    filtered = df[mask]

    st.sidebar.divider()
    active_pct = (len(filtered) / len(df) * 100) if len(df) > 0 else 0
    st.sidebar.markdown(f"**Filtered Shipments:** `{len(filtered):,}` / `{len(df):,}` ({active_pct:.1f}%)")
    st.sidebar.progress(active_pct / 100)

    return filtered


# ---------------------------------------------------------
# KPI Metric Scorecard
# ---------------------------------------------------------
def render_kpis(filtered: pd.DataFrame, full_df: pd.DataFrame):
    """Render executive maritime scorecard with comparative differential."""
    tot_teus = filtered["Container_TEUs"].sum()
    tot_cost = filtered["Total_Logistics_Cost_USD"].sum() / 1e6  # In millions USD
    avg_transit = filtered["Transit_Time_Days"].mean() if not filtered.empty else 0
    avg_rate = filtered["Freight_Rate_USD_TEU"].mean() if not filtered.empty else 0
    tot_co2 = filtered["CO2_Emissions_Tons"].sum() / 1e3  # In k-tons
    on_time_pct = (
        (filtered["Delivery_Status"] == "On-Time").sum() / len(filtered) * 100
        if not filtered.empty else 0
    )

    bench_transit = full_df["Transit_Time_Days"].mean() if not full_df.empty else 0
    transit_delta = avg_transit - bench_transit

    cols = st.columns(6)
    cols[0].metric("Mobilized Volume", f"{tot_teus:,} TEUs")
    cols[1].metric("Total Logistics Cost", f"${tot_cost:,.2f}M USD")
    cols[2].metric("Avg Ocean Transit", f"{avg_transit:.1f} Days", f"{transit_delta:+.1f}d vs Global")
    cols[3].metric("Avg Freight Rate", f"${avg_rate:,.0f} /TEU")
    cols[4].metric("On-Time Compliance", f"{on_time_pct:.1f}%")
    cols[5].metric("CO₂ Emissions", f"{tot_co2:,.1f} kTon")


# ---------------------------------------------------------
# Tab 1: Transit Times & Routing Dynamics
# ---------------------------------------------------------
def render_tab_transit(filtered: pd.DataFrame):
    """Render transit time comparisons and rolling trends."""
    st.markdown("#### ⏱️ Transit Time Comparison: Direct Route vs. Feeder Transshipment")
    st.caption(
        "Chancay connects directly to Asia in 22-28 days (Direct Express Route), "
        "compared to 34-45 days for Callao with transshipments at Manzanillo or Long Beach."
    )

    col1, col2 = st.columns([7, 5])

    with col1:
        st.markdown("##### 📈 14-Day Rolling Transit Time Moving Average")
        daily = (
            filtered.groupby(["Booking_Date", "Origin_Port"])["Transit_Time_Days"]
            .mean()
            .reset_index()
            .sort_values("Booking_Date")
        )
        fig_ts = go.Figure()
        for port, color in zip(["Megapuerto de Chancay", "Puerto del Callao"], ["#0EA5E9", "#F59E0B"]):
            port_data = daily[daily["Origin_Port"] == port].copy()
            if not port_data.empty:
                port_data["Smooth"] = port_data["Transit_Time_Days"].rolling(14, min_periods=1).mean()
                fig_ts.add_trace(go.Scatter(
                    x=port_data["Booking_Date"],
                    y=port_data["Smooth"],
                    name=port,
                    mode="lines",
                    line=dict(color=color, width=2.8)
                ))
        fig_ts.update_layout(
            template="plotly_dark",
            height=380,
            margin=dict(l=30, r=20, t=30, b=30),
            xaxis_title="Departure Date",
            yaxis_title="Ocean Transit Days to Asia",
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_ts, use_container_width=True)

    with col2:
        st.markdown("##### 📦 Ocean Transit Time Distribution by Port")
        fig_box = px.violin(
            filtered,
            x="Origin_Port",
            y="Transit_Time_Days",
            color="Origin_Port",
            box=True,
            points="outliers",
            color_discrete_map={"Megapuerto de Chancay": "#0EA5E9", "Puerto del Callao": "#F59E0B"},
            template="plotly_dark",
            height=380
        )
        fig_box.update_layout(
            margin=dict(l=20, r=20, t=30, b=20),
            xaxis_title="",
            yaxis_title="Ocean Navigation Days",
            showlegend=False
        )
        st.plotly_chart(fig_box, use_container_width=True)


# ---------------------------------------------------------
# Tab 2: Maritime Network & Hub Throughput
# ---------------------------------------------------------
def render_tab_network(filtered: pd.DataFrame):
    """Render destination throughput and shipping line market share."""
    st.markdown("#### 🚢 Trans-Pacific Maritime Network & Asian Hub Throughput")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("##### 🌏 Volume Shipped by Destination Deepwater Hub (TEUs)")
        dest_vol = (
            filtered.groupby(["Destination_Port", "Origin_Port"])["Container_TEUs"]
            .sum()
            .reset_index()
            .sort_values("Container_TEUs", ascending=True)
        )
        fig_bar = px.bar(
            dest_vol,
            x="Container_TEUs",
            y="Destination_Port",
            color="Origin_Port",
            orientation="h",
            barmode="group",
            color_discrete_map={"Megapuerto de Chancay": "#0EA5E9", "Puerto del Callao": "#F59E0B"},
            template="plotly_dark",
            height=400
        )
        fig_bar.update_layout(margin=dict(l=20, r=20, t=30, b=20), xaxis_title="Volume (TEUs)", yaxis_title="")
        st.plotly_chart(fig_bar, use_container_width=True)

    with col2:
        st.markdown("##### ⚓ Shipping Line Market Share (Carrier Alliance)")
        carrier_vol = filtered.groupby("Shipping_Line")["Container_TEUs"].sum().reset_index()
        fig_pie = px.pie(
            carrier_vol,
            values="Container_TEUs",
            names="Shipping_Line",
            hole=0.45,
            template="plotly_dark",
            height=400,
            color_discrete_sequence=px.colors.qualitative.Prism
        )
        fig_pie.update_traces(textposition="inside", textinfo="percent+label")
        fig_pie.update_layout(margin=dict(l=10, r=10, t=20, b=10))
        st.plotly_chart(fig_pie, use_container_width=True)


# ---------------------------------------------------------
# Tab 3: Freight Economics & Demurrage (Seaborn)
# ---------------------------------------------------------
def render_tab_economics(filtered: pd.DataFrame):
    """Render freight elasticity and statistical dwell/demurrage distributions."""
    st.markdown("#### 💰 Freight Economics, Yard Congestion & Statistical Modeling")
    col1, col2 = st.columns(2)

    with col1:
        # Check if statsmodels is available for OLS trendline
        try:
            import statsmodels.api  # noqa: F401
            use_ols = len(filtered) > 1
        except ImportError:
            use_ols = False

        scatter_kwargs = {
            "data_frame": filtered,
            "x": "Transit_Time_Days",
            "y": "Freight_Rate_USD_TEU",
            "color": "Cargo_Type",
            "size": "Container_TEUs",
            "hover_data": ["Origin_Port", "Destination_Port"],
            "template": "plotly_dark",
            "height": 410
        }
        if use_ols:
            scatter_kwargs["trendline"] = "ols"

        fig_scatter = px.scatter(**scatter_kwargs)
        fig_scatter.update_layout(
            margin=dict(l=30, r=20, t=20, b=30),
            xaxis_title="Ocean Transit Days to Destination",
            yaxis_title="Freight Rate ($USD / TEU)"
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    with col2:
        st.markdown("##### ⏱️ Terminal Yard Dwell Time Distribution (Seaborn Boxplot)")
        fig_sns, ax = plt.subplots(figsize=(6, 4.3))
        fig_sns.patch.set_facecolor("#0e1117")
        ax.set_facecolor("#161b22")

        sns.boxplot(
            data=filtered,
            x="Origin_Port",
            y="Port_Dwell_Hours",
            palette=["#0EA5E9", "#F59E0B"],
            ax=ax,
            boxprops=dict(alpha=0.85)
        )
        ax.set_title("Terminal Gate & Yard Congestion (Hours)", color="white", fontsize=11)
        ax.set_xlabel("", color="#94A3B8")
        ax.set_ylabel("Port Dwell Hours", color="#94A3B8")
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
    """Render interactive scenario engine to project migration from Callao to Chancay."""
    st.markdown("#### 🔮 Strategic Route Migration Simulator: Callao ➔ Chancay")
    st.info(
        "Simulate the strategic impact of migrating container volume from Callao to Chancay's "
        "direct deepwater service: calculates saved transit days, logistics cost reductions, "
        "and avoided CO₂ emissions by eliminating North American feeder detours."
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        migration_pct = st.slider("🚢 Callao Cargo Migrated to Chancay (%)", 0, 100, 45, 5)
    with c2:
        chancay_freight_disc = st.slider("🏷️ Chancay Direct Freight Tariff Delta (%)", -20, 20, -8, 1)
    with c3:
        inventory_day_cost = st.slider("💵 In-Transit Inventory Capital Cost ($/day/TEU)", 10, 80, 35, 5)

    # Simulation logic
    callao_mask = filtered["Origin_Port"] == "Puerto del Callao"
    callao_teus = filtered.loc[callao_mask, "Container_TEUs"].sum()
    migrated_teus = callao_teus * (migration_pct / 100.0)

    # Advantages of Chancay vs Callao
    transit_days_saved_per_teu = 12.8  # Average direct speed advantage
    total_days_saved = migrated_teus * transit_days_saved_per_teu

    # Cost savings: freight delta + demurrage savings + inventory capital cost
    avg_freight_callao = filtered.loc[callao_mask, "Freight_Rate_USD_TEU"].mean() if callao_teus > 0 else 2800
    freight_savings_per_teu = avg_freight_callao * (abs(chancay_freight_disc) / 100.0)
    inventory_savings = total_days_saved * inventory_day_cost
    demurrage_savings_per_teu = 85.0  # Automated gates in Chancay reduce yard demurrage

    total_cost_savings = (migrated_teus * (freight_savings_per_teu + demurrage_savings_per_teu)) + inventory_savings
    co2_avoided_tons = migrated_teus * (transit_days_saved_per_teu * 0.16)  # Approx 0.16 ton CO2/day/TEU saved

    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Cargo Migrated to Chancay", f"{migrated_teus:,.0f} TEUs", f"{migration_pct}% of Callao")
    s2.metric("Projected Logistics Savings", f"${total_cost_savings / 1e6:,.2f}M USD", "Total financial savings")
    s3.metric("Transit Days Saved", f"{total_days_saved:,.0f} TEU-Days", "-12.8 days/shipment")
    s4.metric("Avoided CO₂ Mitigated", f"{co2_avoided_tons:,.0f} Metric Tons", "Direct Asia route")

    # Comparative visualization
    base_cost = filtered["Total_Logistics_Cost_USD"].sum()
    proj_cost = base_cost - total_cost_savings

    co2_base = filtered["CO2_Emissions_Tons"].sum() / 1e3
    co2_proj = (filtered["CO2_Emissions_Tons"].sum() - co2_avoided_tons) / 1e3

    comp_df = pd.DataFrame({
        "Scenario": ["Historical Baseline", "Optimized Chancay Strategy"],
        "Total Cost ($M USD)": [base_cost / 1e6, proj_cost / 1e6],
        "CO₂ Emissions (kTon)": [co2_base, co2_proj]
    })
    fig_comp = px.bar(
        comp_df,
        x="Scenario",
        y="Total Cost ($M USD)",
        color="Scenario",
        text_auto=".2f",
        title="Total Logistics Expenditure: Historical Baseline vs. Chancay Migration ($M USD)",
        template="plotly_dark",
        color_discrete_sequence=["#F59E0B", "#0EA5E9"],
        height=360
    )
    fig_comp.update_layout(margin=dict(l=30, r=20, t=40, b=20), showlegend=False)
    st.plotly_chart(fig_comp, use_container_width=True)


# ---------------------------------------------------------
# Tab 5: Granular Shipments Explorer & APN Metadata
# ---------------------------------------------------------
def render_tab_data(filtered: pd.DataFrame, meta: dict):
    """Render granular tabular inspection, metadata catalog, and CSV export."""
    st.markdown("#### 📋 Shipments Explorer & Terminal Technical Catalog")

    with st.expander("ℹ️ Terminal Technical Specifications & APN Metadata", expanded=False):
        if meta:
            st.json(meta)
        else:
            st.info("No metadata.json file found in data/.")

    cols_to_show = st.multiselect(
        "Visible Columns",
        options=list(filtered.columns),
        default=[
            "Shipment_ID", "Booking_Date", "Origin_Port", "Destination_Port",
            "Cargo_Type", "Shipping_Line", "Container_TEUs",
            "Transit_Time_Days", "Freight_Rate_USD_TEU", "Total_Logistics_Cost_USD", "Delivery_Status"
        ]
    )

    st.dataframe(filtered[cols_to_show], use_container_width=True, height=360)

    csv_data = filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Filtered Dataset (CSV)",
        data=csv_data,
        file_name="chancay_callao_logistics_filtered.csv",
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
        st.error("⚠️ Maritime dataset not found. Verify `data/dataset.csv`.")
        return

    filtered_df = render_sidebar(df)

    # Hero Banner
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-title">🚢 Megapuerto de Chancay vs. Puerto del Callao</div>
        <div class="hero-subtitle">
            Executive Business Intelligence & Trans-Pacific Maritime Logistics Platform:
            evaluating ocean transit durations, freight tariffs, terminal dwell congestion, and carbon footprint (Peru - Asia).
        </div>
        <div>
            <span class="pill pill-blue">Direct Pacific Route</span>
            <span class="pill pill-green">Transit Savings: ~12.8 Days</span>
            <span class="pill pill-amber">ULCV up to 24,000 TEUs (17.8m Draft)</span>
            <span class="pill pill-blue">Cargo Migration Simulator</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Executive KPIs
    render_kpis(filtered_df, df)
    st.markdown("<br>", unsafe_allow_html=True)

    # Analytical Tabs
    t1, t2, t3, t4, t5 = st.tabs([
        "⏱️ Transit & Routes",
        "🚢 Maritime Network",
        "💰 Freight & Dwell (Seaborn)",
        "🔮 Chancay Simulator",
        "📋 Data & APN Metadata"
    ])

    with t1:
        render_tab_transit(filtered_df)
    with t2:
        render_tab_network(filtered_df)
    with t3:
        render_tab_economics(filtered_df)
    with t4:
        render_tab_simulator(filtered_df)
    with t5:
        render_tab_data(filtered_df, meta)


if __name__ == "__main__":
    main()
