# MediClaim AI — Medical Insurance Claim Analysis System

A full-stack **Medical Insurance Claim Analysis & Predictive Analytics** web application built with **Python (Flask, scikit-learn, pandas, NumPy)** and **React (Vite, Tailwind CSS, Lucide Icons)**. Designed for exploring healthcare insurance claim portfolios, analyzing cost and status trends across disease categories and hospital types, uploading custom CSV claim datasets, and predicting claim approval outcomes using trained machine learning pipelines.

---

## Project Objectives

- Provide an interactive analytics dashboard to monitor insurance claim volume, total claim value (INR ₹), average claim size, and approval status distribution (`Approved`, `Rejected`, `Pending`).
- Support dynamic CSV dataset ingestion with automatic column standardization, schema telemetry, and one-click reset to the default dataset.
- Enable searchable, sortable, and status-filtered exploration of beneficiary claim records.
- Visualize claim cost patterns across disease categories, calendar months, beneficiary gender, and hospital types (`Private`, `Government`, `Charitable`).
- Predict claim approval status (`Approved`, `Rejected`, `Pending`) with confidence probabilities and rule-based audit signals using scikit-learn classification pipelines.
- Generate printable executive summary reports exportable as PDF via browser print.

---

## System Architecture

The application follows a decoupled **client–server architecture**:

```text
+----------------------------------+         HTTP / JSON (/api/*)        +-----------------------------------+
|      React + Vite Frontend       | <---------------------------------> |        Flask REST API Backend     |
|                                  |     Vite Dev Proxy (:3000 -> :5000) |                                   |
|  - Login (Demo Session Auth)     |     or Static SPA served by Flask   |  - app.py (API & SPA Routes)      |
|  - Dashboard (KPIs & SVG Charts) |                                     |  - data_service.py (CSV/KPIs)     |
|  - UploadDataset (CSV Ingestion) |                                     |  - ml_service.py (ML Pipelines)   |
|  - DataPreview (Table & Filters) |                                     |  - analysis_service.py (EDA)      |
|  - DataAnalysis (Visualizations) |                                     |  - prediction_service.py (Cost)   |
|  - ClaimPrediction (Status ML)   |                                     |  - risk_intelligence_service.py   |
|  - AnalysisReport (Print/PDF)    |                                     |  - report_service.py (Summaries)  |
+----------------------------------+                                     +-----------------------------------+
                                                                                           |
                                                                                           v
                                                                         +-----------------------------------+
                                                                         |   Data & Serialized ML Artifacts  |
                                                                         |  - backend/data/*.csv             |
                                                                         |  - backend/models/*.joblib        |
                                                                         +-----------------------------------+
```

### Repository Structure

```text
mediclaim AI/
├── backend/
│   ├── app.py                              # Main Flask REST API & production SPA server
│   ├── data/
│   │   ├── generate_dataset.py             # Synthetic claim dataset generator (seed=42)
│   │   ├── insurance_claims.csv            # Primary synthetic dataset (13,487 rows, 15 columns)
│   │   └── insurance.csv                   # Fallback public dataset (1,338 rows, 7 columns)
│   ├── models/
│   │   ├── best_classifier.joblib          # Trained scikit-learn classification pipeline
│   │   ├── best_model.joblib               # Trained scikit-learn regression pipeline
│   │   └── kmeans_risk_clusters.joblib     # K-Means (k=3) + StandardScaler bundle
│   ├── services/
│   │   ├── data_service.py                 # CSV loading, column standardization, KPIs, pagination
│   │   ├── ml_service.py                   # Classifier/regressor training, K-Means & status prediction
│   │   ├── prediction_service.py           # Cost regression inference, counterfactuals & risk tiers
│   │   ├── analysis_service.py             # Statistical subgroup breakdowns (smoker, BMI, age, region)
│   │   ├── claim_analysis_service.py       # Individual claim risk scoring & curated samples
│   │   ├── risk_intelligence_service.py    # Portfolio-wide risk scoring & anomaly detection
│   │   ├── preprocessing_service.py        # Missing-value, duplicate & IQR outlier audits
│   │   ├── feature_selection_service.py    # Pearson, Mutual Info, RF MDI & ANOVA F-scores
│   │   ├── visualization_service.py        # Chart payload generation
│   │   ├── report_service.py               # Structured project summary compilation
│   │   └── currency_config.py              # INR (₹) formatting (Crore/Lakh) & USD-to-INR conversion
│   └── tests/
│       └── test_backend.py                 # Unit tests for backend service modules
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Login.jsx                   # Demo login screen with session persistence
│   │   │   ├── Sidebar.jsx                 # Navigation sidebar
│   │   │   ├── Topbar.jsx                  # Page header & active user badge
│   │   │   ├── Dashboard.jsx               # KPI cards, status pie chart & monthly trend chart
│   │   │   ├── UploadDataset.jsx           # Drag-and-drop CSV upload, schema telemetry & reset
│   │   │   ├── DataPreview.jsx             # Searchable, sortable, paginated claim records table
│   │   │   ├── DataAnalysis.jsx            # Disease category, monthly combo, gender & hospital charts
│   │   │   ├── ClaimPrediction.jsx         # Claim approval status ML predictor UI
│   │   │   └── AnalysisReport.jsx          # Executive summary & print-to-PDF report view
│   │   ├── config/
│   │   │   └── currency.js                 # Client-side INR formatting & conversion helpers
│   │   ├── services/
│   │   │   └── api.js                      # Fetch wrapper & offline fallback helpers
│   │   ├── App.jsx                         # Auth state & tab navigation shell
│   │   ├── index.css                       # Tailwind CSS v4 & utility styles
│   │   └── main.jsx                        # React entry point
│   ├── index.html
│   ├── package.json
│   ├── .oxlintrc.json
│   └── vite.config.js                      # Vite config with /api proxy to port 5000
├── requirements.txt                        # Python backend dependencies
├── run.py                                  # Unified launcher (builds frontend if needed + starts Flask)
├── run_server.py                           # Minimal Flask server launcher
└── .gitignore
```

> **Note:** Earlier unmounted prototype components in `frontend/src/components/` are excluded from version control via `.gitignore` so the repository tracks only the active application.

---

## Technologies Used

### Backend
- **Python 3**
- **Flask** & **Flask-CORS** — REST API and static frontend serving
- **scikit-learn** — Classification, regression, preprocessing (`ColumnTransformer`, `StandardScaler`, `OneHotEncoder`), and K-Means clustering pipelines
- **pandas** & **NumPy** — Data ingestion, schema standardization, statistical aggregation
- **joblib** — Model serialization and loading

### Frontend
- **React 19** (`react`, `react-dom`)
- **Vite 8** (`@vitejs/plugin-react`)
- **Tailwind CSS v4** (`@tailwindcss/vite`)
- **Lucide React** (`lucide-react`) — UI iconography
- **clsx** — Conditional class composition
- **Oxlint** (`oxlint`) — Fast JavaScript/JSX linting

---

## Implemented Features

1. **Session Authentication (Demo)**
   - Login screen (`Login.jsx`) backed by `POST /api/auth/login` and `localStorage` session persistence (`App.jsx`).
   - *Implementation note:* Uses demo authentication (any non-empty username and password returns a demo session token) for portfolio demonstration; it is not backed by a user database or production JWT verification.

2. **Executive Analytics Dashboard**
   - Displays portfolio KPIs computed directly from the active dataset (`13,487` claims, `₹134.78 Crore` total claim amount, `₹99,930.53` average claim amount, and `9,193` approved claims on the default dataset).
   - Custom SVG **Claim Status Distribution** pie chart (`Approved` 68.2%, `Rejected` 17.1%, `Pending` 14.8%) and **Monthly Claim Trend** line chart.

3. **CSV Dataset Upload & Management**
   - Drag-and-drop CSV upload (`POST /api/dataset/upload`) with automatic column normalization (mapping aliases like `sex` -> `gender`, `charges` -> `claim_amount`, `status` -> `claim_status`), automatic ML model retraining on upload, schema/column tag display, and reset to the default dataset (`POST /api/dataset/reset`).

4. **Claim Records Browser & Status Filtering**
   - Paginated table (`10`/`25`/`50`/`100` rows per page) with multi-field text search, column sorting (`ID`, `Age`, `Gender`, `Policy_Type`, `Claim_Amount`), and filtering by `Claim_Status` (`All`, `Approved`, `Rejected`, `Pending`).

5. **Exploratory Data Analysis & Visualization**
   - **Disease Category Bar Chart**: Average claim amount across 7 clinical categories (`Heart Disease`, `Cancer`, `Orthopedic`, `Neurology`, `Gastro`, `Respiratory`, `Others`).
   - **Monthly Claim Trend Combo Chart**: Dual-axis bar (claim count) and line (total claim amount in ₹ Lakhs) chart across Jan–Dec.
   - **Demographic & Provider Breakdown**: Comparative average claim bars by `Gender` and `Hospital Type` (`Private`, `Government`, `Charitable`).

6. **Machine Learning Claim Status Prediction**
   - Interactive prediction form (`ClaimPrediction.jsx` -> `POST /api/predict/claim-status`) accepting `age`, `gender`, `policy_type`, `disease_category`, `claim_amount`, `hospital_type`, and `length_of_stay`.
   - Uses the persisted scikit-learn classification pipeline (`best_classifier.joblib`, `ColumnTransformer` with `StandardScaler` + `OneHotEncoder`) selected by `ml_service.py` to predict `Approved`, `Rejected`, or `Pending` along with confidence probability and audit verification signals.
   - Additional backend endpoints support training/evaluating 4 classifiers (`RandomForestClassifier`, `GradientBoostingClassifier`, `DecisionTreeClassifier`, `LogisticRegression`), 5 regressors (`GradientBoostingRegressor`, `RandomForestRegressor`, `DecisionTreeRegressor`, `LinearRegression`, `Ridge`), and 3-tier `KMeans` risk clustering (`POST /api/models/train`), as well as cost estimation (`POST /api/predict`) and portfolio risk intelligence (`/api/risk-intelligence/*`).

7. **Analysis Report & PDF Export**
   - Compiles portfolio KPIs, status counts/percentages, and underwriting findings into a print-styled report view (`AnalysisReport.jsx`) with browser print-to-PDF export (`window.print()`).

---

## Authentication & Security Limitations (Demo Only)

The authentication flow is designed strictly for **academic and portfolio demonstration** and is **not** intended for production use:

- `POST /api/auth/login` (`backend/app.py`) accepts any non-empty `username` and `password` without a user database or password hashing.
- On login, the API returns a static placeholder token (`"demo-jwt-token-mediclaim-2026"`), and the frontend persists session state (`mediclaim_auth_state`, `mediclaim_user`) in browser `localStorage`.
- `loginUser` in `frontend/src/services/api.js` includes a client-side fallback that signs in locally if the backend is unreachable.
- Other `/api/*` endpoints do not enforce token verification middleware or role-based access control (RBAC).

---

## Datasets, Attribution & Data Privacy

- **`backend/data/insurance_claims.csv` (Primary — Synthetic):**
  - `13,487` synthetic claim records across `15` columns (`id`, `age`, `gender`, `policy_type`, `claim_amount`, `claim_status`, `diagnosis`, `disease_category`, `hospital_type`, `month`, `length_of_stay`, `bmi`, `children`, `smoker`, `region`).
  - Generated reproducibly in-repository via `backend/data/generate_dataset.py` (`np.random.seed(42)`).
- **`backend/data/insurance.csv` (Fallback — Public Benchmark Dataset):**
  - `1,338` records across `7` columns (`age`, `sex`, `bmi`, `children`, `smoker`, `region`, `charges`).
  - **Source & Attribution:** Public **Medical Cost Personal Dataset**, originally compiled and published by **Brett Lantz** in *Machine Learning with R* (Packt Publishing, 2013) using U.S. Census Bureau demographic statistics, and widely redistributed as an educational benchmark (e.g., Kaggle: `mirichoi0218/insurance`). Refer to the upstream Packt / Kaggle dataset terms before commercial redistribution.
- **Privacy Verification:** Neither dataset contains Personally Identifiable Information (PII) or Protected Health Information (PHI) — there are no patient names, emails, phone numbers, addresses, government IDs, or real medical record identifiers.

---

## Machine Learning Performance & Serialized Artifacts

All models are built with `scikit-learn` (`ColumnTransformer` with `StandardScaler` + `OneHotEncoder`) and evaluated on the active dataset (`insurance_claims.csv`, `13,487` records, 80/20 split: `10,789` train / `2,698` test, `random_state=42`):

### Claim Status Classification (Active UI Predictor)
Features: `age`, `gender`, `policy_type`, `disease_category`, `claim_amount`, `hospital_type`, `length_of_stay` -> Target: `claim_status` (`Approved` 68.2%, `Rejected` 17.1%, `Pending` 14.8%).

| Model | Test Accuracy | Weighted F1 | Notes |
| :--- | :---: | :---: | :--- |
| **Logistic Regression** (`max_iter=1000`) | **68.16%** | **55.26%** | Highest accuracy on `insurance_claims.csv`; persisted in `best_classifier.joblib` |
| Random Forest Classifier (`max_depth=8`) | 68.09% | 55.51% | Evaluated in `ml_service.py` |
| Decision Tree Classifier (`max_depth=6`) | 68.01% | 55.40% | Evaluated in `ml_service.py` |
| Gradient Boosting Classifier (`max_depth=4`) | 67.57% | 55.69% | Evaluated in `ml_service.py` |

> **Empirical Note:** Classification accuracy (~68.1%–68.2%, e.g., `68.09%` for Random Forest and `68.16%` for Logistic Regression) tracks closely with the majority-class `Approved` baseline (`68.2%`) because `claim_status` in `generate_dataset.py` is sampled probabilistically by claim-amount tier rather than deterministic class boundaries.

### Claim Cost Regression & Risk Clustering (Backend API Services)
- **Regression Pipeline (`best_model.joblib`):** `Ridge` (`alpha=1.0`) selected among 5 candidates (`GradientBoostingRegressor`, `RandomForestRegressor`, `DecisionTreeRegressor`, `LinearRegression`, `Ridge`) trained on `['age', 'bmi', 'children', 'sex', 'smoker', 'region']`. On the synthetic `insurance_claims.csv` dataset, regression baselines achieve low `R²` (`1.62%–2.96%`, MAE `~$380–$382` USD-equivalent) because synthetic `claim_amount` in `generate_dataset.py` is derived from `disease_category` and `hospital_type` rather than `bmi`/`smoker`/`region`.
- **Risk Clustering (`kmeans_risk_clusters.joblib`):** `StandardScaler` + `KMeans(n_clusters=3, random_state=42, n_init=10)` over `[age, bmi, smoker, charges]`.

### Serialized Model Artifacts (`backend/models/`)

| Artifact | Size | Contents |
| :--- | :---: | :--- |
| `best_classifier.joblib` | `4.59 KB` (`4,705 B`) | `Pipeline` (`ColumnTransformer` + `LogisticRegression`) |
| `best_model.joblib` | `3.39 KB` (`3,473 B`) | `Pipeline` (`ColumnTransformer` + `Ridge`) |
| `kmeans_risk_clusters.joblib` | `53.93 KB` (`55,229 B`) | `dict` (`StandardScaler`, `KMeans(n_clusters=3)`) |

---

## REST API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | Service health check (`version: 2.0.0`) |
| `POST` | `/api/auth/login` | Demo session authentication |
| `GET` | `/api/dashboard/kpis` | Portfolio KPIs, status distribution, monthly & category breakdowns |
| `POST` | `/api/dataset/upload` | Upload CSV file or raw CSV payload and retrain ML models |
| `POST` | `/api/dataset/reset` | Reset active dataset to `insurance_claims.csv` |
| `GET` | `/api/dataset/summary` | Dataset schema, data dictionary, numerical & categorical stats |
| `GET` | `/api/dataset/records` | Paginated, searchable, sortable, filterable claim records |
| `GET` | `/api/analysis` | Category, monthly, gender, hospital type & statistical analysis |
| `POST` | `/api/predict/claim-status` | Predict claim status (`Approved` / `Rejected` / `Pending`) |
| `POST` | `/api/predict` | Predict claim charges & K-Means risk tier (regression pipeline) |
| `GET/POST` | `/api/models/train` | Train & evaluate classifiers, regressors, and K-Means clustering |
| `GET` | `/api/report`, `/api/report/summary` | Structured technical report payload |
| `GET` | `/api/claims/sample-list` | Curated sample claim profiles |
| `POST` | `/api/claims/analyze` | Individual claim risk scoring & anomaly breakdown |
| `GET` | `/api/risk-intelligence/summary` | Portfolio risk intelligence summary |
| `GET` | `/api/risk-intelligence/claims` | Filtered portfolio risk records |
| `GET` | `/api/risk-intelligence/investigate/<claim_id>` | Detailed risk breakdown for a single claim ID |

---

## Installation & Setup

### Prerequisites
- **Python 3.10+**
- **Node.js 18+** and **npm**

### 1. Clone the Repository
```bash
git clone https://github.com/<your-username>/<your-repo-name>.git
cd <your-repo-name>
```

### 2. Install Backend Dependencies
```bash
python -m venv .venv
# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1
# macOS / Linux
# source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Install Frontend Dependencies
```bash
cd frontend
npm install
cd ..
```

---

## Running the Application

### Option A: Unified Launcher (Builds Frontend + Starts Flask)
```bash
python run.py
```
This checks if `frontend/dist/index.html` exists (building it via `npm run build` if missing), starts the Flask server at `http://127.0.0.1:5000`, and opens your browser automatically.

### Option B: Development Mode (Separate Backend & Frontend)
1. **Start the Flask backend** (port `5000`):
   ```bash
   python backend/app.py
   ```
2. **Start the Vite dev server** (port `3000`, proxies `/api` to `http://127.0.0.1:5000`):
   ```bash
   cd frontend
   npm run dev
   ```

---

## Running Tests & Linting

- **Backend unit tests** (7 test cases in `backend/tests/test_backend.py`):
  ```bash
  python backend/tests/test_backend.py
  ```
- **Frontend lint & production build**:
  ```bash
  cd frontend
  npm run lint
  npm run build
  ```

---

## Screenshots

No UI screenshots are currently stored in the repository. Once you run the app locally, you can capture screenshots of the **Login**, **Dashboard**, **Upload Dataset**, **Data Preview**, **Data Analysis**, **Claim Prediction**, and **Analysis Report** views into a `docs/screenshots/` folder and embed them here.
