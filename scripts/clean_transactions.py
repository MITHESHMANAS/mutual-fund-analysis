import pandas as pd

df = pd.read_csv(
    "data/raw/08_investor_transactions.csv"
)

print("Original Shape:", df.shape)

# Date conversion
df["transaction_date"] = pd.to_datetime(
    df["transaction_date"]
)

# Standardize transaction type

df["transaction_type"] = (
    df["transaction_type"]
    .astype(str)
    .str.strip()
)

mapping = {
    "SIP": "SIP",
    "Sip": "SIP",
    "sip": "SIP",
    "Lumpsum": "Lumpsum",
    "lumpsum": "Lumpsum",
    "Redemption": "Redemption",
    "redemption": "Redemption"
}

df["transaction_type"] = (
    df["transaction_type"]
    .map(mapping)
)

# Amount validation

df = df[
    df["amount_inr"] > 0
]

# KYC validation

valid_kyc = [
    "Verified",
    "Pending"
]

df = df[
    df["kyc_status"].isin(valid_kyc)
]

# Remove duplicates

before = len(df)

df = df.drop_duplicates()

after = len(df)

print(
    "Duplicates removed:",
    before - after
)

print(
    "Final Shape:",
    df.shape
)

print(
    "\nTransaction Types:"
)

print(
    df["transaction_type"].value_counts()
)

print(
    "\nKYC Status:"
)

print(
    df["kyc_status"].value_counts()
)

df.to_csv(
    "data/processed/investor_transactions_clean.csv",
    index=False
)

print("\nDone ✅")