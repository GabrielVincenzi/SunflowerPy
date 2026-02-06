import pandas as pd
from tools.toolbi import default_connection, create_table_sql
from tools.tooldb import clean_stat, update_json
from functools import reduce
from tools.tooleurostat import get_eurostat_dataset
import config

keys = config.KEYS
countries = config.COUNTRIES
start_year = config.START_YEAR
end_year = config.END_YEAR

# Mean hourly earnings by economic activity, sex, age
# For the following years (each 4 starting from 2002)
year_specs = {
    2002: "A.C-K+C-F+G-K.PPS..ERN..",
    2006: "A.C-K+C-F+G-K.GE10.PPS..ERN..",
    2010: "A.PPS.ERN.B-S_X_O+B-F+G-S_X_O.GE10...",
    2014: "A.PPS.ERN.B-S_X_O+B-F+G-S_X_O.GE10...",
    2018: "A..ERN.B-S_X_O+B-F+G-S_X_O..GE10.PPS.",
    2022: "A..ERN..GE10.B-S_X_O+B-F+G-S_X_O.PPS.",
}

results = []
for year in year_specs:
    filters = year_specs[year]
    if year == 2002:
        dataset_code = 'earn_ses_agt13'
    else:
        dataset_code = f'earn_ses{year % 100:02d}_13'

    df_raw = get_eurostat_dataset(
        dataset_code=dataset_code,
        filters=filters+countries
    )

    expand_map = {
        'Y30-49': ['Y30-39', 'Y40-49'],
        'Y_GE50': ['Y50-59', 'Y_GE60'],
    }

    rows = []
    for _, row in df_raw.iterrows():
        age_val = row.get('age')
        if pd.isna(age_val):
            rows.append(row.to_dict())
            continue
        if age_val in expand_map:
            targets = expand_map[age_val]
            for t in targets:
                new_row = row.copy()
                new_row['age'] = t
                rows.append(new_row.to_dict())
        else:
            # keep as-is
            rows.append(row.to_dict())
        
    df_raw = pd.DataFrame(rows)

    nace_col = [c for c in df_raw.columns if c.lower().startswith("nace_r")][0]
    df_raw[nace_col] = df_raw[nace_col].replace({
        'C-F': 'industry',
        'B-F': 'industry',
        'G-K': 'services',
        'G-S_X_O': 'services',
        'C-K': 'total',
        'B-S_X_O': 'total'
    })

    df_raw['age'] = df_raw['age'].str.replace('_', '-')
    df = clean_stat(df_raw, keys=keys, columns_to_pivot=['age', nace_col, 'sex'], suffix='_mean_pps')
    
    results.append(df)

all_cols = pd.Index(sorted({c for df in results for c in df.columns}))
aligned = [df.reindex(columns=all_cols) for df in results]
earnings_structure_df = pd.concat(aligned, ignore_index=True, sort=False)

# INSERT THE SAME AS BEFORE BUT FOR MONTHLY INCOME

datasets = [earnings_structure_df]
earnings_df = reduce(lambda left, right: pd.merge(left, right, on=[k.lower() for k in keys], how='left'), datasets)
earnings_df = earnings_df.replace({float('nan'): None})
earnings_df = earnings_df.rename(columns=lambda x: f"earn_{x}" if x not in {'geo', 'time_period'} else x)

# ------ JSON update -------- #
db_name = 'e_earnings'
pattern = ["name", "age", "sector", "sex", "unit", "statistic"]
descriptions = {
    'earn': 'Earnings hourly, yearly by sector, age group, sex'
}
update_json(earnings_df, db_name, pattern, descriptions)

# ------ Connection -------- #
create_table_sql(df=earnings_df, db_name=db_name)
default_connection(earnings_df, db_name)


# Earnings Annual, Monthly and Hourly by
# age, sex, activity, worktime and contract
# Define datasets with dataset_code and filters

database_infos = {
    "e_earnings_a_meur": ("earn_ses_annual", f"A..TOTAL+OC7-9+OC1-5+OC6-8+OC0.TOTAL+PT+FT+TOT_FTE..T+M+F.MEAN_E_EUR+MED_E_EUR.{countries}", "earn-a"),
    "e_earnings_a_mpps": ("earn_ses_annual", f"A..TOTAL+OC7-9+OC1-5+OC6-8+OC0.TOTAL+PT+FT+TOT_FTE..T+M+F.MEAN_E_PPS+MED_E_PPS.{countries}", "earn-a"),
    "e_earnings_a_deur": ("earn_ses_annual", f"A..TOTAL+OC7-9+OC1-5+OC6-8+OC0.TOTAL+PT+FT+TOT_FTE..T+M+F.D1_E_EUR+D9_E_EUR.{countries}", "earn-a"),
    "e_earnings_a_dpps": ("earn_ses_annual", f"A..TOTAL+OC7-9+OC1-5+OC6-8+OC0.TOTAL+PT+FT+TOT_FTE..T+M+F.D1_E_PPS+D9_E_PPS.{countries}", "earn-a"),

    "e_earnings_m_meur": ("earn_ses_monthly", f"A..TOTAL+OC7-9+OC1-5+OC6-8+OC0.TOTAL+PT+FT+TOT_FTE..T+M+F.MEAN_E_EUR+MED_E_EUR.{countries}", "earn-m"),
    "e_earnings_m_mpps": ("earn_ses_monthly", f"A..TOTAL+OC7-9+OC1-5+OC6-8+OC0.TOTAL+PT+FT+TOT_FTE..T+M+F.MEAN_E_PPS+MED_E_PPS.{countries}", "earn-m"),
    "e_earnings_m_deur": ("earn_ses_monthly", f"A..TOTAL+OC7-9+OC1-5+OC6-8+OC0.TOTAL+PT+FT+TOT_FTE..T+M+F.D1_E_EUR+D9_E_EUR.{countries}", "earn-m"),
    "e_earnings_m_dpps": ("earn_ses_monthly", f"A..TOTAL+OC7-9+OC1-5+OC6-8+OC0.TOTAL+PT+FT+TOT_FTE..T+M+F.D1_E_PPS+D9_E_PPS.{countries}", "earn-m"),

    "e_earnings_h_meur": ("earn_ses_hourly", f"A..TOTAL+OC7-9+OC1-5+OC6-8+OC0.TOTAL+PT+FT..T+M+F.MEAN_E_EUR+MED_E_EUR.{countries}", "earn-h"),
    "e_earnings_h_mpps": ("earn_ses_hourly", f"A..TOTAL+OC7-9+OC1-5+OC6-8+OC0.TOTAL+PT+FT..T+M+F.MEAN_E_PPS+MED_E_PPS.{countries}", "earn-h"),
    "e_earnings_h_deur": ("earn_ses_hourly", f"A..TOTAL+OC7-9+OC1-5+OC6-8+OC0.TOTAL+PT+FT..T+M+F.D1_E_EUR+D9_E_EUR.{countries}", "earn-h"),
    "e_earnings_h_dpps": ("earn_ses_hourly", f"A..TOTAL+OC7-9+OC1-5+OC6-8+OC0.TOTAL+PT+FT..T+M+F.D1_E_PPS+D9_E_PPS.{countries}", "earn-h"),
}

cols_to_pivot = ["nace_r2", "isco08", "worktime", "age", "sex", "indic_se"]
pattern = ["name", "sector", "isco08", "worktime", "age", "sex", "unit"]
descriptions = {
    "earn-a": "Structure of earnings survey: annual earnings by sex, age, worktime, economic activity and worker type",
    "earn-m": "Structure of earnings survey: monthly earnings by sex, age, worktime, economic activity and worker type",
    "earn-h": "Structure of earnings survey: hourly earnings by sex, age, worktime, economic activity and worker type"
}

# Loop through datasets
dbs_list = [db for db in database_infos.keys()]
for i, db in enumerate(dbs_list):
    db_code, filters, prefix = database_infos.get(db)
    df = get_eurostat_dataset(dataset_code=db_code, filters=filters)

    for col in cols_to_pivot:
        df[col] = df[col].str.replace("_", "-", regex=False)
    
    # Clean and pivot
    df_clean = clean_stat(df, keys=keys, columns_to_pivot=cols_to_pivot, prefix=prefix)
    df_clean = df_clean.dropna(axis=1, thresh=len(df_clean) * 0.25)
    
    # Update JSON metadata
    update_json(df_clean, db, pattern, descriptions)
    
    # Create SQL table and upload
    create_table_sql(df=df_clean, db_name=db)
    default_connection(df_clean, db)
