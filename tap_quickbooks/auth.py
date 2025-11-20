"""QuickBooks Authentication."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from singer_sdk.authenticators import OAuthAuthenticator, SingletonMeta

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override

if TYPE_CHECKING:
    from singer_sdk.streams import RESTStream


# The SingletonMeta metaclass makes your streams reuse the same authenticator instance.
# If this behaviour interferes with your use-case, you can remove the metaclass.
class QuickBooksAuthenticator(OAuthAuthenticator, metaclass=SingletonMeta):
    """Authenticator class for QuickBooks."""

    def __init__(
        self,
        stream: RESTStream,
        auth_endpoint: str | None = None,
        oauth_scopes: str | None = None,
    ) -> None:
        """Initialize the authenticator.

        Args:
            stream: The stream instance.
            auth_endpoint: The OAuth2 token endpoint.
            oauth_scopes: OAuth scopes (not used by QuickBooks).
        """
        super().__init__(stream=stream, auth_endpoint=auth_endpoint, oauth_scopes=oauth_scopes)
        # Store refresh_token from config during initialization
        self._refresh_token = stream.config.get("refresh_token")

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
