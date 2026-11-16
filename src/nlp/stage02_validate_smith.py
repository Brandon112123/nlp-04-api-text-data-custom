"""stage02_validate_smith.py.

Author: Brandon Smith
Date: 2026-11

Source: raw JSON object
Sink: validated JSON object

Purpose

  Inspect JSON structure and validate that the data is usable.

Analytical Questions

- What is the top-level structure of the JSON data?
- What keys are present in each record?
- What data types are associated with each field?
- Does the data meet expectations for transformation?

What I changed from stage02_validate.py:
- The example API returns a list of records.
  USAspending returns a dictionary, and the records are
  inside its "results" key. So we pull out "results" first.
- Added checks for the contract fields we need.
- Added a check that every Award Amount is a number.
"""

# ============================================================
# Section 1. Setup and Imports
# ============================================================

import logging
from typing import Any

# ADDED: The fields every contract record must have.
REQUIRED_KEYS: list[str] = [
    "Award ID",
    "Recipient Name",
    "Award Amount",
    "Description",
    "Awarding Sub Agency",
]

# ============================================================
# Section 2. Define Run Validate Function
# ============================================================


def run_validate(
    json_data: Any,
    LOG: logging.Logger,
) -> list[dict]:
    """Inspect and validate JSON structure.

    Args:
        json_data (Any): The raw JSON data from the Extract stage.
        LOG (logging.Logger): The logger instance.

    Returns:
        list[dict]: The validated contract records.
    """
    LOG.info("========================")
    LOG.info("STAGE 02: VALIDATE starting...")
    LOG.info("========================")

    # ============================================================
    # INSPECT JSON STRUCTURE
    # ============================================================

    LOG.info("JSON STRUCTURE INSPECTION:")

    # Log the type of the top-level JSON structure.
    # Use the built-in type() function to get the type
    # and built-in variable __name__ to log just the type name.
    LOG.info(f"Top-level type: {type(json_data).__name__}")

    # ADDED: USAspending returns a dictionary, not a list.
    # The contract records are stored under the "results" key.
    if not isinstance(json_data, dict):
        raise TypeError("Expected a dictionary with a 'results' key.")

    LOG.info(f"Top-level keys: {list(json_data.keys())}")
    records = json_data.get("results")

    if isinstance(records, list) and len(records) > 0:
        first_record = records[0]

        LOG.info(f"Keys in first record: {list(first_record.keys())}")

        LOG.info("Field types:")
        for key, value in first_record.items():
            LOG.info(f"{key}: {type(value).__name__}")

    # ============================================================
    # VALIDATE EXPECTATIONS
    # ============================================================

    if not isinstance(records, list):
        raise TypeError("Expected 'results' to be a list of records.")

    if len(records) == 0:
        raise ValueError("Expected at least one record.")

    if not all(isinstance(record, dict) for record in records):
        raise ValueError("Expected each record to be a dictionary.")

    # ADDED: Make sure the contract fields we need are there.
    missing = [key for key in REQUIRED_KEYS if key not in records[0]]
    if missing:
        raise ValueError(f"Missing expected fields: {missing}")

    # ADDED: Make sure every Award Amount is a number (so we can do math on it).
    if not all(isinstance(r.get("Award Amount"), (int, float)) for r in records):
        raise ValueError("Expected every Award Amount to be a number.")

    LOG.info(f"Records received: {len(records)}")
    LOG.info("Validation passed.")
    LOG.info("Sink: validated JSON object")

    # Return the validated contract records for use in the next stage.
    return records
