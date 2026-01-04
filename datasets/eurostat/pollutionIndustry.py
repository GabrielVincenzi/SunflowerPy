import pandas as pd
from tools.toolbi import default_connection, create_table_sql
from tools.tooldb import clean_stat, update_json
import tools.tooleurostat as et
import config

keys = config.KEYS
countries = config.COUNTRIES
start_year = config.START_YEAR
end_year = config.END_YEAR

# Air emissions accounts by NACE Rev. 2 activity
pollution_amount_df = et.get_eurostat_dataset(
    dataset_code="env_ac_ainah_r2",
    filters=f"A.GHG.A+B+C+D+E+F+H+I+J+K+L+M+N+O+P+Q+R+S.KG_HAB+THS_T.",
    start_year=start_year,
    end_year=end_year
)

# Air emissions intensities by NACE Rev. 2 activity
pollution_intensity_df = et.get_eurostat_dataset(
    dataset_code="env_ac_aeint_r2",
    filters=f"A.GHG.A+B+C+D+E+F+H+I+J+K+L+M+N+O+P+Q+R+S.P1+B1G.KG_EUR_CP.",
    start_year=start_year,
    end_year=end_year
)

# Electricity production capacities by main fuel groups and operator
energy_prod_df = et.get_eurostat_dataset(
    dataset_code="nrg_inf_epc",
    filters=f"A.TOTAL+CF+RA100+RA200+RA300+RA410+RA420+N9000+X9900.CAP_NET_ELC.PRR_MAIN.MW.",
    start_year=start_year,
    end_year=end_year
)

pollution_amount_df['unit'] = pollution_amount_df['unit'].str.replace('_', '-', regex=False)
pollution_amount_df = clean_stat(pollution_amount_df, keys=keys, columns_to_pivot=['nace_r2','unit'], prefix='pollamount')

pollution_intensity_df['unit'] = pollution_intensity_df['unit'].str.replace('_', '-', regex=False)
pollution_intensity_df = clean_stat(pollution_intensity_df, keys=keys, columns_to_pivot=['nace_r2', 'na_item', 'unit'], prefix='pollintens')

energy_prod_df = clean_stat(energy_prod_df, keys=keys, columns_to_pivot='siec', suffix='mw')
energy_prod_df['n9001_mw'] = energy_prod_df['n9000_mw'] - energy_prod_df['x9900_mw']
energy_prod_df = energy_prod_df.drop(columns=['x9900_mw'])
cols = energy_prod_df.columns.tolist()
cols[2:] = ['elec-prod-' + c for c in cols[2:]]
energy_prod_df.columns = cols

pollution_df = pd.merge(pollution_amount_df, pollution_intensity_df, on=[k.lower() for k in keys], how='outer')
annual_df = pd.merge(pollution_df, energy_prod_df, on=[k.lower() for k in keys], how='outer')
annual_df = annual_df.dropna(how='all')
annual_df = annual_df.replace({float('nan'): None})

# ------ JSON update -------- #
db_name = 'e_pollution_industry'
pattern = ['name', 'sector', 'unit']
descriptions = {'pollamount': 'Pollution amount: in Greenhouse gases C02 equivalent'}
update_json(pollution_amount_df, db_name, pattern, descriptions)

pattern = ['name', 'sector', 'na_item', 'unit']
descriptions = {'pollintens': 'Pollution intensity: in Greenhouse gases C02 equivalent'}
update_json(pollution_intensity_df, db_name, pattern, descriptions)

pattern = ['name', 'unit']
descriptions = {
    'elec-prod-cf' : 'Electricity production capacitiy: Combustible fuels',
    'elec-prod-n9000' : 'Electricity production capacitiy: Nuclear fuels and other fuels nec',
    'elec-prod-ra100' : 'Electricity production capacitiy: Hydro',
    'elec-prod-ra200' : 'Electricity production capacitiy: Geothermal',
    'elec-prod-ra300' : 'Electricity production capacitiy: Wind',
    'elec-prod-ra410' : 'Electricity production capacitiy: Solar thermal',
    'elec-prod-ra420' : 'Electricity production capacitiy: Solar photovoltaic',
    'elec-prod-total' : 'Electricity production capacitiy: Total',
    'elec-prod-n9001' : 'Electricity production capacitiy: Nuclear fuels'
}

update_json(energy_prod_df, db_name, pattern, descriptions)

# ------ Connection -------- #
create_table_sql(df=annual_df, db_name=db_name)
default_connection(annual_df, db_name)