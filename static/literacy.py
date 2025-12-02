# Education at a Glance 2025 - OECD 2025
# PIAAC. Proficiency in key information-processing skills among adults - Chapter PIAAC Proficiency in key information-processing skills among adults Tables
# Version 1 - Last updated: 09-Sep-2025
# Disclaimer: http://oe.cd/disclaimer
# Permanent location of this file: https://stat.link/m8lu47

import pandas as pd
import numpy as np
import re
import config
from functools import reduce
from tooldb import update_json
from toolbi import default_connection, create_table_sql

keys = config.KEYS
geo_codes = config.GEO_MAPPING

educ_dfs = {}

sheets_info = {
    12: ([4,5,6,7], 's_numeracy', "num-prof-i", ['name', 'educ', 'born', 'tongue', 'unit']),
    2:  ([4,5,6,7], 's_literacy_lev_sex', "lit-lev-s", ['name', 'educ', 'sex', 'level', 'unit']),
    9:  ([4,5,6,7], 's_numeracy_lev_sex', "num-lev-s", ['name', 'educ', 'sex', 'level', 'unit']),
    16: ([4,5,6,7], 's_probsolv_lev_sex', "pso-lev-s", ['name', 'educ', 'sex', 'level', 'unit']),
    17: ([4,5,6,7], 's_probsolv', "pso-prof-a", ['name', 'educ', 'age', 'unit']),
    19: ([4,5,6,7], 's_probsolv', "pso-prof-i", ['name', 'educ', 'born', 'tongue', 'unit']),

    1:  ([4,5,6], 's_literacy', "lit-prof-s", ['name', 'educ', 'sex', 'unit']),
    8:  ([4,5,6], 's_numeracy', "num-prof-s", ['name', 'educ', 'sex', 'unit']),
    15: ([4,5,6], 's_probsolv', "pso-prof-s", ['name', 'educ', 'sex', 'unit']),

    3:  ([5,6,7], 's_literacy', "lit-prof-a", ['name', 'educ', 'age', 'unit']),
    10: ([5,6,7], 's_numeracy', "num-prof-a", ['name', 'educ', 'age', 'unit']),

    4:  ([5,6,7,8], 's_literacy_lev_age', "lit-lev-a", ['name', 'educ', 'age', 'level', 'unit']),
    11: ([5,6,7,8], 's_numeracy_lev_age', "num-lev-a", ['name', 'educ', 'age', 'level', 'unit']),
    18: ([5,6,7,8], 's_probsolv_lev_age', "pso-lev-a", ['name', 'educ', 'age', 'level', 'unit']),

    5:  ([7,8,9,10], 's_literacy', "lit-prof-i", ['name', 'educ', 'born', 'tongue', 'unit'])
}

sheet_descriptions = {
    "num-prof-i": "Adults' mean numeracy proficiency, by educational attainment, immigrant background and language spoken at home (2023)",
    "lit-lev-s": "Distribution of adults by literacy proficiency levels, by educational attainment and gender (2023)",
    "num-lev-s": "Distribution of adults by numeracy proficiency levels, by educational attainment and gender (2023)",
    "pso-lev-s": "Distribution of adults by adaptive problem-solving proficiency levels, by educational attainment and gender (2023)",
    "pso-prof-a": "Adults' mean adaptive problem-solving proficiency, by educational attainment and age group (2023)",
    "pso-prof-i": "Adults' mean numeracy proficiency, by educational attainment, immigrant background and language spoken at home (2023)",
    "lit-prof-s": "Adults' mean literacy proficiency, by educational attainment level and gender (2023)",
    "num-prof-s": "Adults' mean numeracy proficiency, by educational attainment level and gender (2023)",
    "pso-prof-s": "Adults' mean adaptive problem-solving proficiency, by educational attainment level and gender (2023)",
    "lit-prof-a": "Adults' mean literacy proficiency, by educational attainment and age group (2023)",
    "num-prof-a": "Adults mean numeracy proficiency, by educational attainment and age group (2023)",
    "lit-lev-a": "Distribution of adults by literacy proficiency levels, by educational attainment and age group (2023)",
    "num-lev-a": "Distribution of adults by numeracy proficiency levels, by educational attainment and age group (2023)",
    "pso-lev-a": "Distribution of adults by adaptive problem-solving proficiency levels, by educational attainment and age group (2023)",
    "lit-prof-i": "Adults' mean literacy proficiency, by educational attainment, immigrant background and language spoken at home (2023)"
}

choosen_tabs = [1,2,3,4,5,8,9,10,11,12,15,16,17,18,19]

for tab in choosen_tabs:
    header_rows, db_name, prefix, pattern = sheets_info.get(tab)
    add = ' (web only)' if tab > 5 else ''
    single_descr = {k: v for k, v in sheet_descriptions.items() if k == prefix}
    ed_df = pd.read_excel('staticTables/oecd/education/educLiteracy.xlsx', sheet_name=f'Table {tab}{add}.', header=header_rows)

    if tab in {1,3,5,8,10,12,15,17}:
        # Keep default order
        cols = ['_'.join([str(level) for level in col]).strip().lower() for col in ed_df.columns.values]
    else:
        # Custom reordering for other tabs (as in your original code)
        cols = ['_'.join([str(col[i]).lower() for i in [1, 0, 2, 3] if str(col[i]) != 'nan']).strip()
                for col in ed_df.columns.values]

    # Replace 'Unnamed: X_level_Y' anywhere with 'all'
    ed_df.columns = [re.sub(r'unnamed:\s*\d+_level_\d+', 'all', col) for col in cols]
    ed_df.columns = ed_df.columns.str.replace(' ', '-')

    # Clean empty strings and single letters
    ed_df = ed_df.replace(r'^\s*$|^[A-Za-z]$', np.nan, regex=True)
    ed_df = ed_df.dropna(subset=ed_df.columns.drop(ed_df.columns[0]), how='all')
    ed_df = ed_df.dropna(subset=ed_df.columns[0])
    ed_df = ed_df.dropna(axis=1, how='all')
    ed_df.columns = [f"{prefix}_{col}" for col in ed_df.columns]
    ed_df = ed_df.rename(columns={ed_df.columns[0]: 'geo'})
    ed_df['geo'] = ed_df['geo'].map(geo_codes)
    ed_df['time_period'] = pd.to_datetime('2023-01-01')

    educ_dfs[tab] = ed_df

    update_json(ed_df, db_name, pattern, single_descr)


datasets = [educ_dfs[1], educ_dfs[3], educ_dfs[5]]
literacy_df = reduce(lambda left, right: pd.merge(left, right, on=[k.lower() for k in keys], how='outer'), datasets)

datasets = [educ_dfs[8], educ_dfs[10], educ_dfs[12]]
numeracy_df = reduce(lambda left, right: pd.merge(left, right, on=[k.lower() for k in keys], how='outer'), datasets)

datasets = [educ_dfs[15], educ_dfs[17], educ_dfs[19]]
probsolv_df = reduce(lambda left, right: pd.merge(left, right, on=[k.lower() for k in keys], how='outer'), datasets)

# ------ Connection -------- #
create_table_sql(df=literacy_df, db_name='s_literacy')
create_table_sql(df=numeracy_df, db_name='s_numeracy')
create_table_sql(df=probsolv_df, db_name='s_probsolv')

create_table_sql(df=educ_dfs[2], db_name='s_literacy_sex')
create_table_sql(df=educ_dfs[4], db_name='s_literacy_age')
create_table_sql(df=educ_dfs[9], db_name='s_numeracy_sex')
create_table_sql(df=educ_dfs[11], db_name='s_numeracy_age')
create_table_sql(df=educ_dfs[16], db_name='s_probsolv_sex')
create_table_sql(df=educ_dfs[18], db_name='s_probsolv_age')

db_source = 'Education at a Glance - OECD'
default_connection(literacy_df, 's_literacy', db_source=db_source)
default_connection(numeracy_df, 's_numeracy', db_source=db_source)
default_connection(probsolv_df, 's_probsolv', db_source=db_source)

default_connection(educ_dfs[2], 's_literacy_sex', db_source=db_source)
default_connection(educ_dfs[4], 's_literacy_age', db_source=db_source) # from this included need to be initiators
default_connection(educ_dfs[9], 's_numeracy_sex', db_source=db_source)
default_connection(educ_dfs[11], 's_numeracy_age', db_source=db_source)
default_connection(educ_dfs[16], 's_probsolv_sex', db_source=db_source)
default_connection(educ_dfs[18], 's_probsolv_age', db_source=db_source)