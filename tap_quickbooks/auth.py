"""QuickBooks Authentication."""

from __future__ import annotations

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
        client_id: str,
        client_secret: str,
        refresh_token: str,
        auth_endpoint: str,
        oauth_scopes: str,
    ) -> None:
        """Initialize the authenticator.

        Args:
            client_id: OAuth2 client ID.
            client_secret: OAuth2 client secret.
            refresh_token: OAuth2 refresh token.
            auth_endpoint: OAuth2 token endpoint URL.
            oauth_scopes: OAuth scopes (not used by QuickBooks).
        """
        super().__init__(
            client_id=client_id,
            client_secret=client_secret,
            auth_endpoint=auth_endpoint,
            oauth_scopes=oauth_scopes,
        )
        self._refresh_token = refresh_token

    @override
    @property
    def oauth_request_body(self) -> dict:
        """Define the OAuth request body for the QuickBooks API.

        Returns:
            A dict with the request body
        """
        return {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": self._refresh_token,
        }
