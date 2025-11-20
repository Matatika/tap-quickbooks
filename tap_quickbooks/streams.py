"""Stream type classes for tap-quickbooks."""

from __future__ import annotations

from tap_quickbooks.client import QuickBooksStream


class AccountsStream(QuickBooksStream):
    """Accounts stream."""

    name = "Account"
    path = "/query"
    primary_keys = ("Id",)
    replication_key = "MetaData.LastUpdatedTime"


class BillsStream(QuickBooksStream):
    """Bills stream."""

    name = "Bill"
    path = "/query"
    primary_keys = ("Id",)
    replication_key = "MetaData.LastUpdatedTime"


class BillPaymentsStream(QuickBooksStream):
    """BillPayments stream."""

    name = "BillPayment"
    path = "/query"
    primary_keys = ("Id",)
    replication_key = "MetaData.LastUpdatedTime"


class BudgetsStream(QuickBooksStream):
    """Budgets stream."""

    name = "Budget"
    path = "/query"
    primary_keys = ("Id",)
    replication_key = "MetaData.LastUpdatedTime"


class ClassesStream(QuickBooksStream):
    """Classes stream."""

    name = "Class"
    path = "/query"
    primary_keys = ("Id",)
    replication_key = "MetaData.LastUpdatedTime"


class CompanyCurrencyStream(QuickBooksStream):
    """CompanyCurrency stream."""

    name = "CompanyCurrency"
    path = "/query"
    primary_keys = ("Id",)
    replication_key = "MetaData.LastUpdatedTime"


class CompanyInfoStream(QuickBooksStream):
    """CompanyInfo stream."""

    name = "CompanyInfo"
    path = "/query"
    primary_keys = ("Id",)
    replication_key = None  # Full table replication


class CreditMemosStream(QuickBooksStream):
    """CreditMemos stream."""

    name = "CreditMemo"
    path = "/query"
    primary_keys = ("Id",)
    replication_key = "MetaData.LastUpdatedTime"


class CustomersStream(QuickBooksStream):
    """Customers stream."""

    name = "Customer"
    path = "/query"
    primary_keys = ("Id",)
    replication_key = "MetaData.LastUpdatedTime"


class CustomerTypesStream(QuickBooksStream):
    """CustomerTypes stream."""

    name = "CustomerType"
    path = "/query"
    primary_keys = ("Id",)
    replication_key = "MetaData.LastUpdatedTime"


class DepartmentsStream(QuickBooksStream):
    """Departments stream."""

    name = "Department"
    path = "/query"
    primary_keys = ("Id",)
    replication_key = "MetaData.LastUpdatedTime"


class EmployeesStream(QuickBooksStream):
    """Employees stream."""

    name = "Employee"
    path = "/query"
    primary_keys = ("Id",)
    replication_key = "MetaData.LastUpdatedTime"


class EstimatesStream(QuickBooksStream):
    """Estimates stream."""

    name = "Estimate"
    path = "/query"
    primary_keys = ("Id",)
    replication_key = "MetaData.LastUpdatedTime"


class InvoicesStream(QuickBooksStream):
    """Invoices stream."""

    name = "Invoice"
    path = "/query"
    primary_keys = ("Id",)
    replication_key = "MetaData.LastUpdatedTime"


class ItemsStream(QuickBooksStream):
    """Items stream."""

    name = "Item"
    path = "/query"
    primary_keys = ("Id",)
    replication_key = "MetaData.LastUpdatedTime"


class JournalEntriesStream(QuickBooksStream):
    """JournalEntries stream."""

    name = "JournalEntry"
    path = "/query"
    primary_keys = ("Id",)
    replication_key = "MetaData.LastUpdatedTime"


class PaymentsStream(QuickBooksStream):
    """Payments stream."""

    name = "Payment"
    path = "/query"
    primary_keys = ("Id",)
    replication_key = "MetaData.LastUpdatedTime"


class PaymentMethodsStream(QuickBooksStream):
    """PaymentMethods stream."""

    name = "PaymentMethod"
    path = "/query"
    primary_keys = ("Id",)
    replication_key = "MetaData.LastUpdatedTime"


class PreferencesStream(QuickBooksStream):
    """Preferences stream."""

    name = "Preferences"
    path = "/query"
    primary_keys = ("Id",)
    replication_key = None  # Full table replication


class PurchasesStream(QuickBooksStream):
    """Purchases stream."""

    name = "Purchase"
    path = "/query"
    primary_keys = ("Id",)
    replication_key = "MetaData.LastUpdatedTime"


class PurchaseOrdersStream(QuickBooksStream):
    """PurchaseOrders stream."""

    name = "PurchaseOrder"
    path = "/query"
    primary_keys = ("Id",)
    replication_key = "MetaData.LastUpdatedTime"


class SalesReceiptsStream(QuickBooksStream):
    """SalesReceipts stream."""

    name = "SalesReceipt"
    path = "/query"
    primary_keys = ("Id",)
    replication_key = "MetaData.LastUpdatedTime"


class TaxCodesStream(QuickBooksStream):
    """TaxCodes stream."""

    name = "TaxCode"
    path = "/query"
    primary_keys = ("Id",)
    replication_key = None  # Full table replication per original tap


class TaxRatesStream(QuickBooksStream):
    """TaxRates stream."""

    name = "TaxRate"
    path = "/query"
    primary_keys = ("Id",)
    replication_key = None  # Full table replication per original tap


class TermsStream(QuickBooksStream):
    """Terms stream."""

    name = "Term"
    path = "/query"
    primary_keys = ("Id",)
    replication_key = "MetaData.LastUpdatedTime"


class TimeActivitiesStream(QuickBooksStream):
    """TimeActivities stream."""

    name = "TimeActivity"
    path = "/query"
    primary_keys = ("Id",)
    replication_key = "MetaData.LastUpdatedTime"


class TransfersStream(QuickBooksStream):
    """Transfers stream."""

    name = "Transfer"
    path = "/query"
    primary_keys = ("Id",)
    replication_key = "MetaData.LastUpdatedTime"


class VendorsStream(QuickBooksStream):
    """Vendors stream."""

    name = "Vendor"
    path = "/query"
    primary_keys = ("Id",)
    replication_key = "MetaData.LastUpdatedTime"


class VendorCreditsStream(QuickBooksStream):
    """VendorCredits stream."""

    name = "VendorCredit"
    path = "/query"
    primary_keys = ("Id",)
    replication_key = "MetaData.LastUpdatedTime"
