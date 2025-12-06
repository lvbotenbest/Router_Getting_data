
import pandas as pd
import os

file_path = 'train-00000-of-00001.parquet'

try:
    df = pd.read_parquet(file_path)
    print("Columns:", df.columns)
    print("First few rows:")
    print(df.head())
except Exception as e:
    print(f"Error reading parquet file: {e}")
