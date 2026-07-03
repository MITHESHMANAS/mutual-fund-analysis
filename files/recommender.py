"""
recommender.py
---------------
Simple fund recommender.

Input:  risk appetite -> "Low" / "Moderate" / "High"
Output: top 3 funds by Sharpe ratio within the matching risk_grade bucket,
        printed as a formatted table.

Usage (command line):
    python recommender.py Moderate
    python recommender.py            # prompts interactively

Usage (as a library, e.g. from the notebook):
    from recommender import recommend_and_print
    recommend_and_print("High", scheme_perf_df)
"""
import sys
import pandas as pd
from pathlib import Path

import analytics_lib as al

RISK_APPETITE_MAP = al.RISK_APPETITE_MAP  # {"Low": [...], "Moderate": [...], "High": [...]}


def recommend_and_print(risk_appetite: str, scheme_perf: pd.DataFrame, top_n: int = 3) -> pd.DataFrame:
    """Compute the top-N recommendation table and pretty-print it."""
    table = al.recommend_funds(risk_appetite, scheme_perf, top_n=top_n)

    print(f"\n{'='*78}")
    print(f"  TOP {top_n} FUND RECOMMENDATIONS — Risk Appetite: {risk_appetite}")
    print(f"  (matching risk_grade: {', '.join(RISK_APPETITE_MAP[risk_appetite])})")
    print(f"{'='*78}")

    if table.empty:
        print("  No funds found matching this risk grade.")
        return table

    display_table = table.copy()
    display_table.insert(0, "Rank", range(1, len(display_table) + 1))
    display_table = display_table.rename(columns={
        "scheme_name": "Fund",
        "fund_house": "Fund House",
        "category": "Category",
        "risk_grade": "Risk Grade",
        "sharpe_ratio": "Sharpe",
        "sortino_ratio": "Sortino",
        "return_3yr_pct": "3Y Return %",
        "std_dev_ann_pct": "Std Dev % (Ann)",
        "expense_ratio_pct": "Expense %",
    })
    print(display_table.to_string(index=False))
    print()
    return table


def main():
    if len(sys.argv) > 1:
        risk_appetite = sys.argv[1].strip().capitalize()
    else:
        risk_appetite = input("Enter risk appetite (Low / Moderate / High): ").strip().capitalize()

    if risk_appetite not in RISK_APPETITE_MAP:
        print(f"Invalid risk appetite '{risk_appetite}'. Choose from: Low, Moderate, High")
        sys.exit(1)

    scheme_perf = al.load_scheme_performance()
    recommend_and_print(risk_appetite, scheme_perf)


if __name__ == "__main__":
    main()
