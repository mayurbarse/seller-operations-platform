from decimal import Decimal

from sqlalchemy.orm import Session
from sqlalchemy import func, or_

from app import models


def money(value):
    """Match the generator's Decimal.quantize rounding behaviour."""
    return Decimal(str(value or 0)).quantize(Decimal("0.01"))


def detect_anomalies(db: Session):
    anomalies = []

    # --------------------------------------------------------
    # 1. SUSPENDED SELLER WITH ACTIVE LISTING
    # --------------------------------------------------------

    suspended_listings = (
        db.query(
            models.ProductListing.listing_id,
            models.ProductListing.seller_id,
            models.ProductListing.product_name,
        )
        .join(
            models.Seller,
            models.Seller.seller_id == models.ProductListing.seller_id,
        )
        .filter(
            models.Seller.status == "suspended",
            models.ProductListing.status == "active",
        )
        .limit(500)
        .all()
    )

    for item in suspended_listings:
        anomalies.append({
            "type": "suspended_seller_active_listing",
            "severity": "high",
            "entity_id": item.listing_id,
            "seller_id": item.seller_id,
            "description": "Suspended seller has an active product listing",
        })

    # --------------------------------------------------------
    # 2. PAYOUT RELEASED BEFORE DELIVERY
    # --------------------------------------------------------

    premature_payouts = (
        db.query(
            models.PayoutLine.payout_line_id,
            models.PayoutLine.payout_id,
            models.PayoutLine.order_line_id,
        )
        .join(
            models.Payout,
            models.Payout.payout_id == models.PayoutLine.payout_id,
        )
        .join(
            models.Fulfillment,
            models.Fulfillment.order_line_id
            == models.PayoutLine.order_line_id,
        )
        .filter(
            models.Payout.status == "paid",
            models.Payout.released_at.isnot(None),
            or_(
                models.Fulfillment.delivered_at.is_(None),
                models.Payout.released_at
                < models.Fulfillment.delivered_at,
            ),
        )
        .limit(500)
        .all()
    )

    for item in premature_payouts:
        anomalies.append({
            "type": "payout_before_delivery",
            "severity": "critical",
            "entity_id": item.payout_line_id,
            "payout_id": item.payout_id,
            "order_line_id": item.order_line_id,
            "description": "Payout was released before fulfillment delivery",
        })

    # --------------------------------------------------------
    # 3. COMMISSION DEDUCTION EXCEEDS EXPECTED AMOUNT
    # --------------------------------------------------------

    commission_records = (
        db.query(
            models.PayoutLine.payout_line_id,
            models.PayoutLine.payout_id,
            models.PayoutLine.order_line_id,
            models.PayoutLine.gross_amount,
            models.PayoutLine.commission_amount,
            models.CommissionRule.commission_rate,
        )
        .join(
            models.Payout,
            models.Payout.payout_id == models.PayoutLine.payout_id,
        )
        .join(
            models.CommissionRule,
            models.CommissionRule.seller_id == models.Payout.seller_id,
        )
        .filter(
            models.CommissionRule.is_active.is_(True),
            models.CommissionRule.effective_from <= models.Payout.period_end,
            or_(
                models.CommissionRule.effective_to.is_(None),
                models.CommissionRule.effective_to
                >= models.Payout.period_start,
            ),
        )
        .yield_per(1000)
    )

    commission_count = 0

    for item in commission_records:
        expected = money(
            Decimal(str(item.gross_amount or 0))
            * Decimal(str(item.commission_rate or 0))
        )

        actual = money(item.commission_amount)

        if actual > expected:
            commission_count += 1

            if commission_count > 500:
                break

            anomalies.append({
                "type": "commission_applied_twice",
                "severity": "high",
                "entity_id": item.payout_line_id,
                "payout_id": item.payout_id,
                "order_line_id": item.order_line_id,
                "gross_amount": float(item.gross_amount or 0),
                "actual_commission": float(actual),
                "expected_commission": float(expected),
                "commission_rate": float(item.commission_rate or 0),
                "description": (
                    "Commission deduction exceeds the applicable seller commission"
                ),
            })

    # --------------------------------------------------------
    # 4. LOST OR REFUNDED DISPUTE NOT FULLY DEDUCTED
    # --------------------------------------------------------

    dispute_records = (
        db.query(
            models.PayoutLine.payout_line_id,
            models.PayoutLine.payout_id,
            models.PayoutLine.order_line_id,
            models.PayoutLine.dispute_deduction,
            models.Dispute.dispute_id,
            models.Dispute.amount,
            models.Dispute.status,
        )
        .join(
            models.Dispute,
            models.Dispute.order_line_id == models.PayoutLine.order_line_id,
        )
        .filter(
            models.Dispute.status.in_(["lost", "refunded"])
        )
        .yield_per(1000)
    )

    dispute_count = 0

    for item in dispute_records:
        amount = money(item.amount)
        actual_deduction = money(item.dispute_deduction)
        expected_deduction = money(amount * Decimal("0.50"))

        if actual_deduction < expected_deduction:
            dispute_count += 1

            if dispute_count > 500:
                break

            anomalies.append({
                "type": "dispute_not_deducted",
                "severity": "critical",
                "entity_id": item.payout_line_id,
                "payout_id": item.payout_id,
                "order_line_id": item.order_line_id,
                "dispute_id": item.dispute_id,
                "dispute_status": item.status,
                "expected_deduction": float(expected_deduction),
                "actual_deduction": float(actual_deduction),
                "description": (
                    "Lost or refunded dispute is not fully reflected in payout deduction"
                ),
            })

    # --------------------------------------------------------
    # 5. PAYOUT TOTAL DOES NOT MATCH PAYOUT LINES
    # --------------------------------------------------------

    payout_mismatches = (
        db.query(
            models.Payout.payout_id,
            models.Payout.total_amount,
            func.coalesce(
                func.sum(models.PayoutLine.net_amount), 0
            ).label("line_total"),
        )
        .outerjoin(
            models.PayoutLine,
            models.PayoutLine.payout_id == models.Payout.payout_id,
        )
        .group_by(models.Payout.payout_id)
        .having(
            func.round(models.Payout.total_amount, 2)
            != func.round(
                func.coalesce(func.sum(models.PayoutLine.net_amount), 0),
                2,
            )
        )
        .limit(500)
        .all()
    )

    for item in payout_mismatches:
        anomalies.append({
            "type": "payout_total_mismatch",
            "severity": "critical",
            "entity_id": item.payout_id,
            "expected_total": float(item.total_amount or 0),
            "actual_line_total": float(item.line_total or 0),
            "description": "Payout total differs from the sum of payout lines",
        })

    return {
        "total_anomalies": len(anomalies),
        "anomalies": anomalies,
    }