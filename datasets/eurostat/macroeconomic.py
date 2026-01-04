import pandas as pd
import config
from functools import reduce
from tools.toolbi import default_connection, create_table_sql
from tools.tooldb import clean_stat, update_json
import tools.tooleurostat as et

keys = config.KEYS
countries = config.COUNTRIES
start_year = config.START_YEAR
end_year = config.END_YEAR

# Gross domestic product (GDP) and main components (output, expenditure and income)
gdp_df = et.get_eurostat_dataset(
    dataset_code="namq_10_gdp",
    filters=f"Q.CP_MEUR+PC_GDP.NSA.B1GQ+D2+D3+P71+P41+P72+P61+P62+P3.", 
    start_year=start_year,
    end_year=end_year
)

# Gross value added and income by main industry
gdp_industry_df = et.get_eurostat_dataset(
    dataset_code="namq_10_a10",
    filters=f"Q.CP_MEUR+PC_GDP.NSA.TOTAL+B-E+C+G-I..", 
    start_year=start_year,
    end_year=end_year
)

# Quarterly government debt
debt_df = et.get_eurostat_dataset(
    dataset_code="gov_10q_ggdebt",
    filters=f"Q.GD+F2+F31+F32+F3+F4+F41+F42.S13.MIO_EUR+PC_GDP.", 
    start_year=start_year,
    end_year=end_year
)

current_account_df = et.get_eurostat_dataset(
    dataset_code="ei_bpm6ca_q",
    filters=f"Q.MIO_EUR+PC_GDP.NSA...WRL_REST.BAL+CRE+DEB.CA+GS+G+S+SA+SB+SC+SD+SE+SF+SG+SI+SL+G1+G2.", 
    start_year=start_year,
    end_year=end_year
)

financial_account_df = et.get_eurostat_dataset(
    dataset_code="ei_bpm6fa_q",
    filters=f"Q.MIO_EUR....NET+ASS+LIAB.WRL_REST.NSA.", 
    start_year=start_year,
    end_year=end_year
)

datasets = [gdp_df, gdp_industry_df, current_account_df, debt_df]
for df in datasets:
    df['unit'] = df['unit'].apply(lambda x: 'pcgdp' if x == 'PC_GDP' else 'cpmeur')
financial_account_df['currency'] = financial_account_df['currency'].apply(lambda x: 'pcgdp' if x == 'PC_GDP' else 'cpmeur')

gdp_df = clean_stat(gdp_df, keys=keys, columns_to_pivot=['na_item', 'unit'])
gdp_industry_df = clean_stat(gdp_industry_df, keys=keys, columns_to_pivot=['na_item', 'unit', 'nace_r2'])
debt_df = clean_stat(debt_df, keys=keys, columns_to_pivot=['na_item', 'unit'])
current_account_df = clean_stat(current_account_df, keys=keys, columns_to_pivot=['bop_item', 'unit',  'stk_flow'])
financial_account_df = clean_stat(financial_account_df, keys=keys, columns_to_pivot=['bop_item', 'stk_flow'])
financial_account_df.rename(
    columns={
        col: col.replace('__', '-')
        for col in financial_account_df.columns
        if col.lower() not in [k.lower() for k in keys]
    },
    inplace=True
)
financial_account_df.rename(
    columns={
        col: f"{col.split('_')[0]}_cpmeur_{col.split('_')[1]}"
        for col in financial_account_df.columns
        if col not in [k.lower() for k in keys]
    }, inplace=True
)

datasets = [gdp_df, gdp_industry_df, debt_df]
gdpdebt_df = reduce(lambda left, right: pd.merge(left, right, on=[k.lower() for k in keys], how='outer'), datasets)
gdpdebt_df = gdpdebt_df.dropna(how='all')
gdpdebt_df = gdpdebt_df.replace({float('nan'): None})

accounts_df = pd.merge(current_account_df, financial_account_df, on=[k.lower() for k in keys], how='outer')
quarterly_df = pd.merge(gdpdebt_df, accounts_df, on=[k.lower() for k in keys], how='outer')
quarterly_df = quarterly_df.dropna(how='all')
quarterly_df = quarterly_df.replace({float('nan'): None})

# ------ JSON update -------- #
db_name = 'e_macroeconomic'
pattern = ['name', 'unit', 'sector']
descriptions = {
    'b1gq': 'Gross domestic product at market prices',
    'b1g': 'Value added, gross', 
    'd1': 'Compensation of employees',
    'd11': 'Wages and salaries',
    'd12': 'Employers social contributions',    
    'd2': 'Taxes on production and imports', 
    'd3': 'Subsidies', 
    'p3': 'Final consumption expenditure', 
    'p41': 'Actual individual consumption',
    'p61': 'Exports of goods', 
    'p62': 'Exports of services',
    'p71': 'Imports of goods', 
    'p72': 'Imports of services', 
    'f2': 'Debt in currency and deposits', 
    'f3': 'Debt securities', 
    'f31': 'Short-term debt securities', 
    'f32': 'Long-term debt securities', 
    'f4': 'Loans', 
    'f41': 'Short-term - loans', 
    'f42': 'Long-term - loans', 
    'gd': 'Government consolidated gross debt',
}

update_json(gdpdebt_df, db_name, pattern, descriptions)

pattern = ['name', 'unit', 'flow']
descriptions = {
    'ca': 'Current account of government balance sheet',
    'g': 'Goods in current account',
    'g1': 'General merchandise on a balance of payments basis',
    'g2': 'Net exports of goods under merchanting',
    'gs': 'Goods and services in current account',
    's': 'Services in current account',
    'fa': 'Financial account of government balance sheet',
    'eo': 'Net errors and omissions in financial accounts',
    'sa': 'Services: manufacturing services on physical inputs owned by others',
    'sb': 'Services: maintenance and repair services n.i.e.',
    'sc': 'Services: transport',
    'sd': 'Services: travel',
    'se': 'Services: construction',
    'sf': 'Services: insurance and pension services',
    'sg': 'Services: financial services',
    'si': 'Services: telecommunications, computer, and information services',
    'sl': 'Services: government goods and services n.i.e.',
    'fa-d-f': 'Financial account; direct investment',
    'fa-f-f7': 'Financial account; financial derivatives and employee stock options',
    'fa-o-f': 'Financial account; other investment',
    'fa-p-f': 'Financial account; portfolio investment',
    'fa-r-f': 'Financial account; reserve assets'
}

update_json(accounts_df, db_name, pattern, descriptions)

# ------ Connection -------- #
create_table_sql(df=quarterly_df, db_name=db_name)
default_connection(quarterly_df, db_name, period_type="Q")

### NEED TO ADD THE UNIT AND MODIFY THE WHOLE STRING METHODS