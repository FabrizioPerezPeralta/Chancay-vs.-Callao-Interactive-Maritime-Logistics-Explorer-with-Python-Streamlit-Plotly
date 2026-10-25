---
title: "Chancay vs. Callao: Engineering an Interactive Maritime Logistics & Freight Explorer with Python, Streamlit, and Plotly"
published: true
description: "How to build an interactive Business Intelligence dashboard in Python to evaluate the trans-Pacific maritime corridor, compare Chancay vs Callao, simulate freight savings, and automate CI/CD with GitHub Actions."
tags: python, datascience, streamlit, logistics
cover_image: https://images.unsplash.com/photo-1578575437130-527eed3abbec?auto=format&fit=crop&w=1200&h=630&q=80
---

> 💡 **Executive Summary:** South America's maritime logistics landscape is undergoing an epochal transformation. The commissioning of the **Megapuerto de Chancay** (Terminal Portuario Multipropósito de Chancay) establishes the first direct deepwater maritime corridor between South America and Asia-Pacific. By circumventing traditional transshipment detours through North America (Manzanillo and Long Beach), Chancay slashes ocean transit times from 35–42 days down to 22–28 days. In this article, we explain how we engineered an interactive **Business Intelligence and Maritime Operations Dashboard** in pure Python using **Streamlit**, **Plotly**, and **Seaborn**, backed by an automated **GitHub Actions CI/CD GitOps pipeline** and deployed live to **Streamlit Community Cloud**.

**Project Resources:**  
[🚀 Live Cloud Dashboard](https://streamlit.io/cloud) · [📦 GitHub Repository](https://github.com/YourUsername/your-repo-name) · [🧪 Automated CI Pipeline](https://github.com/YourUsername/your-repo-name/actions) · [📋 Dataset & Metadata Catalog](data/metadata.json)

---

## ⚓ The Geopolitical & Supply Chain Problem: Chancay vs. Callao

For over a century, the **Puerto del Callao** (operated by DP World and APM Terminals) has concentrated more than 70% of Peru's containerized international trade. Despite substantial modernization, Callao faces intrinsic physical and operational bottlenecks:

1. **Urban Arterial Congestion & Gate Dwell Times:** Callao's terminal access is constrained by the dense Lima-Callao metropolitan grid, generating average container yard dwell times between 30 and 48 hours and severe demurrage penalties for logistics operators.
2. **Draft Limitations & Transshipment Detours:** With drafts capped at 16.0 meters, Callao cannot accommodate fully loaded Ultra Large Container Vessels (ULCVs up to 24,000 TEUs). Cargo bound for Shanghai, Ningbo, or Qingdao must be transshipped via feeder networks or secondary hubs in Central and North America, inflating transit times to 34–45 days.
3. **The Chancay Paradigm Shift:** Situated 80 km north of Lima, the **Megapuerto de Chancay** (Cosco Shipping Ports) features a natural 17.8-meter draft, automated yard cranes (ARMG), and a dedicated 1.8 km subterranean tunnel bypassing urban traffic. The result: direct express routes to Asia in 22–28 days.

### Core Business Intelligence Questions:
* *How do transit times and freight rates per TEU ($/TEU) differ across commercial cargo types (e.g., cold-chain agroexport reefers vs. mineral concentrates)?*
* *How many millions of dollars can Peruvian exporters save in in-transit inventory working capital by routing through Chancay?*
* *What is the quantifiable reduction in bunker fuel carbon footprint ($CO_2$) achieved by eliminating transshipment detours?*

To answer these questions, static spreadsheets and PDF reports are insufficient. Supply chain executives require a real-time, interactive decision-support interface.

---

## 🛠️ Technology Stack: The Case for Python + Streamlit + Plotly

When engineering an analytical portal for maritime logistics, we evaluated competing architectural options:

| Framework | Primary Advantage | Architectural Trade-off | Project Decision |
| :--- | :--- | :--- | :--- |
| **PowerBI / Tableau** | Established proprietary enterprise BI | High per-seat licensing, vendor lock-in, limited custom financial simulation algorithms | Unsuitable for open GitOps workflows |
| **Dash (Plotly)** | Enterprise Flask reactive applications | Demands extensive HTML/CSS boilerplate and explicit callback decorators | Slower iteration speed for agile prototyping |
| **Matplotlib / Seaborn** | Deep statistical distributions and box plots | Static raster bitmaps; lacks native browser zoom, pan, and hover tooltips | Integrated specifically for statistical dwell variance |
| **Streamlit + Plotly** | Pure Python reactive web apps with zero frontend boilerplate | Re-runs top-to-bottom on state changes; requires memoization via `@st.cache_data` | **Selected Architecture:** Rapid development, hardware-accelerated Plotly visuals, automated cloud deployment |

By pairing **Streamlit** for application layout with **Plotly** for GPU-accelerated interactive visualizations, we achieved an executive-grade analytics platform with sub-second filter response times.

---

## 📐 System Architecture & GitOps Pipeline

The application adheres to clean GitOps principles:

```mermaid
flowchart LR
    A["Maritime Operations Data<br/>data/dataset.csv"] -->|"data/metadata.json"| B["Streamlit App Engine<br/>app.py"]
    B -->|"@st.cache_data"| C["In-Memory Engine<br/>Sub-second Caching"]
    C --> D["Interactive Modules<br/>Plotly & Seaborn"]
    B -->|"git push main"| E["GitHub Repository<br/>Version Control"]
    E -->|"Webhook Trigger"| F["GitHub Actions CI<br/>Flake8, Schema & Smoke Tests"]
    E -->|"Continuous Sync"| G["Streamlit Cloud<br/>Automated SaaS Hosting"]
    G --> H["Global Supply Chain Executives<br/>Browser Access"]
```

### GitOps Highlights:
1. **Deterministic Data Snapshot:** 2,400 validated container consignments bundled in `data/dataset.csv` with a comprehensive `data/metadata.json` data dictionary.
2. **Continuous Integration Gate:** Every push to `main` triggers GitHub Actions to execute static linting (**Flake8**), dataset schema assertions, and headless server testing (`timeout 12s streamlit run app.py --server.headless=true`).
3. **Zero-Configuration SaaS Hosting:** Automated continuous delivery to Streamlit Community Cloud upon passing CI checks.

---

## 📊 Inside the Analytical Engine: 5 Core Perspectives

The dashboard is structured around five strategic operational modules:

### 1. Transit Times & 14-Day Rolling Dynamics
Commercial vessel voyages fluctuate due to seasonal trade surges and bunkering schedules. To reveal genuine structural trends, the application computes **14-day rolling moving averages** comparing Chancay's direct Pacific route against Callao's transshipment routing:

```python
# 14-Day Rolling Smoothing for Comparative Transit Times
daily = filtered.groupby(["Booking_Date", "Origin_Port"])["Transit_Time_Days"].mean().reset_index()

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
```

The data demonstrates that Chancay consistently maintains **23–27 days** of ocean transit, yielding an empirical saving of **12 to 14 days per shipment**.

### 2. Trans-Pacific Network & Hub Throughput
An interactive horizontal bar chart breaks down TEU volumes across Asia's primary deepwater gateway hubs: **Shanghai (SIPG)**, **Ningbo-Zhoushan**, **Qingdao**, **Busan**, and **Yokohama**, accompanied by a carrier market share donut chart highlighting Cosco Shipping, Maersk, and MSC.

### 3. Freight Economics & Seaborn Dwell Time Modeling
Promotional and base freight rates are analyzed through an interactive Plotly scatter plot with an **Ordinary Least Squares (OLS) regression trendline**, correlating ocean transit duration with freight tariff ($/TEU).

Simultaneously, a custom-styled dark theme **Seaborn boxplot** models terminal yard dwell time (*Port Dwell Hours*), revealing how Chancay's automated yard reduces gate turnaround from Callao's 38-hour median down to 16.5 hours.

### 4. Strategic What-If Route Migration Simulator
The crown jewel of the dashboard is the interactive scenario engine that allows port authorities and logistics directors to model cargo migration:

```python
# Dynamic Simulation Engine: Callao -> Chancay Migration
migrated_teus = callao_teus * (migration_pct / 100.0)
transit_days_saved = migrated_teus * 12.8

# Financial Savings = Freight Delta + Demurrage Savings + Inventory Financing
freight_savings = migrated_teus * avg_callao_freight * (abs(chancay_freight_disc) / 100.0)
inventory_savings = transit_days_saved * inventory_day_cost
demurrage_savings = migrated_teus * 85.0  # Reduced yard detention

total_cost_savings = freight_savings + demurrage_savings + inventory_savings
co2_avoided_tons = migrated_teus * (12.8 * 0.16)  # Avoided feeder bunker burn
```

Executives can adjust sliders for:
* **Cargo Volume Migrated (% of Callao TEUs)**
* **Chancay Direct Freight Tariff Discount (%)**
* **In-Transit Inventory Working Capital Cost ($/day/TEU)**

The simulator instantaneously projects total dollar savings ($M USD), saved transit days, and metric tons of $CO_2$ avoided, illustrated via a grouped comparative bar chart.

### 5. Granular Shipments Explorer & APN Metadata Catalog
An open inspection tab allows users to review the complete terminal specifications in `data/metadata.json`, filter records by visible columns, and export custom cohorts directly as CSV.

---

## ⚡ High-Performance Reactivity with `@st.cache_data`

To guarantee sub-second interaction across five simultaneous filter widgets, we implemented Streamlit's `@st.cache_data(ttl=3600)`. The dataset is ingested and transformed once into memory:

```python
@st.cache_data(ttl=3600)
def load_dataset() -> pd.DataFrame:
    df = pd.read_csv("data/dataset.csv")
    df["Booking_Date"] = pd.to_datetime(df["Booking_Date"])
    df["Total_Cost_Per_TEU"] = df["Total_Logistics_Cost_USD"] / df["Container_TEUs"]
    return df
```

Subsequent slider and dropdown interactions execute in under 100 milliseconds.

---

## 🧪 CI/CD Testing & GitOps Quality Gate

Reliability is enforced on every commit via `.github/workflows/ci.yml`:

```yaml
- name: 🔍 Static Code Analysis (Flake8)
  run: |
    flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
    flake8 . --count --exit-zero --max-complexity=15 --max-line-length=120 --statistics

- name: 📂 Verify Maritime Dataset Integrity
  run: |
    python -c "
    import os, json, pandas as pd
    assert os.path.exists('data/dataset.csv'), 'Dataset missing!'
    assert os.path.exists('data/metadata.json'), 'Metadata missing!'
    df = pd.read_csv('data/dataset.csv')
    assert len(df) >= 2000, f'Expected at least 2000 records, found {len(df)}'
    "

- name: 🚀 Headless Smoke Test
  run: |
    timeout 12s streamlit run app.py --server.headless=true --server.port=8501 || [ $? -eq 124 ]
```

---

## 🏁 Key Strategic Takeaways

1. **The 12.8-Day Competitive Advantage:** For time-sensitive Peruvian agroexports (fresh blueberries, avocados, and asparagus in reefer containers), saving nearly two weeks of sea transit means arriving in Asian supermarkets with significantly higher shelf life and premium pricing.
2. **Working Capital Optimization:** Eliminating transshipment detours frees up millions in tied-up working capital for exporters.
3. **From Static Reports to Interactive Simulators:** Delivering a pure Python dashboard with what-if scenario modeling transforms raw data into an indispensable tool for strategic supply chain negotiation.

---

*Authored for the Business Intelligence & Analytics Program (Unidad I).*
