# 🚢 Megapuerto de Chancay vs. Puerto del Callao: Maritime Logistics & Freight Explorer

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io/)
[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![CI/CD Pipeline](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-brightgreen.svg)](https://github.com/YourUsername/your-repo-name/actions)
[![APN Data Benchmarks](https://img.shields.io/badge/data-APN%20%2F%20Drewry-orange.svg)](https://www.gob.pe/apn)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

> **Una plataforma interactiva de Inteligencia de Negocios y Analítica Logística Marítima desarrollada en Python, Streamlit, Plotly y Seaborn. Diseñada para evaluar la transformación logística de la costa peruana, comparando el Megapuerto de Chancay frente al Puerto del Callao en tiempos de tránsito hacia Asia, costos de flete por TEU, demoras en patio, emisiones de $CO_2$ y simulación de escenarios de migración de carga.**

---

## 🌟 Live Demo & Enlaces del Proyecto

* 🚀 **Dashboard en la Nube (Streamlit Cloud):** [Desplegar en Streamlit Community Cloud](https://streamlit.io/cloud)
* 📦 **Repositorio Público de GitHub:** [https://github.com/YourUsername/your-repo-name](https://github.com/YourUsername/your-repo-name)
* 📝 **Artículo Técnico Completo (Dev.to / Medium):** Ver [ARTICLE_DEV_TO.md](ARTICLE_DEV_TO.md)

---

## 🧭 ¿Por qué Chancay vs. Callao? La Gran Transformación Logística del Perú

Durante décadas, el **Puerto del Callao** ha concentrado más del 70% del tráfico de contenedores del Perú. No obstante, las limitaciones físicas de calado (16.0 metros) y la severa congestión vial urbana generan demoras en patio de 30 a 48 horas y obligan a transbordos en Norteamérica (Manzanillo/Long Beach), elevando el tiempo de navegación a **34–45 días**.

La inauguración del **Megapuerto de Chancay** (Cosco Shipping Ports) redefine el comercio exterior sudamericano:
- **Calado natural de 17.8 metros:** Permite el atraque de buques portacontenedores de última generación (*Ultra Large Container Vessels* hasta 24,000 TEUs).
- **Ruta Directa Asia Express:** Conecta Perú con Shanghai, Ningbo y Qingdao en **22–28 días**, ahorrando entre **12 y 14 días** de navegación.
- **Ventaja para la Agroexportación:** Para la palta, arándano y uva fresca (contenedores *Reefer*), el ahorro de dos semanas preserva la frescura en góndola y optimiza millones en capital de trabajo.

---

## 📐 Arquitectura del Sistema y Flujo GitOps

```mermaid
flowchart LR
    A[Datos Logísticos APN / Drewry<br/>data/dataset.csv] -->|data/metadata.json| B[Motor Streamlit<br/>app.py]
    B -->|@st.cache_data| C[Memoria Caché<br/>Respuesta Sub-segundo]
    C --> D[Módulos Analíticos<br/>Plotly & Seaborn]
    B -->|git push main| E[Repositorio GitHub<br/>Código Abierto]
    E -->|Webhook Trigger| F[GitHub Actions CI<br/>Flake8, Esquema & Smoke Tests]
    E -->|Continuous Sync| G[Streamlit Cloud<br/>Hospedaje SaaS Automatizado]
    G --> H[Líderes de Cadena de Suministro<br/>Acceso Web Ejecutivo]
```

### Aspectos Clave de GitOps:
1. **Snapshot Determinista de Datos:** 2,400 despachos marítimos empaquetados en `data/dataset.csv` con catálogo técnico en `data/metadata.json`.
2. **Reactividad Sub-segundo:** Uso de `@st.cache_data(ttl=3600)` para memoización inmediata ante cambios de filtros.
3. **Validación Automatizada en CI/CD:** GitHub Actions ejecuta linting estático (**Flake8**), validación de esquema en Python y pruebas de servidor headless.
4. **Despliegue Continuo Zero-Downtime:** Actualización automática en Streamlit Community Cloud al hacer push a la rama `main`.

---

## 📊 Módulos Analíticos de la Aplicación

1. **⏱️ Comparativa de Tiempos de Tránsito:** Medias móviles de 14 días comparando la ruta directa de Chancay (22-28 días) frente al Callao con trasbordo (34-45 días), junto con gráficos de violín de distribución.
2. **🚢 Red Marítima Transpacífica:** Desglose de volumen (TEUs) por puertos de destino en Asia (Shanghai, Ningbo, Qingdao, Busan, Yokohama) y cuota de mercado por naviera (*Cosco, Maersk, MSC, CMA CGM*).
3. **💰 Economía de Fletes y Demoras en Patio (Seaborn):** Gráfico de dispersión con línea de tendencia OLS (*Días de Tránsito vs. Tarifa $/TEU*) y boxplot de Seaborn modelando la congestión y demoras (*Port Dwell Hours*).
4. **🔮 Simulador de Migración de Carga (What-If Engine):** Sliders interactivos para modelar el porcentaje de carga migrada del Callao a Chancay, variación en flete y costo financiero de inventario, proyectando:
   - Días de tránsito ahorrados para exportadores.
   - Ahorro económico anual consolidado ($USD).
   - Toneladas de $CO_2$ evitadas por eliminación de rutas indirectas.
   - Gráfico de barras agrupadas: Línea Base Callao vs. Estrategia Optimizada Chancay.
5. **📋 Explorador de Datos y Metadatos APN:** Visualizador JSON del catálogo de especificaciones portuarias y exportación instantánea a CSV.

---

## 📁 Estructura del Repositorio

```text
├── .github/
│   └── workflows/
│       └── ci.yml               # Pipeline de CI/CD (Flake8, validación de esquema y smoke test)
├── .streamlit/
│   └── config.toml              # Tema oscuro de producción y banderas de servidor
├── data/
│   ├── dataset.csv              # Snapshot de 2,400 despachos transpacíficos
│   └── metadata.json            # Metadatos técnicos de terminales (calado, fuentes APN)
├── app.py                       # Aplicación interactiva Streamlit
├── requirements.txt             # Dependencias del proyecto
├── .gitignore                   # Exclusiones de caché y entornos virtuales
├── README.md                    # Documentación del proyecto
└── ARTICLE_DEV_TO.md            # Artículo técnico completo listo para Dev.to / Medium
```

---

## 🚀 Instalación y Ejecución Local

### 1. Activar Entorno Virtual
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 2. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 3. Iniciar el Servidor de Desarrollo
```bash
streamlit run app.py
```

La aplicación se abrirá automáticamente en tu navegador en `http://localhost:8501`.

---

## 🧪 Pipeline de Integración Continua (CI/CD)

El archivo `.github/workflows/ci.yml` ejecuta en cada `push` o `pull_request` a `main`:
1. **Entorno Python 3.11** con caché de paquetes pip.
2. **Linting Estático con Flake8** (código 100% PEP 8 conforme).
3. **Validación de Integridad:** Comprueba presencia de columnas obligatorias y conteo mínimo de 2,000 registros.
4. **Prueba de Importación:** Valida compilación de `app.py`.
5. **Headless Smoke Test:** Ejecuta Streamlit en modo headless para confirmar estabilidad de inicio.

---

## ☁️ Despliegue en la Nube

Configurado para continuous delivery en **Streamlit Community Cloud**:
1. Conecta tu cuenta de GitHub a [Streamlit Cloud](https://streamlit.io/cloud).
2. Selecciona este repositorio y define el archivo principal como `app.py`.
3. Haz clic en **Deploy**. Cada commit que supere el pipeline de GitHub Actions generará una nueva versión en producción sin tiempo de inactividad.