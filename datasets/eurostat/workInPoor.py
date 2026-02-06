from tools.toolbi import default_connection, create_table_sql
from tools.tooleurostat import get_eurostat_dataset, clean_stat
from tools.tooldb import serial_db, update_json
import config

keys = config.KEYS
countries = config.COUNTRIES
start_year = config.START_YEAR
end_year = config.END_YEAR

database_infos = {
    # original_db_name : (filters, measure_column, prefix, suffix, pattern)
    "ilc_peps01n" : ("A..TOTAL+Y_LT16+Y_GE16+Y_GE18+Y18-24+Y16-24+Y16-64+Y18-64+Y25-49+Y50-64+Y65-74+Y_GE65+Y_GE75.T+F+M.", ['sex', 'age', 'unit'], "wip-sa", "", ['sex', 'age', 'unit']),
    "ilc_peps02n": ("A.POP+EMP+SAL+NSAL+UNE+RET.T+F+M.Y_GE18+Y18-64+Y18-24+Y25-49+Y50-64+Y65-74+Y_GE65+Y_GE75..", ['sex', 'age', 'wstatus', 'unit'], "wip-wstat", "", ['sex', 'age', 'wstat', 'unit']),
    "ilc_peps03n": ("A....", ['quantile', 'hhcomp', 'unit'], "wip-inc", "", ['quantile', 'hhcomp', 'unit']),
    "ilc_peps04n": ("A.T+F+M..Y_GE18+Y18-64+Y18-24+Y25-49+Y50-64+Y65-74+Y_GE65+Y_GE75..", ['sex', 'age', 'isced11', 'unit'], "wip-educ", "", ['sex', 'age', 'educ', 'unit']),
    "ilc_peps05n": ("A.T+F+M.FOR+NAT.Y_GE18+Y16-29+Y25-54+Y55-64+Y_GE65..", ['sex', 'age', 'citizen', 'unit'], "wip-citiz", "", ['sex', 'age', 'citiz', 'unit']),
    "ilc_peps06n": ("A.T+F+M.FOR+NAT.Y_GE18+Y16-29+Y25-54+Y55-64+Y_GE65..", ['sex', 'age', 'c_birth', 'unit'], "wip-brth", "", ['sex', 'age', 'brth', 'unit']),
    "ilc_peps07n": ("A...", ['tenure', 'unit'], "wip-tenr", "", ['tenure', 'unit']),
    "ilc_peps13n": ("A...", ['deg_urb', 'unit'], "wip-urb", "", ['deg-urb', 'unit']),

    "ilc_peps60n": ("A..Y_LT6+Y6-11+Y12-17+Y_LT18..", ['isced11', 'age', 'unit'], "chp-prnt", "", ['educ', 'age', 'unit']),
}

descriptions = {
    "wip-sa": "Persons at risk of poverty or social exclusion by age and sex",
    "wip-wstat": "Persons at risk of poverty or social exclusion by most frequent activity status (population aged 18 and over)",
    "wip-educ": "Persons at risk of poverty or social exclusion by educational attainment level (population aged 18 and over)",
    "wip-inc": "Persons at risk of poverty or social exclusion by income quantile and household composition",
    "wip-citz": "Persons at risk of poverty or social exclusion by group of citizenship (population aged 18 and over)",
    "wip-brth": "Persons at risk of poverty or social exclusion by group of country of birth (population aged 18 and over)",
    "wip-tenr": "Persons at risk of poverty or social exclusion by tenure status",
    "wip-urb": "Persons at risk of poverty or social exclusion by degree of urbanisation",
    "chp-prnt": "Children at risk of poverty or social exclusion by educational attainment level of their parents (population aged 0 to 17 years) ",
}

db_name = "e_workinpoor"

wip_df, dfs = serial_db(db_info=database_infos, 
                                   description=descriptions,
                                   keys=keys, 
                                   db_name=db_name, 
                                   output_dfs=True)


# ------ Connection -------- #
create_table_sql(df=wip_df, db_name=db_name)
default_connection(wip_df, db_name)


# Persons by risk of poverty, material deprivation, work intensity of the household, age and sex of the person
# intersections of EU 2030 poverty target indicators
wip_spec_df = get_eurostat_dataset(
    dataset_code="ilc_pees01n",
    filters=f"A.....TOTAL+Y_LT18+Y_GE18+Y18-64+Y18-29+Y25-54+Y50-64+Y_GE65..",
)

measure_columns = ['sex', 'age', 'yn_rskpov', 'workint', 'lev_depr', 'unit']

for col in measure_columns:
    wip_spec_df[col] = wip_spec_df[col].str.replace('_', '-')

wip_spec_df = clean_stat(wip_spec_df, keys=keys, columns_to_pivot=measure_columns, prefix='wip-insct')

db_name_spec = "e_workinpoor_spec"
pattern_spec = ['sex', 'age', 'yn_rskpov', 'workint', 'lev_depr', 'unit']
descriptions_spec = {
    "wip-insct": "Persons by risk of poverty, material deprivation, work intensity of the household, age and sex of the person - intersections of EU 2030 poverty target indicators",
}

update_json(wip_spec_df, db_name_spec, pattern_spec, descriptions_spec)


# ------ Connection -------- #
create_table_sql(df=wip_spec_df, db_name=db_name_spec)
default_connection(wip_spec_df, db_name_spec)
