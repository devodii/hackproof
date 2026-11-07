# Judge Export

`uv run hackproof export-judges` writes `judges.csv` and `judges.xlsx` with one row per submission and objective columns only. No subjective scores are included.

## Columns

| Column | Source / Meaning | Status |
| --- | --- | --- |
| `repo_url` | Public GitHub repository URL (`project.repo_url`) | Populated |
| `evidence_tier` | Attribution strength (`verified` or `likely`) | Populated |
| `contracts` | Count of Soroban contracts deployed inside the event window | Populated |
| `deploys` | Number of attributed contract deployment transactions in the window | Populated |
| `first_deploy_time` | Earliest `deployed_at` UTC timestamp across window contract deploys, empty when none | Populated |
| `invocations` | Contract invocation count during the event window | Empty (not indexed yet) |
| `failed_transactions` | Count of failed Soroban transactions by attributed accounts | Populated |
| `has_tests` | Whether the repository contains automated test files | Empty (not indexed yet) |
| `test_file_count` | Number of test files detected in the repository | Empty (not indexed yet) |
| `has_ci` | Whether the repository configures a CI workflow | Empty (not indexed yet) |
| `readme_length` | Character length of the repository README | Empty (not indexed yet) |
| `readme_sections` | Count of Markdown headings in the repository README | Empty (not indexed yet) |
| `has_demo_url` | `"true"` when the repository sets a homepage/demo URL, `"false"` otherwise | Populated |
| `has_video_url` | Whether the repository links a demo video | Empty (not indexed yet) |
| `ai_attribution_present` | Whether AI tool attribution is declared in commits or docs | Empty (not indexed yet) |
| `mainnet_status` | Whether the project has deployed on Stellar pubnet/mainnet | Empty (not indexed yet) |
