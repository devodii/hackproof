# Local Development Quickstart

HackProof is configured for instant local development. A fresh clone can be launched with a working UI and pre-seeded anonymized testnet data in under 5 minutes without requiring GitHub tokens or testnet network sync.

## The Five Commands

1. **Clone the repository:**
   ```bash
   git clone https://github.com/devodii/hackproof.git
   ```

2. **Navigate into the project root:**
   ```bash
   cd hackproof
   ```

3. **Start the local Docker stack:**
   ```bash
   docker compose up -d
   ```
   *This automatically starts PostgreSQL, runs the one-shot `seed` container to populate 10 projects and 20 contracts from `data/sample/sample.sql`, starts the FastAPI backend on port 8000, and boots the Vite development server on port 5173.*

4. **Open the application in your browser:**
   ```
   http://localhost:5173
   ```

5. **Follow logs or stop the environment:**
   ```bash
   # Follow logs
   docker compose logs -f

   # Or shut down when finished
   docker compose down
   ```

---

## How It Works

- **Automated Seeding (`seed` service):**
  On initial startup, Docker executes `scripts/load_sample.py`. If the `projects` table is empty, it initializes the database schema and loads `data/sample/sample.sql`. If data already exists, the step is skipped automatically.
- **Privacy & Safety:**
  The sample dataset contains only anonymized testnet activity, mock Soroban contract addresses, and public GitHub repository identifiers. No private keys, email addresses, or secrets are present.

## Regenerating the Sample Dataset

If you have a populated development database with new testnet data and want to refresh the sample fixture:
```bash
uv run python scripts/dump_sample.py
```
This extracts the top 10 projects, 20 contracts, failure logs, and hourly timeline points into `data/sample/sample.sql`.
