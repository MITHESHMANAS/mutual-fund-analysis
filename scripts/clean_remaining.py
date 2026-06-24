import pandas as pd

files = [
    "01_fund_master.csv",
    "03_aum_by_fund_house.csv",
    "04_monthly_sip_inflows.csv",
    "05_category_inflows.csv",
    "06_industry_folio_count.csv",
    "09_portfolio_holdings.csv",
    "10_benchmark_indices.csv"
]

for file in files:
    df = pd.read_csv(f"data/raw/{file}")

    before = len(df)

    df = df.drop_duplicates()

    after = len(df)

    print(f"\n{file}")
    print("Duplicates Removed:", before - after)

    output = file.replace(".csv", "_clean.csv")

    df.to_csv(
        f"data/processed/{output}",
        index=False
    )

print("\nDone ✅")