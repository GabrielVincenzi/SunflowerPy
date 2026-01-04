import pandas as pd
from tools.toolbi import default_connection, create_table_sql
from tools.tooldb import clean_stat, update_json
from functools import reduce
import tools.tooleurostat as et
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

    df_raw = et.get_eurostat_dataset(
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