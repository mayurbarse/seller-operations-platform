
from sqlalchemy.orm import Session
from sqlalchemy import func, case

from app.models import (
    Seller,
    Order,
    OrderLine,
    Fulfillment,
    CustomerReview,
    Dispute,
    Payout,
)


def number(value):
    """Convert database numeric values into JSON-friendly numbers."""
    return float(value or 0)


def get_dashboard_summary(db: Session):
    """Calculate overall marketplace monitoring metrics."""

    total_sellers = db.query(func.count(Seller.seller_id)).scalar() or 0

    active_sellers = (
        db.query(func.count(Seller.seller_id))
        .filter(Seller.status == "active")
        .scalar() or 0
    )

    suspended_sellers = (
        db.query(func.count(Seller.seller_id))
        .filter(Seller.status == "suspended")
        .scalar() or 0
    )

    total_orders = db.query(func.count(Order.order_id)).scalar() or 0

    gmv = (
        db.query(
            func.sum(
                case(
                    (
                        Order.status.notin_(["cancelled", "returned"]),
                        Order.total_amount,
                    ),
                    else_=0,
                )
            )
        ).scalar() or 0
    )

    average_order_value = (
        number(gmv) / total_orders if total_orders else 0
    )

    total_order_lines = (
        db.query(func.count(OrderLine.order_line_id)).scalar() or 0
    )

    total_fulfillments = (
        db.query(func.count(Fulfillment.fulfillment_id)).scalar() or 0
    )

    delivered = (
        db.query(func.count(Fulfillment.fulfillment_id))
        .filter(Fulfillment.status == "delivered")
        .scalar() or 0
    )

    # A seven-day delivery proxy is used because the current
    # schema does not contain a promised delivery date.
    within_seven_days = (
        db.query(func.count(Fulfillment.fulfillment_id))
        .filter(
            Fulfillment.status == "delivered",
            Fulfillment.shipped_at.isnot(None),
            Fulfillment.delivered_at.isnot(None),
            (
                func.julianday(Fulfillment.delivered_at)
                - func.julianday(Fulfillment.shipped_at)
            ) <= 7,
        )
        .scalar() or 0
    )

    delivery_rate = (
        delivered / total_fulfillments * 100
        if total_fulfillments else 0
    )

    delivery_within_seven_days_rate = (
        within_seven_days / delivered * 100
        if delivered else 0
    )

    average_rating = (
        db.query(func.avg(CustomerReview.rating)).scalar()
    )

    total_reviews = (
        db.query(func.count(CustomerReview.review_id)).scalar() or 0
    )

    total_disputes = (
        db.query(func.count(Dispute.dispute_id)).scalar() or 0
    )

    open_disputes = (
        db.query(func.count(Dispute.dispute_id))
        .filter(Dispute.status.in_(["open", "under_review"]))
        .scalar() or 0
    )

    dispute_rate = (
        total_disputes / total_order_lines * 100
        if total_order_lines else 0
    )

    total_payouts = (
        db.query(func.count(Payout.payout_id)).scalar() or 0
    )

    held_payout_amount = (
        db.query(func.sum(Payout.total_amount))
        .filter(Payout.status == "held")
        .scalar() or 0
    )

    eligible_payout_amount = (
        db.query(func.sum(Payout.total_amount))
        .filter(Payout.status == "eligible")
        .scalar() or 0
    )

    paid_payout_amount = (
        db.query(func.sum(Payout.total_amount))
        .filter(Payout.status == "paid")
        .scalar() or 0
    )

    return {
        "sellers": {
            "total": total_sellers,
            "active": active_sellers,
            "suspended": suspended_sellers,
        },
        "orders": {
            "total": total_orders,
            "total_order_lines": total_order_lines,
            "gmv": number(gmv),
            "average_order_value": round(average_order_value, 2),
        },
        "fulfillment": {
            "total": total_fulfillments,
            "delivered": delivered,
            "delivery_rate_percent": round(delivery_rate, 2),
            "delivered_within_7_days_percent": round(
                delivery_within_seven_days_rate, 2
            ),
        },
        "reviews": {
            "total": total_reviews,
            "average_rating": round(number(average_rating), 2),
        },
        "disputes": {
            "total": total_disputes,
            "open": open_disputes,
            "dispute_rate_percent": round(dispute_rate, 2),
        },
        "payouts": {
            "total": total_payouts,
            "held_amount": number(held_payout_amount),
            "eligible_amount": number(eligible_payout_amount),
            "paid_amount": number(paid_payout_amount),
        },
    }


def get_seller_performance(db: Session):
    """Calculate individual seller performance and risk metrics."""

    sellers = db.query(Seller).order_by(Seller.seller_id).all()

    # Order and revenue statistics.
    order_stats = db.query(
        OrderLine.seller_id,
        func.count(func.distinct(OrderLine.order_id)).label("orders"),
        func.count(OrderLine.order_line_id).label("order_lines"),
        func.sum(OrderLine.line_total).label("gmv"),
    ).group_by(OrderLine.seller_id).all()

    order_map = {
        row.seller_id: row for row in order_stats
    }

    # Fulfillment statistics.
    delivery_stats = db.query(
        OrderLine.seller_id,
        func.count(Fulfillment.fulfillment_id).label("total"),
        func.sum(
            case(
                (Fulfillment.status == "delivered", 1),
                else_=0,
            )
        ).label("delivered"),
        func.sum(
            case(
                (
                    (Fulfillment.status == "delivered")
                    & (
                        (
                            func.julianday(Fulfillment.delivered_at)
                            - func.julianday(Fulfillment.shipped_at)
                        ) <= 7
                    )
                    & Fulfillment.shipped_at.isnot(None)
                    & Fulfillment.delivered_at.isnot(None),
                    1,
                ),
                else_=0,
            )
        ).label("within_7_days"),
    ).join(
        OrderLine,
        Fulfillment.order_line_id == OrderLine.order_line_id,
    ).group_by(OrderLine.seller_id).all()

    delivery_map = {
        row.seller_id: row for row in delivery_stats
    }

    # Dispute statistics.
    dispute_stats = db.query(
        Dispute.seller_id,
        func.count(Dispute.dispute_id).label("total"),
        func.sum(
            case(
                (
                    Dispute.status.in_(["open", "under_review"]),
                    1,
                ),
                else_=0,
            )
        ).label("open"),
    ).group_by(Dispute.seller_id).all()

    dispute_map = {
        row.seller_id: row for row in dispute_stats
    }

    # Customer review statistics.
    review_stats = db.query(
        CustomerReview.seller_id,
        func.avg(CustomerReview.rating).label("rating"),
        func.count(CustomerReview.review_id).label("total"),
    ).group_by(CustomerReview.seller_id).all()

    review_map = {
        row.seller_id: row for row in review_stats
    }

    # Payout statistics.
    payout_stats = db.query(
        Payout.seller_id,
        func.sum(
            case(
                (Payout.status == "held", Payout.total_amount),
                else_=0,
            )
        ).label("held_amount"),
        func.sum(
            case(
                (Payout.status == "paid", Payout.total_amount),
                else_=0,
            )
        ).label("paid_amount"),
    ).group_by(Payout.seller_id).all()

    payout_map = {
        row.seller_id: row for row in payout_stats
    }

    results = []

    for seller in sellers:

        orders = order_map.get(seller.seller_id)
        delivery = delivery_map.get(seller.seller_id)
        dispute = dispute_map.get(seller.seller_id)
        review = review_map.get(seller.seller_id)
        payout = payout_map.get(seller.seller_id)

        order_count = orders.orders if orders else 0
        line_count = orders.order_lines if orders else 0

        delivered_count = delivery.delivered if delivery else 0
        delivery_total = delivery.total if delivery else 0

        within_7_days = delivery.within_7_days if delivery else 0

        dispute_count = dispute.total if dispute else 0
        open_dispute_count = dispute.open if dispute else 0

        rating = (
            number(review.rating)
            if review and review.rating is not None
            else number(seller.rating)
        )

        delivery_rate = (
            delivered_count / delivery_total * 100
            if delivery_total else 0
        )

        seven_day_rate = (
            within_7_days / delivered_count * 100
            if delivered_count else 0
        )

        dispute_rate = (
            dispute_count / line_count * 100
            if line_count else 0
        )

        # Weighted performance score.
        rating_score = rating * 20
        dispute_score = max(0, 100 - dispute_rate * 10)

        performance_score = (
            rating_score * 0.40
            + seven_day_rate * 0.40
            + dispute_score * 0.20
        )

        if seller.status != "active":
            risk_level = "high"
        elif open_dispute_count >= 3 or dispute_rate >= 10:
            risk_level = "high"
        elif rating < 3.5 or dispute_rate >= 5:
            risk_level = "medium"
        else:
            risk_level = "low"

        results.append({
            "seller_id": seller.seller_id,
            "seller_name": seller.seller_name,
            "status": seller.status,
            "seller_rating": round(rating, 2),
            "total_orders": order_count,
            "total_order_lines": line_count,
            "gmv": number(orders.gmv if orders else 0),
            "delivered_orders": delivered_count,
            "delivery_rate_percent": round(delivery_rate, 2),
            "delivered_within_7_days_percent": round(
                seven_day_rate, 2
            ),
            "total_disputes": dispute_count,
            "open_disputes": open_dispute_count,
            "dispute_rate_percent": round(dispute_rate, 2),
            "held_payout_amount": number(
                payout.held_amount if payout else 0
            ),
            "paid_payout_amount": number(
                payout.paid_amount if payout else 0
            ),
            "performance_score": round(performance_score, 2),
            "risk_level": risk_level,
        })

    results.sort(
        key=lambda x: x["performance_score"],
        reverse=True,
    )

    return results
