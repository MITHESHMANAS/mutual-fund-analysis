import pandas as pd

# Load
df = pd.read_csv("data/raw/02_nav_history.csv")

print("Original Shape:", df.shape)

# Convert date
df["date"] = pd.to_datetime(df["date"])

# Sort
df = df.sort_values(
    ["amfi_code", "date"]
)

# Remove duplicates
before = len(df)

df = df.drop_duplicates()

after = len(df)

print("Duplicates removed:", before - after)

# Forward fill NAV within each scheme
df["nav"] = (
    df.groupby("amfi_code")["nav"]
      .ffill()
)

# Remove invalid NAV values
df = df[df["nav"] > 0]

# Check missing NAV
print(
    "Missing NAV:",
    df["nav"].isna().sum()
)
print(df.describe())
# Save
df.to_csv(
    "data/processed/nav_history_clean.csv",
    index=False
)

print("Final Shape:", df.shape)

print("Done ✅")