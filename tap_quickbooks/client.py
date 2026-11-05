"""REST client handling, including QuickBooksStream base class."""

from __future__ import annotations

import datetime as dt
import decimal
import sys
from functools import cached_property
from typing import TYPE_CHECKING, Any, ClassVar, TypeVar
from urllib.parse import urlparse

import requests
from singer_sdk import SchemaDirectory, StreamSchema
from singer_sdk.exceptions import FatalAPIError, RetriableAPIError
from singer_sdk.helpers.jsonpath import extract_jsonpath
from singer_sdk.pagination import BaseOffsetPaginator
from singer_sdk.streams import RESTStream, Stream

from tap_quickbooks import schemas
from tap_quickbooks.auth import ProxyQuickBooksAuthenticator, QuickBooksAuthenticator

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override

if TYPE_CHECKING:
    from collections.abc import Iterable

    from singer_sdk.helpers.types import Auth, Context, Record


SCHEMAS_DIR = SchemaDirectory(schemas)

_TStream = TypeVar("_TStream", bound=Stream)

# QuickBooks CDC only accepts a ``changedSince`` up to 30 days in the past
CDC_MAX_LOOKBACK = dt.timedelta(days=30)
# Margin so a request built right at the limit is not rejected by the time it arrives
CDC_LOOKBACK_MARGIN = dt.timedelta(minutes=5)
# QuickBooks CDC returns at most this many objects per entity, with no pagination
CDC_MAX_RESULTS = 1000

# Overlap between consecutive CDC windows, to allow for clock skew with QuickBooks
CDC_CHECKPOINT_MARGIN = dt.timedelta(minutes=5)

SDC_DELETED_AT = "_sdc_deleted_at"

# Stream state key holding the time from which the next CDC request should start
CDC_CHECKPOINT_KEY = "cdc_checkpoint"


class ActiveFilterRejectedError(FatalAPIError):
    """QuickBooks rejected a query that filters on ``Active``."""


class QuickBooksStreamSchema(StreamSchema):
    """Stream schema that adds ``_sdc_deleted_at`` when deletes are captured."""

    @override
    def get_stream_schema(
        self,
        stream: _TStream,
        stream_class: type[_TStream],
    ) -> dict[str, Any]:
        """Get the stream schema, adding ``_sdc_deleted_at`` if deletes are captured.

        Args:
            stream: The stream instance to get the schema from.
            stream_class: The stream class to get the schema from.

        Returns:
            A JSON schema dictionary.
        """
        schema = super().get_stream_schema(stream, stream_class)

        if not getattr(stream, "capture_deletes", False):
            return schema

        return {
            **schema,
            "properties": {
                **schema["properties"],
                SDC_DELETED_AT: {"type": ["null", "string"], "format": "date-time"},
            },
        }


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
            if (
                isinstance(query_response[key], list)
                and len(query_response[key]) >= self._page_size
            ):
                return True

        return False


class QuickBooksStream(RESTStream):
    """QuickBooks stream class."""

    # QuickBooks returns records under QueryResponse.<EntityName>
    # This will be overridden per stream
    records_jsonpath = "$.QueryResponse.*[*]"

    # Page size for QuickBooks API (max 1000)
    page_size = 100

    schema: ClassVar[StreamSchema] = QuickBooksStreamSchema(SCHEMAS_DIR)

    # Most QuickBooks objects use this replication key
    replication_key: str | None = "MetaData.LastUpdatedTime"

    # Set when QuickBooks rejects the ``Active`` filter for this stream's entity
    _active_filter_rejected = False

    @property
    def entity_name(self) -> str:
        """Get the QuickBooks API entity name (PascalCase).

        Override this in subclasses if different from the capitalized stream name.

        Returns:
            The entity name for QuickBooks API queries.
        """
        # Convert snake_case stream name to PascalCase
        # e.g., "bill_payment" -> "BillPayment"
        return "".join(word.capitalize() for word in self.name.split("_"))

    @property
    def capture_deletes(self) -> bool:
        """Whether deleted records are captured for this stream via the CDC endpoint.

        Only incremental streams capture deletes, since the CDC lookback is bounded
        by the stream bookmark.

        Returns:
            True if deleted records should be captured.
        """
        return bool(self.replication_key and self.config.get("capture_deletes", False))

    @property
    def include_inactive(self) -> bool:
        """Whether inactive records are queried for this stream.

        QuickBooks only returns active records for entities with an ``Active`` field
        unless the query filters on ``Active`` explicitly, and records "deleted" in the
        QuickBooks UI are made inactive rather than removed.

        Returns:
            True if the entity has an ``Active`` field and inactive records are included.
        """
        return bool(
            self.config.get("include_inactive", False)
            and "Active" in self.schema["properties"]
            and not self._active_filter_rejected
        )

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
        oauth_credentials: dict = self.config.get("oauth_credentials", {})
        client_id = oauth_credentials.get("client_id")
        client_secret = oauth_credentials.get("client_secret")

        if client_id and client_secret:
            return QuickBooksAuthenticator(
                client_id=client_id,
                client_secret=client_secret,
                refresh_token=oauth_credentials["refresh_token"],
                auth_endpoint="https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer",
                oauth_scopes="",  # QuickBooks doesn't use scopes
            )

        # proxy oauth
        refresh_proxy_url = oauth_credentials.get("refresh_proxy_url")

        if refresh_proxy_url:
            return ProxyQuickBooksAuthenticator(
                refresh_token=oauth_credentials["refresh_token"],
                proxy_auth=oauth_credentials.get("refresh_proxy_url_auth"),
                auth_endpoint=refresh_proxy_url,
            )

        msg = "Insufficient config to establish an authenticator. Must be one of {'oauth_credentials.client_id', 'oauth_credentials.client_secret', 'oauth_credentials.refresh_token'} or {'oauth_credentials.refresh_proxy_url', 'oauth_credentials.refresh_token'}."
        raise ValueError(msg)

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

        # Include inactive records, which QuickBooks omits by default
        if self.include_inactive:
            query_parts.append("Active IN (true, false)")

        # Add replication key filter for incremental sync
        start_date = self.get_starting_timestamp(context)
        if start_date:
            query_parts.append(f"{self.replication_key} >= '{start_date.isoformat()}'")

        # Build the WHERE clause
        where_clause = " AND ".join(query_parts) if query_parts else ""

        # Build the full query using the QuickBooks entity name (PascalCase)
        query = f"SELECT * FROM {self.entity_name}"  # noqa: S608
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
    def validate_response(self, response: requests.Response) -> None:
        """Validate a response, flagging a query rejected because of the ``Active`` filter.

        Args:
            response: The HTTP ``requests.Response`` object.

        Raises:
            ActiveFilterRejectedError: If a query that filters on ``Active`` is rejected.
        """
        if (
            response.status_code == requests.codes.bad_request
            and self.include_inactive
            and urlparse(str(response.request.url)).path.endswith(self.path or "/query")
        ):
            msg = f"QuickBooks rejected the query with the Active filter: {response.text}"
            raise ActiveFilterRejectedError(msg)

        super().validate_response(response)

    @override
    def get_records(self, context: Context | None) -> Iterable[dict[str, Any]]:
        """Return records, followed by deleted records if deletes are captured.

        Args:
            context: The stream context.

        Yields:
            Each record from the source.
        """
        # read before any records are emitted, so they reflect the last run
        state = self.get_context_state(context)
        changed_since = self.get_cdc_changed_since(context)
        # every deletion from here on is captured by this run or the next one
        checkpoint = dt.datetime.now(dt.timezone.utc) - CDC_CHECKPOINT_MARGIN

        yield from self._get_query_records(context)

        if not self.capture_deletes:
            return

        if changed_since is None:
            # first sync: records deleted before now were never extracted
            self.logger.info(
                "No CDC checkpoint for stream '%s', skipping deleted records", self.name
            )
            state[CDC_CHECKPOINT_KEY] = checkpoint.isoformat()
            return

        try:
            deleted = list(self.get_deleted_records(context, changed_since=changed_since))
        except (FatalAPIError, RetriableAPIError, requests.exceptions.RequestException) as e:
            # keep the previous checkpoint, so the next run requests the same deletes again
            self.logger.warning(
                "Could not get deleted records for stream '%s' since %s, they will be "
                "requested again on the next run: %s",
                self.name,
                changed_since.isoformat(),
                e,
            )
            return

        yield from deleted
        state[CDC_CHECKPOINT_KEY] = checkpoint.isoformat()

    def _get_query_records(self, context: Context | None) -> Iterable[dict[str, Any]]:
        """Return records from the query endpoint.

        Falls back to querying active records only if QuickBooks rejects the ``Active``
        filter for this entity.

        Args:
            context: The stream context.

        Yields:
            Each record from the query endpoint.

        Raises:
            ActiveFilterRejectedError: If the filter is rejected after records were emitted.
        """
        emitted = False
        try:
            for record in super().get_records(context):
                emitted = True
                yield record
        except ActiveFilterRejectedError as e:
            if emitted:
                raise

            self.logger.warning(
                "QuickBooks does not support filtering '%s' on Active, so inactive records "
                "cannot be included for stream '%s': %s",
                self.entity_name,
                self.name,
                e,
            )
            self._active_filter_rejected = True
            yield from super().get_records(context)

    def get_cdc_changed_since(self, context: Context | None) -> dt.datetime | None:
        """Get the point in time to request deleted records from.

        This is the checkpoint saved by the last run that requested deleted records or,
        for a stream synced before deletes were captured, its bookmark.

        Args:
            context: The stream context.

        Returns:
            The point in time to request deleted records from, or ``None`` if the stream
            has not been synced yet.
        """
        state = self.get_context_state(context)

        if checkpoint := state.get(CDC_CHECKPOINT_KEY):
            return dt.datetime.fromisoformat(checkpoint)

        if state.get("replication_key_value"):
            return self.get_starting_timestamp(context)

        return None

    @override
    def _increment_stream_state(
        self,
        latest_record: Record,
        *,
        context: Context | None = None,
    ) -> None:
        """Update the stream bookmark from a record, unless it is a deleted record.

        Deleted records are requested after the query has finished, so their deletion
        time says nothing about which updates the query has extracted. Advancing the
        bookmark with it would skip records updated in between.

        Args:
            latest_record: The record to update the bookmark from.
            context: The stream context.
        """
        if latest_record.get(SDC_DELETED_AT):
            return

        super()._increment_stream_state(latest_record, context=context)

    def get_deleted_records(
        self,
        context: Context | None,
        changed_since: dt.datetime,
    ) -> Iterable[dict[str, Any]]:
        """Get records deleted since a point in time from the CDC endpoint.

        Args:
            context: The stream context.
            changed_since: Point in time to get deleted records from.

        Yields:
            Each deleted record, with ``_sdc_deleted_at`` set.
        """
        earliest = dt.datetime.now(dt.timezone.utc) - CDC_MAX_LOOKBACK
        earliest += CDC_LOOKBACK_MARGIN

        if changed_since < earliest:
            self.logger.warning(
                "Deleted records for stream '%s' were last requested at %s, which is "
                "older than the %s-day CDC lookback limit: records deleted before %s "
                "cannot be captured. Run a full refresh of this stream to remove them.",
                self.name,
                changed_since.isoformat(),
                CDC_MAX_LOOKBACK.days,
                earliest.isoformat(),
            )
            changed_since = earliest

        prepared_request = self.build_prepared_request(
            method="GET",
            url=f"{self.url_base}/cdc",
            params={
                "entities": self.entity_name,
                "changedSince": changed_since.isoformat(),
                "minorversion": "65",
            },
            headers=self.http_headers,
        )
        response = self.request_decorator(self._request)(prepared_request, context)

        changed = list(self.parse_cdc_response(response))

        if len(changed) >= CDC_MAX_RESULTS:
            self.logger.warning(
                "CDC returned the maximum of %s changed records (updates and deletes) "
                "for stream '%s' since %s: some deleted records may be missing. Sync "
                "more often to keep the number of changes between runs below this "
                "limit, or run a full refresh of this stream to remove them.",
                CDC_MAX_RESULTS,
                self.name,
                changed_since.isoformat(),
            )

        deleted = [r for r in changed if r.get("status") == "Deleted"]
        self.logger.info(
            "Found %s deleted record(s) for stream '%s' since %s",
            len(deleted),
            self.name,
            changed_since.isoformat(),
        )

        for record in deleted:
            metadata = record.get("MetaData") or {}
            yield {
                "Id": record["Id"],
                "MetaData": metadata,
                SDC_DELETED_AT: metadata.get("LastUpdatedTime"),
            }

    def parse_cdc_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse changed records for this stream's entity from a CDC response.

        Args:
            response: The HTTP ``requests.Response`` object.

        Yields:
            Each changed record (updated or deleted).
        """
        for cdc_response in response.json().get("CDCResponse", []):
            for query_response in cdc_response.get("QueryResponse", []):
                yield from query_response.get(self.entity_name, [])

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
