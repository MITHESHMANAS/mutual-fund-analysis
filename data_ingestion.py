import pandas as pd
import os

DATA_PATH = "data/raw"

csv_files = [
    f for f in os.listdir(DATA_PATH)
    if f.endswith(".csv")
]

for file in csv_files:

    path = os.path.join(DATA_PATH, file)

    print("="*50)
    print("FILE:", file)

    df = pd.read_csv(path)

    print("Shape:")
    print(df.shape)

    print("\nColumns:")
    print(df.columns)

    print("\nHead:")
    print(df.head())