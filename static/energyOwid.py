import pandas as pd
from toolbi import default_connection

# OWID data on energy usage and pollution (useful to build Kaya Identity)
energy_df = pd.read_csv('staticTables/environment/owid-energy-data.csv')
energy_df = energy_df.query('year >= 1965')
energy_df = energy_df[
    ['year', 'iso_code',
     'net_elec_imports', 'net_elec_imports_share_demand', 'primary_energy_consumption',
     'coal_consumption', 'coal_production', 'coal_share_energy', 
     'fossil_fuel_consumption', 'fossil_share_energy',
     'gas_consumption', 'gas_production', 'gas_share_energy',
     'electricity_demand', 'energy_per_capita', 'energy_per_gdp',
     'hydro_consumption', 'hydro_share_energy',
     'low_carbon_consumption', 'low_carbon_share_energy',
     'nuclear_consumption', 'nuclear_share_energy',
     'oil_consumption', 'oil_production', 'oil_share_energy',
     'other_renewable_consumption', 'other_renewables_share_energy',
     'renewables_consumption', 'renewables_share_energy',
     'solar_consumption', 'solar_share_energy',
     'wind_consumption', 'wind_share_energy'
     ]
]
energy_df = energy_df.dropna(subset=['iso_code'])
null_vals = energy_df.groupby('iso_code')['low_carbon_consumption'].apply(lambda x: x.isna().sum())
len_geo = len_geo = energy_df.groupby('iso_code').size().to_list()
nan_ratio = null_vals / len_geo
valid_countries = nan_ratio[nan_ratio <= 0.8].index
energy_df = energy_df[energy_df["iso_code"].isin(valid_countries)]

co2_df = pd.read_csv('staticTables/environment/owid-co2-data.csv')
co2_df = co2_df.query('year >= 1965')
co2_df = co2_df[
    ['country', 'year', 'iso_code', 'population', 'gdp', 'ghg_per_capita', 'total_ghg',
     'co2_growth_abs', 'co2_growth_prct', 'co2_per_capita', 'co2_per_gdp', 'co2_per_unit_energy',
     'share_global_co2', 'share_global_cumulative_co2',
     'share_of_temperature_change_from_ghg', 'temperature_change_from_ghg'
     ]
]
co2_df['gdp_per_capita'] = co2_df['gdp'] / co2_df['population']

annual_df = pd.merge(co2_df, energy_df, on=['year', 'iso_code'], how='inner')
annual_df = annual_df.dropna(how='all')
annual_df = annual_df.replace({float('nan'): None})

# ------ Connection -------- #
default_connection(annual_df, 's_energy_owid', db_source='Our World in Data')