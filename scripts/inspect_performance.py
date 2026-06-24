import pandas as pd

df = pd.read_csv(
    "data/raw/07_scheme_performance.csv"
)

print("Shape:", df.shape)

print("\nExpense Ratio Stats:")
print(df["expense_ratio_pct"].describe())

print("\nReturn 1Y Stats:")
print(df["return_1yr_pct"].describe())

print("\nReturn 3Y Stats:")
print(df["return_3yr_pct"].describe())

print("\nReturn 5Y Stats:")
print(df["return_5yr_pct"].describe())

print("\nMissing Values:")
print(df.isnull().sum())