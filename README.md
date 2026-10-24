# 📊 Enterprise Business Intelligence Explorer

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io/)
[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![CI/CD Pipeline](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-brightgreen.svg)](https://github.com/YourUsername/your-repo-name/actions)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

> **An interactive, web-based business intelligence and operations analytics explorer built with Python, Streamlit, Plotly, and Seaborn. Powered by a deterministic 2,400-record commercial dataset to evaluate profitability, customer segmentation, pricing elasticity, and dynamic financial scenarios.**

---

## 🌟 Live Demo & Public Deployment

* 🚀 **Live Cloud Dashboard:** [Deploy via Streamlit Community Cloud](https://streamlit.io/cloud)
* 📦 **Public Repository:** [GitHub - YourUsername/your-repo-name](https://github.com/YourUsername/your-repo-name)
* 📝 **Technical Article (Dev.to / Medium):** See [ARTICLE_DEV_TO.md](ARTICLE_DEV_TO.md)

---

## 🧭 Strategic Business Intelligence Context

Modern commercial organizations manage thousands of distributed transactions across varied geographies and customer segments. Traditional static reporting leaves key executive questions unanswered:

* *How severely do steep promotional discounts compress operating margins across high-volume categories?*
* *Which macro regions and states generate sustainable operating profits versus high logistics costs?*
* *What happens to projected annual profit if catalog prices are increased by 5% while logistics costs are optimized by 10%?*

This application delivers a real-time, interactive decision-support interface that bridges the gap between historical retrospective reporting and proactive predictive modeling.

---

## 📐 System Architecture & GitOps Flow

```mermaid
flowchart LR
    A[Data Pipeline<br/>data/dataset.csv] -->|data/metadata.json| B[Streamlit App Engine<br/>app.py]
    B -->|@st.cache_data| C[In-Memory Cache<br/>Sub-second Reactivity]
    C --> D[Interactive Visuals<br/>Plotly & Seaborn]
    B -->|git push main| E[GitHub Repository<br/>Public Open Source]
    E -->|Webhook Trigger| F[GitHub Actions CI<br/>Flake8, Schema & Smoke Tests]
    E -->|Continuous Sync| G[Streamlit Community Cloud<br/>Automated SaaS Hosting]
    G --> H[Executive End Users<br/>Interactive Browser Access]
```

### Key Workflow Highlights:
1. **Deterministic Data Snapshot:** 2,400 verified records bundled in `data/dataset.csv` with schema definitions in `data/metadata.json`, guaranteeing reproducible builds without external network bottlenecks.
2. **Sub-second Reactivity:** In-memory caching via `@st.cache_data(ttl=3600)` enables instantaneous cross-filtering across multiple dimensions.
3. **Automated CI/CD:** GitHub Actions executes static analysis (Flake8), data schema integrity validation, and headless production smoke tests on every push.
4. **Zero-Configuration SaaS Deployment:** Automated continuous delivery to Streamlit Community Cloud upon pushing to `main`.

---

## 📊 Core Features & Analytical Modules

- **Executive KPI Metric Scorecards:** Real-time calculation of Gross Revenue, Net Profit, Profit Margin (%) with baseline benchmark comparison, Order Volume, Average Order Value (AOV), and Units Delivered.
- **Dual-Axis Temporal Trends:** Daily revenue and operating profit time series with 14-day rolling moving averages to surface long-term trajectories amidst day-to-day noise.
- **Geospatial & Market Segmentation:** Interactive US State-level choropleth map paired with Customer Segment donut distributions (*Consumer*, *Corporate*, and *Home Office*).
- **Pricing Elasticity & Statistical Distributions:** Scatter plot with Ordinary Least Squares (OLS) trendline analyzing discount rate impact on profitability, alongside Seaborn statistical boxplots.
- **Interactive What-If Financial Simulator:** Dynamic sliders for Price Adjustment (%), Promotional Discount Policy (%), and Logistics Optimization (%) that project revenue, net profit deltas, and margin variance against baseline figures.
- **Dataset Catalog & CSV Exporter:** In-app inspection of metadata schema, column filters, and instant download of filtered cohorts as CSV.

---

## 📁 Repository Structure

```text
├── .github/
│   └── workflows/
│       └── ci.yml               # GitHub Actions pipeline (linting, schema validation & smoke tests)
├── .streamlit/
│   └── config.toml              # Modern dark theme and production server configurations
├── data/
│   ├── dataset.csv              # 2,400 multi-dimensional commercial transactions
│   └── metadata.json            # Schema definitions, coordinates, and data dictionary
├── app.py                       # Main interactive Streamlit application
├── requirements.txt             # Python dependencies (streamlit, pandas, plotly, seaborn, etc.)
├── .gitignore                   # Ignore cache, venv, and temporary OS files
├── README.md                    # Comprehensive repository documentation
└── ARTICLE_DEV_TO.md            # Complete, publishable Dev.to / Medium technical article
```

---

## 🚀 Local Installation & Execution

### Prerequisites
- Python 3.10 or 3.11+
- Git

### 1. Create and Activate a Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Development Server
```bash
streamlit run app.py
```

The application will launch automatically in your browser at `http://localhost:8501`.

---

## 🧪 CI/CD Pipeline (GitOps)

The automated continuous integration workflow is defined in `.github/workflows/ci.yml`. On every pull request or push to `main`:

1. **Environment Setup:** Initializes an Ubuntu runner with Python 3.11 and pip caching.
2. **Static Linting (Flake8):** Enforces PEP 8 compliance and catches syntax errors.
3. **Schema & Integrity Validation:** Verifies file existence, record count, and required column presence.
4. **App Compilation Check:** Validates module imports without fatal runtime exceptions.
5. **Headless Smoke Test:** Launches Streamlit headlessly (`timeout 12s streamlit run app.py --server.headless=true`) to confirm clean server initialization.

---

## ☁️ Cloud Deployment

This application is ready for deployment on **Streamlit Community Cloud**:

1. Log in to [Streamlit Community Cloud](https://streamlit.io/cloud) with your GitHub account.
2. Click **New app** and select this repository.
3. Set the Main file path to `app.py`.
4. Click **Deploy**. Any future commit that passes the GitHub Actions pipeline will automatically trigger a new live build.