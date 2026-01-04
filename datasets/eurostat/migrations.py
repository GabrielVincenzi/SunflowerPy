import pandas as pd
from tools.toolbi import default_connection, create_table_sql
from tools.tooldb import clean_stat, update_json
from functools import reduce
import tools.tooleurostat as et
import config

keys = config.KEYS + ["citizen"]
countries = config.COUNTRIES
start_year = config.START_YEAR
end_year = config.END_YEAR

## MONTHLY DATABASE
# Asylum applicants by type, citizenship, age and sex - monthly data 
asylapp_df = et.get_eurostat_dataset(
    dataset_code="migr_asyappctzm",
    filters=f"M...T+M+F.FRST+TOTAL.TOTAL+Y_LT14+Y14-17+Y_LT18+Y18-34+Y35-64+Y_GE65.",
    start_year=start_year,
    end_year=end_year
)

unit_suffix = asylapp_df["unit"].unique()[0]
asylapp_df["age"] = asylapp_df["age"].str.replace("_", "-")
asylapp_df["citizen"] = asylapp_df["citizen"].str.replace("_", "-")
asylapp_df = clean_stat(asylapp_df, keys=keys, columns_to_pivot=["sex", "age", "applicant"], prefix="asyapp", suffix=unit_suffix)

# Persons subject of asylum applications pending at the end of the month by citizenship, age and sex - monthly data
asypen_df = et.get_eurostat_dataset(
    dataset_code="migr_asypenctzm",
    filters=f"M...T+M+F.TOTAL+Y_LT14+Y14-17+Y_LT18+Y18-34+Y35-64+Y_GE65.",
    start_year=start_year,
    end_year=end_year
)

unit_suffix = asypen_df["unit"].unique()[0]
asypen_df["age"] = asypen_df["age"].str.replace("_", "-")
asypen_df["citizen"] = asypen_df["citizen"].str.replace("_", "-")
asypen_df = clean_stat(asypen_df, keys=keys, columns_to_pivot=["sex", "age"], prefix="asypen", suffix=unit_suffix)

# Decisions granting temporary protection by citizenship, age and sex - monthly data
asyprot_df = et.get_eurostat_dataset(
    dataset_code="migr_asytpfm",
    filters=f"M...T+M+F.TOTAL+Y_LT14+Y14-17+Y_LT18+Y18-34+Y35-64+Y_GE65.",
    start_year=start_year,
    end_year=end_year
)

unit_suffix = asyprot_df["unit"].unique()[0]
asyprot_df["age"] = asyprot_df["age"].str.replace("_", "-")
asyprot_df["citizen"] = asyprot_df["citizen"].str.replace("_", "-")
asyprot_df = clean_stat(asyprot_df, keys=keys, columns_to_pivot=["sex", "age"], prefix="asyprot", suffix=unit_suffix)

# Beneficiaries of temporary protection at the end of the month by citizenship, age and sex - monthly data
asyben_df = et.get_eurostat_dataset(
    dataset_code="migr_asytpsm",
    filters=f"M...T+M+F.TOTAL+Y_LT14+Y14-17+Y_LT18+Y18-34+Y35-64+Y_GE65.",
    start_year=start_year,
    end_year=end_year
)

unit_suffix = asyben_df["unit"].unique()[0]
asyben_df["age"] = asyben_df["age"].str.replace("_", "-")
asyben_df["citizen"] = asyben_df["citizen"].str.replace("_", "-")
asyben_df = clean_stat(asyben_df, keys=keys + ["citizen"], columns_to_pivot=["sex", "age"], prefix="asyben", suffix=unit_suffix)


datasets = [asypen_df, asyprot_df, asyben_df]
migration_interm_df = reduce(lambda left, right: pd.merge(left, right, on=[k.lower() for k in keys], how='outer'), datasets)
migration_m_df = pd.merge(migration_interm_df, asylapp_df, on=[k.lower() for k in keys],  how='outer')
migration_m_df = migration_m_df.replace({float('nan'): None})

# ------ JSON update -------- #
db_name = 'e_migrations_m'
pattern_asylapp = ["name", "sex", "age", "applicant", "unit"]
pattern_interm = ["name", "sex", "age", "unit"]
descriptions = {
    "asyapp": "Asylum applicants by type, citizenship, age and sex - monthly data ",
    "asypen": "Persons subject of asylum applications pending at the end of the month by citizenship, age and sex - monthly data",
    "asyprot": "Decisions granting temporary protection by citizenship, age and sex - monthly data",
    "asyben": "Beneficiaries of temporary protection at the end of the month by citizenship, age and sex - monthly data",
}
update_json(asylapp_df, db_name, pattern_asylapp, descriptions)
update_json(migration_interm_df, db_name, pattern_interm, descriptions)


# ------ Connection -------- #
create_table_sql(df=migration_m_df, db_name=db_name)
default_connection(migration_m_df, db_name)


## ANNUAL DATABASE
# First instance decisions on applications by type of decision, citizenship, age and sex - annual aggregated data
asydec_df = et.get_eurostat_dataset(
    dataset_code="migr_asydcfsta",
    filters=f"A.PER..T+F+M.TOTAL+Y_LT14+Y14-17+Y_LT18+Y18-34+Y35-64+Y_GE65..",
    start_year=start_year,
    end_year=end_year
)

unit_suffix = asydec_df["unit"].unique()[0]
asydec_df["age"] = asydec_df["age"].str.replace("_", "-")
asydec_df["citizen"] = asydec_df["citizen"].str.replace("_", "-")
asydec_df = clean_stat(asydec_df, keys=keys + ["citizen"], columns_to_pivot=["sex", "age", "decision"], prefix="asydec", suffix=unit_suffix)

# Final decisions in appeal or review on applications by type of decision, citizenship, age and sex - annual data
asydecl_df = et.get_eurostat_dataset(
    dataset_code="migr_asydcfina",
    filters=f"A.PER..T+F+M.TOTAL+Y_LT14+Y14-17+Y_LT18+Y18-34+Y35-64+Y_GE65..",
    start_year=start_year,
    end_year=end_year
)

unit_suffix = asydecl_df["unit"].unique()[0]
asydecl_df["age"] = asydecl_df["age"].str.replace("_", "-")
asydecl_df["citizen"] = asydecl_df["citizen"].str.replace("_", "-")
asydecl_df = clean_stat(asydecl_df, keys=keys + ["citizen"], columns_to_pivot=["sex", "age", "decision"], prefix="asydec", suffix=unit_suffix)

# Immigration by age (completed in the year) group, sex and citizenship
immig_df = et.get_eurostat_dataset(
    dataset_code="migr_imm1ctz",
    filters=f"A..COMPLET.TOTAL+Y_LT5+Y5-9+Y10-14+Y_LT15+Y15-19+Y15-64+Y20-24+Y25-29+Y30-34+Y35-39+Y40-44+Y45-49+Y50-54+Y55-59+Y60-64+Y65-69+Y_GE65+Y70-74+Y75-79+Y80-84+Y85-89+Y_GE85+Y90-94+Y95-99+Y_GE100.NR.T+F+M.",
    start_year=start_year,
    end_year=end_year
)

immig_df["age"] = immig_df["age"].str.replace("_", "-")
immig_df["citizen"] = immig_df["citizen"].str.replace("_", "-")
immig_df = clean_stat(immig_df, keys=keys + ["citizen"], columns_to_pivot=["sex", "age", "unit"], prefix="imm")


migration_interm_df = pd.merge(asydec_df, asydecl_df, on=[k.lower() for k in keys],  how='outer')
migration_a_df = pd.merge(migration_interm_df, immig_df, on=[k.lower() for k in keys],  how='outer')
migration_a_df = migration_a_df.replace({float('nan'): None})

# ------ JSON update -------- #
db_name = 'e_migrations_a'
pattern_interm = ["name", "sex", "age", "decision", "unit"]
pattern_imm = ["name", "sex", "age", "unit"]
descriptions = {
    "asydec-fst": "First instance decisions on applications by type of decision, citizenship, age and sex - annual aggregated data",
    "asydec-lst": "Final instance decisions on applications by type of decision, citizenship, age and sex - annual aggregated data",
    "imm": "Immigration by age (completed in the year) group, sex and citizenship",
}
update_json(migration_interm_df, db_name, pattern_interm, descriptions)
update_json(immig_df, db_name, pattern_imm, descriptions)

# ------ Connection -------- #
create_table_sql(df=migration_a_df, db_name=db_name)
default_connection(migration_a_df, db_name)