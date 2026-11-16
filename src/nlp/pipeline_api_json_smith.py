"""pipeline_api_json_smith.py - Module 4 Custom Script.

Author: Brandon Smith
Date: 2026-11

Purpose

  Orchestrate my custom EVTL pipeline.
  Pull Department of Defense contract data from USAspending.gov,
  validate it, transform it, and load it into a CSV file.

What I changed from pipeline_api_json.py:
- Import from my _smith files instead of the example files.
- Pass REQUEST_BODY (the search filters) to the Extract stage.
- The original pipeline_api_json.py still runs unchanged.

Run from root project folder with:

  uv run python -m nlp.pipeline_api_json_smith
"""

# ============================================================
# Section 1. Setup and Imports
# ============================================================

import logging

from datafun_toolkit.logger import get_logger, log_header, log_path

# CHANGED: Import settings from config_smith instead of config.
from nlp.config_smith import (
    API_URL,
    DATA_PATH,
    HTTP_REQUEST_HEADERS,
    PROCESSED_CSV_PATH,
    PROCESSED_PATH,
    RAW_JSON_PATH,
    RAW_PATH,
    REQUEST_BODY,
    ROOT_PATH,
)

# CHANGED: Use my _smith stages. Load stays the same as the example.
from nlp.stage01_extract_smith import run_extract
from nlp.stage02_validate_smith import run_validate
from nlp.stage03_transform_smith import run_transform
from nlp.stage04_load import run_load

# ============================================================
# Section 2. Configure Logging
# ============================================================

LOG: logging.Logger = get_logger("CI", level="DEBUG")


# ============================================================
# Section 3. Define Main Pipeline Function
# ============================================================


def main() -> None:
    """Main function - this is where the execution begins."""
    log_header(LOG, "MODULE 4: CUSTOM EVTL PIPELINE (DoD CONTRACTS)")
    LOG.info("START PIPELINE")

    RAW_PATH.mkdir(parents=True, exist_ok=True)
    PROCESSED_PATH.mkdir(parents=True, exist_ok=True)

    log_path(LOG, "ROOT_PATH", ROOT_PATH)
    log_path(LOG, "DATA_PATH", DATA_PATH)
    log_path(LOG, "RAW_PATH", RAW_PATH)
    log_path(LOG, "PROCESSED_PATH", PROCESSED_PATH)

    # EXTRACT
    # CHANGED: Added request_body so the API gets our search filters.
    json_data = run_extract(
        source_api_url=API_URL,
        http_request_headers=HTTP_REQUEST_HEADERS,
        request_body=REQUEST_BODY,
        raw_json_path=RAW_JSON_PATH,
        LOG=LOG,
    )

    # VALIDATE
    validated_data = run_validate(
        json_data=json_data,
        LOG=LOG,
    )

    # TRANSFORM
    df = run_transform(
        json_data=validated_data,
        LOG=LOG,
    )

    # LOAD
    run_load(
        df=df,
        processed_csv_path=PROCESSED_CSV_PATH,
        LOG=LOG,
    )

    LOG.info("========================")
    LOG.info("Pipeline executed successfully!")
    LOG.info("========================")


# ============================================================
# Section 4. Run Main Function when This File is Executed
# ============================================================

if __name__ == "__main__":
    main()
