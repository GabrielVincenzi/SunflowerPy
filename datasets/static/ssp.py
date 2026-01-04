import pandas as pd
from tools.tooldb import clean_stat, update_json
from tools.toolbi import default_connection, create_table_sql
from collections import defaultdict

## SSP Emissions dataset
keys = ['MODEL', 'REGION', 'TIME_PERIOD']

ssp_emission_df = pd.read_csv('datasets/staticTables/environment/SSP_CMIP6_201811.csv')
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
    default_connection(df_model, db_name, db_source="IPCC scenarios", period_list=True)


## SSP Energy dataset
keys = ['MODEL', 'REGION', 'TIME_PERIOD']

ssp_energy_df = pd.read_csv('datasets/staticTables/environment/SSP_IAM_V2_201811.csv')
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

ssp_energy_clean_df = clean_stat(
                            ssp_energy_df, 
                            keys=keys, 
                            columns_to_pivot=['SCENARIO', 'VARIABLE'], 
                            obs_value='OBS_VALUE'
)
ssp_energy_clean_df = ssp_energy_clean_df.rename(columns={'region': 'geo'})

db_name_map = {
    "AIM/CGE": "ssp_energy_aimcge",
    "GCAM4": "ssp_energy_gcam4",
    "IMAGE": "ssp_energy_image",
    "MESSAGE-GLOBIOM": "ssp_energy_messglob",
    "REMIND-MAGPIE": "ssp_energy_remmag",
    "WITCH-GLOBIOM": "ssp_energy_witchglob"
}

pattern = ["name", "model", "type", "category", "sub-category", "specific"]

descriptions = {

    # ================= SSP1 — Sustainability =================
    "ssp1-baseline": (
        "SSP1 (Sustainability - Green Road): A world that prioritizes sustainable development, "
        "strong environmental protection, low inequality, and efficient use of resources. "
        "Economic growth is inclusive and human well-being improves globally. "
        "The baseline assumes no additional climate policies beyond existing trends."
    ),
    "ssp1-19": (
        "SSP1-1.9: A sustainability-focused world that achieves extremely strong climate mitigation. "
        "Global CO₂ emissions fall rapidly, reaching net-zero around mid-century. "
        "This pathway is consistent with limiting global warming to about 1.5°C. "
        "It requires major shifts in energy, land use, and consumption patterns."
    ),
    "ssp1-26": (
        "SSP1-2.6: A sustainable development pathway combined with strong climate policies. "
        "Emissions peak early and decline steadily throughout the century. "
        "Warming is likely kept close to 2°C above pre-industrial levels. "
        "This scenario assumes high international cooperation."
    ),
    "ssp1-34": (
        "SSP1-3.4: Sustainability-oriented development with moderate mitigation efforts. "
        "Climate action is present but less ambitious than 2°C-consistent pathways. "
        "Global warming reaches intermediate levels. "
        "Environmental goals compete with other development priorities."
    ),
    "ssp1-45": (
        "SSP1-4.5: A world striving for sustainability socially and economically, "
        "but with relatively weak climate mitigation. "
        "Emissions decline slowly or stabilize rather than fall sharply. "
        "This results in higher long-term warming."
    ),
    "ssp1-60": (
        "SSP1-6.0: Sustainable development goals are partially achieved, "
        "but climate policies remain insufficient. "
        "Greenhouse gas emissions stay high throughout the century. "
        "This pathway leads to substantial climate change despite social progress."
    ),

    # ================= SSP2 — Middle of the Road =================
    "ssp2-baseline": (
        "SSP2 (Middle of the Road): A future that broadly follows historical trends. "
        "Economic growth, population change, and technological progress evolve unevenly. "
        "Institutions improve slowly and inequalities persist. "
        "Climate action advances incrementally but not decisively."
    ),
    "ssp2-19": (
        "SSP2-1.9: A continuation of current societal trends combined with unexpectedly strong "
        "global climate policies. "
        "Rapid emissions reductions are achieved despite moderate governance capacity. "
        "This pathway is consistent with limiting warming to around 1.5°C."
    ),
    "ssp2-26": (
        "SSP2-2.6: A middle-of-the-road world that implements strong but achievable climate action. "
        "Emissions peak soon and decline gradually. "
        "Warming is likely limited to around 2°C. "
        "International cooperation is present but imperfect."
    ),
    "ssp2-34": (
        "SSP2-3.4: Current development trends continue with partial climate mitigation. "
        "Policies reduce emissions growth but do not eliminate it. "
        "Warming reaches intermediate levels. "
        "Climate risks increase but remain manageable in some regions."
    ),
    "ssp2-45": (
        "SSP2-4.5: The most representative scenario of moderate climate action. "
        "Some mitigation policies are implemented, but ambition is limited. "
        "Emissions stabilize rather than decline strongly. "
        "This results in moderate to high global warming."
    ),
    "ssp2-60": (
        "SSP2-6.0: A world following historical trends with weak climate policies. "
        "Fossil fuels remain a major energy source. "
        "Emissions remain high throughout the century. "
        "This pathway leads to significant climate impacts."
    ),

    # ================= SSP3 — Regional Rivalry =================
    "ssp3-baseline": (
        "SSP3 (Regional Rivalry - Rocky Road): A fragmented world with strong nationalism "
        "and limited international cooperation. "
        "Economic growth is slow and population growth is high in vulnerable regions. "
        "Institutions are weak and climate action is minimal."
    ),
    "ssp3-34": (
        "SSP3-3.4: A geopolitically divided world that still achieves some climate mitigation. "
        "Emission reductions occur mainly through regional or local efforts. "
        "Global coordination is limited. "
        "Climate risks remain high in many regions."
    ),
    "ssp3-45": (
        "SSP3-4.5: Regional rivalry constrains effective climate action. "
        "Energy systems remain carbon-intensive. "
        "Adaptation and mitigation capacities are uneven. "
        "This leads to substantial warming and high vulnerability."
    ),
    "ssp3-60": (
        "SSP3-6.0: A highly fragmented world with minimal cooperation on climate change. "
        "Emissions continue to rise or stabilize at high levels. "
        "Adaptation capacity is low in many regions. "
        "Severe climate impacts are widespread."
    ),

    # ================= SSP4 — Inequality =================
    "ssp4-baseline": (
        "SSP4 (Inequality - A Road Divided): A world characterized by strong inequalities "
        "within and between countries. "
        "Wealthy groups have access to advanced technology and protection. "
        "Large vulnerable populations face high exposure to climate risks."
    ),
    "ssp4-19": (
        "SSP4-1.9: A deeply unequal world that achieves strong global mitigation. "
        "Advanced technologies allow low emissions pathways. "
        "However, benefits are concentrated among wealthy regions. "
        "Vulnerable populations remain highly exposed."
    ),
    "ssp4-26": (
        "SSP4-2.6: Climate mitigation is driven by elites and technologically advanced regions. "
        "Global warming is limited, but inequality persists. "
        "Adaptation capacity varies strongly across populations. "
        "Social vulnerability remains high."
    ),
    "ssp4-34": (
        "SSP4-3.4: Uneven mitigation efforts lead to moderate warming. "
        "Protected regions cope better with climate change. "
        "Poorer regions face disproportionate impacts. "
        "Global inequality shapes climate outcomes."
    ),
    "ssp4-45": (
        "SSP4-4.5: Moderate climate action in a highly unequal world. "
        "Emissions decline slowly and unevenly. "
        "Climate risks are concentrated among vulnerable populations. "
        "Adaptation gaps widen."
    ),
    "ssp4-60": (
        "SSP4-6.0: High inequality combined with weak mitigation. "
        "Emissions remain high and warming is severe. "
        "Most people lack resources to adapt. "
        "Climate impacts exacerbate social divisions."
    ),

    # ================= SSP5 — Fossil-fuelled Development =================
    "ssp5-baseline": (
        "SSP5 (Fossil-fuelled Development - Highway): Rapid economic growth driven by "
        "energy-intensive lifestyles and fossil fuels. "
        "Technological progress is high, but emissions are very large. "
        "Environmental concerns are secondary."
    ),
    "ssp5-19": (
        "SSP5-1.9: A fossil-fuel-based world that relies on massive technological intervention. "
        "Large-scale carbon capture and removal offset high emissions. "
        "Warming is limited to about 1.5°C. "
        "This pathway assumes unprecedented technological deployment."
    ),
    "ssp5-26": (
        "SSP5-2.6: Continued economic growth with heavy energy use. "
        "Strong mitigation relies on advanced technologies rather than reduced consumption. "
        "Emissions decline later in the century. "
        "Warming is kept close to 2°C."
    ),
    "ssp5-34": (
        "SSP5-3.4: High-energy development with partial technological mitigation. "
        "Emissions remain high for much of the century. "
        "Climate impacts increase but are managed technologically. "
        "Resource use remains intensive."
    ),
    "ssp5-45": (
        "SSP5-4.5: Fossil-fuel-driven growth with moderate climate controls. "
        "Emissions peak late and decline slowly. "
        "Warming reaches high levels. "
        "Adaptation relies heavily on economic capacity."
    ),
    "ssp5-60": (
        "SSP5-6.0: Continued reliance on fossil fuels with limited mitigation. "
        "Economic growth is rapid but emissions stay very high. "
        "Climate change becomes severe. "
        "Long-term sustainability is compromised."
    ),
}

models = ssp_energy_clean_df['model'].unique()
rename_dict = {}

for model in models:
    # filter & drop empty rows/cols
    df_model = (
        ssp_energy_clean_df
        .query('model == @model')
        .dropna(axis=0, how='all')
        .dropna(axis=1, how='all')
        .copy()
    )

    if df_model.empty:
        # optionally log / warn and skip
        print(f"[info] no rows for model {model} — skipping.")
        continue

    # drop the 'model' column entirely
    if 'model' in df_model.columns:
        df_model = df_model.drop(columns=['model'])

    # append model suffix to every column name (sanitize "/" to "-" etc.)
    # append model suffix to every column name (sanitize "/" to "-" etc.)
    base_cols = ['geo', 'time_period']

    # count underscores per column (excluding base cols)
    underscore_count = {
        col: col.count("_")
        for col in df_model.columns
        if col not in base_cols
    }

    # group columns by base name (before first "_")
    groups = defaultdict(list)
    for col in underscore_count:
        base = col.split("_",1)[0]
        groups[base].append(col)

    # compute max depth per group and rename
    pad_rename = {}

    for base, cols in groups.items():
        max_len = max(underscore_count[c] for c in cols)

        for col in cols:
            diff = max_len - underscore_count[col]
            if diff > 0:
                pad_rename[col] = col + "_tot" * diff

    df_model = df_model.rename(columns=pad_rename)

    # Add model suffix
    suffix = "_" + model.replace("/", "-")
    df_model.columns = [
        f"{col}{suffix}" if col not in base_cols else col for col in df_model.columns
    ]

    cols = df_model.columns.drop(base_cols)
    for col in cols:
        parts = col.split("_")

        name = parts[0]
        body = parts[1:-1]
        scenario_model = "_".join(parts[-1:])

        new_col = f"{name}_{scenario_model}"
        if body:
            new_col += "_" + "_".join(body)

        rename_dict[col] = new_col

    df_model = df_model.rename(columns=rename_dict)

    db_name = db_name_map.get(model)

    update_json(df_model, db_name, pattern, descriptions)

    create_table_sql(df=df_model, db_name=db_name)
    default_connection(df_model, db_name, db_source="IPCC scenarios", period_list=True)


# This sheet contains the original Gini projections for 43 countries from the underlying empirical model 
# (See reference to RSP 2016 in the main paper) 
# Rao, ND, M. Gidden, P. Sauer, K. Riahi, 'Income inequality projections for the Shared Socioeconomic Pathways', 
# Futures, doi: https://doi.org/10.1016/j.futures.2018.07.001
# Downloaded 8 march 2025
keys = ["geo", "time_period"]

ssp_gini_df = pd.read_csv('datasets/staticTables/environment/SSP_Gini_proj.csv', sep=';', decimal=',')
ssp_gini_df = ssp_gini_df.melt(id_vars=['scenario', 'year'], var_name='geo', value_name='OBS_VALUE')
ssp_gini_df = ssp_gini_df.rename(columns={'year': 'time_period'})
ssp_gini_df["time_period"] = pd.to_datetime(ssp_gini_df["time_period"], format="%Y")
ssp_gini_clean_df = clean_stat(ssp_gini_df, keys = keys, columns_to_pivot=["scenario"], suffix="gini")

# ------ JSON update -------- #
db_name = 'ssp_gini'
pattern = ['name', 'unit']

descriptions = {
    "ssp5": (
            "SSP5 (Fossil-fuelled Development - Highway): Rapid economic growth driven by "
            "energy-intensive lifestyles and fossil fuels. "
            "Technological progress is high, but emissions are very large. "
        ),
    "ssp4": (
        "SSP4 (Inequality - A Road Divided): A world characterized by strong inequalities "
        "within and between countries. "
        "Wealthy groups have access to advanced technology and protection. "
        "Large vulnerable populations face high exposure to climate risks."
    ),
    "ssp3": (
        "SSP3 (Regional Rivalry - Rocky Road): A fragmented world with strong nationalism "
        "and limited international cooperation. "
        "Economic growth is slow and population growth is high in vulnerable regions. "
    ),
    "ssp2": (
        "SSP2 (Middle of the Road): A future that broadly follows historical trends. "
        "Economic growth, population change, and technological progress evolve unevenly. "
        "Institutions improve slowly and inequalities persist. "
    ),
     "ssp1": (
        "SSP1 (Sustainability - Green Road): A world that prioritizes sustainable development, "
        "strong environmental protection, low inequality, and efficient use of resources. "
        "Economic growth is inclusive and human well-being improves globally. "
    ),
}

update_json(ssp_gini_clean_df, db_name, pattern, descriptions)

# ------ Connection -------- #
create_table_sql(df=ssp_gini_clean_df, db_name=db_name)
default_connection(ssp_gini_clean_df, db_name, db_source="IPCC scenarios", period_list=True)