"""REST client handling, including QuickBooksStream base class."""

from __future__ import annotations

import decimal
import sys
from functools import cached_property
from typing import TYPE_CHECKING, Any, ClassVar
from urllib.parse import urlencode

from singer_sdk import SchemaDirectory, StreamSchema
from singer_sdk.helpers.jsonpath import extract_jsonpath
from singer_sdk.pagination import BaseOffsetPaginator
from singer_sdk.streams import RESTStream

from tap_quickbooks import schemas
from tap_quickbooks.auth import QuickBooksAuthenticator

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override

if TYPE_CHECKING:
    from collections.abc import Iterable

    import requests
    from singer_sdk.helpers.types import Auth, Context


SCHEMAS_DIR = SchemaDirectory(schemas)


class QuickBooksPaginator(BaseOffsetPaginator):
    """QuickBooks offset-based paginator."""

    def __init__(self, start_value: int = 1, page_size: int = 100) -> None:
        """Initialize paginator.

        Args:
            start_value: Starting offset (QuickBooks uses 1-based indexing).
            page_size: Number of records per page.
        """
        super().__init__(start_value, page_size)

    def has_more(self, response: requests.Response) -> bool:
        """Check if there are more pages.

        Args:
            response: HTTP response object.

        Returns:
            True if more pages exist.
        """
        data = response.json()
        query_response = data.get("QueryResponse", {})

        # Check if we got any records
        # The response keys vary by entity type, so we check all possible keys
        for key in query_response:
            if isinstance(query_response[key], list) and len(query_response[key]) >= self._page_size:
                return True

        return False


class QuickBooksStream(RESTStream):
    """QuickBooks stream class."""

    # QuickBooks returns records under QueryResponse.<EntityName>
    # This will be overridden per stream
    records_jsonpath = "$.QueryResponse.*[*]"

    # Page size for QuickBooks API (max 1000)
    page_size = 100

    schema: ClassVar[StreamSchema] = StreamSchema(SCHEMAS_DIR)

    # Most QuickBooks objects use this replication key
    replication_key = "MetaData.LastUpdatedTime"

    @override
    @property
    def url_base(self) -> str:
        """Return the API URL root, configurable via tap settings."""
        realm_id = self.config["realm_id"]

        if self.config.get("sandbox", False):
            base = "https://sandbox-quickbooks.api.intuit.com"
        else:
            base = "https://quickbooks.api.intuit.com"

        return f"{base}/v3/company/{realm_id}"

    @override
    @cached_property
    def authenticator(self) -> Auth:
        """Return a new authenticator object.

        Returns:
            An authenticator instance.
        """
        return QuickBooksAuthenticator(
            stream=self,
            auth_endpoint="https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer",
            oauth_scopes="",  # QuickBooks doesn't use scopes
        )

    @property
    @override
    def http_headers(self) -> dict:
        """Return the http headers needed.

        Returns:
            A dictionary of HTTP headers.
        """
        headers = {}
        if "user_agent" in self.config:
            headers["User-Agent"] = self.config.get("user_agent")

        headers["Accept"] = "application/json"
        headers["Content-Type"] = "application/json"

        return headers

    @override
    def get_new_paginator(self) -> BaseOffsetPaginator:
        """Create a new pagination helper instance.

        Returns:
            A pagination helper instance.
        """
        return QuickBooksPaginator(start_value=1, page_size=self.page_size)

    @override
    def get_url_params(
        self,
        context: Context | None,
        next_page_token: Any | None,
    ) -> dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization.

        Args:
            context: The stream context.
            next_page_token: The next page index or value.

        Returns:
            A dictionary of URL query parameters.
        """
        params: dict = {}

        # Build the SQL-like query for QuickBooks
        query_parts = []

        # Add replication key filter for incremental sync
        if self.replication_key:
            start_date = self.get_starting_replication_key_value(context)
            if start_date:
                query_parts.append(f"{self.replication_key} >= '{start_date}'")

        # Build the WHERE clause
        where_clause = " AND ".join(query_parts) if query_parts else ""

        # Build the full query
        query = f"SELECT * FROM {self.name}"
        if where_clause:
            query += f" WHERE {where_clause}"

        # Add ordering for incremental streams
        if self.replication_key:
            query += f" ORDERBY {self.replication_key}"

        # Add pagination
        if next_page_token:
            query += f" STARTPOSITION {next_page_token} MAXRESULTS {self.page_size}"
        else:
            query += f" MAXRESULTS {self.page_size}"

        params["query"] = query
        params["minorversion"] = "65"  # QuickBooks API minor version

        return params

    @override
    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result records.

        Args:
            response: The HTTP ``requests.Response`` object.

        Yields:
            Each record from the source.
        """
        yield from extract_jsonpath(
            self.records_jsonpath,
            input=response.json(parse_float=decimal.Decimal),
        )

    @override
    def post_process(
        self,
        row: dict,
        context: Context | None = None,
    ) -> dict | None:
        """As needed, append or transform raw data to match expected structure.

        Args:
            row: An individual record from the stream.
            context: The stream context.

        Returns:
            The updated record dictionary, or ``None`` to skip the record.
        """
        # Skip non-dict rows (e.g., pagination metadata)
        if not isinstance(row, dict):
            return None

        # Flatten nested MetaData fields for easier access
        if "MetaData" in row:
            metadata = row["MetaData"]
            if isinstance(metadata, dict):
                row["MetaData.LastUpdatedTime"] = metadata.get("LastUpdatedTime")
                row["MetaData.CreateTime"] = metadata.get("CreateTime")

        return row
