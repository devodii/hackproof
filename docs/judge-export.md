# Judge Export Documentation

The `export-judges` command exports hackathon project submissions into structured tabular files (`.csv` and `.xlsx`) containing objective factual metrics for judges and evaluators. No subjective scores are generated.

## Output Files
- CSV format: comma-delimited, UTF-8 encoded with standard header row.
- XLSX format: Microsoft Excel OpenXML spreadsheet compatible with Google Sheets and LibreOffice.

## Documented Columns

| Column | Type | Description | Status / Source |
| :--- | :--- | :--- | :--- |
| `repo_url` | string | Canonical GitHub repository URL for the submission. | Populated from repository metadata. |
| `evidence_tier` | string | Evidence tier rating (`verified`, `likely`, or `possible`). | Populated from chain reconciliation. |
| `contracts` | integer | Total distinct Soroban smart contract IDs attributed to the project. | Populated from on-chain transactions. |
| `deploys` | integer | Total number of contract deployment transactions in the window. | Populated from on-chain deployments. |
| `first_deploy_time` | ISO 8601 string | UTC timestamp of the earliest contract deployment transaction. Empty if no contracts. | Populated from ledger timestamps. |
| `invocations` | integer / empty | Number of contract invocations observed on-chain. | Empty (pending invocation parser). |
| `failed_transactions` | integer | Number of failed Soroban transactions attributed to the project. | Populated from failed transaction indexer. |
| `has_tests` | boolean / empty | Whether automated test suites exist in the repository. | Empty (pending AST repository analysis). |
| `test_file_count` | integer / empty | Number of recognized test files in repository tree. | Empty (pending file-tree indexing). |
| `has_ci` | boolean / empty | Whether continuous integration configurations (GitHub Actions, etc.) exist. | Empty (pending CI workflow scanner). |
| `readme_length` | integer / empty | Character count of the project's root README file. | Empty (pending markdown parser). |
| `readme_sections` | integer / empty | Count or names of main headings inside the README. | Empty (pending markdown parser). |
| `has_demo_url` | boolean | Whether a valid working demo or live application URL is present. | Populated from repository homepage URL. |
| `has_video_url` | boolean / empty | Whether a video walkthrough or demo presentation is linked. | Empty (pending submission media crawler). |
| `ai_attribution_present` | boolean / empty | Whether AI generation disclosures/attributions are documented. | Empty (pending attribution parser). |
| `mainnet_status` | string / empty | Mainnet deployment status or mainnet contract identifier. | Empty (pending mainnet indexer). |
