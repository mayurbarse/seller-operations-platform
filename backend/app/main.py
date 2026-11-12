
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.database import engine, Base
from app import models

from app.services.analytics import (
    get_dashboard_summary,
    get_seller_performance,
)

from app.services.anomaly_detection import detect_anomalies
from app.services.data_validation import validate_data_integrity


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Seller Operations Platform",
    description="Seller performance, orders, fulfillment, disputes and payout monitoring",
    version="1.0.0",
)


# ============================================================
# CORS CONFIGURATION
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():
    return {
        "message": "Seller Operations Platform API is running",
        "status": "success",
    }


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():
    return {"status": "healthy"}


# ============================================================
# DATABASE STATUS
# ============================================================

@app.get("/database-status")
def database_status():
    return {
        "database": "SQLite",
        "status": "connected",
        "tables": list(Base.metadata.tables.keys()),
    }


# ============================================================
# DASHBOARD
# ============================================================

@app.get("/analytics/dashboard")
def dashboard():
    with Session(engine) as db:
        return get_dashboard_summary(db)


# ============================================================
# SELLERS
# ============================================================

@app.get("/analytics/sellers")
def seller_performance(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    risk_level: str = None,
):
    with Session(engine) as db:
        results = get_seller_performance(db)

        if risk_level:
            results = [
                s for s in results
                if s["risk_level"] == risk_level.lower()
            ]

        return {
            "total": len(results),
            "limit": limit,
            "offset": offset,
            "sellers": results[offset:offset + limit],
        }


@app.get("/analytics/sellers/{seller_id}")
def seller_details(seller_id: str):
    with Session(engine) as db:
        seller = db.query(models.Seller).filter(
            models.Seller.seller_id == seller_id
        ).first()

        if not seller:
            raise HTTPException(404, "Seller not found")

        performance = get_seller_performance(db)

        result = next(
            (
                s for s in performance
                if s["seller_id"] == seller_id
            ),
            None,
        )

        if not result:
            raise HTTPException(404, "Seller performance not found")

        return result


# ============================================================
# ORDERS
# ============================================================

@app.get("/orders")
def get_orders(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    status: str = None,
):
    with Session(engine) as db:
        query = db.query(models.Order)

        if status:
            query = query.filter(models.Order.status == status)

        total = query.count()

        records = (
            query.order_by(models.Order.order_date.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        return {
            "total": total,
            "orders": [
                {
                    "order_id": x.order_id,
                    "customer_id": x.customer_id,
                    "order_date": x.order_date,
                    "status": x.status,
                    "total_amount": x.total_amount,
                    "currency": x.currency,
                }
                for x in records
            ],
        }


# ============================================================
# PRODUCT LISTINGS
# ============================================================

@app.get("/listings")
def get_listings(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    seller_id: str = None,
    status: str = None,
):
    with Session(engine) as db:
        query = db.query(models.ProductListing)

        if seller_id:
            query = query.filter(
                models.ProductListing.seller_id == seller_id
            )

        if status:
            query = query.filter(
                models.ProductListing.status == status
            )

        total = query.count()

        records = (
            query.order_by(models.ProductListing.listing_id)
            .offset(offset)
            .limit(limit)
            .all()
        )

        return {
            "total": total,
            "listings": [
                {
                    "listing_id": x.listing_id,
                    "seller_id": x.seller_id,
                    "product_name": x.product_name,
                    "sku": x.sku,
                    "category": x.category,
                    "price": x.price,
                    "stock_quantity": x.stock_quantity,
                    "status": x.status,
                }
                for x in records
            ],
        }


# ============================================================
# FULFILLMENTS
# ============================================================

@app.get("/fulfillments")
def get_fulfillments(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    status: str = None,
):
    with Session(engine) as db:
        query = db.query(models.Fulfillment)

        if status:
            query = query.filter(
                models.Fulfillment.status == status
            )

        total = query.count()

        records = (
            query.order_by(models.Fulfillment.fulfillment_id)
            .offset(offset)
            .limit(limit)
            .all()
        )

        return {
            "total": total,
            "fulfillments": [
                {
                    "fulfillment_id": x.fulfillment_id,
                    "order_line_id": x.order_line_id,
                    "seller_id": x.seller_id,
                    "status": x.status,
                    "carrier": x.carrier,
                    "tracking_code": x.tracking_code,
                    "shipped_at": x.shipped_at,
                    "delivered_at": x.delivered_at,
                }
                for x in records
            ],
        }


# ============================================================
# DISPUTES
# ============================================================

@app.get("/disputes")
def get_disputes(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    status: str = None,
):
    with Session(engine) as db:
        query = db.query(models.Dispute)

        if status:
            query = query.filter(
                models.Dispute.status == status
            )

        total = query.count()

        records = (
            query.order_by(models.Dispute.opened_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        return {
            "total": total,
            "disputes": [
                {
                    "dispute_id": x.dispute_id,
                    "order_id": x.order_id,
                    "order_line_id": x.order_line_id,
                    "seller_id": x.seller_id,
                    "amount": x.amount,
                    "reason": x.reason,
                    "status": x.status,
                    "opened_at": x.opened_at,
                    "resolved_at": x.resolved_at,
                }
                for x in records
            ],
        }


# ============================================================
# PAYOUTS
# ============================================================

@app.get("/payouts")
def get_payouts(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    seller_id: str = None,
    status: str = None,
):
    with Session(engine) as db:
        query = db.query(models.Payout)

        if seller_id:
            query = query.filter(
                models.Payout.seller_id == seller_id
            )

        if status:
            query = query.filter(
                models.Payout.status == status
            )

        total = query.count()

        records = (
            query.order_by(models.Payout.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        return {
            "total": total,
            "payouts": [
                {
                    "payout_id": x.payout_id,
                    "seller_id": x.seller_id,
                    "period_start": x.period_start,
                    "period_end": x.period_end,
                    "total_amount": x.total_amount,
                    "status": x.status,
                    "created_at": x.created_at,
                    "released_at": x.released_at,
                }
                for x in records
            ],
        }


# ============================================================
# ANOMALY MONITORING
# ============================================================

@app.get("/analytics/anomalies")
def get_anomalies():
    with Session(engine) as db:
        return detect_anomalies(db)


# ============================================================
# DATA INTEGRITY VALIDATION
# ============================================================

@app.get("/analytics/data-integrity")
def data_integrity():
    with Session(engine) as db:
        return validate_data_integrity(db)
