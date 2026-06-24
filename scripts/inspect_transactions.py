import pandas as pd

df = pd.read_csv("data/raw/08_investor_transactions.csv")

print("Shape:", df.shape)

print("\nTransaction Types:")
print(df["transaction_type"].value_counts(dropna=False))

print("\nKYC Status:")
print(df["kyc_status"].value_counts(dropna=False))

print("\nAmount Statistics:")
print(df["amount_inr"].describe())

print("\nDate Sample:")
print(df["transaction_date"].head())