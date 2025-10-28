import pandas as pd
import os

HISTORY_FOLDER = "history/"

def save_run(df, name):
    os.makedirs(HISTORY_FOLDER, exist_ok=True)
    file = f"{HISTORY_FOLDER}{name}.csv"
    df.to_csv(file, index=False)
    return file

def list_runs():
    os.makedirs(HISTORY_FOLDER, exist_ok=True)
    return [f for f in os.listdir(HISTORY_FOLDER) if f.endswith(".csv")]

def load_run(name):
    return pd.read_csv(f"{HISTORY_FOLDER}{name}")
