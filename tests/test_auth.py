"""Behavioral tests for authentication."""

import datetime
import json
from typing import Any

import pytest
import responses

from tap_quickbooks.auth import ProxyQuickBooksAuthenticator, QuickBooksAuthenticator
from tap_quickbooks.client import QuickBooksStream
from tap_quickbooks.tap import TapQuickBooks

# Proxy OAuth configuration (nested settings)
PROXY_CONFIG: dict[str, Any] = {
    "oauth_credentials": {
        "refresh_proxy_url": "http://localhost:8080/api/tokens/oauth2-quickbooks/token",
        "refresh_proxy_url_auth": "Bearer proxy_test_token",
        "refresh_token": "test_refresh_token_1234",
    },
    "realm_id": "test_realm_id",
    "start_date": datetime.datetime.now(datetime.timezone.utc).strftime(r"%Y-%m-%dT%H:%M:%SZ"),
    "sandbox": True,
}

# Standard OAuth configuration (nested oauth_credentials)
STANDARD_CONFIG: dict[str, Any] = {
    "oauth_credentials": {
        "client_id": "test_client_id",
        "client_secret": "test_client_secret",
        "refresh_token": "test_refresh_token",
    },
    "realm_id": "test_realm_id",
    "start_date": datetime.datetime.now(datetime.timezone.utc).strftime(r"%Y-%m-%dT%H:%M:%SZ"),
    "sandbox": True,
}


@responses.activate
def test_proxy_oauth_uses_correct_authenticator():
    """Test that proxy config uses ProxyQuickBooksAuthenticator."""
    # Mock proxy endpoint
    responses.add(
        responses.POST,
        "http://localhost:8080/api/tokens/oauth2-quickbooks/token",
        json={"access_token": "test_token", "expires_in": 3600},
        status=200,
    )

    tap = TapQuickBooks(config=PROXY_CONFIG)
    streams = tap.discover_streams()
    stream = streams[0]
    assert isinstance(stream, QuickBooksStream)

    assert isinstance(
        stream.authenticator,
        ProxyQuickBooksAuthenticator,
    ), f"Expected ProxyQuickBooksAuthenticator, got {type(stream.authenticator).__name__}"


@responses.activate
def test_proxy_oauth_request_format():
    """Test that proxy OAuth makes correctly formatted HTTP requests."""
    # Mock proxy endpoint
    responses.add(
        responses.POST,
        "http://localhost:8080/api/tokens/oauth2-quickbooks/token",
        json={"access_token": "proxy_access_token", "expires_in": 3600},
        status=200,
    )

    tap = TapQuickBooks(config=PROXY_CONFIG)
    streams = tap.discover_streams()
    stream = streams[0]
    assert isinstance(stream, QuickBooksStream)

    # Trigger token refresh
    authenticator = stream.authenticator
    authenticator.update_access_token()

    # Verify request was made
    assert len(responses.calls) == 1

    request = responses.calls[0].request

    # Verify request
    assert request.url == "http://localhost:8080/api/tokens/oauth2-quickbooks/token"
    assert request.headers["authorization"] == "Bearer proxy_test_token"
    assert request.headers["Content-Type"] == "application/json"
    assert request.body is not None

    body = json.loads(request.body)
    assert body["refresh_token"] == "test_refresh_token_1234"
    assert body["grant_type"] == "refresh_token"

    # Verify token was set
    assert authenticator.access_token == "proxy_access_token"


@responses.activate
def test_standard_oauth_uses_correct_authenticator():
    """Test that standard config uses QuickBooksAuthenticator."""
    # Mock standard QuickBooks endpoint
    responses.add(
        responses.POST,
        "https://identity.quickbooks.com/connect/token",
        json={"access_token": "standard_token", "expires_in": 3600},
        status=200,
    )

    tap = TapQuickBooks(config=STANDARD_CONFIG)
    streams = tap.discover_streams()
    stream = streams[0]
    assert isinstance(stream, QuickBooksStream)
    assert isinstance(stream.authenticator, QuickBooksAuthenticator), (
        f"Expected QuickBooksAuthenticator, got {type(stream.authenticator).__name__}"
    )


def test_invalid_oauth_config_raises_validation_error():
    """Test that incomplete OAuth configuration raises ConfigValidationError during schema validation."""
    from singer_sdk.exceptions import ConfigValidationError

    # Config with oauth_credentials but missing required fields for both modes
    invalid_config = {
        "oauth_credentials": {
            "refresh_token": "test_token",
            # Missing client_id + client_secret for standard OAuth
            # Missing refresh_proxy_url for proxy OAuth
        },
        "realm_id": "test-realm-id",
        "start_date": datetime.datetime.now(datetime.timezone.utc).strftime(r"%Y-%m-%dT%H:%M:%SZ"),
    }

    # Schema validation should fail during tap initialization
    with pytest.raises(ConfigValidationError):
        TapQuickBooks(config=invalid_config)


def test_invalid_oauth_config_raises_value_error_when_validation_skipped():
    """Test that incomplete OAuth configuration raises ValueError when schema validation is skipped."""

    # Config with oauth_credentials but missing required fields for both modes
    invalid_config = {
        "oauth_credentials": {
            "refresh_token": "test_token",
            # Missing client_id + client_secret for standard OAuth
            # Missing refresh_proxy_url for proxy OAuth
        },
        "realm_id": "test-realm-id",
        "start_date": datetime.datetime.now(datetime.timezone.utc).strftime(r"%Y-%m-%dT%H:%M:%SZ"),
    }

    # Schema validation should fail during tap initialization
    with pytest.raises(ValueError):
        tap = TapQuickBooks(config=invalid_config, validate_config=False)
        tap.sync_all()