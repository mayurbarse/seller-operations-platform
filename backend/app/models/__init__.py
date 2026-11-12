
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Boolean,
    DateTime,
    Date,
    ForeignKey,
    Numeric,
    Text,
    UniqueConstraint,
    CheckConstraint,
    Index,
)
from sqlalchemy.sql import func

from app.database import Base


# =========================================================
# 1. CUSTOMER
# =========================================================

class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(String(30), primary_key=True)
    email = Column(String(150), unique=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())


# =========================================================
# 2. SELLER
# =========================================================

class Seller(Base):
    __tablename__ = "sellers"

    seller_id = Column(String(30), primary_key=True)
    seller_name = Column(String(150), nullable=False)
    email = Column(String(150), unique=True, nullable=False)

    status = Column(
        String(30),
        nullable=False,
        default="active"
    )

    rating = Column(Numeric(3, 2), default=0)
    created_at = Column(DateTime, server_default=func.now())
    suspended_at = Column(DateTime, nullable=True)

    __table_args__ = (
        CheckConstraint(
            "status IN ('active', 'suspended', 'inactive')",
            name="check_seller_status"
        ),
        CheckConstraint(
            "rating >= 0 AND rating <= 5",
            name="check_seller_rating"
        ),
    )


# =========================================================
# 3. PRODUCT LISTING
# =========================================================

class ProductListing(Base):
    __tablename__ = "product_listings"

    listing_id = Column(String(100), primary_key=True)

    seller_id = Column(
        String(30),
        ForeignKey("sellers.seller_id"),
        nullable=False
    )

    product_name = Column(String(200), nullable=False)
    sku = Column(String(100), nullable=False)
    category = Column(String(100), nullable=False)

    price = Column(Numeric(12, 2), nullable=False)
    stock_quantity = Column(Integer, nullable=False, default=0)

    status = Column(String(30), default="active", nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("seller_id", "sku", name="uq_seller_sku"),
        CheckConstraint("price > 0", name="check_listing_price"),
        CheckConstraint(
            "stock_quantity >= 0",
            name="check_listing_stock"
        ),
        CheckConstraint(
            "status IN ('active', 'inactive', 'suspended')",
            name="check_listing_status"
        ),
    )


# =========================================================
# 4. ORDER
# =========================================================

class Order(Base):
    __tablename__ = "orders"

    order_id = Column(String(30), primary_key=True)

    customer_id = Column(
        String(30),
        ForeignKey("customers.customer_id"),
        nullable=False
    )

    order_date = Column(DateTime, nullable=False)
    status = Column(String(30), nullable=False, default="placed")

    total_amount = Column(Numeric(14, 2), nullable=False)
    currency = Column(String(3), default="INR", nullable=False)

    __table_args__ = (
        CheckConstraint(
            "status IN ('placed', 'confirmed', 'processing', "
            "'partially_shipped', 'shipped', 'delivered', "
            "'cancelled', 'returned')",
            name="check_order_status"
        ),
        CheckConstraint(
            "total_amount >= 0",
            name="check_order_amount"
        ),
    )


# =========================================================
# 5. ORDER LINE
# =========================================================

class OrderLine(Base):
    __tablename__ = "order_lines"

    order_line_id = Column(String(100), primary_key=True)

    order_id = Column(
        String(30),
        ForeignKey("orders.order_id"),
        nullable=False
    )

    listing_id = Column(
        String(100),
        ForeignKey("product_listings.listing_id"),
        nullable=False
    )

    seller_id = Column(
        String(30),
        ForeignKey("sellers.seller_id"),
        nullable=False
    )

    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(12, 2), nullable=False)
    line_total = Column(Numeric(14, 2), nullable=False)

    status = Column(String(30), default="created", nullable=False)

    __table_args__ = (
        CheckConstraint("quantity > 0", name="check_line_quantity"),
        CheckConstraint("unit_price > 0", name="check_line_price"),
        CheckConstraint("line_total >= 0", name="check_line_total"),
    )


# =========================================================
# 6. FULFILLMENT
# =========================================================

class Fulfillment(Base):
    __tablename__ = "fulfillments"

    fulfillment_id = Column(String(120), primary_key=True)

    order_line_id = Column(
        String(100),
        ForeignKey("order_lines.order_line_id"),
        nullable=False,
        unique=True
    )

    seller_id = Column(
        String(30),
        ForeignKey("sellers.seller_id"),
        nullable=False
    )

    status = Column(String(30), default="pending", nullable=False)

    carrier = Column(String(100), nullable=True)
    tracking_code = Column(String(100), nullable=True)

    shipped_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'packed', 'shipped', "
            "'delivered', 'returned', 'cancelled')",
            name="check_fulfillment_status"
        ),
    )


# =========================================================
# 7. CUSTOMER REVIEW
# =========================================================

class CustomerReview(Base):
    __tablename__ = "customer_reviews"

    review_id = Column(String(30), primary_key=True)

    customer_id = Column(
        String(30),
        ForeignKey("customers.customer_id"),
        nullable=False
    )

    seller_id = Column(
        String(30),
        ForeignKey("sellers.seller_id"),
        nullable=False
    )

    order_line_id = Column(
        String(100),
        ForeignKey("order_lines.order_line_id"),
        nullable=False,
        unique=True
    )

    rating = Column(Integer, nullable=False)
    review_text = Column(Text, nullable=True)

    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        CheckConstraint(
            "rating BETWEEN 1 AND 5",
            name="check_review_rating"
        ),
    )


# =========================================================
# 8. DISPUTE
# =========================================================

class Dispute(Base):
    __tablename__ = "disputes"

    dispute_id = Column(String(30), primary_key=True)

    order_id = Column(
        String(30),
        ForeignKey("orders.order_id"),
        nullable=False
    )

    order_line_id = Column(
        String(100),
        ForeignKey("order_lines.order_line_id"),
        nullable=True
    )

    seller_id = Column(
        String(30),
        ForeignKey("sellers.seller_id"),
        nullable=False
    )

    amount = Column(Numeric(14, 2), nullable=False)

    reason = Column(String(100), nullable=False)

    status = Column(
        String(30),
        default="open",
        nullable=False
    )

    opened_at = Column(DateTime, nullable=False)
    resolved_at = Column(DateTime, nullable=True)

    __table_args__ = (
        CheckConstraint("amount > 0", name="check_dispute_amount"),
        CheckConstraint(
            "status IN ('open', 'under_review', 'won', "
            "'lost', 'refunded', 'closed')",
            name="check_dispute_status"
        ),
    )


# =========================================================
# 9. COMMISSION RULE
# =========================================================

class CommissionRule(Base):
    __tablename__ = "commission_rules"

    rule_id = Column(String(30), primary_key=True)

    # NULL seller_id means a platform-wide default rule
    seller_id = Column(
        String(30),
        ForeignKey("sellers.seller_id"),
        nullable=True
    )

    commission_rate = Column(Numeric(6, 4), nullable=False)
    reserve_rate = Column(Numeric(6, 4), nullable=False)

    reserve_days = Column(Integer, nullable=False, default=7)

    effective_from = Column(Date, nullable=False)
    effective_to = Column(Date, nullable=True)

    is_active = Column(Boolean, default=True)

    __table_args__ = (
        CheckConstraint(
            "commission_rate >= 0 AND commission_rate <= 1",
            name="check_commission_rate"
        ),
        CheckConstraint(
            "reserve_rate >= 0 AND reserve_rate <= 1",
            name="check_reserve_rate"
        ),
        CheckConstraint(
            "reserve_days >= 0",
            name="check_reserve_days"
        ),
    )


# =========================================================
# 10. PAYOUT
# =========================================================

class Payout(Base):
    __tablename__ = "payouts"

    payout_id = Column(String(30), primary_key=True)

    seller_id = Column(
        String(30),
        ForeignKey("sellers.seller_id"),
        nullable=False
    )

    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)

    total_amount = Column(Numeric(14, 2), nullable=False, default=0)

    status = Column(
        String(30),
        default="pending",
        nullable=False
    )

    created_at = Column(DateTime, server_default=func.now())
    released_at = Column(DateTime, nullable=True)

    __table_args__ = (
        CheckConstraint(
            "period_end >= period_start",
            name="check_payout_period"
        ),
        CheckConstraint(
            "total_amount >= 0",
            name="check_payout_total"
        ),
        CheckConstraint(
            "status IN ('pending', 'eligible', 'held', "
            "'paid', 'failed', 'cancelled')",
            name="check_payout_status"
        ),
    )


# =========================================================
# 11. PAYOUT LINE
# =========================================================

class PayoutLine(Base):
    __tablename__ = "payout_lines"

    payout_line_id = Column(String(40), primary_key=True)

    payout_id = Column(
        String(30),
        ForeignKey("payouts.payout_id"),
        nullable=False
    )

    order_line_id = Column(
        String(100),
        ForeignKey("order_lines.order_line_id"),
        nullable=False
    )

    gross_amount = Column(Numeric(14, 2), nullable=False)
    commission_amount = Column(Numeric(14, 2), nullable=False, default=0)

    refund_amount = Column(Numeric(14, 2), nullable=False, default=0)
    dispute_deduction = Column(Numeric(14, 2), nullable=False, default=0)

    reserve_held = Column(Numeric(14, 2), nullable=False, default=0)
    reserve_released = Column(Numeric(14, 2), nullable=False, default=0)

    net_amount = Column(Numeric(14, 2), nullable=False)

    eligibility_status = Column(
        String(30),
        nullable=False,
        default="pending"
    )

    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        UniqueConstraint(
            "payout_id",
            "order_line_id",
            name="uq_payout_order_line"
        ),
        CheckConstraint(
            "gross_amount >= 0 AND commission_amount >= 0 "
            "AND refund_amount >= 0 AND dispute_deduction >= 0 "
            "AND reserve_held >= 0 AND reserve_released >= 0",
            name="check_payout_line_amounts"
        ),
        CheckConstraint(
            "eligibility_status IN ('pending', 'eligible', "
            "'held', 'paid', 'rejected')",
            name="check_payout_line_status"
        ),
    )


# =========================================================
# 12. STATE EVENT - AUDIT HISTORY
# =========================================================

class StateEvent(Base):
    __tablename__ = "state_events"

    event_id = Column(Integer, primary_key=True, autoincrement=True)

    entity_type = Column(String(50), nullable=False)
    entity_id = Column(String(120), nullable=False)

    event_type = Column(String(100), nullable=False)

    old_state = Column(String(50), nullable=True)
    new_state = Column(String(50), nullable=True)

    event_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )

    details = Column(Text, nullable=True)

    __table_args__ = (
        Index(
            "idx_state_event_entity",
            "entity_type",
            "entity_id"
        ),
    )
