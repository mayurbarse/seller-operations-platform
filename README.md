# Seller Operations Platform

A full-stack seller operations monitoring and analytics platform designed to help e-commerce marketplaces monitor seller performance, product listings, order fulfillment, customer disputes, commission deductions, and payout eligibility.

The platform uses a synthetic marketplace dataset to demonstrate end-to-end operational monitoring, financial reconciliation, data integrity validation, and rule-based anomaly detection.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Business Problem](#2-business-problem)
3. [Key Features](#3-key-features)
4. [Technology Stack](#4-technology-stack)
5. [System Architecture](#5-system-architecture)
6. [Business Workflow](#6-business-workflow)
7. [Database Design](#7-database-design)
8. [Anomaly Detection](#8-anomaly-detection)
9. [Data Integrity and Validation](#9-data-integrity-and-validation)
10. [Synthetic Dataset](#10-synthetic-dataset)
11. [Project Structure](#11-project-structure)
12. [Installation and Setup](#12-installation-and-setup)
13. [Running the Application](#13-running-the-application)
14. [API Documentation](#14-api-documentation)
15. [Testing](#15-testing)
16. [Data Generation and Reproducibility](#16-data-generation-and-reproducibility)
17. [Generated Exports](#17-generated-exports)
18. [Future Improvements](#18-future-improvements)

---

## 1. Project Overview

The Seller Operations Platform provides a centralized monitoring interface for marketplace operations.

In a multi-seller e-commerce environment, a single customer order can contain products from multiple sellers. Each seller has separate fulfillment responsibilities, commission rules, dispute exposure, and payout calculations.

Managing these operations independently can lead to:

- Delayed order fulfillment.
- Suspended sellers continuing to sell products.
- Incorrect commission deductions.
- Disputes not being reflected in seller payouts.
- Premature payout releases.
- Financial mismatches between payout records and their individual transaction lines.

This platform models these operational processes and identifies inconsistencies using rule-based anomaly detection and data validation.

The application consists of:

- A React-based operational dashboard.
- A FastAPI backend.
- A relational SQLite database.
- A synthetic marketplace data generator.
- Analytics and anomaly detection services.
- Automated tests and data integrity checks.
- CSV and JSON exports for analysis and auditability.

## 2. Business Problem

Marketplace operations involve several interconnected entities and business rules.

For example, when a customer purchases products from multiple sellers:

1. The customer places an order.
2. The order is divided into individual order lines.
3. Each order line is associated with its respective seller and product listing.
4. Fulfillment records track shipment and delivery.
5. Commission and reserve rules determine the seller's payable amount.
6. Disputes and refunds can affect payout calculations.
7. Payouts are released only when eligibility conditions are satisfied.

The platform monitors these relationships and checks whether operational and financial records follow the expected business rules.

### Primary objectives

- Monitor seller performance and operational status.
- Track listings, orders, and fulfillment.
- Identify delayed or incomplete fulfillment.
- Monitor customer disputes.
- Validate commission and payout calculations.
- Identify suspicious or inconsistent operational records.
- Maintain traceable entity state changes.
- Provide measurable data quality and anomaly detection results.

## 3. Key Features

### Dashboard and Analytics

- Marketplace-wide operational summary.
- Seller performance monitoring.
- Order and fulfillment statistics.
- Dispute and payout monitoring.
- Anomaly summaries.
- Operational data visibility through a centralized dashboard.

### Seller Management

- Seller identification and status tracking.
- Active, suspended, and inactive seller records.
- Seller-level performance information.
- Seller-specific product listings.

### Order Management

- Customer orders and individual order lines.
- Multi-seller order relationships.
- Order amount tracking.
- Order status monitoring.

### Fulfillment Monitoring

- Shipment and delivery status.
- Carrier and tracking information.
- Shipment and delivery timestamps.
- Fulfillment-to-order-line relationships.

### Dispute Monitoring

- Dispute amount and reason tracking.
- Dispute lifecycle statuses.
- Seller and order associations.
- Monitoring of dispute deductions in payouts.

### Commission and Payout Monitoring

- Seller-specific and platform-wide commission rules.
- Commission rate and reserve rate tracking.
- Reserve holding periods.
- Payout and payout-line reconciliation.
- Payout eligibility monitoring.

### Anomaly Detection

The platform implements five rule-based anomaly categories:

1. Suspended seller with an active product listing.
2. Payout released before delivery.
3. Excessive commission deduction.
4. Missing dispute deduction.
5. Payout total mismatch.

### Data Integrity Validation

The backend provides automated validation for:

- Database integrity.
- Foreign key relationships.
- Seller and listing consistency.
- Fulfillment ownership consistency.
- Dispute ownership consistency.
- Payout ownership consistency.
- Order-line arithmetic.
- Order total reconciliation.
- Payout total reconciliation.
- Fulfillment date consistency.
- Dispute date consistency.
- Duplicate payout lines.

---

## 4. Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React 19 |
| Frontend build tool | Vite |
| Routing | React Router |
| HTTP client | Axios |
| Icons | Lucide React |
| Backend | Python |
| API framework | FastAPI |
| ORM | SQLAlchemy |
| Database | SQLite |
| Data processing | Pandas, NumPy |
| Data validation | Python and SQL queries |
| Testing | Pytest |
| API testing | HTTPX |
| Data exports | CSV and JSON |

---

## 5. System Architecture

The application follows a frontend-backend architecture.

```text
                 USER
                   |
                   v
        REACT FRONTEND (VITE)
                   |
             AXIOS / HTTP
                   |
                   v
          FASTAPI BACKEND
                   |
        -----------------------
        |          |          |
        v          v          v
     Analytics  Anomaly    Validation
     Services   Detection  Services
        |          |          |
        -----------------------
                   |
                   v
           SQLALCHEMY ORM
                   |
                   v
            SQLITE DATABASE
                   |
                   v
        SYNTHETIC DATA GENERATOR
                   |
                   v
            CSV / JSON EXPORTS
```

### Backend responsibilities

- Expose REST API endpoints.
- Retrieve and aggregate marketplace data.
- Apply business validation rules.
- Detect operational and financial anomalies.
- Reconcile payout and order amounts.
- Maintain relational database consistency.

### Frontend responsibilities

- Display marketplace analytics.
- Present seller and order information.
- Display fulfillment and dispute records.
- Present payout information.
- Provide an operational view of detected anomalies.

---

## 6. Business Workflow

The platform models the following marketplace lifecycle.

### Step 1: Master Data Creation

Generate the foundational records:

- Customers.
- Sellers.
- Product listings.
- Commission rules.

### Step 2: Order Creation

- Customers place orders.
- Orders contain one or more order lines.
- Each order line references a product listing and seller.
- Orders can contain products belonging to different sellers.

### Step 3: Fulfillment Processing

- Fulfillment records are associated with individual order lines.
- Shipment and delivery statuses are maintained.
- Carrier and tracking information are recorded.
- Shipment and delivery timestamps are tracked.

### Step 4: Commission Calculation

- Applicable commission rules determine deductions.
- Seller reserve percentages and holding periods are considered.
- Commission and reserve amounts are reflected in payout lines.

### Step 5: Dispute Processing

- Disputes are associated with orders, sellers, and optionally individual order lines.
- Dispute statuses represent their lifecycle.
- Financial deductions are checked against dispute outcomes.

### Step 6: Payout Processing

- Payout records are associated with sellers.
- Payout lines reference individual order lines.
- Gross amounts, commission, refunds, dispute deductions, and reserves are tracked.
- Net amounts contribute to payout totals.
- Payout eligibility is monitored.

### Step 7: Monitoring and Validation

- Anomaly detection checks operational and financial rules.
- Data integrity validation checks database relationships and calculations.
- Results are exposed through backend API endpoints.

---

## 7. Database Design

The platform uses a relational database containing 12 core entities.

| Entity | Purpose |
|---|---|
| Customer | Stores customer information |
| Seller | Stores marketplace seller information |
| ProductListing | Stores seller product listings |
| Order | Stores customer order information |
| OrderLine | Stores individual products within orders |
| Fulfillment | Tracks shipment and delivery |
| CustomerReview | Stores customer reviews |
| Dispute | Tracks customer disputes |
| CommissionRule | Defines commission and reserve rules |
| Payout | Stores seller payout records |
| PayoutLine | Stores individual payout calculations |
| StateEvent | Maintains entity state-change history |

### Important relationships

| Relationship | Cardinality |
|---|---|
| Customer → Order | One-to-Many |
| Customer → CustomerReview | One-to-Many |
| Seller → ProductListing | One-to-Many |
| Seller → OrderLine | One-to-Many |
| Order → OrderLine | One-to-Many |
| ProductListing → OrderLine | One-to-Many |
| OrderLine → Fulfillment | One-to-Zero-or-One |
| OrderLine → CustomerReview | One-to-Zero-or-One |
| Seller → Dispute | One-to-Many |
| Order → Dispute | One-to-Many |
| Seller → Payout | One-to-Many |
| Payout → PayoutLine | One-to-Many |
| OrderLine → PayoutLine | One-to-Many |

A `CommissionRule` can be associated with a specific seller or configured as a platform-wide rule when `seller_id` is NULL.

The `OrderLine` entity connects orders with product listings and sellers. This supports orders containing products from multiple sellers.

The `StateEvent` entity provides an audit trail for tracked entity state changes, rather than relying exclusively on overwritten current-state values.

For detailed fields, constraints, and relationships, see:

[`documentation/data_dictionary.md`](documentation/data_dictionary.md)

---

## 8. Anomaly Detection

The anomaly detection service evaluates operational and financial records against defined business rules.

**Backend file:** `backend/app/services/anomaly_detection.py`

**API endpoint:** `GET /analytics/anomalies`

### Implemented anomaly rules

| Anomaly | Detection rule |
|---|---|
| Suspended seller active listing | A suspended seller has an active product listing |
| Payout before delivery | A payout is released before the associated order line is delivered or has no delivery timestamp |
| Commission applied twice | Commission deduction exceeds the applicable commission-rule amount |
| Dispute not deducted | A lost or refunded dispute has an insufficient payout deduction |
| Payout total mismatch | Payout total differs from the sum of its payout-line net amounts |

### Ground truth scenarios

The generator maintains five documented edge-case scenarios in:

`backend/exports/edge_case_ground_truth.json`

Each scenario includes:

- Scenario ID.
- Issue type.
- Entity type.
- Description.
- Expected detection behavior.

Ground truth is maintained separately from the generated business records to make the expected anomaly conditions identifiable.

### Baseline verification

The existing production dataset was checked using the anomaly detection endpoint.

**Observed result: 0 anomalies in the verified baseline dataset.**

The automated test suite also includes individual scenarios to verify that each anomaly rule can detect its corresponding issue.

---

## 9. Data Integrity and Validation

**Backend file:** `backend/app/services/data_validation.py`

**API endpoint:** `GET /analytics/data-integrity`

The validation service checks database integrity and consistency across related marketplace entities.

### Implemented validation checks

1. SQLite database integrity check.
2. SQLite foreign key integrity check.
3. Order-line seller and product-listing seller consistency.
4. Fulfillment seller and order-line seller consistency.
5. Dispute seller and order-line seller consistency.
6. Payout seller and order-line seller consistency.
7. Order-line amount calculation.
8. Order total reconciliation against order lines.
9. Payout total reconciliation against payout lines.
10. Fulfillment shipment and delivery date validation.
11. Dispute opening and resolution date validation.
12. Duplicate payout-line detection.

### Verified validation result

The existing production dataset returned the following result:

| Metric | Result |
|---|---:|
| Total checks | 12 |
| Passed checks | 12 |
| Failed checks | 0 |
| Total issues | 0 |
| Overall status | Passed |

This result represents the validation run performed against the current dataset, not a guarantee that every possible future dataset will pass.

---

## 10. Synthetic Dataset

The platform uses synthetic marketplace data generated with a fixed random seed.

**Seed:** `20261022`

**Dataset end date:** `2026-10-22`

### Full-scale generation configuration

| Entity | Configured count |
|---|---:|
| Sellers | 2,000 |
| Customers | 20,000 |
| Product listings | 20,000 |
| Orders | 100,000 |
| Disputes | 10,000 |

### Recorded generated counts

The existing generated dataset contains:

| Entity | Generated records |
|---|---:|
| Sellers | 2,000 |
| Customers | 20,000 |
| Product listings | 20,000 |
| Orders | 100,000 |
| Order lines | 200,062 |
| Fulfillments | 200,062 |
| Customer reviews | 18,105 |
| Disputes | 10,000 |
| Commission rules | 2,000 |
| Payouts | 7,995 |
| Payout lines | 200,062 |
| State events | 202,000 |

Order-line, fulfillment, payout, and state-event counts are derived from the generated marketplace workflow and are not expected to equal the number of orders.

### Reproducibility

The data generator uses Python's seeded random-number generator.

A fixed seed makes the synthetic generation process reproducible when the same configuration, code, and execution environment are used.

The generator also creates a source manifest containing SHA-256 hashes and file sizes for generated exports.

---

## 11. Project Structure

```text
seller-operations-platform/
│
├── backend/
│   ├── app/
│   │   ├── generators/
│   │   │   └── seed_data.py
│   │   │
│   │   ├── models/
│   │   │   └── __init__.py
│   │   │
│   │   ├── services/
│   │   │   ├── analytics.py
│   │   │   ├── anomaly_detection.py
│   │   │   └── data_validation.py
│   │   │
│   │   ├── database.py
│   │   └── main.py
│   │
│   ├── exports/
│   │   ├── sellers.csv
│   │   ├── customers.csv
│   │   ├── product_listings.csv
│   │   ├── orders.csv
│   │   ├── order_lines.csv
│   │   ├── fulfillments.csv
│   │   ├── customer_reviews.csv
│   │   ├── disputes.csv
│   │   ├── commission_rules.csv
│   │   ├── payouts.csv
│   │   ├── payout_lines.csv
│   │   ├── state_events.csv
│   │   ├── edge_case_ground_truth.json
│   │   ├── source_manifest.json
│   │   └── validation reports
│   │
│   ├── tests/
│   │   ├── conftest.py
│   │   └── test_anomalies.py
│   │
│   ├── requirements.txt
│   └── app/
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── vite.config.js
│
├── documentation/
│   └── data_dictionary.md
│
├── .gitignore
└── README.md
```

*The tree illustrates the main application components; individual frontend and backend files may vary as development continues.*

---

## 12. Installation and Setup

### Prerequisites

Install the following:

- Python 3.10 or later.
- Node.js and npm.
- Git.
- Visual Studio Code (recommended).

### Step 1: Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/seller-operations-platform.git

cd seller-operations-platform
```

Replace `YOUR_USERNAME` with the actual GitHub account or repository owner.

### Step 2: Configure the backend

Open a terminal:

```bash
cd backend
```

Create a Python virtual environment:

**Windows PowerShell**

```powershell
python -m venv venv
```

Activate it:

```powershell
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

### Step 3: Configure the frontend

Open a second terminal:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

---

## 13. Running the Application

Run the backend and frontend in separate terminals.

### Start the backend

From the `backend` directory:

```powershell
.\venv\Scripts\Activate.ps1

uvicorn app.main:app --reload
```

Backend URL:

```text
http://127.0.0.1:8000
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

### Start the frontend

From the `frontend` directory:

```bash
npm run dev
```

Vite will display the local frontend URL in the terminal. The default is:

```text
http://localhost:5173
```

If that port is already occupied, Vite automatically selects another available port.

### Verify the backend

Open:

```text
http://127.0.0.1:8000/health
```

Also verify:

```text
http://127.0.0.1:8000/database-status
```

---

## 14. API Documentation

The backend exposes REST endpoints through FastAPI.

### General

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Root endpoint |
| GET | `/health` | Application health check |
| GET | `/database-status` | Database status |

### Analytics

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/analytics/dashboard` | Marketplace dashboard summary |
| GET | `/analytics/sellers` | Seller analytics |
| GET | `/analytics/sellers/{seller_id}` | Individual seller performance |
| GET | `/analytics/anomalies` | Detect operational and financial anomalies |
| GET | `/analytics/data-integrity` | Run database integrity checks |

### Marketplace operations

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/orders` | Retrieve order records |
| GET | `/listings` | Retrieve product listings |
| GET | `/fulfillments` | Retrieve fulfillment records |
| GET | `/disputes` | Retrieve dispute records |
| GET | `/payouts` | Retrieve payout records |

### Example requests

Dashboard:

```bash
curl http://127.0.0.1:8000/analytics/dashboard
```

Anomaly detection:

```bash
curl http://127.0.0.1:8000/analytics/anomalies
```

Data integrity:

```bash
curl http://127.0.0.1:8000/analytics/data-integrity
```

For request parameters and response schemas, use the interactive Swagger documentation at `/docs`.

---

## 15. Testing

The backend uses Pytest for automated testing.

The anomaly detection tests cover:

1. Clean data produces no anomalies.
2. Suspended seller with an active listing is detected.
3. Payout released before delivery is detected.
4. Excessive commission deduction is detected.
5. Missing dispute deduction is detected.
6. Payout total mismatch is detected.

The test environment uses an isolated in-memory SQLite database with foreign key enforcement enabled.

This prevents anomaly tests from modifying the application's existing production dataset.

### Run tests

From the `backend` directory:

```powershell
.\venv\Scripts\Activate.ps1

python -m pytest -v
```

### Expected verified result

```text
6 passed
```

This is the previously verified result for the current six-test anomaly suite. Run the command to confirm the result against the current checkout.

### Build the frontend

From the `frontend` directory:

```bash
npm run build
```

This checks whether the frontend can be compiled for production.

---

## 16. Data Generation and Reproducibility

The synthetic data generator is located at:

```text
backend/app/generators/seed_data.py
```

It supports three command-line options:

| Option | Description |
|---|---|
| `--scale starter` | Generate the smaller starter dataset |
| `--scale full` | Generate the full-scale dataset |
| `--seed` | Set the random seed |
| `--reset` | Clear existing database records before generation |

### Important database safety note

The database currently uses a relative SQLite URL:

```python
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./seller_operations.db")
```

The database file is therefore determined by the generator's working directory.

Run the generator only in a fresh, disposable database environment. Do not run it with `--reset` against an existing database containing data you want to preserve.

### Starter dataset

From the `backend` directory, in a clean disposable project copy:

```powershell
python -m app.generators.seed_data --scale starter --seed 20261022
```

### Full dataset

```powershell
python -m app.generators.seed_data --scale full --seed 20261022
```

### Reset option

```powershell
python -m app.generators.seed_data --scale full --seed 20261022 --reset
```

**Warning:** `--reset` deletes existing generated records before creating new ones. Use it only with a disposable database.

### Generated artifacts

The generator creates CSV and JSON exports in:

```text
backend/exports/
```

The source manifest records SHA-256 hashes and file sizes for generated files.

---

## 17. Generated Exports

The platform provides export files for further analysis, verification, and reporting.

### CSV exports

- `sellers.csv`
- `customers.csv`
- `product_listings.csv`
- `orders.csv`
- `order_lines.csv`
- `fulfillments.csv`
- `customer_reviews.csv`
- `disputes.csv`
- `commission_rules.csv`
- `payouts.csv`
- `payout_lines.csv`
- `state_events.csv`

### JSON exports

- `edge_case_ground_truth.json`
- `source_manifest.json`
- `validation_checks.json`
- `validation_summary.json`

### Purpose

The exports support:

- Dataset inspection.
- Financial reconciliation.
- Ground truth verification.
- Data integrity analysis.
- Reproducibility checks.
- External reporting and analysis.

---

## 18. Future Improvements

Potential extensions include:

- Role-based access control for operations managers and analysts.
- Advanced seller performance scoring.
- Automated payout eligibility processing.
- More detailed dispute lifecycle workflows.
- Configurable commission and reserve policies.
- Historical seller performance trends.
- Scheduled anomaly monitoring and notifications.
- More extensive integration and API tests.
- PostgreSQL support for larger production deployments.
- Machine-learning-based anomaly detection alongside existing business-rule checks.

---

## Project Status

The current implementation includes:

- Full-stack React and FastAPI application.
- Relational marketplace data model.
- Synthetic full-scale dataset.
- CSV and JSON data exports.
- Five anomaly detection rules.
- Twelve data integrity validation checks.
- Automated anomaly detection tests.
- Data dictionary and ground truth documentation.

**Verified baseline results:**

| Verification | Result |
|---|---:|
| Anomalies in existing baseline dataset | 0 |
| Data integrity checks passed | 12/12 |
| Data integrity issues | 0 |
| Anomaly tests passed in previous run | 6/6 |

---

## Author

**Seller Operations Platform**

A marketplace operations monitoring and analytics project built using React, FastAPI, SQLAlchemy, and SQLite.

