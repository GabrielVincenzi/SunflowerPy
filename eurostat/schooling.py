import pandas as pd
from toolbi import default_connection, create_table_sql
from tooldb import clean_stat
from functools import reduce
import tooleurostat as et
from tooleurostat import serial_db
import config

keys = config.KEYS
countries = config.COUNTRIES
start_year = config.START_YEAR
end_year = config.END_YEAR

# Pupils and students enrolled by education level, sex and field of education
# Sum of short-cycle tertiary, bachelor and master degree
enrolled_df = et.get_eurostat_dataset(
    dataset_code="educ_uoe_enra03",
    filters=f"A.NR.TOTAL+F01+F02+F03+F04+F05+F06+F07+F08+F09+F10.ED5+ED6+ED7.T+F+M.{countries}",
    start_year=start_year,
    end_year=end_year
)

merged_df = pd.merge(enrolled_df.query('isced11 == "ED6"'), enrolled_df.query('isced11 == "ED7"'), 
                     on=enrolled_df.columns.drop(['isced11', 'OBS_VALUE']).to_list(), how='inner', suffixes=['_ed6', '_ed7'])

merged_df['isced11'] = 'ED6_7'
merged_df['OBS_VALUE'] = merged_df['OBS_VALUE_ed6'] + merged_df['OBS_VALUE_ed7']
enrolled_df = merged_df.drop(columns=['isced11_ed6', 'OBS_VALUE_ed6', 'isced11_ed7', 'OBS_VALUE_ed7'])
enrolled_df = clean_stat(enrolled_df, keys=keys, columns_to_pivot=['iscedf13', 'isced11', 'sex'])

# Out-of-school rate in population of lower secondary school age, by sex
out_lowersec_df = et.get_eurostat_dataset(
    dataset_code="educ_uoe_enra28",
    filters=f"A...{countries}",
    start_year=start_year,
    end_year=end_year
)

out_lowersec_df = clean_stat(out_lowersec_df, keys=keys, columns_to_pivot=['sex'])
cols = out_lowersec_df.columns.tolist()
cols[2:] = ['out_lowersec_' + c for c in cols[2:]]
out_lowersec_df.columns = cols

# Out-of-school rate in population of upper secondary school age, by sex
out_uppersec_df = et.get_eurostat_dataset(
    dataset_code="educ_uoe_enra29",
    filters=f"A...{countries}",
    start_year=start_year,
    end_year=end_year
)

out_uppersec_df = clean_stat(out_uppersec_df, keys=keys, columns_to_pivot=['sex'])
cols = out_uppersec_df.columns.tolist()
cols[2:] = ['out_uppersec_' + c for c in cols[2:]]
out_uppersec_df.columns = cols

datasets = [enrolled_df, out_lowersec_df, out_uppersec_df]
school1_df = reduce(lambda left, right: pd.merge(left, right, on=[k.lower() for k in keys], how='outer'), datasets)
school1_df = school1_df.replace({float('nan'): None})


db_name = "e_schooling"

descriptions = {
    "educ_uoe_fini04": "Annual expenditure on educational institutions per pupil/student based on FTE, by education level and programme orientation",
    "edu-nwen": "New entrants by education level, programme orientation, sex and field of education",
    "edu-dnwen": "Distribution of new entrants at education level and programme orientation by sex and field of education",
    "tch-part": "Teachers working part-time - as percent of all teachers, by education level",
    "tch-stud1": "Ratio of pupils to teachers and teacher aides by education level and programme orientation",
    "tch-stud2": "Ratio of pupils and students to teachers and academic staff by education level and programme orientation",
    "tch-pop": "Classroom teachers and academic staff by education level, programme orientation, sex and age groups",
    "tch-fem": "Female teachers - as percent of all teachers, by education level",
    "mng-fem": "Female school-management personnel - as perc of total school-management personnel, by education level",
    "edu-lvl": "Pupils and students by education level - as perc of total age population"
}

database_infos = {
    # original_db_name : (filters, measure_column, prefix, suffix, pattern)
    "educ_uoe_fini04" : (f"A.PPS.PUBL+TOT_SEC.ED0+ED1+ED2+ED3_4+ED5-8+ED02-8.", ["isced11", "sector", "unit"], "edu-expst", "", ["name", "edu", "sector", "unit"]),
    "educ_uoe_ent02" : (f"A.NR.F01+F02+F021+F022+F023+F03+F031+F032+F04+F041+F042+F05+F051+F052+F053+F054+F06+F07+F071+F072+F073+F08+F081+F082+F083+F084+F09+F091+F092+F10+F101+F102+F103+F104.ED35+ED45+ED54+ED55+ED6+ED7+ED8.T+F+M.",
                         ["sex","isced11", "iscedf13", "unit"], "edu-nwen", "", ["name", "sex", "edu", "prog", "unit"]),
    "educ_uoe_ent03" : (f"A.PC.ED35+ED45+ED54+ED55+ED6+ED7+ED8.F01+F02+F021+F022+F023+F03+F031+F032+F04+F041+F042+F05+F051+F052+F053+F054+F06+F07+F071+F072+F073+F08+F081+F082+F083+F084+F09+F091+F092+F10+F101+F102+F103+F104.T+F+M.",
                         ["sex","isced11", "iscedf13", "unit"], "edu-dnwen", "", ["name", "sex", "edu", "prog", "unit"]),
    "educ_uoe_enra04" : (f"A...", ["isced11", "unit"], "edu-lvl", "", ["name", "edu", "unit"]),
    "educ_uoe_perd05" : (f"A...", ["isced11", "unit"], "tch-part", "", ["name", "edu", "unit"]),
    "educ_uoe_perp05" : (f"A...", ["isced11", "unit"], "tch-stud1", "", ["name", "edu", "unit"]),
    "educ_uoe_perp04" : (f"A...", ["isced11", "unit"], "tch-stud2", "", ["name", "edu", "unit"]),
    "educ_uoe_perd04" : (f"A...", ["isced11", "unit"], "mng-fem", "", ["name", "edu", "unit"]),
    "educ_uoe_perd03" : (f"A...", ["isced11", "unit"], "tch-fem", "", ["name", "edu", "unit"]),
    "educ_uoe_perp01" : (f"A.....", ["sex","isced11", "age", "unit"], "tch-pop", "", ["name", "sex", "edu", "age", "unit"]),
}

db_name = 'e_schooling_stud'

school2_df, dfs = serial_db(db_info=database_infos, 
                                description=descriptions, 
                                keys=keys, 
                                db_name=db_name, 
                                output_dfs=True)

schooling_df = pd.merge(school2_df, school1_df, on=[k.lower() for k in keys], how='outer')
## INSTEAD DIVIDE BETWEEN STUDENT AND TEACHER

# ------ Connection -------- #
create_table_sql(df=schooling_df, db_name=db_name)
default_connection(schooling_df, db_name)

db_name = 'e_schooling_teacher'
# ------ Connection -------- #
create_table_sql(df=teacher_df, db_name=db_name)
default_connection(teacher_df, db_name)