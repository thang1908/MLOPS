from pathlib import Path

import pandas as pd


data = [
    {"name": "Alice", "age": 24},
    {"name": "Bob", "age": 28},
    {"name": "Charlie", "age": 31},
]

output_directory = Path("data")
output_directory.mkdir(exist_ok=True)

dataframe = pd.DataFrame(data)

output_path = output_directory / "sample_data.csv"
dataframe.to_csv(output_path, index=False)

print(f"Created {output_path} with {len(dataframe)} rows")
