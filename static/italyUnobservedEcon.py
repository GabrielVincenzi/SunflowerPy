import pandas as pd
import numpy as np
import re
import config
from functools import reduce
import tooldb as tb
from tooldb import clean_stat, update_json
from toolbi import default_connection, create_table_sql

keys = config.KEYS

# MEF: Relazione sull'economia non osservata e sull'evasione fiscale e contributiva (dati più aggiornati per anno)
tax_gap_df = pd.read_csv('staticTables/Italy/italy_tax_gap.csv', sep=';')
tax_gap_df['Unita'] = tax_gap_df['Unita'].map({
    'Entrate (milioni di euro)': 'cpmeur',
    'Propensione (%)': 'prop-perc'
})
comp_col = tax_gap_df.columns[0]
tax_gap_df[comp_col] = (
        tax_gap_df[comp_col]
        .str.strip()
        .str.lower()
        .str.replace(r'(, |\.\s| )', '-', regex=True)
    )
tax_gap_df = tax_gap_df.rename(columns={'Anno': 'time_period', 'Valore': 'OBS_VALUE', 'Unita': 'unit', 'Tipologia di imposta': 'tax'})
tax_gap_df['tax'] = tax_gap_df['tax'].replace({'IMU': 'IMU-TASI'})
tax_gap_df = clean_stat(tax_gap_df, keys=['time_period'], columns_to_pivot=['tax', 'unit'], prefix='tax-gap')
tax_gap_df['geo'] = 'IT'

pattern = ['name', 'tax', 'unit']

## ATTENTION: THIS SCRIPT HAS NOT BEEN ASSIGNED TO A DATABASE


# ISTAT Relazione sull'evasione fiscale e lavoro sommerso
sheets_info = {
    1: ([3,4,5], 'underg_econ', 'underg-general', '', ['name', 'type', 'unit']),
    2: ([3], 'underg_econ', 'underg-comp', '%', ['name', 'type', 'unit']),
    3: ([3,4], 'underg_val', 'underg-val-inc', '%', ['name', 'sector', 'type', 'unit']),
    4: ([3,4], 'underg_val', 'underg-val-distr', '%', ['name', 'sector', 'type', 'unit']),
    5: ([3,4], 'underg_econ', 'econ-val-inc', '%', ['name', 'sector', 'type', 'unit']),
    6: ([5], 'underg_ula', 'underg-ula', 'ula', ['name', 'emp', 'sector', 'unit']),
    7: ([5], 'underg_ula', 'underg-ula', '%', ['name', 'emp', 'sector', 'unit']),
    8: ([3,4], 'underg_econ', 'illeg-econ', '%', ['name', 'sector', 'type', 'unit']),
}

sheet_descriptions = {
    "underg-general": "Economia sommersa e attivita illegali, Valori correnti (milioni di euro) ed incidenza percentuale delle componenti sul Pil",
    "underg-comp": "Composizione delle componenti dell'economia sommersa e attivita illegali",
    "underg-val-inc": "Incidenza delle componeneti dell'economia sommersa sul valore aggiunto totale e per attivita economica",
    "underg-val-distr": "Distribuzione per attivita economica del valore aggiunto totale e del valore aggiuno generato dall'economia sommersa",
    "econ-val-inc": "Contributi alla variazione del valore aggiunto per attivita economica",
    "underg-ula": "Unita di lavoro a tempo pieno (ULA) non regolari per attivita economica e posizione nella professione",
    "illeg-econ": "Principali aggregati economici per tipologia di attivita illegale",
}

choosen_tabs = [1,3,4,5,8]
unobs_econ_df = {}
keys = config.KEYS

for tab in choosen_tabs:
    header_rows, db_name, prefix, suffix, pattern = sheets_info.get(tab)
    single_descr = {k: v for k, v in sheet_descriptions.items() if k == prefix}
    df = pd.read_excel('staticTables/Italy/italy_unobserved_econ.xlsx', sheet_name=f'TAVOLA {tab}', header=header_rows)
    cols = ['_'.join([str(level) for level in col]).strip().lower() for col in df.columns.values]

    df.columns = [re.sub(r'unnamed:\s*\d+_level_\d+', '', col) for col in cols]
    df.columns = (
        df.columns
        .str.replace('milioni di euro correnti', 'cpmeur')
        .str.replace(r'incidenza\s*%\s*sul\s*pil', 'pctgdp', regex=True)
        .str.replace(r'_+$', '', regex=True)
        .str.replace(r'(, |\.\s| )', '-', regex=True)
    )
    df = df.rename(columns={df.columns[0]: 'components'})
    comp_col = df.columns[0]
    df[comp_col] = (
        df[comp_col]
        .str.strip() 
        .str.replace(r'(, |\.\s| )', '-', regex=True)
        .str.replace(r'^-+', '', regex=True)  
        .str.replace('à', 'a')
    )

    # melt -> split -> tidy
    df = (
        df
        .melt(id_vars=comp_col, var_name='year_unit', value_name='value')
        .assign(year_unit=lambda d: d['year_unit'].str.strip())
    )
    # robust split: year = 4 digits, unit = rest
    year_unit = df['year_unit'].str.extract(r'(?P<year>\d{4}).*?(?:_(?P<unit>.*))?$', expand=True)
    df = pd.concat([df.drop(columns='year_unit'), year_unit], axis=1)
    df = df.rename(columns={'value': 'OBS_VALUE', 'year': 'time_period'})[[comp_col,'time_period','unit','OBS_VALUE']]
    df['time_period'] = pd.to_datetime(df['time_period'].astype(str), format='%Y')

    df = tb.clean_stat(df, keys=['time_period'], columns_to_pivot=[comp_col, 'unit'], prefix=prefix, suffix=suffix)
    df = df.dropna(axis=1, how='all')
    df['geo'] = 'IT'

    unobs_econ_df[tab] = df

    update_json(df, db_name, pattern, single_descr)

for tab in [2,6,7]:
    header_rows, db_name, prefix, suffix, pattern = sheets_info.get(tab)
    single_descr = {k: v for k, v in sheet_descriptions.items() if k == prefix}
    df = pd.read_excel('staticTables/Italy/italy_unobserved_econ.xlsx', sheet_name=f'TAVOLA {tab}', header=header_rows)
    df = df.rename(columns={df.columns[0]: 'components'})
    comp_col = df.columns[0]

    df[comp_col] = (
        df[comp_col]
        .str.strip()
        .str.lower()
        .str.replace(r'(, |\.\s| )', '-', regex=True)
        .str.replace(r'^-+', '', regex=True)  
        .str.replace('à', 'a')
    )
    if tab in [6,7]:
        descr_col = df.columns[1]
        label_series = df[descr_col].where(df[comp_col].isna())
        label_series = label_series.astype(str).str.strip()
        label_series = label_series.replace({'nan': np.nan}).str.lower().str[:3].add('_').ffill()
        mask = df[comp_col].notna() & label_series.notna()

        df.loc[mask, comp_col] = label_series[mask] + df.loc[mask, comp_col].astype(str).str.strip()
        df = df.dropna(subset=comp_col)

    df = df.melt(id_vars=comp_col, var_name='time_period', value_name='OBS_VALUE')
    df['time_period'] = pd.to_datetime(df['time_period'].astype(str), format='%Y')
    df = tb.clean_stat(df, keys=['time_period'], columns_to_pivot=[comp_col], prefix=prefix, suffix=suffix)
    df['geo'] = 'IT'

    unobs_econ_df[tab] = df

    update_json(df, db_name, pattern, single_descr)


datasets = [unobs_econ_df[1], unobs_econ_df[2], unobs_econ_df[5], unobs_econ_df[8]]
underg_econ_df = reduce(lambda left, right: pd.merge(left, right, on=[k.lower() for k in keys], how='outer'), datasets)

datasets = [unobs_econ_df[3], unobs_econ_df[4]]
underg_val_df = reduce(lambda left, right: pd.merge(left, right, on=[k.lower() for k in keys], how='outer'), datasets)

datasets = [unobs_econ_df[6], unobs_econ_df[7]]
underg_ula_df = reduce(lambda left, right: pd.merge(left, right, on=[k.lower() for k in keys], how='outer'), datasets)
underg_ula_df = underg_ula_df.replace(r'^\s*-\s*$', np.nan, regex=True)
underg_ula_df = underg_ula_df.dropna(axis=1, how='all')

# ------ Connection -------- #
create_table_sql(df=underg_econ_df, db_name='s_underg_econ')
create_table_sql(df=underg_val_df, db_name='s_underg_val')
create_table_sql(df=underg_ula_df, db_name='s_underg_ula')

db_source = "ISTAT"
default_connection(underg_econ_df, 's_underg_econ', db_source=db_source)
default_connection(underg_val_df, 's_underg_val', db_source=db_source)
default_connection(underg_ula_df, 's_underg_ula', db_source=db_source)