# This Excel file contains the data for the following figure or table:
# Education at a Glance 2025 - © OECD 2025
# Chapter A6. How are social outcomes related to education? - Chapter A6 Tables
# Version 1 - Last updated: 09-Sep-2025
# Disclaimer: http://oe.cd/disclaimer
# Permanent location of this file: https://stat.link/m6ny83

import pandas as pd
import numpy as np
import re
import config
from tooldb import update_json
from toolbi import default_connection, create_table_sql

keys = config.KEYS
geo_codes = config.GEO_MAPPING

educ_dfs = {}

sheets_info = {
    1: ([4,5,6], 's_health_self', "health-status", ['name', 'educ', 'heal_stat', 'unit']),
    3:  ([5,6], 's_health_self', "health-mental", ['name', 'educ', 'heal_ment']),
}

sheet_descriptions = {
    "health-status": "Self-reported health status, by educational attainment (2021, 2022, 2023 or 2024) ",
    "health-mental": "Share of adults who responded 'all or almost all the time' or 'most of the time' to items assessing their mental health during the past week, by educational attainment (2021 or 2023)",
}

choosen_tabs = [1,3]

for tab in choosen_tabs:
    header_rows, db_name, prefix, pattern = sheets_info.get(tab)
    single_descr = {k: v for k, v in sheet_descriptions.items() if k == prefix}
    ed_df = pd.read_excel('staticTables/oecd/education/EducHealth.xlsx', sheet_name=f'Table A6.{tab}.', header=header_rows)

    cols = ['_'.join([str(level) for level in col]).strip().lower() for col in ed_df.columns.values]

    # Replace 'Unnamed: X_level_Y' anywhere with 'all'
    ed_df.columns = [re.sub(r'unnamed:\s*\d+_level_\d+', 'all', col) for col in cols]
    ed_df.columns = (
        ed_df.columns
        .str.replace(r'\s*\+\s*', '+', regex=True)
        .str.replace(r'\s+', '-', regex=True)
        .str.replace(r'(poor|fair)-', r'\1', regex=True)
    )

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

health_mental_df = pd.merge(educ_dfs[1], educ_dfs[3], on=[k.lower() for k in keys], how='outer')
health_mental_df = health_mental_df.dropna(subset='geo')
health_mental_df = health_mental_df.replace({float('nan'): None})

db_name = 's_health_self'

# ------ Connection -------- #
create_table_sql(df=health_mental_df, db_name=db_name)
default_connection(health_mental_df, db_name, db_source='Education at a Glance - OECD')