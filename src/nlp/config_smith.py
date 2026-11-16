"""config_smith.py.

Author: Brandon Smith
Date: 2026-11

Purpose

  Store configuration values for my custom EVTL pipeline.
  This is a copy of config.py, changed to pull U.S. military
  (Department of Defense) contract data instead of practice posts.

Analytical Questions

- What API endpoint should be used as the data source?
- What HTTP request headers are required?
- What search filters should be sent to the API?
- Where should raw and processed data be stored?

What I changed from config.py:
- API URL (now USAspending.gov, the official federal spending website),
- the HTTP Request Headers (my app name in the user-agent header),
- added a REQUEST_BODY (the search filters USAspending needs),
- my own output file names (smith_ instead of case_).
"""

from pathlib import Path
from typing import Any

# ============================================================
# API CONFIGURATION
# ============================================================

# CHANGED: The URL now points to the USAspending.gov award search.
# This is where the government publishes what it spends money on.
API_URL: str = "https://api.usaspending.gov/api/v2/search/spending_by_award/"

# CHANGED: The user-agent now names my project.
# ADDED: "Content-Type" tells the API we are sending it JSON (our search filters).
HTTP_REQUEST_HEADERS: dict[str, str] = {
    "User-Agent": "nlp-04-dod-contracts-smith/1.0",
    "Accept": "application/json",
    "Content-Type": "application/json",
}

# ADDED: The search filters sent to the API.
# The example API returns everything when you visit the link.
# USAspending is too big for that, so we tell it exactly what we want.
REQUEST_BODY: dict[str, Any] = {
    "filters": {
        # A, B, C, D are the four types of contracts (no grants or loans).
        "award_type_codes": ["A", "B", "C", "D"],
        # Only contracts awarded by the Department of Defense.
        "agencies": [
            {"type": "awarding", "tier": "toptier", "name": "Department of Defense"}
        ],
        # Fiscal year 2025 (Oct 1, 2024 to Sep 30, 2025).
        "time_period": [{"start_date": "2024-10-01", "end_date": "2025-09-30"}],
    },
    # The columns we want back for each contract.
    "fields": [
        "Award ID",
        "Recipient Name",
        "Award Amount",
        "Description",
        "Awarding Sub Agency",
        "Start Date",
    ],
    # Get the 100 biggest contracts, largest dollar amount first.
    "limit": 100,
    "page": 1,
    "sort": "Award Amount",
    "order": "desc",
}

# ============================================================
# PATH CONFIGURATION
# ============================================================

# These folder paths are the same as the example.
ROOT_PATH: Path = Path.cwd()
DATA_PATH: Path = ROOT_PATH / "data"
RAW_PATH: Path = DATA_PATH / "raw"
PROCESSED_PATH: Path = DATA_PATH / "processed"

# CHANGED: Output file names now start with smith_ instead of case_.
RAW_JSON_PATH: Path = RAW_PATH / "smith_dod_contracts_raw.json"
PROCESSED_CSV_PATH: Path = PROCESSED_PATH / "smith_dod_contracts_processed.csv"
