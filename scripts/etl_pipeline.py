"""
etl_pipeline.py
================
Bluestock Mutual Fund Analytics — end-to-end ETL pipeline.

Consolidates: raw ingestion -> validation -> cleaning -> transformation
-> processed CSV output, for every dataset used downstream by the
notebooks, the SQLite database, and the dashboard.

Design goals (per project requirements):
  - No hard-coded file paths -> everything routed through pathlib.Path
  - Idempotent -> safe to re-run any number of times
  - Error handling -> a failure in one dataset does not crash the whole
    pipeline; failures are logged and summarized at the end
  - Weekday/holiday gaps in NAV handled by reindexing to the full
    business-day calendar and forward-filling (never silently drops
    non-trading days, never back-fills into the future)
  - Clean, readable, single-responsibility functions; runs with zero
    manual steps: `python scripts/etl_pipeline.py`

Usage:
    python scripts/etl_pipeline.py
    python scripts/etl_pipeline.py --data-dir /path/to/project/data
"""
from __future__ import annotations

import argparse
import logging
import sys
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

# --------------------------------------------------------------------------- 
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("etl")


@dataclass
class PipelineResult:
    """Tracks per-step success/failure so one bad dataset can't kill the run."""
    succeeded: list[str] = field(default_factory=list)
    failed: list[tuple[str, str]] = field(default_factory=list)

    def ok(self, step: str):
        self.succeeded.append(step)
        log.info(f"✅ {step}")

    def fail(self, step: str, err: Exception):
        self.failed.append((step, str(err)))
        log.error(f"❌ {step} -> {err}")

    def summary(self):
        log.info("=" * 60)
        log.info(f"ETL SUMMARY: {len(self.succeeded)} succeeded, {len(self.failed)} failed")
        for step, err in self.failed:
            log.info(f"   FAILED: {step} ({err})")
        log.info("=" * 60)


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
class Paths:
    def __init__(self, data_dir: Path):
        self.root = data_dir
        self.raw = data_dir / "raw"
        self.processed = data_dir / "processed"
        self.db = data_dir / "db"
        for p in (self.raw, self.processed, self.db):
            p.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Step: NAV history
# ---------------------------------------------------------------------------
def clean_nav_history(paths: Paths) -> pd.DataFrame:
    """
    Cleans raw NAV history:
      - parses dates, sorts by (amfi_code, date)
      - drops exact duplicate rows
      - reindexes EACH scheme to the full business-day (Mon-Fri) calendar
        spanning its own first->last observed date, then forward-fills NAV
        across weekends/holidays (never leaves gaps, never fills backward)
      - drops non-positive / invalid NAV values
    """
    src = paths.raw / "02_nav_history.csv"
    df = pd.read_csv(src)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(["amfi_code", "date"]).drop_duplicates()

    filled_frames = []
    for code, grp in df.groupby("amfi_code"):
        grp = grp.set_index("date").sort_index()
        full_range = pd.bdate_range(grp.index.min(), grp.index.max())  # business days only
        grp = grp.reindex(full_range)
        grp["nav"] = grp["nav"].ffill()
        grp["amfi_code"] = code
        grp.index.name = "date"
        filled_frames.append(grp.reset_index())

    out = pd.concat(filled_frames, ignore_index=True)
    out = out[out["nav"] > 0]
    out = out.dropna(subset=["nav"])
    out = out[["amfi_code", "date", "nav"]].sort_values(["amfi_code", "date"])

    out.to_csv(paths.processed / "nav_history_clean.csv", index=False)
    return out


# ---------------------------------------------------------------------------
# Step: Scheme performance
# ---------------------------------------------------------------------------
def clean_scheme_performance(paths: Paths) -> pd.DataFrame:
    """Coerces return columns to numeric, drops rows with clearly invalid
    (>|100%|) returns or an out-of-band expense ratio."""
    src = paths.raw / "07_scheme_performance.csv"
    df = pd.read_csv(src)

    return_cols = ["return_1yr_pct", "return_3yr_pct", "return_5yr_pct"]
    for col in return_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    n_before = len(df)
    anomalies = df[
        (df[return_cols].abs() > 100).any(axis=1)
    ]
    if len(anomalies):
        log.warning(f"scheme_performance: {len(anomalies)} rows with |return| > 100% dropped")

    df = df[~df.index.isin(anomalies.index)]
    df = df[(df["expense_ratio_pct"] >= 0.1) & (df["expense_ratio_pct"] <= 2.5)]
    log.info(f"scheme_performance: {n_before} -> {len(df)} rows after validation")

    df.to_csv(paths.processed / "scheme_performance_clean.csv", index=False)
    return df


# ---------------------------------------------------------------------------
# Step: Fund master + all "remaining" reference tables (dedupe only)
# ---------------------------------------------------------------------------
REMAINING_FILES = {
    "01_fund_master.csv": "01_fund_master_clean.csv",
    "03_aum_by_fund_house.csv": "03_aum_by_fund_house_clean.csv",
    "04_monthly_sip_inflows.csv": "04_monthly_sip_inflows_clean.csv",
    "05_category_inflows.csv": "05_category_inflows_clean.csv",
    "06_industry_folio_count.csv": "06_industry_folio_count_clean.csv",
    "09_portfolio_holdings.csv": "09_portfolio_holdings_clean.csv",
    "10_benchmark_indices.csv": "10_benchmark_indices_clean.csv",
}


def clean_remaining(paths: Paths) -> dict[str, pd.DataFrame]:
    outputs = {}
    for src_name, out_name in REMAINING_FILES.items():
        src = paths.raw / src_name
        if not src.exists():
            raise FileNotFoundError(src)
        df = pd.read_csv(src)
        before = len(df)
        df = df.drop_duplicates()
        if before != len(df):
            log.info(f"{src_name}: removed {before - len(df)} duplicate rows")
        df.to_csv(paths.processed / out_name, index=False)
        outputs[out_name] = df
    return outputs


# ---------------------------------------------------------------------------
# Step: Investor transactions
# ---------------------------------------------------------------------------
def clean_transactions(paths: Paths) -> pd.DataFrame:
    """
    Cleans the investor transactions feed. NOTE: the original
    `08_investor_transactions.csv` was not part of the source export;
    this step consumes the synthetic, clearly-labeled stand-in
    (`08_investor_transactions_SYNTHETIC.csv`) generated by
    generate_synthetic_transactions.py. Swap in the real file with the
    same schema and this function requires no changes.
    """
    src = paths.raw / "08_investor_transactions_SYNTHETIC.csv"
    if not src.exists():
        raise FileNotFoundError(
            f"{src} not found — run scripts/generate_synthetic_transactions.py first, "
            "or supply the real 08_investor_transactions.csv"
        )
    df = pd.read_csv(src)
    df["transaction_date"] = pd.to_datetime(df["transaction_date"])
    df = df.drop_duplicates()
    df = df[df["amount_inr"] > 0]
    df = df.dropna(subset=["investor_id", "amfi_code", "transaction_date", "transaction_type"])

    df.to_csv(paths.processed / "investor_transactions_clean.csv", index=False)
    return df


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------
STEPS = [
    ("nav_history", clean_nav_history),
    ("scheme_performance", clean_scheme_performance),
    ("reference_tables", clean_remaining),
    ("investor_transactions", clean_transactions),
]


def run_pipeline(data_dir: Path) -> PipelineResult:
    paths = Paths(data_dir)
    result = PipelineResult()
    log.info(f"Starting ETL pipeline. data_dir={data_dir}")

    for name, fn in STEPS:
        try:
            fn(paths)
            result.ok(name)
        except Exception as e:  # noqa: BLE001 - intentional: keep pipeline alive
            result.fail(name, e)

    result.summary()
    return result


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Bluestock MF ETL pipeline")
    default_data_dir = Path(__file__).resolve().parent.parent / "data"
    parser.add_argument(
        "--data-dir", type=Path, default=default_data_dir,
        help=f"Path to the project's data/ directory (default: {default_data_dir})",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    result = run_pipeline(args.data_dir)
    sys.exit(1 if result.failed else 0)


if __name__ == "__main__":
    main()
