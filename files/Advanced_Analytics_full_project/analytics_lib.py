"""
analytics_lib.py
-----------------
Reusable analytics functions for the Mutual Fund Advanced Analytics project.
Used by Advanced_Analytics.ipynb and recommender.py.
"""
import numpy as np
import pandas as pd
from pathlib import Path

BASE = Path(__file__).parent
DATA = BASE / "data"


# ---------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------
def load_fund_master():
    return pd.read_csv(DATA / "processed/01_fund_master_clean.csv")


def load_scheme_performance():
    return pd.read_csv(DATA / "processed/scheme_performance_clean.csv")


def load_nav_history():
    nav = pd.read_csv(DATA / "processed/nav_history_clean.csv", parse_dates=["date"])
    return nav.sort_values(["amfi_code", "date"]).reset_index(drop=True)


def load_portfolio_holdings():
    return pd.read_csv(DATA / "processed/09_portfolio_holdings_clean.csv")


def load_transactions():
    """Loads the SYNTHETIC investor transactions dataset."""
    df = pd.read_csv(DATA / "raw/08_investor_transactions_SYNTHETIC.csv",
                      parse_dates=["transaction_date"])
    return df


def compute_daily_returns(nav: pd.DataFrame) -> pd.DataFrame:
    """Wide dataframe of daily returns, indexed by date, one column per amfi_code."""
    wide_nav = nav.pivot(index="date", columns="amfi_code", values="nav").sort_index()
    returns = wide_nav.pct_change().dropna(how="all")
    return returns


# ---------------------------------------------------------------------
# Task 1: Historical VaR / CVaR (95%)
# ---------------------------------------------------------------------
def compute_var_cvar(returns: pd.DataFrame, confidence: float = 0.95) -> pd.DataFrame:
    """
    Historical VaR(95%) = 5th percentile of the daily-return distribution.
    CVaR(95%) = mean of returns at/below the VaR threshold (Expected Shortfall).
    Returns a per-fund summary table (values as % of NAV, i.e. daily return units).
    """
    alpha = 1 - confidence
    rows = []
    for code in returns.columns:
        r = returns[code].dropna()
        if len(r) == 0:
            continue
        var_threshold = np.percentile(r, alpha * 100)
        cvar = r[r <= var_threshold].mean()
        rows.append({
            "amfi_code": code,
            "n_obs": len(r),
            "mean_daily_return_pct": r.mean() * 100,
            "std_daily_return_pct": r.std() * 100,
            "VaR_95_pct": var_threshold * 100,
            "CVaR_95_pct": cvar * 100,
        })
    out = pd.DataFrame(rows).sort_values("VaR_95_pct")  # most negative (riskiest) first
    return out.reset_index(drop=True)


# ---------------------------------------------------------------------
# Task 2: Rolling 90-day Sharpe ratio
# ---------------------------------------------------------------------
def compute_rolling_sharpe(returns: pd.DataFrame, window: int = 90,
                            risk_free_annual: float = 0.0) -> pd.DataFrame:
    """
    Rolling annualized Sharpe = rolling_mean(daily_return) / rolling_std(daily_return) * sqrt(252)
    A daily risk-free rate can optionally be subtracted from returns first.
    """
    rf_daily = risk_free_annual / 252
    excess = returns - rf_daily
    roll_mean = excess.rolling(window).mean()
    roll_std = excess.rolling(window).std()
    rolling_sharpe = (roll_mean / roll_std) * np.sqrt(252)
    return rolling_sharpe


# ---------------------------------------------------------------------
# Task 3: Investor cohort analysis
# ---------------------------------------------------------------------
def compute_investor_cohorts(txns: pd.DataFrame, fund_master: pd.DataFrame) -> pd.DataFrame:
    """
    Cohort = the calendar year of an investor's FIRST transaction.
    For each cohort computes: number of investors, avg SIP amount,
    total amount invested (SIP+Lumpsum), and the single most-preferred
    fund (by transaction count) within that cohort.
    """
    txns = txns.copy()
    first_txn = txns.groupby("investor_id")["transaction_date"].min().rename("cohort_join_date")
    txns = txns.merge(first_txn, on="investor_id")
    txns["cohort_year"] = txns["cohort_join_date"].dt.year

    fund_names = fund_master.set_index("amfi_code")["scheme_name"]

    sip = txns[txns["transaction_type"] == "SIP"]
    invest_types = txns[txns["transaction_type"].isin(["SIP", "Lumpsum"])]

    summary = []
    for year, grp in txns.groupby("cohort_year"):
        n_investors = grp["investor_id"].nunique()
        sip_grp = sip[sip["cohort_year"] == year]
        avg_sip_amount = sip_grp["amount_inr"].mean() if len(sip_grp) else np.nan
        total_invested = invest_types.loc[invest_types["cohort_year"] == year, "amount_inr"].sum()

        fund_counts = grp["amfi_code"].value_counts()
        top_fund_code = fund_counts.idxmax() if len(fund_counts) else None
        top_fund_name = fund_names.get(top_fund_code, "Unknown")

        summary.append({
            "cohort_year": int(year),
            "n_investors": n_investors,
            "avg_sip_amount_inr": round(avg_sip_amount, 2) if pd.notna(avg_sip_amount) else np.nan,
            "total_invested_inr": round(total_invested, 2),
            "top_fund_preference": top_fund_name,
            "top_fund_amfi_code": top_fund_code,
        })
    return pd.DataFrame(summary).sort_values("cohort_year").reset_index(drop=True)


# ---------------------------------------------------------------------
# Task 4: SIP continuity analysis
# ---------------------------------------------------------------------
def compute_sip_continuity(txns: pd.DataFrame, min_sips: int = 6,
                            at_risk_gap_days: float = 35) -> pd.DataFrame:
    """
    For investors with >= min_sips SIP transactions, computes the average
    gap (days) between consecutive SIP dates. Investors whose average gap
    exceeds at_risk_gap_days are flagged as "at-risk" (SIP discipline
    breaking down / lapsing).
    """
    sip = txns[txns["transaction_type"] == "SIP"].copy()
    sip = sip.sort_values(["investor_id", "transaction_date"])

    rows = []
    for inv_id, grp in sip.groupby("investor_id"):
        if len(grp) < min_sips:
            continue
        dates = grp["transaction_date"].sort_values()
        gaps = dates.diff().dropna().dt.days
        avg_gap = gaps.mean()
        max_gap = gaps.max()
        rows.append({
            "investor_id": inv_id,
            "n_sip_transactions": len(grp),
            "avg_gap_days": round(avg_gap, 1),
            "max_gap_days": int(max_gap),
            "at_risk": avg_gap > at_risk_gap_days,
        })
    out = pd.DataFrame(rows).sort_values("avg_gap_days", ascending=False).reset_index(drop=True)
    return out


# ---------------------------------------------------------------------
# Task 5: Fund recommender
# ---------------------------------------------------------------------
RISK_APPETITE_MAP = {
    "Low": ["Low"],
    "Moderate": ["Moderate", "Moderately High"],
    "High": ["High", "Very High"],
}


def recommend_funds(risk_appetite: str, scheme_performance: pd.DataFrame, top_n: int = 3) -> pd.DataFrame:
    """
    Simple content-based recommender: filters funds whose risk_grade matches
    the requested risk appetite bucket, then ranks by Sharpe ratio (desc).
    """
    if risk_appetite not in RISK_APPETITE_MAP:
        raise ValueError(f"risk_appetite must be one of {list(RISK_APPETITE_MAP)}")

    grades = RISK_APPETITE_MAP[risk_appetite]
    pool = scheme_performance[scheme_performance["risk_grade"].isin(grades)].copy()
    pool = pool.sort_values("sharpe_ratio", ascending=False).head(top_n)

    cols = ["scheme_name", "fund_house", "category", "risk_grade",
            "sharpe_ratio", "sortino_ratio", "return_3yr_pct", "std_dev_ann_pct",
            "expense_ratio_pct"]
    return pool[cols].reset_index(drop=True)


# ---------------------------------------------------------------------
# Task 6: Sector HHI concentration
# ---------------------------------------------------------------------
def compute_sector_hhi(holdings: pd.DataFrame, fund_master: pd.DataFrame) -> pd.DataFrame:
    """
    HHI = sum(weight_i^2) per fund, using sector-level weights (weights
    aggregated by sector within each fund's portfolio, then squared and
    summed). weight_pct is on a 0-100 scale, so HHI is scaled to the
    conventional 0-10,000 index range.
    """
    sector_weights = (
        holdings.groupby(["amfi_code", "sector"])["weight_pct"].sum().reset_index()
    )
    hhi = (
        sector_weights.assign(w2=lambda d: d["weight_pct"] ** 2)
        .groupby("amfi_code")["w2"].sum()
        .rename("HHI")
        .reset_index()
    )
    hhi["HHI"] = hhi["HHI"].round(1)

    def bucket(h):
        if h < 1500:
            return "Diversified"
        elif h < 2500:
            return "Moderately Concentrated"
        else:
            return "Highly Concentrated"

    hhi["concentration"] = hhi["HHI"].apply(bucket)

    name_cat = fund_master.set_index("amfi_code")[["scheme_name", "category"]]
    hhi = hhi.merge(name_cat, on="amfi_code", how="left")
    return hhi.sort_values("HHI", ascending=False).reset_index(drop=True)
