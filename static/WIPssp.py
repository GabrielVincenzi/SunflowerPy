import pandas as pd
from toolbi import default_connection
from tooldb import clean_stat, update_json
from toolbi import default_connection, create_table_sql

## SSP Emissions dataset
keys = ['MODEL', 'REGION', 'TIME_PERIOD']

ssp_emission_df = pd.read_csv('staticTables/environment/SSP_CMIP6_201811.csv')
ssp_emission_df = pd.melt(
    ssp_emission_df,
    id_vars=['MODEL', 'SCENARIO', 'REGION', 'VARIABLE', 'UNIT'],
    var_name="TIME_PERIOD",
    value_name="OBS_VALUE"
)

ssp_regions = ["R5.2ASIA", "R5.2LAM", "R5.2MAF", "R5.2OECD", "R5.2REF", "World"]
ssp_emission_df["TIME_PERIOD"] = pd.to_datetime(ssp_emission_df["TIME_PERIOD"])
ssp_emission_df['SCENARIO'] = ssp_emission_df['SCENARIO'].str.replace(' ', '-')
ssp_emission_df = ssp_emission_df[~ssp_emission_df["REGION"].isin(ssp_regions)]
ssp_emission_df['VARIABLE'] = (
    ssp_emission_df['VARIABLE']
        .str.replace('|', '_', regex=False)
        .str.replace(' ', '-', regex=False)
        .apply(lambda x: '_'.join(x.split('_')[:2] + ['total'] + x.split('_')[2:]) if x.count('_') != 2 else x)
        .apply(lambda x: x.replace('_', '-', 1))
)

ssp_emission_df = clean_stat(
                            ssp_emission_df, 
                            keys=keys, 
                            columns_to_pivot=['VARIABLE', 'SCENARIO'], 
                            obs_value='OBS_VALUE'
)
ssp_emission_df = ssp_emission_df.rename(columns={'region': 'geo'})

# Divide for each model and save
models = ssp_emission_df['model'].unique()

pattern = ["name", "type", "scenario", "model"]
descriptions = {
    'cmip6-emissions-cf4': 'Emissions (kt/yr) from CMIP6 model of Carbon Tetrafluorid: a long-lived fluorinated greenhouse gas (PFC) with strong radiative forcing.',
    'cmip6-emissions-co2': 'Emissions (Mt/yr) from CMIP6 model of Carbon Dioxid: the main anthropogenic greenhouse gas driving global warming.',
    'cmip6-emissions-bc': 'Emissions (Mt/yr) from CMIP6 model of Black Carbo: a short-lived climate forcer and aerosol component that absorbs sunlight (warming effect).',
    'cmip6-emissions-voc': 'Emissions (Mt/yr) from CMIP6 model of Volatile Organic Compounds (often NMVOC: ozone precursors that participate in tropospheric photochemistry.',
    'cmip6-emissions-ch4': 'Emissions (Mt/yr) from CMIP6 model of Methan: a potent greenhouse gas and ozone precursor with a shorter lifetime than CO2.',
    'cmip6-emissions-co': 'Emissions (Mt/yr) from CMIP6 model of Carbon Monoxid: an indirect greenhouse gas affecting atmospheric chemistry and methane lifetime.',
    'cmip6-emissions-nh3': 'Emissions (Mt/yr) from CMIP6 model of Ammoni: a precursor to secondary inorganic aerosols (e.g. ammonium sulfate/nitrate).',
    'cmip6-emissions-nox': 'Emissions (Mt/yr) from CMIP6 model of Nitrogen Oxides (NO + NO2: precursors to ozone and nitrate aerosols; affect atmospheric chemistry.',
    'cmip6-emissions-oc': 'Emissions (Mt/yr) from CMIP6 model of Organic Carbo: a component of particulate matter (PM); contributes to aerosol formation and cooling.',
    'cmip6-emissions-sulfur': 'Emissions (Mt/yr) from CMIP6 model of Sulfur Compounds (typically SO2: aerosol precursor that forms sulfate aerosols with a cooling effect.'
}

db_name_map = {
    "AIM/CGE": "ssp_emiss_aimcge",
    "GCAM4": "ssp_emiss_gcam4",
    "IMAGE": "ssp_emiss_image",
    "MESSAGE-GLOBIOM": "ssp_emiss_messglob",
    "REMIND-MAGPIE": "ssp_emiss_remmag",
}

for model in models:
    # filter & drop empty rows/cols
    df_model = (
        ssp_emission_df
        .query('model == @model')
        .dropna(axis=0, how='all')
        .dropna(axis=1, how='all')
        .copy()
    )

    if df_model.empty:
        # optionally log / warn and skip
        print(f"[info] no rows for model {model} — skipping.")
        continue

    # drop the 'model' column entirely as requested
    if 'model' in df_model.columns:
        df_model = df_model.drop(columns=['model'])

    # append model suffix to every column name (sanitize "/" to "-" etc.)
    suffix = "_" + model.replace("/", "-")
    df_model.columns = [
        f"{col}{suffix}" if col not in ["geo", "time_period"] else col for col in df_model.columns
    ]
    db_name = db_name_map.get(model)

    update_json(df_model, db_name, pattern, descriptions)

    create_table_sql(df=df_model, db_name=db_name)
    default_connection(df_model, db_name)


## SSP Energy dataset
ssp_energy_df = pd.read_csv('staticTables/environment/SSP_IAM_V2_201811.csv')
ssp_energy_df = pd.melt(
    ssp_energy_df,
    id_vars=['MODEL', 'SCENARIO', 'REGION', 'VARIABLE', 'UNIT'],
    var_name="TIME_PERIOD",
    value_name="OBS_VALUE"
)

ssp_regions = []
ssp_vars = ['diagnostics', 'harmonized']
units = ssp_energy_df['UNIT'].unique()
ssp_energy_df["TIME_PERIOD"] = pd.to_datetime(ssp_energy_df["TIME_PERIOD"])
ssp_energy_df['VARIABLE'] = ssp_energy_df['VARIABLE'].str.replace('|', '_').str.replace(' ', '-')
ssp_energy_df = ssp_energy_df[~ssp_energy_df["REGION"].isin(ssp_regions)]
mask = ~ssp_energy_df['VARIABLE'].str.contains('|'.join(ssp_vars), case=False, na=False)
ssp_energy_df = ssp_energy_df[mask]

ssp_energy_df = clean_stat(
                            ssp_energy_df, 
                            keys=keys, 
                            columns_to_pivot=['VARIABLE'], 
                            obs_value='OBS_VALUE'
)
ssp_energy_df = ssp_energy_df.rename(columns={'region': 'time_period'})

pattern = ['name', ]
descriptions = {
    'Agricultural-Demand': 'in million t DM/yr',
    'Capacity': 'in ',
    'Consumption': 'in billion US$2005/yr',
    'GDP_PPP': 'in ',
    'Emissions': 'in Mt BC/yr',
    'Final-Energy': 'in Mt of the chemical / yr, for N20 in kt',
    'Primary-Energy': 'in EJ/yr',
    'Secondary-Energy': 'in EJ/yr',
    'Land-Cover': 'in million ha (hectars)',
    'Population': 'in million people',
    'Price': 'in US$2005/t CO2',
    'Energy-Service': 'in bn tkm/yr',
    'Energy-Service': 'in bn pkm/yr',
}

# This sheet contains the original Gini projections for 43 countries from the underlying empirical model 
# (See reference to RSP 2016 in the main paper) 
# Rao, ND, M. Gidden, P. Sauer, K. Riahi, 'Income inequality projections for the Shared Socioeconomic Pathways', 
# Futures, doi: https://doi.org/10.1016/j.futures.2018.07.001
# Downloaded 8 march 2025
ssp_gini_df = pd.read_csv('staticTables/environment/SSP_Gini_proj.csv', sep=';')
ssp_gini_df = ssp_gini_df.melt(id_vars=['scenario', 'year'], var_name='geo', value_name='OBSERVATION')
ssp_gini_df = ssp_gini_df.rename(columns={'year': 'time_period'})

