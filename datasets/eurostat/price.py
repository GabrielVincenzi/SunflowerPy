import pandas as pd
from tools.toolbi import default_connection, create_table_sql, chunk_list
from tools.tooldb import clean_stat, update_json
import tools.tooleurostat as et
import config

keys = config.KEYS
start_year = config.START_YEAR
end_year = config.END_YEAR

# Annual net earnings
countries = [
    'AL', 'AT', 'BE', 'BG', 'CH', 'CY', 'CZ', 'DE', 'DK', 'EA', 
    'EE', 'EEA', 'EL', 'ES', 'EU', 'FI', 'FR', 'HR', 'HU', 'IE', 'IS',
    'IT', 'LT', 'LU', 'LV', 'ME', 'MK', 'MT', 'NL', 'NO', 'PL', 'PT', 'RO',
    'RS', 'SE', 'SI', 'SK', 'TR', 'UK', 'US'
]

countries_lists = chunk_list(countries, size=4)
datasets = {}

for i, countries in enumerate(countries_lists):
    c = "+".join(countries)
    df = et.get_eurostat_dataset(
        dataset_code="prc_hicp_manr",
        filters=f"M.RCH_A..{c}",
    )

    datasets[i] = df

hicp_df = pd.concat(datasets, ignore_index=True, sort=False)

mask = (
    hicp_df["coicop"].str.startswith("CP", na=False) &
    (hicp_df["coicop"].str.len() > 7)
)

hicp_df = hicp_df[~mask]
cols = ["coicop", "unit"]

for col in cols:
    hicp_df[col] = hicp_df[col].str.replace('_', '-')

hicp_df = clean_stat(hicp_df, keys=keys, columns_to_pivot=cols, prefix="hicp")



# ------ JSON update -------- #
db_name = 'e_price'
pattern = ["name", "coicop", "unit"]
descriptions = {
    'hicp': 'Household Index of Consumption prices (HICP): the index of prices that an individual pays when buying goods or services',
}
update_json(hicp_df, db_name, pattern, descriptions)

# ------ Connection -------- #
create_table_sql(df=hicp_df, db_name=db_name)
default_connection(hicp_df, db_name)