"""stage03_transform_smith.py.

Author: Brandon Smith
Date: 2026-11

Source: validated JSON object
Sink: Polars DataFrame

Purpose

  Transform validated JSON data into a structured format.

Analytical Questions

- Which fields are needed from the JSON data?
- How can records be normalized into tabular form?
- What derived fields would support analysis?

What I changed from stage03_transform.py:
- Pull contract fields instead of post fields.
- Derived fields:
    award_millions     - contract value in millions of dollars
    description_words  - number of words in the contract description
    work_type          - type of work, found by keywords in the description
- Log totals by type of work, by military branch, and the top 5 companies.
"""

# ============================================================
# Section 1. Setup and Imports
# ============================================================

import logging
from typing import Any

import polars as pl

# ADDED: Keywords used to label each contract's type of work.
# Checked top to bottom; the first match wins. No match = "Other".
# \b means "whole word only," so "ship" does not match "leadership".
WORK_TYPE_KEYWORDS: dict[str, str] = {
    "Aircraft": r"\b(aircraft|f-35|helicopters?|aviation|engines?)\b",
    "Ships & Submarines": r"\b(ships?|shipbuilding|submarines?|vessels?)\b",
    "Missiles & Munitions": r"\b(missiles?|munitions?|ammunition|rockets?)\b",
    "IT & Software": r"\b(software|cyber|network|cloud|data)\b",
    "Construction": r"\b(construction|facility|facilities|building)\b",
    "Support Services": r"\b(maintenance|logistics|support|services|repair|fuel)\b",
}

# ============================================================
# Section 2. Define Run Transform Function
# ============================================================


def run_transform(
    json_data: list[dict[str, Any]],
    LOG: logging.Logger,
) -> pl.DataFrame:
    """Transform JSON into a structured DataFrame.

    Args:
        json_data (list[dict[str, Any]]): Validated JSON data.
        LOG (logging.Logger): The logger instance.

    Returns:
        pl.DataFrame: The transformed dataset.
    """
    LOG.info("========================")
    LOG.info("STAGE 03: TRANSFORM starting...")
    LOG.info("========================")

    records: list[dict[str, Any]] = []

    # CHANGED: Pull contract fields instead of post fields.
    # .get() is used so a missing field becomes empty instead of crashing.
    for record in json_data:
        records.append(
            {
                "award_id": record.get("Award ID"),
                "company": record.get("Recipient Name"),
                "branch": record.get("Awarding Sub Agency"),
                "award_amount": record.get("Award Amount"),
                "start_date": record.get("Start Date"),
                "description": record.get("Description") or "",
            }
        )

    df: pl.DataFrame = pl.DataFrame(records)

    # ADDED: Build the work_type label from the keyword list above.
    description = pl.col("description").str.to_lowercase()
    work_type = pl.lit("Other")
    for label, pattern in reversed(WORK_TYPE_KEYWORDS.items()):
        work_type = (
            pl.when(description.str.contains(pattern))
            .then(pl.lit(label))
            .otherwise(work_type)
        )

    # Derived fields
    # CHANGED: New derived fields for contract data.
    df = df.with_columns(
        [
            (pl.col("award_amount") / 1_000_000).round(2).alias("award_millions"),
            pl.col("description").str.count_matches(r"\S+").alias("description_words"),
            work_type.alias("work_type"),
        ]
    )

    # ADDED: Quick summaries printed to the log.
    total_billions = df["award_millions"].sum() / 1000
    LOG.info(f"Total value: ${total_billions:,.1f} billion")

    by_work_type = (
        df.group_by("work_type")
        .agg(pl.len().alias("contracts"), pl.col("award_millions").sum().round(1))
        .sort("award_millions", descending=True)
    )
    LOG.info(f"Spending by type of work:\n{by_work_type}")

    by_branch = (
        df.group_by("branch")
        .agg(pl.col("award_millions").sum().round(1))
        .sort("award_millions", descending=True)
    )
    LOG.info(f"Spending by branch:\n{by_branch}")

    top_companies = (
        df.group_by("company")
        .agg(pl.col("award_millions").sum().round(1))
        .sort("award_millions", descending=True)
        .head(5)
    )
    LOG.info(f"Top 5 companies:\n{top_companies}")

    LOG.info("Transformation complete.")
    LOG.info(f"DataFrame preview:\n{df.head()}")
    LOG.info("Sink: Polars DataFrame created")

    # Return the transformed DataFrame for use in the next stage.
    return df
