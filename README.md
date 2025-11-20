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
| client_id | True | None | QuickBooks OAuth2 client ID |
| client_secret | True | None | QuickBooks OAuth2 client secret |
| refresh_token | True | None | QuickBooks OAuth2 refresh token |
| realm_id | True | None | QuickBooks company/realm ID |
| start_date | True | None | The earliest record date to sync (RFC3339 format) |
| user_agent | False | None | Custom User-Agent header to send with each request |
| sandbox | False | False | Whether to use the QuickBooks sandbox environment |
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
  "client_id": "your_client_id",
  "client_secret": "your_client_secret",
  "refresh_token": "your_refresh_token",
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
- [ ] Deleted records tracking
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
