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

# Population and employment - national accounts
pop_df = et.get_eurostat_dataset(
    dataset_code="namq_10_pe",
    filters=f"Q.THS_PER.NSA.POP_NC+EMP_NC+SAL_NC+SELF_NC+EMP_DC+SAL_DC+SELF_DC.", 
    start_year=start_year,
    end_year=end_year
)

# Employment by main industry (NACE Rev.2) - national accounts
employment_industry_df = et.get_eurostat_dataset(
    dataset_code="namq_10_a10_e",
    filters=f"Q.THS_PER.TOTAL+B-E+C+G-I.NSA..", 
    start_year=start_year,
    end_year=end_year
)

inactive_df = et.get_eurostat_dataset(
    dataset_code="lfsq_ipga",
    filters=f"Q.PC..Y15-24+Y15-64+Y25-54+Y55-64.", 
    start_year=start_year,
    end_year=end_year
)

unemployment_df = et.get_eurostat_dataset(
    dataset_code="lfsq_urgaed",
    filters=f"Q.PC..Y15-24+Y15-64+Y25-54+Y55-64.ED0-2+ED3_4+ED5-8+TOTAL.", 
    start_year=start_year,
    end_year=end_year
)

employment_df = et.get_eurostat_dataset(
    dataset_code="lfsq_ergaed",
    filters=f"Q.PC..Y15-24+Y15-64+Y25-54+Y55-64.ED0-2+ED3_4+ED5-8+TOTAL.", 
    start_year=start_year,
    end_year=end_year
)

pop_df['na_item'] = pop_df['na_item'].str.replace('_', '-')
employment_df['isced11'] = employment_df['isced11'].str.replace('_', '-')
unemployment_df['isced11'] = unemployment_df['isced11'].str.replace('_', '-')

pop_df = clean_stat(pop_df, keys=keys, columns_to_pivot='na_item', prefix='emp')
pop_df = pop_df.rename(columns={'emp_emp-nc': 'emp_total-nc', 'emp_emp-dc': 'emp_total-dc'})
employment_industry_df = clean_stat(employment_industry_df, keys= keys, columns_to_pivot=['nace_r2', 'na_item'], prefix='emp')
employment_df = clean_stat(employment_df, keys= keys, columns_to_pivot=['age', 'sex', 'isced11'], prefix='emp')
unemployment_df = clean_stat(unemployment_df, keys= keys, columns_to_pivot=['age', 'sex', 'isced11'], prefix='unemp')
inactive_df = clean_stat(inactive_df, keys= keys, columns_to_pivot=['age', 'sex'], prefix='inact')

datasets = [employment_df, unemployment_df, inactive_df]
workforce_df = reduce(lambda left, right: pd.merge(left, right, on=[k.lower() for k in keys], how='outer'), datasets)

datasets = [workforce_df, pop_df, employment_industry_df]
quarterly_df = reduce(lambda left, right: pd.merge(left, right, on=[k.lower() for k in keys], how='outer'), datasets)

quarterly_df = quarterly_df.dropna(how='all')
quarterly_df = quarterly_df.replace({float('nan'): None})

# ------ JSON update -------- #
db_name = 'e_employment'
pattern = ['name', 'age', 'sex', 'educ']
descriptions = {
    'emp': 'Employment',
    'unemp': 'Unemployment',
    'inact': 'Inactivity',
}
update_json(workforce_df, db_name, pattern, descriptions)

pattern = ['name', 'type']
descriptions = {
    'emp': 'Employment',
}
update_json(pop_df, db_name, pattern, descriptions)

pattern = ['name', 'sector']
descriptions = {
    'emp': 'Employment',
}
update_json(employment_industry_df, db_name, pattern, descriptions)

# ------ Connection -------- #
create_table_sql(df=quarterly_df, db_name=db_name)
default_connection(quarterly_df, db_name, period_type="Q")