
import argparse
import csv
import hashlib
import json
import random
from collections import defaultdict
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path

from sqlalchemy import delete, insert, select, func, update
from sqlalchemy.orm import Session

from app.database import engine
from app.models import (
    Customer,
    Seller,
    ProductListing,
    Order,
    OrderLine,
    Fulfillment,
    CustomerReview,
    Dispute,
    CommissionRule,
    Payout,
    PayoutLine,
    StateEvent,
)

# ============================================================
# CONFIGURATION
# ============================================================

SEED = 20261022
END_DATE = datetime(2026, 10, 22)

STARTER_COUNTS = {
    "sellers": 50,
    "customers": 500,
    "listings": 500,
    "orders": 1000,
    "disputes": 100,
}

FULL_COUNTS = {
    "sellers": 2000,
    "customers": 20000,
    "listings": 20000,
    "orders": 100000,
    "disputes": 10000,
}

BATCH_SIZE = 2000

EXPORT_DIR = Path(__file__).resolve().parents[2] / "exports"

CATEGORIES = [
    "Electronics", "Fashion", "Home & Kitchen", "Beauty",
    "Sports", "Books", "Grocery", "Toys",
]

PRODUCTS = [
    "Wireless Headphones", "Smart Watch", "Cotton T-Shirt",
    "Running Shoes", "Laptop Stand", "Water Bottle",
    "Backpack", "Desk Lamp", "Bluetooth Speaker",
    "Fitness Band", "Coffee Maker", "Travel Bag",
]

SELLER_NAMES = [
    "Prime Retail", "Urban Store", "Tech World",
    "Smart Shopping", "Global Traders", "Daily Deals",
    "Modern Living", "Digital Hub", "Fashion Point",
    "Value Mart", "Elite Products", "Mega Store",
]

CARRIERS = [
    "BlueDart", "Delhivery", "DTDC", "Ekart", "XpressBees",
]

ORDER_STATUSES = [
    "placed", "confirmed", "processing", "partially_shipped",
    "shipped", "delivered", "cancelled", "returned",
]

DISPUTE_REASONS = [
    "Item not received",
    "Product damaged",
    "Wrong item delivered",
    "Refund not received",
    "Product not as described",
]

MODELS = [
    Seller, Customer, ProductListing, Order, OrderLine,
    Fulfillment, CustomerReview, Dispute, CommissionRule,
    Payout, PayoutLine, StateEvent,
]


# ============================================================
# HELPERS
# ============================================================

def money(value):
    return Decimal(str(value)).quantize(Decimal("0.01"))


def random_datetime(rng, start_days=90):
    days = rng.randint(0, start_days)
    seconds = rng.randint(0, 86399)
    return END_DATE - timedelta(days=days, seconds=seconds)


def safe_datetime(value):
    return min(value, END_DATE)


def random_email(prefix, number):
    return f"{prefix}{number}@example.com"


def insert_batches(session, model, rows):
    for start in range(0, len(rows), BATCH_SIZE):
        session.execute(
            insert(model),
            rows[start:start + BATCH_SIZE],
        )


def existing_data(session):
    return {
        model.__tablename__: session.scalar(
            select(model).limit(1)
        ) is not None
        for model in MODELS
    }


def clear_database(session):
    delete_order = [
        StateEvent, PayoutLine, Payout, Dispute,
        CustomerReview, Fulfillment, OrderLine, Order,
        CommissionRule, ProductListing, Customer, Seller,
    ]

    for model in delete_order:
        session.execute(delete(model))


def json_value(value):
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    return value


def export_csv(filename, rows):
    if not rows:
        return

    path = EXPORT_DIR / filename

    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=list(rows[0].keys()),
        )
        writer.writeheader()

        for row in rows:
            writer.writerow({
                key: json_value(value)
                for key, value in row.items()
            })


def write_json(filename, data):
    path = EXPORT_DIR / filename

    with path.open("w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            indent=2,
            default=json_value,
        )


def file_checksum(path):
    digest = hashlib.sha256()

    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


# ============================================================
# GROUND-TRUTH ANOMALY INJECTION
# ============================================================

def inject_ground_truth_scenarios(
    session,
    sellers,
    listings,
    fulfillments,
    disputes,
    payouts,
    payout_lines,
    order_line_lookup,
    commission_lookup,
    events,
):
    """
    Inject five intentional anomalies into the generated dataset.

    Database records and export dictionaries are both updated.
    Each scenario records the IDs of its affected records.
    """

    ground_truth = []
    used_payout_ids = set()

    fulfillment_lookup = {
        item["order_line_id"]: item
        for item in fulfillments
    }

    payout_lookup = {
        item["payout_id"]: item
        for item in payouts
    }

    dispute_lookup = {
        item["order_line_id"]: item
        for item in disputes
    }

    def choose_line(predicate):
        for line in payout_lines:
            if (
                line["payout_id"] not in used_payout_ids
                and predicate(line)
            ):
                used_payout_ids.add(line["payout_id"])
                return line

        raise ValueError(
            "Could not find a suitable independent payout line "
            "for a ground-truth anomaly scenario."
        )

    def add_ground_truth(
        scenario_id,
        issue_type,
        description,
        **affected_ids,
    ):
        ground_truth.append({
            "scenario_id": scenario_id,
            "issue_type": issue_type,
            "description": description,
            "expected_detection": True,
            **affected_ids,
        })

    # --------------------------------------------------------
    # EDGE-001: Payout released before delivery
    # --------------------------------------------------------

    line = choose_line(
        lambda item: (
            fulfillment_lookup[item["order_line_id"]]["delivered_at"]
            is None
        )
    )

    payout = payout_lookup[line["payout_id"]]

    payout["status"] = "paid"
    payout["released_at"] = END_DATE

    add_ground_truth(
        "EDGE-001",
        "payout_before_delivery",
        "Payout released while its order line is undelivered.",
        payout_id=payout["payout_id"],
        payout_line_id=line["payout_line_id"],
        order_line_id=line["order_line_id"],
        fulfillment_id=fulfillment_lookup[
            line["order_line_id"]
        ]["fulfillment_id"],
    )

    # --------------------------------------------------------
    # EDGE-002: Commission applied twice
    # --------------------------------------------------------

    line = choose_line(
        lambda item: item["gross_amount"] > Decimal("0.00")
    )

    seller_id = order_line_lookup[
        line["order_line_id"]
    ]["seller_id"]

    expected_commission = money(
        line["gross_amount"]
        * commission_lookup[seller_id]["commission_rate"]
    )

    excessive_commission = money(expected_commission * 2)

    old_net = line["net_amount"]

    new_net = money(max(
        Decimal("0.00"),
        line["gross_amount"]
        - excessive_commission
        - line["refund_amount"]
        - line["dispute_deduction"]
        - line["reserve_held"],
    ))

    line["commission_amount"] = excessive_commission
    line["net_amount"] = new_net

    payout = payout_lookup[line["payout_id"]]

    payout["total_amount"] = money(
        payout["total_amount"] + new_net - old_net
    )

    add_ground_truth(
        "EDGE-002",
        "commission_applied_twice",
        "Commission exceeds the applicable seller commission rule.",
        payout_id=line["payout_id"],
        payout_line_id=line["payout_line_id"],
        order_line_id=line["order_line_id"],
    )

    # --------------------------------------------------------
    # EDGE-003: Suspended seller with active listings
    # --------------------------------------------------------

    seller = next(
        (
            item for item in sellers
            if item["status"] != "suspended"
            and any(
                listing["seller_id"] == item["seller_id"]
                for listing in listings
            )
        ),
        None,
    )

    if seller is None:
        raise ValueError(
            "No suitable seller found for suspended-seller scenario."
        )

    previous_status = seller["status"]
    seller_id = seller["seller_id"]

    seller["status"] = "suspended"
    seller["suspended_at"] = END_DATE

    affected_listings = []

    for listing in listings:
        if listing["seller_id"] == seller_id:
            listing["status"] = "active"
            affected_listings.append(listing["listing_id"])

    # Update the actual database records too.
    session.execute(
        update(Seller)
        .where(Seller.seller_id == seller_id)
        .values(
            status="suspended",
            suspended_at=END_DATE,
        )
    )

    session.execute(
        update(ProductListing)
        .where(ProductListing.seller_id == seller_id)
        .values(status="active")
    )

    events.append({
        "entity_type": "seller",
        "entity_id": seller_id,
        "event_type": "seller_suspended",
        "old_state": previous_status,
        "new_state": "suspended",
        "event_at": END_DATE,
        "details": "Ground-truth anomaly scenario",
    })

    add_ground_truth(
        "EDGE-003",
        "suspended_seller_active_listing",
        "Suspended seller has active product listings.",
        seller_id=seller_id,
        listing_ids=affected_listings,
    )

    # --------------------------------------------------------
    # EDGE-004: Dispute not deducted
    # --------------------------------------------------------

    line = choose_line(
        lambda item: (
            item["order_line_id"] in dispute_lookup
            and dispute_lookup[item["order_line_id"]]["status"]
            in ("lost", "refunded")
        )
    )

    dispute = dispute_lookup[line["order_line_id"]]

    old_net = line["net_amount"]

    line["dispute_deduction"] = Decimal("0.00")

    new_net = money(max(
        Decimal("0.00"),
        line["gross_amount"]
        - line["commission_amount"]
        - line["refund_amount"]
        - line["dispute_deduction"]
        - line["reserve_held"],
    ))

    line["net_amount"] = new_net

    payout = payout_lookup[line["payout_id"]]

    payout["total_amount"] = money(
        payout["total_amount"] + new_net - old_net
    )

    add_ground_truth(
        "EDGE-004",
        "dispute_not_deducted",
        "Lost or refunded dispute has no payout deduction.",
        dispute_id=dispute["dispute_id"],
        payout_id=line["payout_id"],
        payout_line_id=line["payout_line_id"],
        order_line_id=line["order_line_id"],
    )

    # --------------------------------------------------------
    # EDGE-005: Payout total mismatch
    # --------------------------------------------------------

    line = next(
        (
            item for item in payout_lines
            if item["payout_id"] not in used_payout_ids
        ),
        None,
    )

    if line is None:
        raise ValueError(
            "No independent payout available for total-mismatch scenario."
        )

    used_payout_ids.add(line["payout_id"])

    payout = payout_lookup[line["payout_id"]]

    payout["total_amount"] = money(
        payout["total_amount"] + Decimal("1.00")
    )

    expected_mismatches = {payout["payout_id"]}

    add_ground_truth(
        "EDGE-005",
        "payout_total_mismatch",
        "Payout total differs from the sum of its payout lines.",
        payout_id=payout["payout_id"],
    )

    return ground_truth, expected_mismatches


# ============================================================
# EXPORTS AND GROUND TRUTH
# ============================================================

def export_dataset(data, counts, seed, ground_truth):
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)

    for filename, rows in data.items():
        export_csv(filename, rows)

    write_json("edge_case_ground_truth.json", ground_truth)

    summary = {
        "project": "Seller Operations Platform",
        "seed": seed,
        "end_date": END_DATE.isoformat(),
        "requested_counts": counts,
        "generated_counts": {
            filename.replace(".csv", ""): len(rows)
            for filename, rows in data.items()
        },
        "ground_truth_scenarios": len(ground_truth),
        "ground_truth_file": "edge_case_ground_truth.json",
    }

    write_json("validation_summary.json", summary)

    manifest = {
        "seed": seed,
        "generated_at": datetime.now().isoformat(),
        "files": {},
    }

    for path in sorted(EXPORT_DIR.iterdir()):
        if path.is_file() and path.name != "source_manifest.json":
            manifest["files"][path.name] = {
                "sha256": file_checksum(path),
                "size_bytes": path.stat().st_size,
            }

    write_json("source_manifest.json", manifest)

    print(f"\nExports saved to: {EXPORT_DIR}")


# ============================================================
# VALIDATION
# ============================================================

def validate_dataset(
    sellers,
    customers,
    listings,
    orders,
    order_lines,
    fulfillments,
    disputes,
    payouts,
    payout_lines,
    expected_disputes,
    expected_payout_mismatches=None,
):
    checks = []

    def check(name, passed, detail):
        checks.append({
            "check": name,
            "passed": bool(passed),
            "detail": detail,
        })

    check(
        "Unique seller IDs",
        len({x["seller_id"] for x in sellers}) == len(sellers),
        f"{len(sellers)} seller records",
    )

    check(
        "Unique customer IDs",
        len({x["customer_id"] for x in customers}) == len(customers),
        f"{len(customers)} customer records",
    )

    check(
        "Unique listing IDs",
        len({x["listing_id"] for x in listings}) == len(listings),
        f"{len(listings)} listing records",
    )

    check(
        "Unique order IDs",
        len({x["order_id"] for x in orders}) == len(orders),
        f"{len(orders)} order records",
    )

    check(
        "Unique order-line IDs",
        len({x["order_line_id"] for x in order_lines}) == len(order_lines),
        f"{len(order_lines)} order-line records",
    )

    check(
        "Unique dispute IDs",
        len({x["dispute_id"] for x in disputes}) == len(disputes),
        f"{len(disputes)} dispute records",
    )

    check(
        "Exact dispute target",
        len(disputes) == expected_disputes,
        f"Expected {expected_disputes}; generated {len(disputes)}",
    )

    seller_ids = {x["seller_id"] for x in sellers}
    customer_ids = {x["customer_id"] for x in customers}
    listing_ids = {x["listing_id"] for x in listings}
    order_ids = {x["order_id"] for x in orders}

    check(
        "Listing seller references",
        all(x["seller_id"] in seller_ids for x in listings),
        "All listings reference existing sellers",
    )

    check(
        "Order customer references",
        all(x["customer_id"] in customer_ids for x in orders),
        "All orders reference existing customers",
    )

    check(
        "Order-line references",
        all(
            x["order_id"] in order_ids
            and x["listing_id"] in listing_ids
            and x["seller_id"] in seller_ids
            for x in order_lines
        ),
        "Order lines reference existing records",
    )

    check(
        "Fulfillment count",
        len(fulfillments) == len(order_lines),
        "One fulfillment per order line",
    )

    check(
        "Date ordering",
        all(
            x["delivered_at"] is None
            or (
                x["shipped_at"] is not None
                and x["delivered_at"] >= x["shipped_at"]
            )
            for x in fulfillments
        ),
        "Delivery does not occur before shipment",
    )

    # Only the deliberately injected payout mismatch is accepted.
    expected_mismatches = set(
        expected_payout_mismatches or []
    )

    actual_mismatches = set()

    for payout in payouts:
        calculated_total = money(sum(
            (
                line["net_amount"]
                for line in payout_lines
                if line["payout_id"] == payout["payout_id"]
            ),
            Decimal("0.00"),
        ))

        if calculated_total != money(payout["total_amount"]):
            actual_mismatches.add(payout["payout_id"])

    check(
        "Payout reconciliation",
        actual_mismatches == expected_mismatches,
        (
            f"Expected mismatches: {len(expected_mismatches)}; "
            f"Actual mismatches: {len(actual_mismatches)}"
        ),
    )

    failed = [
        item for item in checks
        if not item["passed"]
    ]

    print("\nVALIDATION RESULTS")

    for item in checks:
        status = "PASS" if item["passed"] else "FAIL"
        print(f"[{status}] {item['check']}: {item['detail']}")

    if failed:
        raise ValueError(
            f"Dataset validation failed: {len(failed)} checks failed."
        )

    return checks


# ============================================================
# MAIN DATA GENERATOR
# ============================================================

def generate_data(counts=None, reset=False, seed=SEED):

    rng = random.Random(seed)
    counts = dict(counts or STARTER_COUNTS)

    required_keys = {
        "sellers", "customers", "listings", "orders", "disputes"
    }

    if not required_keys.issubset(counts):
        raise ValueError(
            "Dataset configuration is missing required counts."
        )

    if any(counts[key] < 1 for key in required_keys):
        raise ValueError(
            "All dataset counts must be greater than zero."
        )

    if counts["listings"] < 1 or counts["customers"] < 1:
        raise ValueError(
            "At least one listing and customer are required."
        )

    with Session(engine) as session:
        try:
            if reset:
                clear_database(session)
                session.commit()
                print("Existing records cleared.")

            if any(existing_data(session).values()):
                raise RuntimeError(
                    "Database already contains data. "
                    "Use --reset to regenerate everything."
                )

            print("\nStarting synthetic data generation...")
            print(f"Random seed: {seed}")
            print(f"Configuration: {counts}")

            # ------------------------------------------------
            # 1. SELLERS
            # ------------------------------------------------

            sellers = []
            seller_ids = []
            seller_status_lookup = {}

            for i in range(counts["sellers"]):
                seller_id = f"SELL-{i + 1:06d}"

                status = rng.choices(
                    ["active", "suspended", "inactive"],
                    weights=[85, 10, 5],
                )[0]

                created_at = random_datetime(rng)

                seller_ids.append(seller_id)
                seller_status_lookup[seller_id] = status

                sellers.append({
                    "seller_id": seller_id,
                    "seller_name": (
                        f"{rng.choice(SELLER_NAMES)} {i + 1}"
                    ),
                    "email": random_email("seller", i + 1),
                    "status": status,
                    "rating": money(rng.uniform(2.5, 5.0)),
                    "created_at": created_at,
                    "suspended_at": (
                        safe_datetime(
                            created_at + timedelta(days=10)
                        )
                        if status == "suspended"
                        else None
                    ),
                })

            insert_batches(session, Seller, sellers)
            print(f"Created {len(sellers)} sellers.")

            # ------------------------------------------------
            # 2. CUSTOMERS
            # ------------------------------------------------

            customers = []
            customer_ids = []

            for i in range(counts["customers"]):
                customer_id = f"CUS{i + 1:07d}"
                customer_ids.append(customer_id)

                customers.append({
                    "customer_id": customer_id,
                    "email": random_email("customer", i + 1),
                    "created_at": random_datetime(rng),
                })

            insert_batches(session, Customer, customers)
            print(f"Created {len(customers)} customers.")

            # ------------------------------------------------
            # 3. PRODUCT LISTINGS
            # ------------------------------------------------

            listings = []
            listing_lookup = []
            seller_listing_counts = defaultdict(int)

            for i in range(counts["listings"]):
                seller_id = rng.choice(seller_ids)

                seller_listing_counts[seller_id] += 1

                listing_id = (
                    f"LIST-{seller_id}-"
                    f"{seller_listing_counts[seller_id]:06d}"
                )

                seller_status = seller_status_lookup[seller_id]

                if seller_status == "suspended":
                    listing_status = "suspended"
                else:
                    listing_status = rng.choices(
                        ["active", "inactive"],
                        weights=[90, 10],
                    )[0]

                price = money(rng.uniform(99, 25000))

                listing = {
                    "listing_id": listing_id,
                    "seller_id": seller_id,
                    "product_name": rng.choice(PRODUCTS),
                    "sku": f"SKU-{i + 1:07d}",
                    "category": rng.choice(CATEGORIES),
                    "price": price,
                    "stock_quantity": rng.randint(0, 500),
                    "status": listing_status,
                    "created_at": random_datetime(rng),
                }

                listings.append(listing)

                listing_lookup.append({
                    "listing_id": listing_id,
                    "seller_id": seller_id,
                    "price": price,
                    "status": listing_status,
                })

            insert_batches(session, ProductListing, listings)
            print(f"Created {len(listings)} product listings.")

            # ------------------------------------------------
            # 4. COMMISSION RULES
            # ------------------------------------------------

            commission_rules = []
            commission_lookup = {}

            for i, seller_id in enumerate(seller_ids):
                commission_rate = money(rng.uniform(0.05, 0.20))
                reserve_rate = money(rng.uniform(0.02, 0.10))

                commission_lookup[seller_id] = {
                    "commission_rate": commission_rate,
                    "reserve_rate": reserve_rate,
                    "reserve_days": 14,
                }

                commission_rules.append({
                    "rule_id": f"RULE{i + 1:06d}",
                    "seller_id": seller_id,
                    "commission_rate": commission_rate,
                    "reserve_rate": reserve_rate,
                    "reserve_days": 14,
                    "effective_from": date(2026, 1, 1),
                    "effective_to": None,
                    "is_active": True,
                })

            insert_batches(session, CommissionRule, commission_rules)
            print(f"Created {len(commission_rules)} commission rules.")

            # ------------------------------------------------
            # 5. ORDERS, ORDER LINES AND FULFILLMENTS
            # ------------------------------------------------

            orders = []
            order_lines = []
            fulfillments = []
            reviews = []
            disputes = []
            events = []

            order_line_lookup = {}
            payout_groups = defaultdict(list)
            dispute_candidates = []

            order_status_weights = [5, 5, 10, 10, 15, 45, 5, 5]

            for i in range(counts["orders"]):
                order_id = f"ORD-2026-{i + 1:06d}"

                customer_id = rng.choice(customer_ids)
                order_date = random_datetime(rng)

                order_status = rng.choices(
                    ORDER_STATUSES,
                    weights=order_status_weights,
                )[0]

                selected = rng.sample(
                    listing_lookup,
                    k=rng.randint(
                        1,
                        min(3, len(listing_lookup)),
                    ),
                )

                # Ensure some orders contain multiple sellers.
                if i % 5 == 0 and len(listing_lookup) > 1:
                    first_seller = selected[0]["seller_id"]

                    alternatives = [
                        item for item in listing_lookup
                        if item["seller_id"] != first_seller
                    ]

                    if alternatives and len(selected) > 1:
                        selected[1] = rng.choice(alternatives)

                order_total = Decimal("0.00")

                for j, listing in enumerate(selected):
                    line_id = (
                        f"LINE-2026-{i + 1:06d}-{j + 1:02d}"
                    )

                    seller_id = listing["seller_id"]
                    quantity = rng.randint(1, 3)
                    unit_price = listing["price"]

                    line_total = money(unit_price * quantity)
                    order_total += line_total

                    if order_status == "partially_shipped":
                        line_status = (
                            "shipped" if j == 0 else "processing"
                        )
                    else:
                        line_status = order_status

                    order_lines.append({
                        "order_line_id": line_id,
                        "order_id": order_id,
                        "listing_id": listing["listing_id"],
                        "seller_id": seller_id,
                        "quantity": quantity,
                        "unit_price": unit_price,
                        "line_total": line_total,
                        "status": line_status,
                    })

                    shipped_at = None
                    delivered_at = None

                    if line_status in (
                        "shipped", "delivered", "returned"
                    ):
                        shipped_at = safe_datetime(
                            order_date + timedelta(
                                days=rng.randint(1, 4)
                            )
                        )

                    if line_status in ("delivered", "returned"):
                        delivered_at = safe_datetime(
                            shipped_at + timedelta(
                                days=rng.randint(1, 8)
                            )
                        )

                    fulfillment_status = {
                        "placed": "pending",
                        "confirmed": "pending",
                        "processing": "packed",
                        "shipped": "shipped",
                        "delivered": "delivered",
                        "cancelled": "cancelled",
                        "returned": "returned",
                    }.get(line_status, "pending")

                    fulfillments.append({
                        "fulfillment_id": f"FUL-{line_id}",
                        "order_line_id": line_id,
                        "seller_id": seller_id,
                        "status": fulfillment_status,
                        "carrier": (
                            rng.choice(CARRIERS)
                            if shipped_at else None
                        ),
                        "tracking_code": (
                            f"TRK{i + 1:08d}{j + 1}"
                            if shipped_at else None
                        ),
                        "shipped_at": shipped_at,
                        "delivered_at": delivered_at,
                    })

                    order_line_lookup[line_id] = {
                        "order_id": order_id,
                        "seller_id": seller_id,
                        "customer_id": customer_id,
                        "order_date": order_date,
                        "line_total": line_total,
                        "line_status": line_status,
                        "delivered_at": delivered_at,
                    }

                    if (
                        line_status == "delivered"
                        and rng.random() < 0.20
                    ):
                        reviews.append({
                            "review_id": f"REV-{line_id}",
                            "customer_id": customer_id,
                            "seller_id": seller_id,
                            "order_line_id": line_id,
                            "rating": rng.choices(
                                [1, 2, 3, 4, 5],
                                weights=[5, 5, 10, 25, 55],
                            )[0],
                            "review_text": rng.choice([
                                "Good product.",
                                "Excellent service.",
                                "Delivery was delayed.",
                                "Product quality was average.",
                                "Very satisfied with the purchase.",
                            ]),
                            "created_at": safe_datetime(
                                delivered_at + timedelta(days=1)
                            ),
                        })

                    if line_status not in ("cancelled", "placed"):
                        dispute_candidates.append(line_id)

                    payout_groups[
                        (seller_id, order_date.year, order_date.month)
                    ].append(line_id)

                orders.append({
                    "order_id": order_id,
                    "customer_id": customer_id,
                    "order_date": order_date,
                    "status": order_status,
                    "total_amount": money(order_total),
                    "currency": "INR",
                })

                events.extend([
                    {
                        "entity_type": "order",
                        "entity_id": order_id,
                        "event_type": "order_created",
                        "old_state": None,
                        "new_state": "placed",
                        "event_at": order_date,
                        "details": "Synthetic order creation event",
                    },
                    {
                        "entity_type": "order",
                        "entity_id": order_id,
                        "event_type": "order_status_updated",
                        "old_state": "placed",
                        "new_state": order_status,
                        "event_at": safe_datetime(
                            order_date + timedelta(hours=1)
                        ),
                        "details": "Synthetic order status event",
                    },
                ])

            # Generate exactly the configured dispute count.
            if len(dispute_candidates) < counts["disputes"]:
                raise ValueError(
                    "Not enough eligible order lines to generate "
                    f"{counts['disputes']} disputes. "
                    f"Only {len(dispute_candidates)} are available."
                )

            selected_dispute_lines = rng.sample(
                dispute_candidates,
                counts["disputes"],
            )

            for index, line_id in enumerate(
                selected_dispute_lines,
                start=1,
            ):
                line = order_line_lookup[line_id]

                dispute_status = rng.choices(
                    [
                        "open", "under_review", "won",
                        "lost", "refunded", "closed",
                    ],
                    weights=[20, 15, 20, 15, 20, 10],
                )[0]

                opened_at = safe_datetime(
                    line["order_date"] + timedelta(
                        days=rng.randint(1, 15)
                    )
                )

                resolved_at = (
                    safe_datetime(
                        opened_at + timedelta(
                            days=rng.randint(1, 20)
                        )
                    )
                    if dispute_status not in ("open", "under_review")
                    else None
                )

                disputes.append({
                    "dispute_id": f"DSP-2026-{index:06d}",
                    "order_id": line["order_id"],
                    "order_line_id": line_id,
                    "seller_id": line["seller_id"],
                    "amount": line["line_total"],
                    "reason": rng.choice(DISPUTE_REASONS),
                    "status": dispute_status,
                    "opened_at": opened_at,
                    "resolved_at": resolved_at,
                })

            insert_batches(session, Order, orders)
            insert_batches(session, OrderLine, order_lines)
            insert_batches(session, Fulfillment, fulfillments)
            insert_batches(session, CustomerReview, reviews)
            insert_batches(session, Dispute, disputes)

            print(f"Created {len(orders)} orders.")
            print(f"Created {len(order_lines)} order lines.")
            print(f"Created {len(fulfillments)} fulfillments.")
            print(f"Created {len(reviews)} reviews.")
            print(f"Created {len(disputes)} disputes.")

            # ------------------------------------------------
            # 6. PAYOUTS AND PAYOUT LINES
            # ------------------------------------------------

            payouts = []
            payout_lines = []

            dispute_lookup = {
                item["order_line_id"]: item
                for item in disputes
            }

            for group_number, (group_key, line_ids) in enumerate(
                payout_groups.items(),
                start=1,
            ):
                seller_id, year, month = group_key

                period_start = date(year, month, 1)

                if month == 12:
                    period_end = (
                        date(year + 1, 1, 1) - timedelta(days=1)
                    )
                else:
                    period_end = (
                        date(year, month + 1, 1) - timedelta(days=1)
                    )

                payout_id = f"PAYOUT-2026-{group_number:06d}"
                rule = commission_lookup[seller_id]

                group_net = Decimal("0.00")
                group_eligibility = []

                for line_id in line_ids:
                    line = order_line_lookup[line_id]
                    gross = line["line_total"]

                    commission = money(
                        gross * rule["commission_rate"]
                    )

                    reserve = money(
                        gross * rule["reserve_rate"]
                    )

                    refund = Decimal("0.00")
                    deduction = Decimal("0.00")

                    if (
                        line["line_status"] == "delivered"
                        and rng.random() < 0.025
                    ):
                        refund = money(
                            gross * Decimal("0.25")
                        )

                    dispute = dispute_lookup.get(line_id)

                    if (
                        dispute
                        and dispute["status"] in ("lost", "refunded")
                    ):
                        deduction = money(
                            gross * Decimal("0.50")
                        )

                    delivered_at = line["delivered_at"]

                    reserve_released = Decimal("0.00")
                    reserve_held = reserve

                    if (
                        delivered_at is not None
                        and delivered_at + timedelta(
                            days=rule["reserve_days"]
                        ) <= END_DATE
                    ):
                        reserve_released = reserve
                        reserve_held = Decimal("0.00")

                    if line["line_status"] == "cancelled":
                        eligibility = "rejected"
                    elif (
                        dispute
                        and dispute["status"] in (
                            "open", "under_review"
                        )
                    ):
                        eligibility = "held"
                    elif delivered_at is None:
                        eligibility = "pending"
                    elif reserve_held > 0:
                        eligibility = "held"
                    else:
                        eligibility = "eligible"

                    net = max(
                        Decimal("0.00"),
                        gross - commission - refund
                        - deduction - reserve_held,
                    )
                    net = money(net)

                    group_net += net
                    group_eligibility.append(eligibility)

                    payout_lines.append({
                        "payout_line_id": f"PL-{line_id}",
                        "payout_id": payout_id,
                        "order_line_id": line_id,
                        "gross_amount": gross,
                        "commission_amount": commission,
                        "refund_amount": refund,
                        "dispute_deduction": deduction,
                        "reserve_held": reserve_held,
                        "reserve_released": reserve_released,
                        "net_amount": net,
                        "eligibility_status": eligibility,
                        "created_at": END_DATE,
                    })

                if all(
                    x == "rejected" for x in group_eligibility
                ):
                    payout_status = "cancelled"
                elif "held" in group_eligibility:
                    payout_status = "held"
                elif "pending" in group_eligibility:
                    payout_status = "pending"
                elif "eligible" in group_eligibility:
                    payout_status = "eligible"
                else:
                    payout_status = "cancelled"

                payouts.append({
                    "payout_id": payout_id,
                    "seller_id": seller_id,
                    "period_start": period_start,
                    "period_end": period_end,
                    "total_amount": money(group_net),
                    "status": payout_status,
                    "created_at": END_DATE,
                    "released_at": None,
                })

            # ------------------------------------------------
            # 7. SELLER EVENTS AND ANOMALY SCENARIOS
            # ------------------------------------------------

            # Record original seller states before scenario changes.
            for seller in sellers:
                events.append({
                    "entity_type": "seller",
                    "entity_id": seller["seller_id"],
                    "event_type": "seller_created",
                    "old_state": None,
                    "new_state": seller["status"],
                    "event_at": seller["created_at"],
                    "details": "Synthetic seller creation event",
                })

            ground_truth, expected_mismatches = (
                inject_ground_truth_scenarios(
                    session,
                    sellers,
                    listings,
                    fulfillments,
                    disputes,
                    payouts,
                    payout_lines,
                    order_line_lookup,
                    commission_lookup,
                    events,
                )
            )

            insert_batches(session, Payout, payouts)
            insert_batches(session, PayoutLine, payout_lines)

            print(f"Created {len(payouts)} payouts.")
            print(f"Created {len(payout_lines)} payout lines.")
            print(
                f"Injected {len(ground_truth)} anomaly scenarios."
            )

            # ------------------------------------------------
            # 8. STATE EVENTS
            # ------------------------------------------------

            insert_batches(session, StateEvent, events)

            # ------------------------------------------------
            # 9. VALIDATION
            # ------------------------------------------------

            checks = validate_dataset(
                sellers,
                customers,
                listings,
                orders,
                order_lines,
                fulfillments,
                disputes,
                payouts,
                payout_lines,
                counts["disputes"],
                expected_mismatches,
            )

            session.commit()

            print("\n====================================")
            print("SYNTHETIC DATA GENERATION COMPLETED")
            print("====================================")

            for model in MODELS:
                total = session.scalar(
                    select(func.count()).select_from(model)
                )
                print(f"{model.__tablename__}: {total}")

            # ------------------------------------------------
            # 10. EXPORTS
            # ------------------------------------------------

            export_data = {
                "sellers.csv": sellers,
                "customers.csv": customers,
                "product_listings.csv": listings,
                "orders.csv": orders,
                "order_lines.csv": order_lines,
                "fulfillments.csv": fulfillments,
                "customer_reviews.csv": reviews,
                "disputes.csv": disputes,
                "commission_rules.csv": commission_rules,
                "payouts.csv": payouts,
                "payout_lines.csv": payout_lines,
                "state_events.csv": events,
            }

            export_dataset(
                export_data,
                counts,
                seed,
                ground_truth,
            )

            write_json(
                "validation_checks.json",
                checks,
            )

            print("\nAll records committed and exports created.")

        except Exception:
            session.rollback()
            raise


# ============================================================
# COMMAND LINE
# ============================================================

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Seller Operations synthetic data generator"
    )

    parser.add_argument(
        "--scale",
        choices=["starter", "full"],
        default="starter",
        help="Choose starter or full dataset",
    )

    parser.add_argument(
        "--reset",
        action="store_true",
        help="Delete existing records before generation",
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=SEED,
        help="Random seed for reproducible generation",
    )

    args = parser.parse_args()

    selected_counts = (
        FULL_COUNTS if args.scale == "full"
        else STARTER_COUNTS
    )

    generate_data(
        counts=selected_counts,
        reset=args.reset,
        seed=args.seed,
    )
