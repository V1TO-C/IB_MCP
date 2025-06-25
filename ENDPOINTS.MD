# Portfolio API Endpoints

| Category  | Endpoint                                     | Description                                                                                                                    | Status          |
|-----------|----------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------|-----------------|
| Portfolio | `/portfolio/accounts`                        | Returns a list of accounts for viewing position and account information.                                                      | 🟢         |
| Portfolio | `/portfolio/subaccounts`                     | Returns up to 100 sub-accounts for viewing position and account information in tiered structures.                             | 🟢  |
| Portfolio | `/portfolio/subaccounts2`                    | Returns sub-accounts for large tiered account structures.                                                                      | 🟠   |
| Portfolio | `/portfolio/{accountId}/meta`                | Returns metadata (name, currency, etc.) for a specific account.                                                                | 🟠     |
| Portfolio | `/portfolio/{accountId}/allocation`          | Returns position allocation by asset class, industry, and category for a single account.                                       | 🟠       |
| Portfolio | `/portfolio/{accountId}/combo/positions`     | Returns combination positions (e.g., complex options) for a single account.                                                    | 🟠       |
| Portfolio | `/portfolio/allocation`                      | Returns allocation information for multiple accounts combined.                                                                 | 🟠   |
| Portfolio | `/portfolio/{accountId}/positions/{pageId}`  | Returns paginated positions for a specific account.                                                                            | 🟠  |
| Portfolio | `/portfolio/{acctId}/position/{conid}`       | Returns all positions for a given contract ID within a specific account.                                                       | 🟢    |
| Portfolio | `/portfolio/{accountId}/positions/invalidate`| Invalidates backend cache for the account's portfolio data.                                                                    | 🟠  |
| Portfolio | `/portfolio/{accountId}/summary`             | Returns a summary of account information and portfolio positions.                                                              | 🟢|
| Portfolio | `/portfolio/{accountId}/ledger`              | Returns the cash balance and ledger information for a specific account.                                                        | 🟠  |
| Portfolio | `/portfolio/positions/{conid}`               | Returns all positions for a contract ID across all accounts, along with contract info.                                         | 🟢   |


## Status categories

| Icon | Status           |
|------|------------------|
| 🟢   | Ready            |
| 🟡   | Work in Progress |
| 🔘   | Not started      |
| 🟠   | Not tested       |
