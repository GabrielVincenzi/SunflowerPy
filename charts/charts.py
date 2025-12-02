import pandas as pd
import os
from toolbi import send_df

# ------- Build the file if it does not exist or is empty
file_path = "charts/chartsData.csv"
columns = ["id", "title", "description", "db_name", "category", "chart_type", "vars", "vector_dim"]
if os.path.exists(file_path):
    try:
        df = pd.read_csv(file_path)
        # If it has no columns (completely empty), reset it
        if df.empty and len(df.columns) == 0:
            df = pd.DataFrame(columns=columns)
            df.to_csv(file_path, index=False)
    except pd.errors.EmptyDataError:
        df = pd.DataFrame(columns=columns)
        df.to_csv(file_path, index=False)
else:
    df = pd.DataFrame(columns=columns)
    df.to_csv(file_path, index=False)

# ------- Automatically determine the next id
if df.empty:
    next_id = 1
else:
    next_id = int(df["id"].max() + 1)


# ------- New plots to insert
rows =[]

rows.append({
    "id": next_id,
    "title": "Pie1",
    "description": "Description",
    "db_name": "demographic",
    "vars": "youngdep1+depratio1+medagepop+fmedagepop+mmedagepop",
    "chart_type": "pie",
    "category": "population",
    "vector_dim": "",
})

# ------ Connection -------- #
send_df(df, dest_table="charts", new_rows=rows, file_path=file_path, by_row=True, vectorization=True)
#send_charts(df, dest_table="charts", file_path=file_path, by_row=False, vectorization=True)