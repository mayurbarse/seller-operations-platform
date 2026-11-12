
from decimal import Decimal

from sqlalchemy import func, text
from sqlalchemy.orm import Session

from app import models


def money(value):
    return Decimal(str(value or 0)).quantize(Decimal("0.01"))


def validate_data_integrity(db: Session):
    checks = []

    def add_check(name, count, description):
        checks.append({
            "name": name,
            "issue_count": int(count),
            "status": "passed" if count == 0 else "failed",
            "description": description,
        })

    # 1. SQLite database integrity
    integrity = db.execute(text("PRAGMA integrity_check")).scalar()
    add_check(
        "database_integrity",
        0 if integrity == "ok" else 1,
        "SQLite database structural integrity",
    )

    # 2. Foreign-key violations
    fk_errors = db.execute(
        text("PRAGMA foreign_key_check")
    ).all()

    add_check(
        "foreign_key_integrity",
        len(fk_errors),
        "Records referencing missing parent records",
    )

    # 3. Order line seller must match listing seller
    listing_seller_mismatches = (
        db.query(models.OrderLine.order_line_id)
        .join(
            models.ProductListing,
            models.ProductListing.listing_id == models.OrderLine.listing_id,
        )
        .filter(
            models.OrderLine.seller_id != models.ProductListing.seller_id
        )
        .count()
    )

    add_check(
        "order_line_seller_consistency",
        listing_seller_mismatches,
        "Order line seller must match product listing seller",
    )

    # 4. Fulfillment seller must match order line seller
    fulfillment_mismatches = (
        db.query(models.Fulfillment.fulfillment_id)
        .join(
            models.OrderLine,
            models.OrderLine.order_line_id == models.Fulfillment.order_line_id,
        )
        .filter(
            models.Fulfillment.seller_id != models.OrderLine.seller_id
        )
        .count()
    )

    add_check(
        "fulfillment_seller_consistency",
        fulfillment_mismatches,
        "Fulfillment seller must match order line seller",
    )

    # 5. Dispute seller must match order line seller
    dispute_mismatches = (
        db.query(models.Dispute.dispute_id)
        .join(
            models.OrderLine,
            models.OrderLine.order_line_id == models.Dispute.order_line_id,
        )
        .filter(
            models.Dispute.seller_id != models.OrderLine.seller_id
        )
        .count()
    )

    add_check(
        "dispute_seller_consistency",
        dispute_mismatches,
        "Dispute seller must match its order line seller",
    )

    # 6. Payout seller must match order line seller
    payout_seller_mismatches = (
        db.query(models.PayoutLine.payout_line_id)
        .join(
            models.Payout,
            models.Payout.payout_id == models.PayoutLine.payout_id,
        )
        .join(
            models.OrderLine,
            models.OrderLine.order_line_id == models.PayoutLine.order_line_id,
        )
        .filter(
            models.Payout.seller_id != models.OrderLine.seller_id
        )
        .count()
    )

    add_check(
        "payout_seller_consistency",
        payout_seller_mismatches,
        "Payout seller must match the seller of its order line",
    )

    # 7. Order line arithmetic
    line_errors = 0

    order_lines = db.query(
        models.OrderLine.quantity,
        models.OrderLine.unit_price,
        models.OrderLine.line_total,
    ).yield_per(5000)

    for line in order_lines:
        expected = money(
            Decimal(str(line.quantity))
            * Decimal(str(line.unit_price))
        )

        if money(line.line_total) != expected:
            line_errors += 1

    add_check(
        "order_line_amounts",
        line_errors,
        "Line total must equal quantity multiplied by unit price",
    )

    # 8. Order total versus order lines
    order_totals = (
        db.query(
            models.Order.order_id,
            models.Order.total_amount,
            func.coalesce(func.sum(models.OrderLine.line_total), 0),
        )
        .outerjoin(
            models.OrderLine,
            models.OrderLine.order_id == models.Order.order_id,
        )
        .group_by(models.Order.order_id)
        .all()
    )

    order_total_errors = sum(
        1
        for _, total, line_total in order_totals
        if money(total) != money(line_total)
    )

    add_check(
        "order_total_reconciliation",
        order_total_errors,
        "Order total must match the sum of its order lines",
    )

    # 9. Payout total versus payout lines
    payout_totals = (
        db.query(
            models.Payout.payout_id,
            models.Payout.total_amount,
            func.coalesce(func.sum(models.PayoutLine.net_amount), 0),
        )
        .outerjoin(
            models.PayoutLine,
            models.PayoutLine.payout_id == models.Payout.payout_id,
        )
        .group_by(models.Payout.payout_id)
        .all()
    )

    payout_total_errors = sum(
        1
        for _, total, line_total in payout_totals
        if money(total) != money(line_total)
    )

    add_check(
        "payout_total_reconciliation",
        payout_total_errors,
        "Payout total must match the sum of payout line net amounts",
    )

    # 10. Invalid date sequences
    fulfillment_date_errors = (
        db.query(models.Fulfillment.fulfillment_id)
        .filter(
            models.Fulfillment.shipped_at.isnot(None),
            models.Fulfillment.delivered_at.isnot(None),
            models.Fulfillment.delivered_at < models.Fulfillment.shipped_at,
        )
        .count()
    )

    add_check(
        "fulfillment_date_sequence",
        fulfillment_date_errors,
        "Delivery date cannot precede shipment date",
    )

    dispute_date_errors = (
        db.query(models.Dispute.dispute_id)
        .filter(
            models.Dispute.resolved_at.isnot(None),
            models.Dispute.resolved_at < models.Dispute.opened_at,
        )
        .count()
    )

    add_check(
        "dispute_date_sequence",
        dispute_date_errors,
        "Dispute resolution cannot precede dispute opening",
    )

    # 11. Duplicate payout lines
    duplicate_payout_lines = (
        db.query(
            models.PayoutLine.payout_id,
            models.PayoutLine.order_line_id,
        )
        .group_by(
            models.PayoutLine.payout_id,
            models.PayoutLine.order_line_id,
        )
        .having(func.count() > 1)
        .count()
    )

    add_check(
        "duplicate_payout_lines",
        duplicate_payout_lines,
        "An order line must not appear twice in the same payout",
    )

    total_issues = sum(item["issue_count"] for item in checks)

    return {
        "overall_status": "passed" if total_issues == 0 else "failed",
        "total_checks": len(checks),
        "passed_checks": sum(
            1 for item in checks if item["status"] == "passed"
        ),
        "failed_checks": sum(
            1 for item in checks if item["status"] == "failed"
        ),
        "total_issues": total_issues,
        "checks": checks,
    }
