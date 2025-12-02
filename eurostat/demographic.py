import pandas as pd
from toolbi import default_connection, create_table_sql
from tooldb import clean_stat, update_json
from functools import reduce
import tooleurostat as et
import config

keys = config.KEYS
countries = config.COUNTRIES
start_year = config.START_YEAR
end_year = config.END_YEAR

pop_df = et.get_eurostat_dataset(
    dataset_code="demo_pjanind",
    filters=f"A.DEPRATIO1+OLDDEP1+YOUNGDEP1+MEDAGEPOP+FMEDAGEPOP+MMEDAGEPOP+PC_FM+PC_Y0_14+PC_Y0_4+PC_Y0_18+PC_Y10_14+PC_Y15_19+PC_Y15_24+PC_Y15_29+PC_Y15_74+PC_Y20_24+PC_Y20_39+PC_Y20_64+PC_Y25_29+PC_Y25_44+PC_Y25_49+PC_Y30_34+PC_Y35_39+PC_Y40_44+PC_Y40_59+PC_Y45_49+PC_Y45_64+PC_Y50_54+PC_Y50_64+PC_Y55_59+PC_Y5_9+PC_Y60_64+PC_Y60_79+PC_Y60_MAX+PC_Y65_69+PC_Y65_79+PC_Y65_MAX+PC_Y70_74+PC_Y75_79+PC_Y75_MAX+PC_Y80_84+PC_Y80_MAX+PC_Y85_MAX+PC_Y100_MAX.{countries}",
    start_year=start_year,
    end_year=end_year
)

poptot_df = et.get_eurostat_dataset(
    dataset_code="demo_gind",
    filters=f"A.AVG+CNMIGRAT+GROWRT+NATGROWRT+POPTRT.{countries}",
    start_year=start_year,
    end_year=end_year
)

pension_replacement_rate = et.get_eurostat_dataset(
    dataset_code="ilc_pnp3",
    filters=f"A..PC.{countries}",
    start_year=start_year,
    end_year=end_year
)

pop_gen_df = et.get_eurostat_dataset(
    dataset_code="demo_pjangroup",
    filters=f"A....{countries}",
    start_year=start_year,
    end_year=end_year
)

fertility_df = et.get_eurostat_dataset(
    dataset_code="demo_find",
    filters=f"A.AGEMOTH+AGEMOTH1+AGEMOTH2+AGEMOTH3+AGEMOTH4_MAX+LBIRTHR1PC+LBIRTHR2PC+LBIRTHR3PC+LBIRTHR4_MAXPC+MEDAGEMOTH+NMARPCT+TOTFERRT.{countries}",
    start_year=start_year,
    end_year=end_year
)

# pop_gen_birth_df = et.get_eurostat_dataset(
#     dataset_code="migr_pop8ctb",
#     filters=f"A...NR..{countries}",
#     start_year=start_year,
#     end_year=end_year
# )
# pop_gen_birth_df["c_birth"] = pop_gen_birth_df["c_birth"].str.replace("_", "-")
# pop_gen_birth_df["c_birth"] = "c-birth_" + pop_gen_birth_df["c_birth"]
# 
# pop_gen_cit_df = et.get_eurostat_dataset(
#     dataset_code="migr_pop7ctz",
#     filters=f"A.NAT+TOTAL+EU28_FOR+NEU28_FOR+EFTA_FOR+EXT_FOR_HDI_VH+EXT_FOR_HDI_H+EXT_FOR_HDI_L+EXT_FOR_HDI_M..NR..{countries}",
#     start_year=start_year,
#     end_year=end_year
# )

pop_df["indic_de"] = (
    pop_df["indic_de"]
    .str.replace("_", "-", regex=False)
    .str.replace("FMEDAGEPOP", "MEDAGEPOP_F", regex=False)
    .str.replace("MMEDAGEPOP", "MEDAGEPOP_M", regex=False)
    .str.replace(r"^PC-", r"pop-pc_total_", regex=True)
)
pop_df = clean_stat(pop_df, keys=keys, columns_to_pivot='indic_de')
poptot_df = clean_stat(poptot_df, keys=keys, columns_to_pivot='indic_de')
pension_replacement_rate = clean_stat(pension_replacement_rate, keys=keys, columns_to_pivot=['sex'])
pop_gen_df = clean_stat(pop_gen_df, keys=keys, columns_to_pivot=['sex', 'age'], prefix='pop')
pension_replacement_rate.columns = [
    (f"pensarr_{col}" if i >= len(pension_replacement_rate.columns) - 3 else col)
    for i, col in enumerate(pension_replacement_rate.columns)
]
fertility_df["indic_de"] = fertility_df["indic_de"].str.replace("_", "-")
fertility_df = clean_stat(fertility_df, keys=keys, columns_to_pivot='indic_de')

datasets = [pop_df, poptot_df, pension_replacement_rate, pop_gen_df, fertility_df]
dem_df = reduce(lambda left, right: pd.merge(left, right, on=[k.lower() for k in keys], how='outer'), datasets)
dem_df = dem_df.replace({float('nan'): None})

# ------ JSON update -------- #
db_name = 'e_demographic'
pattern = ['name', 'sex', 'age']
descriptions = {
    "pop": "Population at 1 January by age group and sex",
    "pop-pc": "Population proportion at 1 January by age group",
    'depratio1': 'Age dependency ratio: population 0-14 and 65+ relative to population 15-64',
    'medagepop': 'Median age: of population',
    'olddep1': 'Old-age dependency ratio: population 65+ to population 15-64',
    'youngdep1': 'Young-age dependency ratio: population 0-14 to population 15-64',
    'avg': 'Average population',
    'cnmigrat': 'Net migration: net migration rate plus statistical adjustment rate',
    'growrt': 'Crude rate of population growth: total population change per value of base / average population',
    'natgrowrt': 'Crude rate of natural population change: births minus deaths) per average population',
    'poptrt': 'Crude rate of total population change: or population turnover / total change rate',
    'pensarr': 'Pension replacement rate: Pension income over 50-64 income (last income)',
    'agemoth': 'Mean age of women at childbirth',
    'agemoth1': 'Mean age of women at birth of first child',
    'agemoth2': 'Mean age of women at birth of second child',
    'agemoth3': 'Mean age of women at birth of third child',
    'agemoth4-max': 'Mean age of women at birth of fourth and higher order child',
    'lbirthr1pc': 'Percentage first order live births',
    'lbirthr2pc': 'Percentage second order live births',
    'lbirthr3pc': 'Percentage third order live births',
    'lbirthr4-maxpc': 'Percentage fourth and higher order live births',
    'nmarpct': 'Proportion of live births outside marriage',
    'totferrt': 'Total fertility rate',
    'medagemoth': 'Median age of women at childbirth',
}
update_json(dem_df, db_name, pattern, descriptions)


# ------ Connection -------- #
create_table_sql(df=dem_df, db_name=db_name)
default_connection(dem_df, db_name)