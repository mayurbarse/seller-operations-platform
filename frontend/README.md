# Seller Operations Platform – Frontend

The frontend of the Seller Operations Monitoring Platform is built using React and Vite. It provides an interface for monitoring marketplace operations, seller performance, orders, fulfillment, disputes, payouts, and operational anomalies.

## 1. Technology Stack

| Technology | Purpose |
|---|---|
| React 19 | UI development |
| Vite | Development server and build tool |
| JavaScript | Application logic |
| React Router | Client-side navigation |
| Axios | HTTP requests to backend APIs |
| Lucide React | Icons |

## 2. Features

- Marketplace dashboard and analytics
- Seller performance monitoring
- Product listing information
- Order and fulfillment monitoring
- Customer dispute monitoring
- Commission and payout information
- Anomaly monitoring
- Data integrity results
- API-driven data presentation

## 3. Project Structure

```text
frontend/
├── public/
├── src/
│   ├── components/
│   ├── assets/
│   ├── App.jsx
│   └── main.jsx
├── index.html
├── package.json
└── vite.config.js
```

The structure above illustrates the main frontend components. Refer to the actual source directory for the complete implementation.

## 4. Prerequisites

Install:

- Node.js
- npm
- Git

## 5. Installation

From the repository root:

```powershell
cd frontend
npm install
```

## 6. Run the Development Server

```powershell
npm run dev
```

Vite displays the local development URL in the terminal. The default address is:

```text
http://localhost:5173
```

## 7. Backend Integration

The frontend communicates with the FastAPI backend through HTTP requests using Axios.

Start the backend separately from the `backend` directory:

```powershell
uvicorn app.main:app --reload
```

Backend API documentation:

```text
http://127.0.0.1:8000/docs
```

Ensure the frontend API configuration points to the running backend.

## 8. Production Build

To generate a production build:

```powershell
npm run build
```

Vite generates the production assets in the `dist/` directory.

## 9. Preview Production Build

```powershell
npm run preview
```

## 10. Related Documentation

For the complete project documentation, including system architecture, business workflows, database design, synthetic dataset generation, anomaly detection, validation, and API details, see the repository's root `README.md`.

**Project:** Seller Operations Monitoring Platform  
**Frontend:** React + Vite  
**Backend:** FastAPI + SQLAlchemy + SQLite