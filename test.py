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
    "title": "Gender Violence againts Women by Age",
    "description": "Gender Violence againts Women by age groups",
    "db_name": "e_gender_violence",
    "vars": "vage-y18-29_any-perp_%+vage-y18-74_any-perp_%+vage-y30-44_any-perp_%+vage-y45-64_any-perp_%+vage-y65-74_any-perp_%",
    "chart_type": "hist",
    "category": "gender_violence",
    "vector_dim": "",
})

rows.append({
    "id": next_id+1,
    "title": "Reporting of Gender Violence againts Women",
    "description": "Reporting of Gender Violence againts Women by receiver of the information: a close person, Health or social service, Support service, Police or Any person or service",
    "db_name": "e_gender_violence",
    "vars": "vrp-clsper_any-perp_%+vrp-hlth-soc_any-perp_%+vrp-supp_any-perp_%+vrp-polc_any-perp_%+vrp-any_any-perp_%+vrp-hlth-soc-supp-polc_any-perp_%",
    "chart_type": "hist",
    "category": "gender_violence",
    "vector_dim": "",
})

rows.append({
    "id": next_id+2,
    "title": "Consequences of Gender Violence againts Women",
    "description": "Consequences of Gender Violence againts Women such as Physical injury, Psychological consequences or that their life was in danger after violence",
    "db_name": "e_gender_violence",
    "vars": "veff-inj_any-perp_%+veff-psy_any-perp_%+veff-inj-psy_any-perp_%+veff-life-dng_any-perp_%",
    "chart_type": "hist",
    "category": "gender_violence",
    "vector_dim": "",
})

rows.append({
    "id": next_id+3,
    "title": "Gender Violence againts Women by Education",
    "description": "Gender Violence againts Women by ISCED levels of education.",
    "db_name": "e_gender_violence",
    "vars": "veduc-ed0-2_any-perp_%+veduc-ed3-4_any-perp_%+veduc-ed5-8_any-perp_%",
    "chart_type": "hist",
    "category": "gender_violence",
    "vector_dim": "",
})

rows.append({
    "id": next_id+4,
    "title": "Gender Violence againts Women by Urbanization",
    "description": "Gender Violence againts Women by degree of urbanization (Cities, Towns or Rural areas) of the area of living",
    "db_name": "e_gender_violence",
    "vars": "vurb-deg1_any-perp_%+vurb-deg2_any-perp_%+vurb-deg3_any-perp_%",
    "chart_type": "hist",
    "category": "gender_violence",
    "vector_dim": "",
})

rows.append({
    "id": next_id+5,
    "title": "Gender Violence againts Women by Citizenship",
    "description": "Gender Violence againts Women by citizenship (EU, non eu and national)",
    "db_name": "e_gender_violence",
    "vars": "vbrth-eu-for_any-perp_%+vbrth-neu-for+vbrth-nat_any-perp_%",
    "chart_type": "hist",
    "category": "gender_violence",
    "vector_dim": "",
})



_any-perp_%

# ------ Connection -------- #
send_df(df, dest_table="charts", new_rows=rows, file_path=file_path, by_row=True, vectorization=True)
#send_df(df, dest_table="charts", file_path=file_path, by_row=False, vectorization=True)