"""
generate_synthetic_transactions.py
-----------------------------------
The original file `data/raw/08_investor_transactions.csv` referenced by
scripts/clean_transactions.py and scripts/inspect_transactions.py was NOT
present in the uploaded project zip (only 07 and 09 were included).

This script generates a SYNTHETIC investor-transactions dataset with the
same schema the project's own cleaning script expects, so that the
investor-cohort and SIP-continuity tasks can run end-to-end. It is
seeded (reproducible) and is clearly labeled as synthetic everywhere it
is used (filenames, notebook markdown, CSV itself is NOT a substitute
for real data).

Schema (matches scripts/clean_transactions.py expectations):
    investor_id, amfi_code, transaction_date, transaction_type,
    amount_inr, kyc_status
"""
import numpy as np
import pandas as pd
from pathlib import Path

rng = np.random.default_rng(42)

BASE = Path(__file__).parent
fund_master = pd.read_csv(BASE / "data/processed/01_fund_master_clean.csv")
amfi_codes = fund_master["amfi_code"].tolist()
n_funds = len(amfi_codes)

# fund "popularity" weights so some funds are favored (adds realism to
# "top fund preference per cohort")
fund_weights = rng.dirichlet(np.ones(n_funds) * 0.6)

N_INVESTORS = 1900
START_DATE = pd.Timestamp("2022-01-03")
END_DATE = pd.Timestamp("2026-05-29")
TOTAL_DAYS = (END_DATE - START_DATE).days

kyc_status_choices = ["Verified", "Pending", "Verified", "Verified"]  # mostly verified

records = []
investor_ids = [f"INV{100000+i}" for i in range(N_INVESTORS)]

for inv_id in investor_ids:
    # each investor's first-ever transaction date (cohort join date)
    join_offset = rng.integers(0, max(TOTAL_DAYS - 30, 1))
    join_date = START_DATE + pd.Timedelta(days=int(join_offset))

    # each investor prefers 1-2 funds (their "primary" holdings)
    n_pref_funds = rng.choice([1, 1, 2], p=[0.6, 0.0, 0.4]) if False else rng.integers(1, 3)
    pref_funds = rng.choice(amfi_codes, size=n_pref_funds, replace=False, p=fund_weights)

    kyc = rng.choice(kyc_status_choices)

    # Behavioral archetype per investor affects SIP regularity
    archetype = rng.choice(["disciplined", "irregular", "lapsed"], p=[0.55, 0.30, 0.15])
    if archetype == "disciplined":
        gap_mean, gap_std = 30, 4
    elif archetype == "irregular":
        gap_mean, gap_std = 45, 20
    else:  # lapsed -> stops SIPs after a while
        gap_mean, gap_std = 30, 5

    # ---- SIP transactions (monthly-ish recurring) ----
    n_sips = rng.integers(3, 40)
    sip_amount_base = int(rng.choice([500, 1000, 1500, 2000, 2500, 3000, 5000, 10000],
                                      p=[0.10, 0.20, 0.15, 0.20, 0.10, 0.10, 0.10, 0.05]))
    current_date = join_date
    sip_count = 0
    for k in range(n_sips):
        if archetype == "lapsed" and k > n_sips * 0.5:
            gap = rng.normal(gap_mean * 2.2, gap_std * 2)  # big gaps -> stops
        else:
            gap = rng.normal(gap_mean, gap_std)
        gap = max(int(gap), 5)
        current_date = current_date + pd.Timedelta(days=gap)
        if current_date > END_DATE:
            break
        fund = rng.choice(pref_funds)
        amt = max(sip_amount_base + int(rng.normal(0, sip_amount_base * 0.05)), 500)
        records.append((inv_id, int(fund), current_date, "SIP", amt, kyc))
        sip_count += 1

    # ---- Occasional Lumpsum transactions ----
    n_lump = rng.integers(0, 4)
    for _ in range(n_lump):
        offset = rng.integers(0, max((END_DATE - join_date).days, 1))
        t_date = join_date + pd.Timedelta(days=int(offset))
        if t_date > END_DATE:
            continue
        fund = rng.choice(amfi_codes, p=fund_weights)
        amt = int(rng.choice([5000, 10000, 25000, 50000, 100000],
                              p=[0.30, 0.30, 0.20, 0.15, 0.05]))
        records.append((inv_id, int(fund), t_date, "Lumpsum", amt, kyc))

    # ---- Occasional Redemption transactions ----
    n_redeem = rng.integers(0, 2)
    for _ in range(n_redeem):
        offset = rng.integers(60, max((END_DATE - join_date).days, 61))
        t_date = join_date + pd.Timedelta(days=int(offset))
        if t_date > END_DATE:
            continue
        fund = rng.choice(pref_funds)
        amt = int(rng.choice([2000, 5000, 10000, 20000]))
        records.append((inv_id, int(fund), t_date, "Redemption", amt, kyc))

df = pd.DataFrame(records, columns=[
    "investor_id", "amfi_code", "transaction_date", "transaction_type",
    "amount_inr", "kyc_status"
])
df = df.sort_values(["investor_id", "transaction_date"]).reset_index(drop=True)
df["transaction_date"] = pd.to_datetime(df["transaction_date"]).dt.strftime("%Y-%m-%d")

out_raw = BASE / "data/raw"
out_raw.mkdir(parents=True, exist_ok=True)
df.to_csv(out_raw / "08_investor_transactions_SYNTHETIC.csv", index=False)

print("SYNTHETIC investor transactions generated")
print("Shape:", df.shape)
print("Investors:", df["investor_id"].nunique())
print(df["transaction_type"].value_counts())
