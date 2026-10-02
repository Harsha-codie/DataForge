# DataForge

> **Intelligent Data Preparation, Profiling & ML Readiness Platform**

[![Live Deployment](https://img.shields.io/badge/Deployed%20on-Render-46E3B7?style=for-the-badge&logo=render&logoColor=white)](https://dataforge-1-9ycn.onrender.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.2+-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev/)
[![Polars](https://img.shields.io/badge/Engine-Polars%20%7C%20Rust-CD792C?style=for-the-badge&logo=rust&logoColor=white)](https://pola.rs/)
[![Apache Arrow](https://img.shields.io/badge/Memory-Apache%20Arrow-E74C3C?style=for-the-badge&logo=apache-arrow&logoColor=white)](https://arrow.apache.org/)

---

## 🌐 Live Deployment

DataForge is deployed and live on Render:

🔗 **Production URL**: [https://dataforge-1-9ycn.onrender.com/](https://dataforge-1-9ycn.onrender.com/)

You can test file uploads, data quality profiling, interactive previews, transformations, and ML readiness evaluations directly in the live environment.

---

## 📋 Overview

**DataForge** bridges the gap between raw, messy data ingestion and production-grade Machine Learning pipelines. Over 70% of a data engineer's time is spent identifying data corruption, fixing missing values, and preventing data leakage. 

DataForge automates this process through:
- **Rust-powered columnar data processing** via Polars and Apache Arrow.
- **Snappy-compressed Parquet storage** for sub-second query speeds and small storage footprints.
- **A deterministic ML Readiness audit** that checks mathematical constraints before training.
- **Immutable version lineage** (Version 1 &rarr; Version 2) ensuring full auditability and one-click rollbacks.
- **Interactive SVG-based data visualizations** powered by Recharts.

---

## 🚀 Key Features & Workflow Modules

```
┌────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   PREPARATION WORKFLOW                                     │
├──────────────────────────────┬─────────────────────────────┬───────────────────────────────┤
│ 1. Profiling & Quality       │ 2. Interactive Preview      │ 3. Schema Compatibility       │
│    Calculates summary stats  │    Zero-copy pagination     │    Validates types & regex    │
│    and Health Score (0-100)  │    and dry-run sandbox      │    constraints vs a contract  │
├──────────────────────────────┼─────────────────────────────┼───────────────────────────────┤
│ 4. Transformation Builder    │ 5. ML Readiness Engine      │ 6. Dataset Export             │
│    Append-only versioning    │    Deterministic audit of   │    Serializes clean data to   │
│    (v1 -> v2) for all edits  │    mathematical ML rules    │    CSV, Parquet, JSON, Excel  │
└──────────────────────────────┴─────────────────────────────┴───────────────────────────────┘
```

### 1. Profiling & Quality Engine
- **Automated Health Score (0–100)**: Starts at 100 and applies weighted deductions for nulls, duplicates, and critical data errors.
- **Defect Detection**:
  - **Duplicate Rows**: Detected using `df.height - df.unique().height`.
  - **Constant Columns (Zero Variance)**: Flags columns where $\min == \max$, which provide zero predictive power.
  - **Mixed Data Types**: Flags text columns where numbers are mixed with dirty placeholders like `"N/A"`, `"-"`, or `"unknown"`.
  - **Date String Detection**: Detects ISO (`YYYY-MM-DD`) and common text date formats for conversion.
- **1.5 &times; IQR Outlier Detection**:
  - Computes 25th percentile ($Q_1$) and 75th percentile ($Q_3$) using NumPy.
  - Identifies points outside the boundary fences: $[Q_1 - 1.5 \times IQR,\; Q_3 + 1.5 \times IQR]$.

### 2. Interactive Preview & Simulation
- **Zero-Copy Pagination**: Streams 50 rows per page using Polars pointer slicing (`df.slice(offset, page_size)`) without loading entire tables into browser memory.
- **Dry-Run Safety Sandbox**: Simulates operations in memory before committing, alerting users to high data loss (e.g. operations dropping $>25\%$ of rows).

### 3. Schema Compatibility & Contracts
- Compares incoming datasets against user-defined schema specifications.
- Validates missing columns, unexpected columns, type compatibility (e.g. `Int64` vs `integer`), and regex pattern constraints (e.g. email formats).

### 4. Transformation Builder (Immutable Lineage)
- **20+ Built-in Transformations**:
  - **Imputation**: Fill missing values with Mean, Median, Mode, or custom constants.
  - **Mathematical Scaling**: Standard Scaler ($z = \frac{x - \mu}{\sigma}$), Min-Max Scaler ($[0, 1]$), and Log1p transforms.
  - **Categorical Encoding**: One-Hot Encoding and Ordinal Encoding.
  - **Outlier Capping**: `clip_outliers` caps values at IQR fences instead of dropping rows.
  - **String Cleaning**: Trimming whitespace, regex replacement, case conversions.
- **Append-Only Versioning**: Transforms never overwrite raw data. Applying an operation creates **Version $N+1$** as a new Parquet file, tracking exact parameters in the database.

### 5. ML Readiness Engine
- **Algorithmic Evaluation Checklist**: Transparent, explainable rulebook that evaluates dataset readiness for machine learning.
- **Critical Checks**:
  - **Target Quality**: Verifies target column existence, zero missing labels, and valid class counts ($\ge 2$ classes for classification, continuous numeric for regression).
  - **Feature Nulls**: Identifies nulls that cause standard algorithms (`scikit-learn`) to fail matrix multiplication.
  - **Data Leakage (ID Columns)**: Detects high-cardinality alphanumeric columns ($>85\%$ unique values like `User_ID`) that cause tree models to memorize keys rather than learn patterns.
  - **Train/Test Splitting**: Verifies that transformations are fitted strictly on training data splits.

### 6. Data Visualizations
- **Backend Statistical Binning**: Instead of sending 500,000 raw points, the backend computes histograms via `np.histogram` and continuous Gaussian curves via Kernel Density Estimation (KDE) evaluated over 80 points using Silverman's bandwidth.
- **Frontend SVG Rendering**: Rendered at 60 FPS using **Recharts** with interactive hover tooltips, box plots, scatter plots with Pearson correlation, and missing value heatmaps.

### 7. Multi-Format Export
- Exports any version to **CSV**, **Parquet** (with Snappy compression), **JSON**, or **Excel (.xlsx)** via `openpyxl`.

---

## 🛠️ Architecture & Tech Stack

```
[React 18 + Vite Frontend] (Port 3000)
       │
       │ HTTP / REST API (JWT Bearer Token Authentication)
       ▼
[FastAPI Backend] (Port 8000)
       │
       ├──► [Polars + Apache Arrow Engine] (Rust multi-threaded table computing)
       ├──► [NumPy Engine] (Percentiles, IQR Outlier Math, Histogram Binning, KDE)
       ├──► [Storage Engine] (Local Directory or MinIO S3 -> Snappy Parquet files)
       └──► [Database Layer] (SQLAlchemy ORM -> SQLite in dev / PostgreSQL in prod)
```

| Layer | Technologies Used | Purpose |
| :--- | :--- | :--- |
| **Frontend** | React 18, TypeScript, Vite, Tailwind CSS | High-performance, responsive UI |
| **Client State & Cache**| TanStack React Query (`@tanstack/react-query`) | Automatic caching, background refetching, query invalidation |
| **Charting Engine** | Recharts, Lucide React | Interactive vector SVG data visualizations |
| **Backend API** | FastAPI, Pydantic v2, Uvicorn | Asynchronous Python REST API with auto OpenAPI docs |
| **Data Processing** | Polars (Rust core), Apache Arrow, NumPy | Multi-core parallel table and statistical processing |
| **Encoding Engine** | `chardet` | Automatic byte-level character encoding detection (UTF-8, Windows-1252) |
| **Database & ORM** | SQLAlchemy, Alembic, SQLite, PostgreSQL | Relational metadata storage and immutable version lineage |
| **Storage Backend** | Apache Parquet (Snappy), MinIO, Local Disk | Compressed, columnar on-disk data persistence |
| **Task Delegation** | Celery + Redis (with threading fallback) | Asynchronous background processing for large datasets |

---

## 📁 Repository Structure

```
DataForge/
├── backend/
│   ├── app/
│   │   ├── api/routes/         # FastAPI route handlers (auth, datasets, visualizations)
│   │   ├── core/               # Security, storage services, Celery configurations
│   │   ├── engine/             # Core compute engines
│   │   │   ├── reader.py       # Ingestion (chardet, Polars CSV/JSON/Parquet parsing)
│   │   │   ├── profiler.py     # Health scoring, duplicate checks, statistical summary
│   │   │   ├── preview.py      # Pagination slicing & dry-run simulation
│   │   │   ├── schema_engine.py# Contract & schema compatibility validator
│   │   │   ├── transformer.py  # 20+ data cleaning and transformation operations
│   │   │   ├── ml_engine.py    # ML readiness audit, target checks, ID leakage
│   │   │   ├── visualizer.py   # Statistical payload generation (KDE, histograms, box plots)
│   │   │   └── exporter.py     # Multi-format serialization (CSV, Parquet, JSON, Excel)
│   │   ├── models/             # SQLAlchemy database models (User, Dataset, DatasetVersion)
│   │   ├── schemas/            # Pydantic validation schemas
│   │   ├── database.py         # Database engine and session setup
│   │   └── main.py             # Application entrypoint & CORS middleware
│   ├── requirements.txt        # Python backend dependencies
│   └── Dockerfile              # Backend containerization
├── frontend/
│   ├── src/
│   │   ├── api/                # API client with JWT interception and error handlers
│   │   ├── pages/              # UI views (Profiling, Preview, Visualisation, ML Readiness, etc.)
│   │   ├── components/         # Shared UI components and layout wrappers
│   │   └── App.tsx             # Route definitions and navigation layout
│   ├── package.json            # Node.js dependencies
│   ├── vite.config.ts          # Vite configuration with /api development proxy
│   └── Dockerfile              # Frontend containerization
├── docker-compose.yml          # Multi-container orchestration (Backend, Frontend, Postgres, Redis, MinIO)
└── README.md                   # Project documentation
```

---

## 💻 Local Development Setup

### Prerequisites
- **Python 3.12+**
- **Node.js 18+ & npm**
- *(Optional)* Docker & Docker Compose

---

### Step 1: Clone the Repository
```bash
git clone https://github.com/Harsha-codie/DataForge.git
cd DataForge
```

---

### Step 2: Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a Python virtual environment:
   ```bash
   # On Windows (PowerShell):
   py -3.12 -m venv venv
   .\venv\Scripts\activate

   # On macOS / Linux:
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure environment variables:
   Create a `.env` file in the `backend/` directory:
   ```env
   PROJECT_NAME=DataForge
   API_V1_STR=/api/v1
   API_PORT=8000
   ENVIRONMENT=development
   SECRET_KEY=dataforge-super-secret-key-change-in-production-min-32-chars
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=1440
   CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173

   # Local SQLite Database
   DATABASE_URL=sqlite:///./dataforge.db

   # Local file storage
   STORAGE_BACKEND=local
   LOCAL_STORAGE_DIR=./data_storage
   ```
5. Start the backend server:
   ```bash
   python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```
   * Interactive API Documentation (Swagger UI): [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
   * Health Check: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

### Step 3: Frontend Setup
1. In a new terminal, navigate to the frontend directory:
   ```bash
   cd ../frontend
   ```
2. Install Node dependencies:
   ```bash
   npm install
   ```
3. Configure environment variables:
   Create a `.env` file in `frontend/`:
   ```env
   VITE_API_BASE_URL=http://localhost:8000/api/v1
   ```
4. Start the frontend development server:
   ```bash
   npm run dev
   ```
   * Open your browser and navigate to: [http://localhost:3000](http://localhost:3000)

---

### Step 4: Running with Docker Compose (Optional)
To run the full stack (Frontend, Backend, PostgreSQL, Redis, MinIO) in containers:
```bash
docker compose up --build
```

---

## 🔌 API Reference Overview

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/auth/register` | Register a new user |
| `POST` | `/api/v1/auth/login` | Authenticate user and receive JWT access token |
| `GET` | `/api/v1/auth/me` | Fetch authenticated user profile |
| `POST` | `/api/v1/datasets/upload` | Upload raw CSV, JSON, Parquet, or Excel dataset |
| `GET` | `/api/v1/datasets` | List all user datasets with pagination |
| `GET` | `/api/v1/datasets/{id}` | Retrieve dataset details and current version pointer |
| `GET` | `/api/v1/datasets/{id}/preview` | Paginated zero-copy tabular rows with column data types |
| `GET` | `/api/v1/datasets/{id}/profile` | Comprehensive health report, statistical metrics, quality score |
| `POST` | `/api/v1/datasets/{id}/transform/preview`| Dry-run simulation of an operation before committing |
| `POST` | `/api/v1/datasets/{id}/transform` | Execute transformation and create immutable Version $N+1$ |
| `GET` | `/api/v1/datasets/{id}/ml-readiness` | Evaluate task readiness (classification/regression) and leakage |
| `GET` | `/api/v1/visualizations/{id}/chart` | Generate statistical chart payloads (KDE, Histogram, Box plot) |
| `GET` | `/api/v1/datasets/{id}/export` | Download clean dataset in CSV, Parquet, JSON, or Excel |

---

## 📄 License

This project is licensed under the MIT License.
