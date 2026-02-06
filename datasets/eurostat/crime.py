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

db_name = "e_crimes"

database_infos = {
    # original_db_name : (filters, measure_column, prefix, suffix, pattern)
    "crim_pris_off" : ("A.ICCS0101+ICCS03011+ICCS03012..NR+P_HTHAB.", ['sex', 'iccs', 'unit'], "prs-off", "", ['name', 'sex', 'iccs', 'unit']),
    "crim_pris_age" : ("A...NR+P_HTHAB.", ['sex', 'age', 'unit'], "prs-age", "", ['name', 'sex', 'age', 'unit']),
    "crim_pris_cap" : ("A.PRIS_ACT_CAP+PRIS_OFF_CAP.NR+P_HTHAB.", ['indic_cr', 'unit'], "prn-cap", "", ['name', 'indic_cr', 'unit']),
    "crim_pris_ctz" : ("A...", ['citizen', 'unit'], "prs-ctz", "", ['name', 'citiz', 'unit']),
    "crim_pris_tri" : ("A...", ['leg_stat', 'unit'], "prs-lgst", "", ['name', 'lgst', 'unit']),
}

descriptions = {
    "prs-off": "Prisoners by offence category and sex",
    "prs-age": "Prisoners by age and sex",
    "prn-cap": "Prison capacity and number of persons held",
    "prs-ctz": "Prisoners by citizenship",
    "prs-lgst": "Prisoners by legal status of the trial process",
}

prison_dfs = {}
dbs_list = [db for db in database_infos.keys()]

for i, db in enumerate(dbs_list):
    filters, measure_columns, prefix, suffix, pattern = database_infos.get(db)
    measure_columns = measure_columns if isinstance(measure_columns, (list, tuple)) else [measure_columns]
    df = get_eurostat_dataset(
        dataset_code=db,
        filters=filters
    )

    for col in measure_columns:
        df[col] = df[col].str.replace('_', '-')
    df = clean_stat(df, keys=keys, columns_to_pivot=measure_columns, prefix=prefix, suffix=suffix)

    if db == "crim_pris_cap":
        df["prn-cap_pris-ovrcrw_nr"] = df["prn-cap_pris-act-cap_nr"] / df["prn-cap_pris-off-cap_nr"]
        df["prn-cap_pris-ovrcrw_p-hthab"] = df["prn-cap_pris-act-cap_p-hthab"] / df["prn-cap_pris-off-cap_p-hthab"]

    prison_dfs[i+1] = df

    if db in descriptions:
        update_json(df, db_name, pattern, descriptions[db])
    else:
        update_json(df, db_name, pattern, descriptions)

prs_df = reduce(lambda left, right: pd.merge(left, right, on=["geo", "time_period"], how="outer"), prison_dfs.values())

# ------ Connection -------- #
create_table_sql(df=prs_df, db_name=db_name)
default_connection(prs_df, db_name, db_source='Eurostat')