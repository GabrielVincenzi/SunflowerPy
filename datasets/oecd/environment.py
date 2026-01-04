import pandas as pd
from tools.toolbi import default_connection
from tools.tooldb import clean_stat
from functools import reduce
import tools.tooloecd as to
import config

keys = config.KEYS
countries = config.OECD_COUNTRIES
start_year = config.START_YEAR
end_year = config.END_YEAR

# Coastal flooding exposure database:
# Population share, land (% land) and built-up land (% buit-up land) exposed to flooding 
# In the next 10 and 100 years
coastal_flood_df = to.get_oecd_dataset(
    dataset_id= "OECD.ENV.EPI,DSD_ECH@COAS_FLOOD,2.0",
    filters= f"{countries}.A.CF_LAND_EXP+CF_BUILT_EXP+CF_PO P_EXP....Y_100+Y_10.....",
    start_year=2000,
    end_year=2022
)

drop_cols = {'DURATION', 'TEMP_THRESHOLD', 'HURRICANE_WIND_SCALE', 'UNIT_MEASURE',
             'CLIMATE_SCENARIO', 'STATISTICAL_OPERATION', 'ANOMALY'}

coastal_flood_df.drop(columns=drop_cols.intersection(coastal_flood_df.columns), inplace=True)
coastal_flood_df = coastal_flood_df.rename(columns={'REF_AREA': 'geo'})
coastal_flood_df = clean_stat(coastal_flood_df, keys=['geo', 'TIME_PERIOD'], columns_to_pivot=['MEASURE', 'RET_PERIOD'])

datasets = [coastal_flood_df]
environment_df = reduce(lambda left, right: pd.merge(left, right, on=[k.lower() for k in keys], how='outer'), datasets)
environment_df = environment_df.replace({float('nan'): None})

# ------ Connection -------- #
default_connection(environment_df, 'o_environment')