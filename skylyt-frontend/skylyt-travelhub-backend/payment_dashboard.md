Payment Management Flow
1. Payment Management Page
* Dashboard view of all payments across bookings
* Filters: by payment status, provider, date, amount range
* Payment detail view with provider metadata, booking reference, transaction ID
* Option to verify, refund, cancel or mark payments
* Display of failed or pending transactions
* Export option for financial reconciliation

2. Data Models
Payment Model (extended for management)
* Payment ID, booking reference, provider, method
* Amount, currency, payment status
* Provider transaction ID and metadata
* Linked booking details for context
* Created/updated timestamps
* Refund records (amount, date, reason)

3. Service Layer
PaymentService
* list_payments()
* get_payment_details()
* manual_verify_payment()
* refund_payment()
* update_payment_status()
* export_payments()
Responsibilities
* Centralize all payment queries
* Sync with provider APIs when verification needed
* Process refunds and status changes safely
* Provide export-ready reports for finance team
* Trigger booking updates when payment status changes

4. Payment Management Components
* Payment list table with provider icons and status badges
* Payment detail panel showing full metadata and booking link
* Refund form and status update dialog
* Filters for quick search by provider or status
* Export button for reports (CSV, XLSX)

5. Payment Context / Store
* Manage selected payment and details
* Store active filters and sort options
* Handle loading states, success/error feedback
* Support bulk actions (e.g., export selected payments)

6. Error Handling
* Retry mechanism for failed payment syncs
* Warnings before irreversible actions (refunds, status overrides)
* Clear error messages when provider API is unavailable
* Transaction audit logs for compliance
