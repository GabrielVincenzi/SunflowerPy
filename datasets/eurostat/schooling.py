import pandas as pd
from tools.toolbi import default_connection, create_table_sql
from tools.tooldb import clean_stat, update_json
from functools import reduce
from tools.tooleurostat import serial_db, get_eurostat_dataset
import config

keys = config.KEYS
countries = config.COUNTRIES
start_year = config.START_YEAR
end_year = config.END_YEAR

# Pupils and students enrolled by education level, sex and field of education
# Sum of short-cycle tertiary, bachelor and master degree
enrolled_df = get_eurostat_dataset(
    dataset_code="educ_uoe_enra03",
    filters=f"A.NR.TOTAL+F01+F02+F03+F04+F05+F06+F07+F08+F09+F10.ED5+ED6+ED7.T+F+M.",
    start_year=start_year,
    end_year=end_year
)

enrolled_df = clean_stat(enrolled_df, keys=keys, columns_to_pivot=['iscedf13', 'isced11', 'sex'])
cols = enrolled_df.columns.tolist()
cols[2:] = ['stud-enrl_' + c + '_nr' for c in cols[2:]]
enrolled_df.columns = cols

# Out-of-school rate in population of lower secondary school age, by sex
out_lowersec_df = get_eurostat_dataset(
    dataset_code="educ_uoe_enra28",
    filters=f"A...",
    start_year=start_year,
    end_year=end_year
)

out_lowersec_df = clean_stat(out_lowersec_df, keys=keys, columns_to_pivot=['sex'])
cols = out_lowersec_df.columns.tolist()
cols[2:] = ['out-lowersec_' + c + '_pc' for c in cols[2:]]
out_lowersec_df.columns = cols

# Out-of-school rate in population of upper secondary school age, by sex
out_uppersec_df = get_eurostat_dataset(
    dataset_code="educ_uoe_enra29",
    filters=f"A...",
    start_year=start_year,
    end_year=end_year
)

out_uppersec_df = clean_stat(out_uppersec_df, keys=keys, columns_to_pivot=['sex'])
cols = out_uppersec_df.columns.tolist()
cols[2:] = ['out-uppersec_' + c + '_pc' for c in cols[2:]]
out_uppersec_df.columns = cols

datasets = [enrolled_df, out_lowersec_df, out_uppersec_df]
school1_df = reduce(lambda left, right: pd.merge(left, right, on=[k.lower() for k in keys], how='outer'), datasets)
school1_df = school1_df.replace({float('nan'): None})


descriptions_student = {
    "edu-expst": "Annual expenditure on educational institutions per pupil/student based on FTE, by education level and programme orientation",
    "edu-nwen": "New entrants by education level, sex and field of education",
    "edu-dnwen": "Distribution of new entrants at education level and programme orientation by sex and field of education",
    "tch-stud1": "Ratio of pupils to teachers and teacher aides by education level and programme orientation",
    "tch-stud2": "Ratio of pupils and students to teachers and academic staff by education level and programme orientation",
    "edu-lvl": "Pupils and students by education level - as perc of total age population"
}

descriptions_teacher = {
    "tch-part": "Teachers working part-time - as percent of all teachers, by education level",
    "tch-pop": "Classroom teachers and academic staff by education level, programme orientation, sex and age groups",
    "tch-fem": "Female teachers - as percent of all teachers, by education level",
    "mng-fem": "Female school-management personnel - as perc of total school-management personnel, by education level",
}

database_infos_student = {
    # original_db_name : (filters, measure_column, prefix, suffix, pattern)
    "educ_uoe_fini04" : (f"A.PPS.PUBL+TOT_SEC.ED0+ED1+ED2+ED3_4+ED5-8+ED02-8.", ["isced11", "sector", "unit"], "edu-expst", "", ["name", "edu", "sector", "unit"]),
    "educ_uoe_ent02" : (f"A.NR.F01+F02+F021+F022+F023+F03+F031+F032+F04+F041+F042+F05+F051+F052+F053+F054+F06+F07+F071+F072+F073+F08+F081+F082+F083+F084+F09+F091+F092+F10+F101+F102+F103+F104.ED35+ED45+ED54+ED55+ED6+ED7+ED8.T+F+M.",
                         ["sex","isced11", "iscedf13", "unit"], "edu-nwen", "", ["name", "sex", "edu", "prog", "unit"]),
    "educ_uoe_ent03" : (f"A.PC.ED35+ED45+ED54+ED55+ED6+ED7+ED8.F01+F02+F021+F022+F023+F03+F031+F032+F04+F041+F042+F05+F051+F052+F053+F054+F06+F07+F071+F072+F073+F08+F081+F082+F083+F084+F09+F091+F092+F10+F101+F102+F103+F104.T+F+M.",
                         ["sex","isced11", "iscedf13", "unit"], "edu-dnwen", "", ["name", "sex", "edu", "prog", "unit"]),
    "educ_uoe_enra04" : (f"A...", ["isced11", "unit"], "edu-lvl", "", ["name", "edu", "unit"]),
    "educ_uoe_perp05" : (f"A...", ["isced11", "unit"], "tch-stud1", "", ["name", "edu", "unit"]),
    "educ_uoe_perp04" : (f"A...", ["isced11", "unit"], "tch-stud2", "", ["name", "edu", "unit"])
}

database_infos_teacher = {
    # original_db_name : (filters, measure_column, prefix, suffix, pattern)
    "educ_uoe_perd05" : (f"A...", ["isced11", "unit"], "tch-part", "", ["name", "edu", "unit"]),
    "educ_uoe_perd04" : (f"A...", ["isced11", "unit"], "mng-fem", "", ["name", "edu", "unit"]),
    "educ_uoe_perd03" : (f"A...", ["isced11", "unit"], "tch-fem", "", ["name", "edu", "unit"]),
    "educ_uoe_perp01" : (f"A.....", ["sex","isced11", "age", "unit"], "tch-pop", "", ["name", "sex", "edu", "age", "unit"])
}

db_name_student = 'e_schooling_student'
students_raw_df, dfs = serial_db(db_info=database_infos_student, 
                                description=descriptions_student, 
                                keys=keys, 
                                db_name=db_name_student, 
                                output_dfs=True)

students_df = pd.merge(students_raw_df, school1_df, on=[k.lower() for k in keys], how='outer')

pattern = ['name', 'sex', 'unit']
descriptions = {
    'out-uppersec': 'Out-of-school rate in population of upper secondary school age, by sex',
    'out-lowersec': 'Out-of-school rate in population of lower secondary school age, by sex',
    'stud-enrl': 'Pupils and students enrolled by education level, sex and field of education',
}
update_json(out_lowersec_df, db_name_student, pattern, descriptions) 
update_json(out_uppersec_df, db_name_student, pattern, descriptions)

pattern = ['name', 'prog', 'educ', 'sex', 'unit']
update_json(enrolled_df, db_name_student, pattern, descriptions) 

db_name_teacher = 'e_schooling_teacher'
teacher_df, dfs = serial_db(db_info=database_infos_teacher, 
                                description=descriptions_teacher, 
                                keys=keys, 
                                db_name=db_name_teacher, 
                                output_dfs=True)

# ------ Connection -------- #
create_table_sql(df=students_df, db_name=db_name_student)
default_connection(students_df, db_name_student)

# ------ Connection -------- #
create_table_sql(df=teacher_df, db_name=db_name_teacher)
default_connection(teacher_df, db_name_teacher)