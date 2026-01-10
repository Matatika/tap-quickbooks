"""QuickBooks Authentication."""

from __future__ import annotations

import base64
import json
import sys

from singer_sdk.authenticators import OAuthAuthenticator, SingletonMeta

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override


# The SingletonMeta metaclass makes your streams reuse the same authenticator instance.
# If this behaviour interferes with your use-case, you can remove the metaclass.
class QuickBooksAuthenticator(OAuthAuthenticator, metaclass=SingletonMeta):
    """Authenticator class for QuickBooks."""

    def __init__(
        self,
        *args,
        refresh_token=None,
        **kwargs,
    ) -> None:
        """Initialize the authenticator.

        Args:
            refresh_token: OAuth2 refresh token.
        """
        super().__init__(*args, **kwargs)
        self._oauth_headers = self.oauth_request_headers
        self._refresh_token = refresh_token

    @property
    def oauth_request_headers(self) -> dict:
        """Return headers for OAuth token request.

        Uses Basic auth with base64 encoded client_id:client_secret.

        Returns:
            A dict with headers for the OAuth token request.
        """
        client_id = self.client_id
        client_secret = self.client_secret
        credentials = f"{client_id}:{client_secret}"
        encoded = base64.b64encode(credentials.encode()).decode()

        return {
            "Authorization": f"Basic {encoded}",
            "Content-Type": "application/x-www-form-urlencoded",
        }

    @override
    @property
    def oauth_request_body(self) -> dict:
        """Define the OAuth request body for the QuickBooks API.

        Returns:
            A dict with the request body
        """
        return {
            "grant_type": "refresh_token",
            "refresh_token": self._refresh_token,
        }


class ProxyQuickBooksAuthenticator(QuickBooksAuthenticator, metaclass=SingletonMeta):
    @override
    def __init__(self, refresh_token=None, proxy_auth=None, **kwargs):
        self._proxy_auth = proxy_auth

        super().__init__(refresh_token=refresh_token, **kwargs)

    @override
    @property
    def oauth_request_headers(self):
        headers = {"Content-Type": "application/json"}

        if self._proxy_auth:
            headers["Authorization"] = self._proxy_auth

        return headers

    @override
    @property
    def oauth_request_body(self):
        return json.dumps(super().oauth_request_body)
