# 📊 Interactive Data Visualization Dashboard

An interactive, web-based data analytics dashboard designed to explore complex datasets dynamically. This project demonstrates how to build and deploy robust data applications using Python and Streamlit, automate testing via GitHub Actions, and host on a public cloud provider.

## 🛠️ Architecture & Tech Stack

* **Frontend & Backend:** Python, Streamlit
* **Data Processing:** Pandas, NumPy
* **Visualization:** Plotly, Seaborn
* **CI/CD Automation:** GitHub Actions (Linting, Headless Smoke Tests)
* **Cloud Deployment:** Streamlit Community Cloud

## ✨ Key Features

1. **Interactive Visualizations:** Cross-filtering, zooming, and dynamic metric calculations with Plotly.
2. **High-Performance Caching:** Utilizing `@st.cache_data` to ensure sub-second response times during data manipulation.
3. **Automated CI/CD Pipeline:** Every push to `main` is validated for syntax errors and runtime stability.
4. **Zero-Downtime Deployment:** Fully automated continuous delivery to Streamlit Community Cloud.

## ⚙️ Local Setup Instructions

1. **Create and activate a virtual environment:**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate
   
   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Run the development server:**
   ```bash
   streamlit run app.py
   ```

## 🧪 CI/CD Pipeline (GitOps)

This repository uses **GitHub Actions** for continuous integration. The workflow is defined in `.github/workflows/ci.yml`.
On every pull request or push to the `main` branch, the pipeline will:

1. Initialize an Ubuntu runner with Python 3.9+.
2. Run **Flake8** to enforce code quality and catch syntax errors.
3. Execute a headless smoke test (`timeout 10s streamlit run app.py --server.headless=true`) to ensure the app compiles without fatal exceptions.

## ☁️ Cloud Deployment

This application is configured for continuous deployment on **Streamlit Community Cloud**.

1. Log in to [Streamlit Community Cloud](https://streamlit.io/cloud) and connect your GitHub account.
2. Click "New app" and select this repository.
3. Set the main file path to `app.py`.
4. Click "Deploy". Any future commit that passes the GitHub Actions pipeline will automatically trigger a new live build.

## 📁 Repository Structure

```text
├── .github/
│   └── workflows/
│       └── ci.yml          # GitHub Actions pipeline
├── data/
│   └── dataset.csv         # Static data snapshot
├── app.py                  # Main Streamlit application entrypoint
├── requirements.txt        # Python dependencies (streamlit, pandas, plotly, etc.)
└── README.md               # Project documentation
```