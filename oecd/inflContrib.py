from toolbi import default_connection, create_table_sql
from tooldb import clean_stat, update_json
import tooloecd as to
import config
import pandas as pd

keys = config.KEYS
countries = config.OECD_COUNTRIES

# This dataset contains statistics on contributions to national year-on-year inflation by COICOP 2018 divisions.
# Contributions show how much each of the COICOP Divisions contributes to the annual inflation. 
# All data are calculated by the OECD following the Ribe formula.
infl_contr_df = to.get_oecd_dataset(
    dataset_id= "OECD.SDD.TPS,DSD_PRICES@DF_PRICES_CONTRIB,1.0",
    filters= f"{countries}.M..CPI.._T+CP01+CP02+CP03+CP04+CP05+CP06+CP07+CP08+CP09+CP10+CP11+CP045_0722+GD+CP041T043+_TXCP01_NRG+SERVXCP041_042_0432+SERV+CPRES..",
    start_year="2010"
)

infl_contr_df['EXPENDITURE'] = infl_contr_df['EXPENDITURE'].str.replace('_', '-')
infl_contr_df = infl_contr_df.rename(columns={'REF_AREA': 'geo'})
infl_contr_df = clean_stat(infl_contr_df, keys=keys, columns_to_pivot=['EXPENDITURE', 'MEASURE'])
infl_contr_df['time_period'] = pd.to_datetime(infl_contr_df['time_period'].astype(str) + '-01', format='%Y-%m-%d')
infl_contr_df.columns = [
    ('goy-' + col if col not in [k.lower() for k in keys] else col).replace('--', '-')
    for col in infl_contr_df.columns
]

# ------ JSON update -------- #
db_name = 'o_infl_contrib'
pattern = ['name', 'unit']
descriptions = {
    'goy-cp03': 'Clothing and footwear Contribution to growth rate, over 1 year', 
    'goy-cp08': 'Communication Contribution to growth rate, over 1 year', 
    'goy-cp10': 'Education Contribution to growth rate, over 1 year',
    'goy-cp02': 'Alcoholic beverages, tobacco and narcotics Contribution to growth rate, over 1 year', 
    'goy-cp04': 'Housing, water, electricity, gas and other fuels Contribution to growth rate, over 1 year', 
    'goy-cpres': 'Residuals Contribution to growth rate, over 1 year', 
    'goy-cp07': 'Transport Contribution to growth rate, over 1 year',
    'goy-cp01': 'Food and non-alcoholic beverages Contribution to growth rate, over 1 year', 
    'goy-cp05': 'Furnishings, household equipment and routine household maintenance Contribution to growth rate, over 1 year', 
    'goy-cp045-0722': 'Energy Contribution to growth rate, over 1 year', 
    'goy-cp09': 'Recreation and culture Contribution to growth rate, over 1 year',
    'goy-cp11': 'Restaurants and hotels Contribution to growth rate, over 1 year', 
    'goy-cp06': 'Health Contribution to growth rate, over 1 year', 
    'goy-t': 'Total Contribution to growth rate, over 1 year', 
    'goy-txcp01-nrg': 'All items non-food non-energy Contribution to growth rate, over 1 year',
    'goy-serv': 'Services Contribution to growth rate, over 1 year', 
    'goy-gd': 'Goods Contribution to growth rate, over 1 year', 
    'goy-cp041t043': 'Housing Contribution to growth rate, over 1 year',
    'goy-servxcp041-042-0432': 'Services less housing Contribution to growth rate, over 1 year'
}
update_json(infl_contr_df, db_name, pattern, descriptions)

# ------ Connection -------- #
create_table_sql(df=infl_contr_df, db_name=db_name)
default_connection(infl_contr_df, db_name, db_source='OECD')