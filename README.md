# Seller Operations Monitoring Platform

A full-stack application for monitoring seller performance, order fulfillment, disputes, commissions, payouts, and operational exceptions in a marketplace.

## 1. Business Problem

Marketplace operations involve multiple connected processes. Delayed fulfillment, seller policy violations, unresolved disputes, incorrect commission calculations, and payout mismatches can affect customers and business operations.

This platform brings these processes together, applies business rules, identifies anomalies, and maintains traceability through recorded state events.

## 2. Key Features

- Seller, customer, product listing, and order management
- Order-line and fulfillment tracking
- Customer review and dispute monitoring
- Commission rule and payout management
- Payout eligibility and reconciliation monitoring
- Anomaly detection with explainable exception reasons
- Data integrity and referential validation
- Dashboard and operational analytics
- CSV and JSON dataset exports
- Synthetic data generation with a fixed seed

## 3. Technology Stack

| Layer | Technologies |
|---|---|
| Frontend | React, Vite, JavaScript, Axios |
| Backend | Python, FastAPI |
| ORM | SQLAlchemy |
| Database | SQLite |
| Testing | Pytest |
| Data exports | CSV, JSON |

## 4. System Architecture

The frontend communicates with the FastAPI backend through REST APIs. The backend uses SQLAlchemy models and a SQLite database to manage marketplace entities. Business logic services perform analytics, validation, and anomaly detection. Generated datasets and validation outputs are available under `backend/exports/`.

## 5. Business Workflow

1. Register sellers, customers, and product listings.
2. Create orders and order lines.
3. Track fulfillment and delivery status.
4. Record customer reviews and disputes.
5. Apply seller commission rules.
6. Calculate payout lines and payout totals.
7. Evaluate payout eligibility and operational exceptions.
8. Display analytics and validation results.

## 6. Data Model

The platform includes these 12 core entities:

- Customer
- Seller
- ProductListing
- Order
- OrderLine
- Fulfillment
- CustomerReview
- Dispute
- CommissionRule
- Payout
- PayoutLine
- StateEvent

Relationships and field information are documented in [`documentation/data_dictionary.md`](documentation/data_dictionary.md).

## 7. Anomaly Detection

The platform includes five defined edge-case scenarios:

| Scenario | Description |
|---|---|
| EDGE-001 | Payout released before delivery |
| EDGE-002 | Commission applied twice |
| EDGE-003 | Suspended seller has an active listing |
| EDGE-004 | Dispute deduction missing from payout |
| EDGE-005 | Payout total mismatch |

Expected outcomes are maintained separately in the edge-case ground-truth export.

## 8. Data Validation

The data generation workflow includes validation checks for record relationships, entity counts, and generated data consistency. Validation outputs are stored in:

- `backend/exports/validation_checks.json`
- `backend/exports/validation_summary.json`

## 9. Synthetic Dataset

The project uses a fixed random seed (`20261022`) to support repeatable synthetic data generation.

The generated dataset includes:

| Entity | Records |
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

The source manifest records generated export files, their sizes, and SHA-256 checksums.

## 10. Project Structure

```text
seller-operations-platform/
├── backend/
│   ├── app/
│   │   ├── generators/
│   │   ├── models/
│   │   └── services/
│   ├── exports/
│   └── tests/
├── documentation/
│   └── data_dictionary.md
├── frontend/
├── .gitignore
└── README.md
```

## 11. Installation

Clone the repository:

```bash
git clone https://github.com/mayurbarse/seller-operations-platform.git
cd seller-operations-platform
```

### Backend

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Start the backend:

```powershell
uvicorn app.main:app --reload
```

The API documentation is available at:

`http://127.0.0.1:8000/docs`

### Frontend

Open another terminal:

```powershell
cd frontend
npm install
npm run dev
```

Use the local URL printed by Vite.

## 12. Testing

From the backend directory, activate the virtual environment and run:

```powershell
pytest -q
```

## 13. Data Generation

The generator is located at:

`backend/app/generators/seed_data.py`

Inspect its supported options before running:

```powershell
python -m app.generators.seed_data --help
```

Use the fixed seed `20261022` when reproducing the dataset. Review reset-related options carefully before executing any generation command against an existing database.

## 14. Generated Exports

The `backend/exports/` directory contains generated CSV and JSON datasets, edge-case ground truth, validation results, and the source manifest.

The source manifest contains SHA-256 checksums and file-size information for the listed exports.

## 15. Future Improvements

- Role-based access control
- More advanced seller risk scoring
- Automated payout reconciliation
- Additional anomaly scenarios
- Production database support
- Expanded monitoring and reporting

---

**Repository:** https://github.com/mayurbarse/seller-operations-platform
