"""Tests standard tap features using the built-in SDK tests library."""

import datetime

from singer_sdk.testing import get_tap_test_class

from tap_quickbooks.tap import TapQuickBooks

SAMPLE_CONFIG = {
    "oauth_credentials": {
        "client_id": "test_client_id",
        "client_secret": "test_client_secret",
        "refresh_token": "test_refresh_token",
    },
    "realm_id": "test_realm_id",
    "start_date": datetime.datetime.now(datetime.timezone.utc).strftime(r"%Y-%m-%dT%H:%M:%SZ"),
    "sandbox": True,
}


# Run standard built-in tap tests from the SDK:
TestTapQuickBooks = get_tap_test_class(
    tap_class=TapQuickBooks,
    config=SAMPLE_CONFIG,
)
