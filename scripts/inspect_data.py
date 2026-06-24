import pandas as pd
import os

path = "data/raw"

for file in os.listdir(path):
    if file.endswith(".csv"):
        print("\n" + "="*60)
        print("FILE:", file)

        df = pd.read_csv(os.path.join(path, file))

        print("Shape:", df.shape)
        print("Columns:")
        print(df.columns.tolist())