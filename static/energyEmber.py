import pandas as pd
from toolbi import default_connection
from tooldb import clean_stat

# Energy data on past and future paths (no nuclear)
energy_df = pd.read_csv('staticTables/environment/oecd-ember-energy-data.csv')
energy_df = energy_df[(energy_df["Category"] == "Capacity") & (energy_df["ISO 3 code"].notna())]
energy_df.rename(columns={'ISO 3 code': 'country_code', 'Year': 'year', 'Area': 'country_name', 'Unit': 'unit'}, inplace=True)
energy_df = energy_df[['country_name', 'country_code', 'year', 'Ember region', 'Variable', 'unit', 'Value']]
energy_df.fillna(0, inplace=True)
energy_df = clean_stat(energy_df, keys=['country_name', 'country_code', 'year'], columns_to_pivot='Variable', obs_value='Value')
energy_df['bio and other renewables'] = energy_df['bioenergy'] + energy_df['other renewables']
energy_df.drop(columns=['clean', 'gas', 'other fossil', 'renewables', 'bioenergy', 'other renewables',
                        'hydro, bioenergy and other renewables', 'wind and solar', 'nuclear'], inplace=True)


# Targets for renewable energy for 2030
targets_df = pd.read_csv('staticTables/environment/oecd-ember-energy-targets.csv', sep=';', decimal=',')
targets_df.drop(columns=['res_capacity_target', 'res_share_target', 'ember_region', 'unit'], inplace=True)
targets_df.columns = targets_df.columns.str.lower()

targets_df.fillna(0, inplace=True)
targets_df.rename(columns={'target_year': 'year', }, inplace=True)
targets_df['bio and other renewables'] = targets_df['rest of renewables'] + targets_df['other renewables'] + targets_df['bioenergy']
targets_df['winds'] = targets_df['wind'] + targets_df['offshore wind'] + targets_df['onshore wind']

mask = (targets_df[["hydro", "solar", "bio and other renewables", "wind"]] == 0).all(axis=1)
targets_df.loc[mask, "bio and other renewables"] = targets_df.loc[mask, "renewables"]

targets_df.drop(columns=['rest of renewables', 'other renewables', 'wind', 'bioenergy', 'renewables',
                         'offshore wind', 'onshore wind', 'hydro, bio and other renewables'], inplace=True)
targets_df.rename(columns={'winds': 'wind', }, inplace=True)


entar_df = pd.concat([energy_df, targets_df], ignore_index=True)
numeric_cols = entar_df.columns[3:]
entar_df[numeric_cols] = entar_df[numeric_cols].apply(pd.to_numeric, errors="coerce")
entar_df[numeric_cols] = entar_df[numeric_cols].fillna(0).infer_objects(copy=False)


# Monthly prices for energy by country
energy_monthly_df = pd.read_csv('staticTables/environment/european_ember-monthly-energy-prices.csv')
energy_monthly_df = energy_monthly_df.rename(columns={'ISO3 Code': 'geo', 'Date': 'time_period'})
energy_monthly_df = energy_monthly_df.drop(columns=['Country'])

# ------ Connection -------- #
default_connection(entar_df, 's_energy_ember', db_source='Ember')
default_connection(energy_monthly_df, 's_energy_monthly_ember', db_source='Ember')