import json
import csv
import pandas as pd

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

def load_csv(path):
    data = []
    with open(path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
    return data

def load_excel(path):
    df = pd.read_excel(path)
    return df.to_dict(orient="records")
