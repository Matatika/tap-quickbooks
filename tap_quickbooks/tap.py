"""QuickBooks tap class."""

from __future__ import annotations

import sys

from singer_sdk import Tap
from singer_sdk import typing as th  # JSON schema typing helpers

from tap_quickbooks import streams

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override


class TapQuickBooks(Tap):
    """Singer tap for QuickBooks."""

    name = "tap-quickbooks"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "client_id",
            th.StringType(nullable=False),
            secret=True,
            title="Client ID",
            description="QuickBooks OAuth2 client ID",
        ),
        th.Property(
            "client_secret",
            th.StringType(nullable=False),
            secret=True,
            title="Client Secret",
            description="QuickBooks OAuth2 client secret",
        ),
        th.Property(
            "refresh_token",
            th.StringType(nullable=False),
            required=True,
            secret=True,
            title="Refresh Token",
            description="QuickBooks OAuth2 refresh token",
        ),
        th.Property(
            "realm_id",
            th.StringType(nullable=False),
            required=True,
            title="Realm ID",
            description="QuickBooks company/realm ID",
        ),
        th.Property(
            "start_date",
            th.DateTimeType(nullable=False),
            required=True,
            title="Start Date",
            description="The earliest record date to sync (RFC3339 format)",
        ),
        th.Property(
            "user_agent",
            th.StringType(nullable=True),
            description=(
                "A custom User-Agent header to send with each request. Default is "
                "'<tap_name>/<tap_version>'"
            ),
        ),
        th.Property(
            "sandbox",
            th.BooleanType(nullable=False),
            default=False,
            description="Whether to use the QuickBooks sandbox environment",
        ),
        th.Property(
            "refresh_proxy_url",
            th.StringType(nullable=False),
            description="Proxy URL to enable token refresh without a client ID/secret",
        ),
        th.Property(
            "refresh_proxy_url_auth",
            th.StringType(nullable=False),
            secret=True,
            description="Authorization for proxy URL.",
        ),
    ).to_dict()

    @override
    def discover_streams(self) -> list[streams.QuickBooksStream]:
        """Return a list of discovered streams.

        Returns:
            A list of discovered streams.
        """
        return [
            streams.AccountsStream(self),
            streams.BillsStream(self),
            streams.BillPaymentsStream(self),
            streams.BudgetsStream(self),
            streams.ClassesStream(self),
            streams.CompanyCurrencyStream(self),
            streams.CompanyInfoStream(self),
            streams.CreditMemosStream(self),
            streams.CustomersStream(self),
            streams.CustomerTypesStream(self),
            streams.DepartmentsStream(self),
            streams.EmployeesStream(self),
            streams.EstimatesStream(self),
            streams.InvoicesStream(self),
            streams.ItemsStream(self),
            streams.JournalEntriesStream(self),
            streams.PaymentsStream(self),
            streams.PaymentMethodsStream(self),
            streams.PreferencesStream(self),
            streams.PurchasesStream(self),
            streams.PurchaseOrdersStream(self),
            streams.SalesReceiptsStream(self),
            streams.TaxCodesStream(self),
            streams.TaxRatesStream(self),
            streams.TermsStream(self),
            streams.TimeActivitiesStream(self),
            streams.TransfersStream(self),
            streams.VendorsStream(self),
            streams.VendorCreditsStream(self),
        ]


if __name__ == "__main__":
    TapQuickBooks.cli()
