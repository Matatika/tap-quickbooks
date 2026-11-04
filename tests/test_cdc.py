"""Tests for capturing inactive and deleted records."""

from __future__ import annotations

import datetime as dt
import json
import re
from typing import Any
from urllib.parse import parse_qs, urlparse

import pytest
import responses

from tap_quickbooks.client import CDC_MAX_RESULTS, QuickBooksStream
from tap_quickbooks.tap import TapQuickBooks

BASE_CONFIG: dict[str, Any] = {
    "oauth_credentials": {
        "client_id": "test_client_id",
        "client_secret": "test_client_secret",
        "refresh_token": "test_refresh_token",
    },
    "realm_id": "123",
    "start_date": "2020-01-01T00:00:00Z",
    "sandbox": True,
}

QUERY_URL = re.compile(r"https://sandbox-quickbooks\.api\.intuit\.com/v3/company/123/query.*")
CDC_URL = re.compile(r"https://sandbox-quickbooks\.api\.intuit\.com/v3/company/123/cdc.*")
AUTH_ENDPOINT = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"


def _now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0)


def _iso(value: dt.datetime) -> str:
    return value.isoformat()


def _state(stream: str, bookmark: str) -> dict:
    return {
        "bookmarks": {
            stream: {
                "replication_key": "MetaData.LastUpdatedTime",
                "replication_key_value": bookmark,
            },
        },
    }


def _tap(
    *,
    capture_deletes: bool = True,
    include_inactive: bool = True,
    state: dict | None = None,
) -> TapQuickBooks:
    return TapQuickBooks(
        config={
            **BASE_CONFIG,
            "capture_deletes": capture_deletes,
            "include_inactive": include_inactive,
        },
        state=state,
    )


def _mock_token() -> None:
    responses.add(
        responses.POST,
        AUTH_ENDPOINT,
        json={"access_token": "token", "expires_in": 3600},
    )


def _mock_query(entity: str, records: list[dict]) -> None:
    responses.add(
        responses.GET,
        QUERY_URL,
        json={"QueryResponse": {entity: records}},
    )


def _mock_cdc(entity: str, records: list[dict]) -> None:
    responses.add(
        responses.GET,
        CDC_URL,
        json={"CDCResponse": [{"QueryResponse": [{entity: records}]}]},
    )


def _url(call: responses.Call) -> str:
    return str(call.request.url)


def _cdc_calls() -> list[responses.Call]:
    return [c for c in responses.calls if "/cdc" in _url(c)]


def _params(call: responses.Call) -> dict[str, str]:
    return {k: v[0] for k, v in parse_qs(urlparse(_url(call)).query).items()}


def _stream(tap: TapQuickBooks, name: str) -> QuickBooksStream:
    stream = tap.streams[name]
    assert isinstance(stream, QuickBooksStream)
    return stream


def _sync_messages(tap: TapQuickBooks, stream_name: str, capsys: pytest.CaptureFixture) -> list:
    tap.streams[stream_name].sync()
    return [json.loads(line) for line in capsys.readouterr().out.splitlines() if line]


# Schema


def test_schema_has_sdc_deleted_at_when_capturing_deletes() -> None:
    """Incremental streams get `_sdc_deleted_at` when deletes are captured."""
    tap = _tap()
    assert "_sdc_deleted_at" in tap.streams["invoice"].schema["properties"]


def test_schema_has_no_sdc_deleted_at_by_default() -> None:
    """The schema is unchanged when deletes are not captured."""
    tap = _tap(capture_deletes=False)
    assert "_sdc_deleted_at" not in tap.streams["invoice"].schema["properties"]


def test_schema_has_no_sdc_deleted_at_for_full_table_streams() -> None:
    """Full-table streams never get `_sdc_deleted_at`."""
    tap = _tap()
    assert "_sdc_deleted_at" not in tap.streams["tax_code"].schema["properties"]


# Inactive records


@pytest.mark.parametrize("stream_name", ["customer", "account", "tax_code"])
def test_query_includes_inactive_records(stream_name: str) -> None:
    """Entities with an `Active` field are queried for inactive records too."""
    stream = _stream(_tap(capture_deletes=False), stream_name)
    query = stream.get_url_params(None, None)["query"]
    assert "Active IN (true, false)" in query


@responses.activate
def test_query_combines_active_and_replication_key_filters(capsys: pytest.CaptureFixture) -> None:
    """The `Active` filter is combined with the replication key filter."""
    _mock_token()
    _mock_query("Customer", [])

    _sync_messages(_tap(capture_deletes=False), "customer", capsys)

    (query_call,) = [c for c in responses.calls if "/query" in _url(c)]
    assert _params(query_call)["query"].startswith(
        "SELECT * FROM Customer WHERE Active IN (true, false) AND MetaData.LastUpdatedTime >= "
    )


@pytest.mark.parametrize("stream_name", ["invoice", "company_info"])
def test_query_has_no_active_filter_for_entities_without_it(stream_name: str) -> None:
    """Entities without an `Active` field are not filtered on it."""
    stream = _stream(_tap(capture_deletes=False), stream_name)
    assert "Active" not in stream.get_url_params(None, None)["query"]


@pytest.mark.parametrize("stream_name", ["customer", "account", "tax_code"])
def test_query_has_no_active_filter_by_default(stream_name: str) -> None:
    """Inactive records are not queried unless `include_inactive` is set."""
    stream = _stream(_tap(capture_deletes=False, include_inactive=False), stream_name)
    assert "Active" not in stream.get_url_params(None, None)["query"]


# Deleted records


@responses.activate
def test_deleted_records_are_emitted_with_sdc_deleted_at(capsys: pytest.CaptureFixture) -> None:
    """Deleted records from CDC are emitted with `_sdc_deleted_at` set."""
    bookmark = _iso(_now() - dt.timedelta(days=1))
    deleted_at = _iso(_now() - dt.timedelta(hours=1))
    _mock_token()
    _mock_query(
        "Invoice",
        [{"Id": "1", "TotalAmt": 10, "MetaData": {"LastUpdatedTime": deleted_at}}],
    )
    _mock_cdc(
        "Invoice",
        [
            # updated record: already extracted by the query, so not emitted again
            {"Id": "1", "TotalAmt": 10, "MetaData": {"LastUpdatedTime": deleted_at}},
            # voided record: an update, not a delete
            {"Id": "3", "TotalAmt": 0, "Balance": 0, "MetaData": {"LastUpdatedTime": deleted_at}},
            {
                "Id": "2",
                "domain": "QBO",
                "status": "Deleted",
                "MetaData": {"LastUpdatedTime": deleted_at},
            },
        ],
    )

    messages = _sync_messages(_tap(state=_state("invoice", bookmark)), "invoice", capsys)
    records = [m["record"] for m in messages if m["type"] == "RECORD"]

    assert [r["Id"] for r in records] == ["1", "2"]
    assert records[0].get("_sdc_deleted_at") is None
    assert records[1]["_sdc_deleted_at"] == deleted_at
    assert records[1]["MetaData.LastUpdatedTime"] == deleted_at
    assert "status" not in records[1]

    (cdc_call,) = _cdc_calls()
    params = _params(cdc_call)
    assert params["entities"] == "Invoice"
    assert dt.datetime.fromisoformat(params["changedSince"]) == dt.datetime.fromisoformat(bookmark)


@responses.activate
def test_inactive_records_from_cdc_are_not_marked_deleted(capsys: pytest.CaptureFixture) -> None:
    """Inactive records come from the query and are not marked deleted."""
    bookmark = _iso(_now() - dt.timedelta(days=1))
    updated = _iso(_now() - dt.timedelta(hours=1))
    customer = {"Id": "58", "Active": False, "MetaData": {"LastUpdatedTime": updated}}
    _mock_token()
    _mock_query("Customer", [customer])
    _mock_cdc("Customer", [customer])

    messages = _sync_messages(_tap(state=_state("customer", bookmark)), "customer", capsys)
    records = [m["record"] for m in messages if m["type"] == "RECORD"]

    assert len(records) == 1
    assert records[0]["Active"] is False
    assert records[0].get("_sdc_deleted_at") is None


@responses.activate
def test_no_cdc_request_without_bookmark(capsys: pytest.CaptureFixture) -> None:
    """CDC is skipped on a first sync, when there is no bookmark."""
    _mock_token()
    _mock_query("Invoice", [])

    _sync_messages(_tap(), "invoice", capsys)

    assert _cdc_calls() == []


@responses.activate
def test_no_cdc_request_when_capture_deletes_disabled(capsys: pytest.CaptureFixture) -> None:
    """CDC is skipped when deletes are not captured."""
    bookmark = _iso(_now() - dt.timedelta(days=1))
    _mock_token()
    _mock_query("Invoice", [])

    _sync_messages(
        _tap(capture_deletes=False, state=_state("invoice", bookmark)),
        "invoice",
        capsys,
    )

    assert _cdc_calls() == []


@responses.activate
def test_cdc_lookback_is_clamped_to_30_days(
    capsys: pytest.CaptureFixture,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """A bookmark older than the CDC lookback limit is clamped, with a warning."""
    bookmark = _iso(_now() - dt.timedelta(days=90))
    _mock_token()
    _mock_query("Invoice", [])
    _mock_cdc("Invoice", [])

    _sync_messages(_tap(state=_state("invoice", bookmark)), "invoice", capsys)

    changed_since = dt.datetime.fromisoformat(_params(_cdc_calls()[0])["changedSince"])
    assert _now() - dt.timedelta(days=30) < changed_since
    assert changed_since < _now() - dt.timedelta(days=29)
    assert "older than the 30-day CDC lookback limit" in caplog.text


@responses.activate
def test_warns_when_cdc_result_limit_reached(
    capsys: pytest.CaptureFixture,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """A warning is logged when CDC returns its maximum number of records."""
    bookmark = _iso(_now() - dt.timedelta(days=1))
    updated = _iso(_now() - dt.timedelta(hours=1))
    _mock_token()
    _mock_query("Invoice", [])
    _mock_cdc(
        "Invoice",
        [{"Id": str(i), "MetaData": {"LastUpdatedTime": updated}} for i in range(CDC_MAX_RESULTS)],
    )

    _sync_messages(_tap(state=_state("invoice", bookmark)), "invoice", capsys)

    assert "some deleted records may be missing" in caplog.text
