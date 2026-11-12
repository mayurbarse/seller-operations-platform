# Seller Operations Platform

A full-stack marketplace operations monitoring platform built with **React, FastAPI, SQLAlchemy, and SQLite**. It helps monitor seller performance, product listings, order fulfillment, customer disputes, commissions, and payout eligibility.

The project uses synthetic marketplace data to demonstrate operational monitoring, financial reconciliation, data validation, and rule-based anomaly detection.

## Features

- **Dashboard & Analytics:** Marketplace metrics, seller performance, orders, fulfillment, disputes, and payouts.
- **Seller Management:** Seller status and product listing monitoring.
- **Order Management:** Multi-seller orders and order-line tracking.
- **Fulfillment Monitoring:** Shipment, delivery, carrier, and tracking details.
- **Dispute Management:** Dispute lifecycle and payout deduction monitoring.
- **Commission & Payouts:** Commission rules, reserves, payout calculations, and reconciliation.
- **Anomaly Detection:** Five business-rule-based anomaly categories.
- **Data Validation:** Database integrity and financial consistency checks.
- **Audit Trail:** Entity state changes recorded through state events.

## Technology Stack

| Layer | Technologies |
|---|---|
| Frontend | React 19, Vite, React Router, Axios |
| Backend | Python, FastAPI |
| ORM | SQLAlchemy |
| Database | SQLite |
| Data Processing | Pandas, NumPy |
| Testing | Pytest, HTTPX |
| Exports | CSV, JSON, SQL |

## Architecture

```text
React Frontend (Vite)
        |
     Axios / HTTP
        |
   FastAPI Backend
        |
  ---------------------
  |         |         |
Analytics  Anomaly  Validation
Services  Detection  Services
  |         |         |
  ---------------------
        |
   SQLAlchemy ORM
        |
    SQLite DB
        |
 Synthetic Data Generator
        |
    CSV / JSON / SQL
```

## Business Workflow

1. Create sellers, customers, product listings, and commission rules.
2. Generate customer orders and order lines.
3. Track shipment and delivery through fulfillment records.
4. Calculate commissions and seller reserves.
5. Track customer disputes and applicable deductions.
6. Calculate payouts and evaluate payout eligibility.
7. Run anomaly detection and data integrity validation.

## Database Design

The platform uses 12 core entities:

| Entity | Purpose |
|---|---|
| Customer | Customer records |
| Seller | Marketplace sellers |
| ProductListing | Seller product listings |
| Order | Customer orders |
| OrderLine | Individual products in orders |
| Fulfillment | Shipment and delivery tracking |
| CustomerReview | Customer reviews |
| Dispute | Customer disputes |
| CommissionRule | Commission and reserve policies |
| Payout | Seller payout records |
| PayoutLine | Individual payout calculations |
| StateEvent | Entity state-change history |

For detailed fields, constraints, and relationships, see [`documentation/data_dictionary.md`](documentation/data_dictionary.md).

## Anomaly Detection

The platform implements five anomaly categories:

1. **Suspended Seller with Active Listing** – Detects active listings belonging to suspended sellers.
2. **Payout Before Delivery** – Detects payouts released before delivery or without a delivery timestamp.
3. **Commission Applied Twice** – Identifies excessive commission deductions.
4. **Dispute Not Deducted** – Detects insufficient deductions for applicable disputes.
5. **Payout Total Mismatch** – Identifies differences between payout totals and payout-line calculations.

**API:** `GET /analytics/anomalies`

Five documented edge-case scenarios are maintained in `backend/exports/edge_case_ground_truth.json`.

## Data Integrity Validation

The validation service checks:

- Database and foreign-key integrity.
- Seller, listing, order-line, fulfillment, and payout relationships.
- Order-line and order-total calculations.
- Payout reconciliation.
- Shipment, delivery, and dispute date consistency.
- Duplicate payout lines.

**Previously verified baseline result:** 12/12 checks passed, with zero reported issues.

**API:** `GET /analytics/data-integrity`

## Synthetic Dataset

The full-scale generated dataset uses random seed `20261022`.

| Entity | Generated Records |
|---|---:|
| Sellers | 2,000 |
| Customers | 20,000 |
| Product Listings | 20,000 |
| Orders | 100,000 |
| Order Lines | 200,062 |
| Fulfillments | 200,062 |
| Customer Reviews | 18,105 |
| Disputes | 10,000 |
| Commission Rules | 2,000 |
| Payouts | 7,995 |
| Payout Lines | 200,062 |
| State Events | 202,000 |

These are generated synthetic records, not real customer or marketplace data.

## Installation and Setup

### Prerequisites

- Python 3.10+
- Node.js and npm
- Git

### 1. Clone the repository

```bash
git clone https://github.com/mayurbarse/seller-operations-platform.git
cd seller-operations-platform
```

### 2. Set up the backend

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. Set up the frontend

Open another terminal:

```bash
cd frontend
npm install
```

## Running the Application

### Backend

From the `backend` directory:

```powershell
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

Backend: `http://127.0.0.1:8000`

Interactive API documentation: `http://127.0.0.1:8000/docs`

### Frontend

From the `frontend` directory:

```bash
npm run dev
```

Default frontend URL: `http://localhost:5173`

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Application health |
| GET | `/database-status` | Database status |
| GET | `/analytics/dashboard` | Dashboard metrics |
| GET | `/analytics/sellers` | Seller analytics |
| GET | `/analytics/sellers/{seller_id}` | Individual seller metrics |
| GET | `/analytics/anomalies` | Anomaly detection |
| GET | `/analytics/data-integrity` | Data validation |
| GET | `/orders` | Order records |
| GET | `/listings` | Product listings |
| GET | `/fulfillments` | Fulfillment records |
| GET | `/disputes` | Dispute records |
| GET | `/payouts` | Payout records |

Use `/docs` for interactive API exploration and response schemas.

## Testing

From the `backend` directory:

```powershell
.\venv\Scripts\Activate.ps1
python -m pytest -v
```

The anomaly test scenarios cover clean data and all five anomaly categories.

To build the frontend:

```bash
cd frontend
npm run build
```

## Data Generation and Reproducibility

Generator location: `backend/app/generators/seed_data.py`

Supported options:

| Option | Description |
|---|---|
| `--scale starter` | Generate starter dataset |
| `--scale full` | Generate full dataset |
| `--seed` | Set random seed |
| `--reset` | Clear existing records before generation |

Example:

```powershell
cd backend
python -m app.generators.seed_data --scale starter --seed 20261022
```

**Database safety:** Run generation in a fresh, disposable database environment. Do not use `--reset` against a database containing data you want to preserve.

The reproducibility verification used two independent starter-scale runs with seed `20261022`. All 12 CSV exports had matching row counts and SHA-256 checksums.

The comparison result is recorded in:

`backend/exports/reproducibility_report.json`

## Generated Exports

The `backend/exports/` directory contains:

- CSV exports for marketplace entities.
- JSON ground-truth and validation reports.
- Source manifest with SHA-256 hashes.
- Compressed SQL seed export: `seller_operations_seed.sql.gz`
- Reproducibility comparison report.

## Project Documentation

- [Data Dictionary](documentation/data_dictionary.md)
- [Backend README](backend/README.md)
- [Frontend README](frontend/README.md)

## Future Improvements

- Role-based access control.
- Advanced seller performance scoring.
- Automated payout eligibility workflows.
- Scheduled anomaly alerts.
- PostgreSQL support.
- Machine-learning-based anomaly detection.

---

**Seller Operations Platform**  
Built with React, FastAPI, SQLAlchemy, and SQLite.

GitHub: https://github.com/mayurbarse/seller-operations-platform