# tap-quickbooks

`tap-quickbooks` is a Singer tap for QuickBooks, built with the [Meltano Singer SDK](https://sdk.meltano.com).

Built with the [Meltano Singer SDK](https://sdk.meltano.com) for Singer Taps.

## Capabilities

- `catalog`
- `state`
- `discover`
- `about`
- `stream-maps`
- `schema-flattening`
- `batch`

## Installation

Install from GitHub:

```bash
pipx install git+https://github.com/Matatika/tap-quickbooks.git
```

Or using uv:

```bash
uv tool install git+https://github.com/Matatika/tap-quickbooks.git
```

## Configuration

### Accepted Config Options

| Setting | Required | Default | Description |
|:--------|:--------:|:-------:|:------------|
| oauth_credentials.client_id | True | None | QuickBooks OAuth2 client ID |
| oauth_credentials.client_secret | True | None | QuickBooks OAuth2 client secret |
| oauth_credentials.refresh_token | True | None | QuickBooks OAuth2 refresh token |
| realm_id | True | None | QuickBooks company/realm ID |
| start_date | True | None | The earliest record date to sync (RFC3339 format) |
| user_agent | False | None | Custom User-Agent header to send with each request |
| sandbox | False | False | Whether to use the QuickBooks sandbox environment |
| include_inactive | False | False | Whether to include inactive records for entities with an `Active` field, which QuickBooks omits by default. See [Deleted and inactive records](#deleted-and-inactive-records) |
| capture_deletes | False | False | Whether to capture records deleted in QuickBooks, using the Change Data Capture (CDC) endpoint. See [Deleted and inactive records](#deleted-and-inactive-records) |
| stream_maps | False | None | Config object for stream maps capability |
| stream_map_config | False | None | User-defined config values to be used within map expressions |
| flattening_enabled | False | None | 'True' to enable schema flattening and automatically expand nested properties |
| flattening_max_depth | False | None | The max depth to flatten schemas |
| batch_config | False | None | Configuration for batch message capabilities |

A full list of supported settings and capabilities for this tap is available by running:

```bash
tap-quickbooks --about
```

### Configure using environment variables

This Singer tap will automatically import any environment variables within the working directory's
`.env` if the `--config=ENV` is provided, such that config values will be considered if a matching
environment variable is set either in the terminal context or in the `.env` file.

Example `.env` file:

```bash
TAP_QUICKBOOKS_CLIENT_ID=your_client_id
TAP_QUICKBOOKS_CLIENT_SECRET=your_client_secret
TAP_QUICKBOOKS_REFRESH_TOKEN=your_refresh_token
TAP_QUICKBOOKS_REALM_ID=your_realm_id
TAP_QUICKBOOKS_START_DATE=2020-01-01T00:00:00Z
TAP_QUICKBOOKS_SANDBOX=false
```

### QuickBooks OAuth Setup

To use this tap, you'll need to:

1. **Create a QuickBooks App**
   - Go to the [QuickBooks Developer Portal](https://developer.intuit.com/)
   - Create a new app and note your Client ID and Client Secret
   - Configure redirect URI for OAuth

2. **Obtain OAuth Credentials**
   - Complete the OAuth 2.0 authorization flow to obtain a refresh token
   - Follow the [QuickBooks OAuth 2.0 Guide](https://developer.intuit.com/app/developer/qbo/docs/develop/authentication-and-authorization/oauth-2.0)

3. **Get your Realm ID**
   - The Realm ID (Company ID) is available in your QuickBooks Company Settings
   - Or it can be obtained from the OAuth callback URL after authorization

### Source Authentication and Authorization

This tap uses OAuth 2.0 for authentication with QuickBooks. The authenticator will automatically refresh access tokens using the provided refresh token.

## Usage

You can easily run `tap-quickbooks` by itself or in a pipeline using [Meltano](https://meltano.com/).

### Executing the Tap Directly

```bash
tap-quickbooks --version
tap-quickbooks --help
tap-quickbooks --config CONFIG --discover > ./catalog.json
```

### Example Configuration

Create a `config.json` file:

```json
{
  "oauth_credentials": {
    "client_id": "your_client_id",
    "client_secret": "your_client_secret",
    "refresh_token": "your_refresh_token"
  },
  "realm_id": "your_realm_id",
  "start_date": "2020-01-01T00:00:00Z",
  "sandbox": false
}
```

Then run the tap:

```bash
# Discover available streams
tap-quickbooks --config config.json --discover > catalog.json

# Run a sync
tap-quickbooks --config config.json --catalog catalog.json
```

## Supported Streams

This tap extracts data from the following QuickBooks streams:

### Incremental Replication (25 streams)

These streams support incremental replication using `MetaData.LastUpdatedTime`:

- **Account** - Chart of accounts
- **Bill** - Vendor bills
- **BillPayment** - Vendor payments
- **Budget** - Budget planning
- **Class** - Cost allocation categories
- **CompanyCurrency** - Multi-currency support
- **CreditMemo** - Customer credits
- **Customer** - Customer master data
- **CustomerType** - Customer classifications
- **Department** - Organizational divisions
- **Employee** - Staff records
- **Estimate** - Sales proposals
- **Invoice** - Sales invoices
- **Item** - Product/service inventory
- **JournalEntry** - Accounting entries
- **Payment** - Customer payments
- **PaymentMethod** - Payment type definitions
- **Purchase** - Purchase transactions
- **PurchaseOrder** - Procurement orders
- **SalesReceipt** - Point-of-sale transactions
- **Term** - Payment terms
- **TimeActivity** - Employee time tracking
- **Transfer** - Account transfers
- **Vendor** - Vendor master data
- **VendorCredit** - Vendor credits

### Full Table Replication (4 streams)

These streams use full table replication:

- **CompanyInfo** - Business details and settings
- **Preferences** - System settings
- **TaxCode** - Tax code groupings
- **TaxRate** - Tax rate definitions

## Developer Resources

Follow these instructions to contribute to this project.

### Initialize your Development Environment

Prerequisites:

- Python 3.10+
- [uv](https://docs.astral.sh/uv/)

```bash
# Clone the repository
git clone https://github.com/Matatika/tap-quickbooks.git
cd tap-quickbooks

# Install dependencies
uv sync
```

### Create and Run Tests

Run the test suite:

```bash
uv run pytest
```

Run with verbose output:

```bash
uv run pytest -v
```

You can also test the `tap-quickbooks` CLI interface directly:

```bash
uv run tap-quickbooks --help
uv run tap-quickbooks --discover
```

### Testing with [Meltano](https://www.meltano.com)

_**Note:** This tap will work in any Singer environment and does not require Meltano.
Examples here are for convenience and to streamline end-to-end orchestration scenarios._

Install Meltano and run an EL pipeline:

```bash
# Install meltano
uv tool install meltano

# Initialize meltano within this directory
meltano install

# Test invocation
meltano invoke tap-quickbooks --version

# Run a test EL pipeline
meltano run tap-quickbooks target-jsonl
```

### SDK Dev Guide

See the [dev guide](https://sdk.meltano.com/en/latest/dev_guide.html) for more instructions on how to use the SDK to
develop your own taps and targets.

## Features

### Authentication

- OAuth 2.0 with automatic token refresh
- Support for both production and sandbox environments
- Secure credential handling

### Replication

- Incremental replication using `MetaData.LastUpdatedTime`
- Full table replication for configuration streams
- State management for resumable syncs
- Proper primary key handling
- Optional inclusion of inactive records for entities with an `Active` field (`include_inactive`)
- Optional capture of deleted records via Change Data Capture (`capture_deletes`)

### Deleted and inactive records

QuickBooks handles removal in two ways:

- **Inactive records.** List entities (`Account`, `Customer`, `Vendor`, `Item`, `Employee`,
  `Class`, `Department`, `Term`, `PaymentMethod`, `TaxCode`, `TaxRate` and so on) are not
  deleted. Deleting one in the QuickBooks UI makes it inactive (`Active` is `false`). QuickBooks
  queries only return active records by default, so without `include_inactive` a record that
  becomes inactive stops being synced, and the destination keeps its last active version. With
  `include_inactive` set to `true`, the tap queries with `Active IN (true, false)` and emits
  inactive records like any other record, with `Active` set to `false`. If QuickBooks rejects
  the `Active` filter for an entity, the tap logs a warning and syncs that stream's active
  records only.

  Turning `include_inactive` on for an existing pipeline only emits records that become inactive
  (or otherwise change) after the stream's bookmark. Run a full refresh of the stream to also
  emit records that were already inactive.
- **Deleted records.** Transactions (`Invoice`, `Bill`, `Payment`, `JournalEntry` and so on) are
  removed, and queries no longer return them. With `capture_deletes` set to `true`, after each
  incremental stream is synced, the tap asks the
  [Change Data Capture (CDC) endpoint](https://developer.intuit.com/app/developer/qbo/docs/learn/explore-the-quickbooks-online-api/change-data-capture)
  for records of that entity deleted since the stream's last sync. Each one is emitted with only
  `Id`, `MetaData` and `_sdc_deleted_at` set, and `_sdc_deleted_at` is set to the time it was
  deleted. `_sdc_deleted_at` is added to the schema of incremental streams when the setting is
  on. Deleted records do not move the stream's bookmark.

  The tap saves the time it last requested deleted records in the stream state
  (`cdc_checkpoint`), and the next run requests deletes from that time. If the request fails,
  the tap logs a warning, the run carries on, and the same deletes are requested again on the
  next run.

#### Applying deletes in the destination

Deleted records only carry `Id` and `MetaData`, so how they land depends on the target:

- **Targets that delete rows with `_sdc_deleted_at` set**, such as the pipelinewise-based
  `target-postgres` with `hard_delete: true`, remove deleted records from the destination. This
  is the recommended setup.
- **Most Meltano SDK targets** (for example the MeltanoLabs `target-postgres`) do not delete rows
  on `_sdc_deleted_at`: their `hard_delete` setting only applies to `ACTIVATE_VERSION` messages.
  They upsert the deleted record like any other record, which **overwrites the existing row's
  other columns with null**. With `add_record_metadata: true`, the row is kept with
  `_sdc_deleted_at` set, so it can be filtered out downstream, but its other values are lost.
  Without it, `_sdc_deleted_at` is dropped and the row is left with only `Id` and `MetaData`
  set, with nothing to show it was deleted.

Check how your target handles `_sdc_deleted_at` before turning `capture_deletes` on.

Consecutive runs request deletes with a few minutes of overlap, so the same deleted record can be
emitted twice. That is harmless for targets that upsert or delete by key, but an append-only
target gets a duplicate row. A record created and deleted between two runs is also emitted as a
deleted record, although the destination never had it, so a target that upserts it adds a row
with only `Id`, `MetaData` and `_sdc_deleted_at` set.

Voided transactions are not deleted: QuickBooks sets their amounts to zero, and they are emitted
as normal updates.

Limitations of `capture_deletes`:

- **30-day lookback.** QuickBooks only keeps 30 days of changes. If deleted records were last
  requested more than 30 days ago (for example because the pipeline was paused), the tap warns
  and only captures deletes from the last 30 days. Sync at least every 30 days, or run a full
  refresh of the stream to remove older deletes.
- **1,000 changes per sync.** CDC returns at most 1,000 changed records per entity, with no
  pagination, and the limit counts updates as well as deletes. If an entity has more changes than
  that since the last run, the tap warns that some deletes may be missing. Sync busy streams
  more often to stay under the limit, or run a full refresh of the stream to remove the missed
  deletes.
- **No deletes on the first sync.** Deleted records are only requested from the second sync of a
  stream on. Records deleted before the first sync were never extracted, so there is nothing to
  remove.
- **Full-table streams** (`CompanyInfo`, `Preferences`, `TaxCode`, `TaxRate`) do not use CDC.

### Pagination

- Custom pagination for QuickBooks offset-based API
- Automatic handling of large result sets
- Configurable page size (default: 100 records)

### Data Transformation

- Automatic flattening of nested `MetaData` fields
- Proper type conversion for numeric and datetime fields
- Schema validation for all streams

### SDK Features

- Stream maps for custom transformations
- Schema flattening support
- Batch message support
- Structured logging

## API Rate Limits

QuickBooks has API rate limits. The tap handles pagination automatically but does not currently implement rate limit backoff. For high-volume syncs, consider:

- Reducing the page size
- Running syncs during off-peak hours
- Monitoring API usage in QuickBooks Developer Dashboard

## Troubleshooting

### OAuth Errors

If you receive OAuth errors, verify that:
- Your `client_id` and `client_secret` are correct
- Your `refresh_token` is still valid (they can expire)
- Your app has the necessary permissions in QuickBooks
- The `realm_id` matches your QuickBooks company

### No Records Returned

If streams return no records:
- Verify the `start_date` is not too recent
- Check that your QuickBooks company has data for the requested streams
- Ensure the stream is selected in your catalog

### Schema Validation Errors

If you encounter schema validation errors:
- The QuickBooks API may have added new fields
- Report the issue with the stream name and field details

## Roadmap

Potential future enhancements:

- [ ] Report streams (BalanceSheet, CashFlow, ProfitAndLoss, etc.)
- [x] Deleted records tracking
- [ ] Attachable stream with file downloads
- [ ] Query timeout retry logic with date chunking
- [ ] Rate limit backoff handling
- [ ] Custom field mapping support

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Credits

This tap was created using the [Meltano Singer SDK](https://sdk.meltano.com) and is based on the original
[tap-quickbooks](https://github.com/hotgluexyz/tap-quickbooks) implementation by hotglue.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Support

For issues and questions:
- Open an issue on [GitHub](https://github.com/Matatika/tap-quickbooks/issues)
- Consult the [Meltano SDK documentation](https://sdk.meltano.com)
- Check the [QuickBooks API documentation](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/most-commonly-used/account)
