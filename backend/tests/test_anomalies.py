
from datetime import date, datetime
from decimal import Decimal

from app import models
from app.services.anomaly_detection import detect_anomalies


def create_scenario(
    db,
    seller_status="active",
    commission_amount="10.00",
    dispute_status=None,
    dispute_deduction="0.00",
    payout_total="90.00",
    released_at=datetime(2026, 10, 10),
    delivered_at=datetime(2026, 9, 5),
):
    """Create a small, internally consistent seller transaction."""

    # --------------------------------------------------
    # Stage 1: Create parent records
    # --------------------------------------------------
    customer = models.Customer(
        customer_id="CUST-TEST-001",
        email="customer@example.com",
    )

    seller = models.Seller(
        seller_id="SELL-TEST-001",
        seller_name="Test Seller",
        email="seller@example.com",
        status=seller_status,
        rating=Decimal("4.50"),
    )

    db.add_all([customer, seller])
    db.flush()

    # --------------------------------------------------
    # Stage 2: Create listing and order
    # --------------------------------------------------
    listing = models.ProductListing(
        listing_id="LIST-TEST-001",
        seller_id=seller.seller_id,
        product_name="Test Product",
        sku="TEST-SKU-001",
        category="Electronics",
        price=Decimal("100.00"),
        stock_quantity=10,
        status="active",
    )

    order = models.Order(
        order_id="ORD-TEST-001",
        customer_id=customer.customer_id,
        order_date=datetime(2026, 9, 2),
        status="delivered",
        total_amount=Decimal("100.00"),
        currency="INR",
    )

    db.add_all([listing, order])
    db.flush()

    # --------------------------------------------------
    # Stage 3: Create order line
    # --------------------------------------------------
    order_line = models.OrderLine(
        order_line_id="LINE-TEST-001",
        order_id=order.order_id,
        listing_id=listing.listing_id,
        seller_id=seller.seller_id,
        quantity=1,
        unit_price=Decimal("100.00"),
        line_total=Decimal("100.00"),
    )

    db.add(order_line)
    db.flush()

    # --------------------------------------------------
    # Stage 4: Create fulfillment, commission rule,
    # and payout
    # --------------------------------------------------
    fulfillment = models.Fulfillment(
        fulfillment_id="FUL-LINE-TEST-001",
        order_line_id=order_line.order_line_id,
        seller_id=seller.seller_id,
        status="delivered",
        carrier="Test Carrier",
        tracking_code="TRACK-TEST-001",
        shipped_at=datetime(2026, 9, 3),
        delivered_at=delivered_at,
    )

    commission_rule = models.CommissionRule(
        rule_id="RULE-TEST-001",
        seller_id=seller.seller_id,
        commission_rate=Decimal("0.1000"),
        reserve_rate=Decimal("0.0500"),
        reserve_days=7,
        effective_from=date(2026, 1, 1),
        effective_to=None,
        is_active=True,
    )

    payout = models.Payout(
        payout_id="PAYOUT-TEST-001",
        seller_id=seller.seller_id,
        period_start=date(2026, 9, 1),
        period_end=date(2026, 9, 30),
        total_amount=Decimal(payout_total),
        status="paid",
        released_at=released_at,
    )

    db.add_all([fulfillment, commission_rule, payout])
    db.flush()

    # --------------------------------------------------
    # Stage 5: Create payout line
    # --------------------------------------------------
    payout_line = models.PayoutLine(
        payout_line_id="PL-TEST-001",
        payout_id=payout.payout_id,
        order_line_id=order_line.order_line_id,
        gross_amount=Decimal("100.00"),
        commission_amount=Decimal(commission_amount),
        refund_amount=Decimal("0.00"),
        dispute_deduction=Decimal(dispute_deduction),
        reserve_held=Decimal("0.00"),
        reserve_released=Decimal("0.00"),
        net_amount=Decimal("90.00"),
        eligibility_status="paid",
    )

    db.add(payout_line)
    db.flush()

    # --------------------------------------------------
    # Stage 6: Optional dispute
    # --------------------------------------------------
    if dispute_status:
        dispute = models.Dispute(
            dispute_id="DSP-TEST-001",
            order_id=order.order_id,
            order_line_id=order_line.order_line_id,
            seller_id=seller.seller_id,
            amount=Decimal("100.00"),
            reason="Test dispute",
            status=dispute_status,
            opened_at=datetime(2026, 9, 6),
            resolved_at=datetime(2026, 9, 10),
        )

        db.add(dispute)
        db.flush()

    db.commit()


def anomaly_types(result):
    return {item["type"] for item in result["anomalies"]}


def test_clean_data_has_no_anomalies(db_session):
    create_scenario(db_session)

    result = detect_anomalies(db_session)

    assert result["total_anomalies"] == 0
    assert result["anomalies"] == []


def test_detects_suspended_seller_active_listing(db_session):
    create_scenario(
        db_session,
        seller_status="suspended",
    )

    result = detect_anomalies(db_session)

    assert "suspended_seller_active_listing" in anomaly_types(result)


def test_detects_payout_released_before_delivery(db_session):
    create_scenario(
        db_session,
        released_at=datetime(2026, 9, 4),
        delivered_at=datetime(2026, 9, 5),
    )

    result = detect_anomalies(db_session)

    assert "payout_before_delivery" in anomaly_types(result)


def test_detects_excessive_commission_deduction(db_session):
    create_scenario(
        db_session,
        commission_amount="20.00",
    )

    result = detect_anomalies(db_session)

    assert "commission_applied_twice" in anomaly_types(result)


def test_detects_missing_dispute_deduction(db_session):
    create_scenario(
        db_session,
        dispute_status="lost",
        dispute_deduction="0.00",
    )

    result = detect_anomalies(db_session)

    assert "dispute_not_deducted" in anomaly_types(result)


def test_detects_payout_total_mismatch(db_session):
    create_scenario(
        db_session,
        payout_total="100.00",
    )

    result = detect_anomalies(db_session)

    assert "payout_total_mismatch" in anomaly_types(result)
