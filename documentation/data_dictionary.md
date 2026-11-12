
# Seller Operations Platform - Data Dictionary

## 1. Customer
- customer_id: String, Primary Key, Required, Unique.
- email: String, Required, Unique.
- created_at: DateTime, Automatically generated.

## 2. Seller
- seller_id: String, Primary Key, Required.
- seller_name: String, Required.
- email: String, Required, Unique.
- status: String, active/suspended/inactive.
- rating: Decimal, 0 to 5.
- created_at: DateTime.
- suspended_at: DateTime, Optional.

## 3. ProductListing
- listing_id: String, Primary Key, Required.
- seller_id: String, Foreign Key, Required.
- product_name: String, Required.
- sku: String, Required, Unique per seller.
- category: String, Required.
- price: Decimal, Greater than zero.
- stock_quantity: Integer, Zero or greater.
- status: active/inactive/suspended.
- created_at: DateTime.

## 4. Order
- order_id: String, Primary Key, Required.
- customer_id: String, Foreign Key, Required.
- order_date: DateTime, Required.
- status: placed/confirmed/processing/partially_shipped/
  shipped/delivered/cancelled/returned.
- total_amount: Decimal, Zero or greater.
- currency: String, Default INR.

## 5. OrderLine
- order_line_id: String, Primary Key, Required.
- order_id: String, Foreign Key, Required.
- listing_id: String, Foreign Key, Required.
- seller_id: String, Foreign Key, Required.
- quantity: Integer, Greater than zero.
- unit_price: Decimal, Greater than zero.
- line_total: Decimal, Derived from quantity * unit_price.
- status: String, Required.

## 6. Fulfillment
- fulfillment_id: String, Primary Key.
- order_line_id: String, Foreign Key, Unique, Required.
- seller_id: String, Foreign Key, Required.
- status: pending/packed/shipped/delivered/returned/cancelled.
- carrier: String, Optional.
- tracking_code: String, Optional.
- shipped_at: DateTime, Optional.
- delivered_at: DateTime, Optional.

## 7. CustomerReview
- review_id: String, Primary Key.
- customer_id: String, Foreign Key.
- seller_id: String, Foreign Key.
- order_line_id: String, Foreign Key, Unique.
- rating: Integer, 1 to 5.
- review_text: Text, Optional.
- created_at: DateTime.

## 8. Dispute
- dispute_id: String, Primary Key.
- order_id: String, Foreign Key.
- order_line_id: String, Foreign Key, Optional.
- seller_id: String, Foreign Key.
- amount: Decimal, Greater than zero.
- reason: String, Required.
- status: open/under_review/won/lost/refunded/closed.
- opened_at: DateTime.
- resolved_at: DateTime, Optional.

## 9. CommissionRule
- rule_id: String, Primary Key.
- seller_id: String, Foreign Key, Optional for global rules.
- commission_rate: Decimal, Between 0 and 1.
- reserve_rate: Decimal, Between 0 and 1.
- reserve_days: Integer, Zero or greater.
- effective_from: Date, Required.
- effective_to: Date, Optional.
- is_active: Boolean.

## 10. Payout
- payout_id: String, Primary Key.
- seller_id: String, Foreign Key.
- period_start: Date, Required.
- period_end: Date, Must be on or after period_start.
- total_amount: Decimal, Zero or greater.
- status: pending/eligible/held/paid/failed/cancelled.
- created_at: DateTime.
- released_at: DateTime, Optional.

## 11. PayoutLine
- payout_line_id: String, Primary Key.
- payout_id: String, Foreign Key.
- order_line_id: String, Foreign Key.
- gross_amount: Decimal.
- commission_amount: Decimal.
- refund_amount: Decimal.
- dispute_deduction: Decimal.
- reserve_held: Decimal.
- reserve_released: Decimal.
- net_amount: Decimal, Derived financial amount.
- eligibility_status: pending/eligible/held/paid/rejected.
- created_at: DateTime.

## 12. StateEvent
- event_id: Integer, Primary Key.
- entity_type: String, Required.
- entity_id: String, Required.
- event_type: String, Required.
- old_state: String, Optional.
- new_state: String, Optional.
- event_at: DateTime.
- details: Text, Optional.

## Relationships and Cardinality

- Customer 1:N Order.
- Customer 1:N CustomerReview.
- Seller 1:N ProductListing.
- Seller 1:N OrderLine.
- Order 1:N OrderLine.
- ProductListing 1:N OrderLine.
- OrderLine 1:0..1 Fulfillment.
- OrderLine 1:0..1 CustomerReview.
- Seller 1:N Dispute.
- Order 1:N Dispute.
- Seller 1:N CommissionRule (seller-specific rules).
- Seller 1:N Payout.
- Payout 1:N PayoutLine.
- OrderLine 1:N PayoutLine.
- Any tracked entity 1:N StateEvent.

A global CommissionRule has no seller_id.

OrderLine records connect orders to product listings.
This represents the order-to-product relationship.

Fulfillment is created separately for each order line,
allowing one customer order to contain products from
multiple sellers.

StateEvent maintains an audit trail of status changes.
