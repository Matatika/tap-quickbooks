"""Stream type classes for tap-quickbooks."""

from __future__ import annotations

from tap_quickbooks.client import QuickBooksStream


class AccountsStream(QuickBooksStream):
    """Accounts stream."""

    name = "account"
    path = "/query"
    primary_keys = ("Id",)
    replication_key = "MetaData.LastUpdatedTime"


class BillsStream(QuickBooksStream):
    """Bills stream."""

    name = "bill"
    path = "/query"
    primary_keys = ("Id",)
    replication_key = "MetaData.LastUpdatedTime"


class BillPaymentsStream(QuickBooksStream):
    """BillPayments stream."""

    name = "bill_payment"
    path = "/query"
    primary_keys = ("Id",)
    replication_key = "MetaData.LastUpdatedTime"


class BudgetsStream(QuickBooksStream):
    """Budgets stream."""

    name = "budget"
    path = "/query"
    primary_keys = ("Id",)
    replication_key = "MetaData.LastUpdatedTime"


class ClassesStream(QuickBooksStream):
    """Classes stream."""

    name = "class"
    path = "/query"
    primary_keys = ("Id",)
    replication_key = "MetaData.LastUpdatedTime"


class CompanyCurrencyStream(QuickBooksStream):
    """CompanyCurrency stream."""

    name = "company_currency"
    path = "/query"
    primary_keys = ("Id",)
    replication_key = "MetaData.LastUpdatedTime"


class CompanyInfoStream(QuickBooksStream):
    """CompanyInfo stream."""

    name = "company_info"
    path = "/query"
    primary_keys = ("Id",)
    replication_key = None  # Full table replication


class CreditMemosStream(QuickBooksStream):
    """CreditMemos stream."""

    name = "credit_memo"
    path = "/query"
    primary_keys = ("Id",)
    replication_key = "MetaData.LastUpdatedTime"


class CustomersStream(QuickBooksStream):
    """Customers stream."""

    name = "customer"
    path = "/query"
    primary_keys = ("Id",)
    replication_key = "MetaData.LastUpdatedTime"


class CustomerTypesStream(QuickBooksStream):
    """CustomerTypes stream."""

    name = "customer_type"
    path = "/query"
    primary_keys = ("Id",)
    replication_key = "MetaData.LastUpdatedTime"


class DepartmentsStream(QuickBooksStream):
    """Departments stream."""

    name = "department"
    path = "/query"
    primary_keys = ("Id",)
    replication_key = "MetaData.LastUpdatedTime"


class EmployeesStream(QuickBooksStream):
    """Employees stream."""

    name = "employee"
    path = "/query"
    primary_keys = ("Id",)
    replication_key = "MetaData.LastUpdatedTime"


class EstimatesStream(QuickBooksStream):
    """Estimates stream."""

    name = "estimate"
    path = "/query"
    primary_keys = ("Id",)
    replication_key = "MetaData.LastUpdatedTime"


class InvoicesStream(QuickBooksStream):
    """Invoices stream."""

    name = "invoice"
    path = "/query"
    primary_keys = ("Id",)
    replication_key = "MetaData.LastUpdatedTime"


class ItemsStream(QuickBooksStream):
    """Items stream."""

    name = "item"
    path = "/query"
    primary_keys = ("Id",)
    replication_key = "MetaData.LastUpdatedTime"


class JournalEntriesStream(QuickBooksStream):
    """JournalEntries stream."""

    name = "journal_entry"
    path = "/query"
    primary_keys = ("Id",)
    replication_key = "MetaData.LastUpdatedTime"


class PaymentsStream(QuickBooksStream):
    """Payments stream."""

    name = "payment"
    path = "/query"
    primary_keys = ("Id",)
    replication_key = "MetaData.LastUpdatedTime"


class PaymentMethodsStream(QuickBooksStream):
    """PaymentMethods stream."""

    name = "payment_method"
    path = "/query"
    primary_keys = ("Id",)
    replication_key = "MetaData.LastUpdatedTime"


class PreferencesStream(QuickBooksStream):
    """Preferences stream."""

    name = "preferences"
    path = "/query"
    primary_keys = ("Id",)
    replication_key = None  # Full table replication


class PurchasesStream(QuickBooksStream):
    """Purchases stream."""

    name = "purchase"
    path = "/query"
    primary_keys = ("Id",)
    replication_key = "MetaData.LastUpdatedTime"


class PurchaseOrdersStream(QuickBooksStream):
    """PurchaseOrders stream."""

    name = "purchase_order"
    path = "/query"
    primary_keys = ("Id",)
    replication_key = "MetaData.LastUpdatedTime"


class SalesReceiptsStream(QuickBooksStream):
    """SalesReceipts stream."""

    name = "sales_receipt"
    path = "/query"
    primary_keys = ("Id",)
    replication_key = "MetaData.LastUpdatedTime"


class TaxCodesStream(QuickBooksStream):
    """TaxCodes stream."""

    name = "tax_code"
    path = "/query"
    primary_keys = ("Id",)
    replication_key = None  # Full table replication per original tap


class TaxRatesStream(QuickBooksStream):
    """TaxRates stream."""

    name = "tax_rate"
    path = "/query"
    primary_keys = ("Id",)
    replication_key = None  # Full table replication per original tap


class TermsStream(QuickBooksStream):
    """Terms stream."""

    name = "term"
    path = "/query"
    primary_keys = ("Id",)
    replication_key = "MetaData.LastUpdatedTime"


class TimeActivitiesStream(QuickBooksStream):
    """TimeActivities stream."""

    name = "time_activity"
    path = "/query"
    primary_keys = ("Id",)
    replication_key = "MetaData.LastUpdatedTime"


class TransfersStream(QuickBooksStream):
    """Transfers stream."""

    name = "transfer"
    path = "/query"
    primary_keys = ("Id",)
    replication_key = "MetaData.LastUpdatedTime"


class VendorsStream(QuickBooksStream):
    """Vendors stream."""

    name = "vendor"
    path = "/query"
    primary_keys = ("Id",)
    replication_key = "MetaData.LastUpdatedTime"


class VendorCreditsStream(QuickBooksStream):
    """VendorCredits stream."""

    name = "vendor_credit"
    path = "/query"
    primary_keys = ("Id",)
    replication_key = "MetaData.LastUpdatedTime"
