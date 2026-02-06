from tools.toolbi import default_connection, create_table_sql
from tools.tooleurostat import serial_db
import config

keys = config.KEYS
countries = config.COUNTRIES
start_year = config.START_YEAR
end_year = config.END_YEAR

import config

keys = config.KEYS
countries = config.COUNTRIES
start_year = config.START_YEAR
end_year = config.END_YEAR

descriptions_selfrep = {
    "svdp-lim": "Severity of current depressive symptoms by level of disability (activity limitation), sex and age",
    "svdp-edu": "Severity of current depressive symptoms by level of education, sex and age",
    "svdp-inc": "Severity of current depressive symptoms by income quintile, sex and age",
    "svdp-urb": "Severity of current depressive symptoms by sex, age and degree of urbanisation",
    "svdp-citiz": "Severity of current depressive symptoms by sex, age and country of citizenhip",
    
    "svbp-lim": "Severity of bodily pain by level of disability (activity limitation), sex and age",
    "svbp-edu": "Severity of bodily pain by sex, age and educational attainment level",
    "svbp-citiz": "Severity of bodily pain by sex, age and country of citizenship",

    "sph-lab": "Self-perceived health by sex, age and labour status",
    "sph-edu": "Self-perceived health by sex, age and educational attainment level",
    "sph-inc": "Self-perceived health by sex, age and income quintile",
    "sph-urb": "Self-perceived health by sex, age and degree of urbanisation",
    "sph-citiz": "Self-perceived health by sex, age and groups of country of citizenship",
}

db_name_selfrep_dep = "e_health_selfrep_dep"
db_name_selfrep_bod = "e_health_selfrep_bod"
db_name_selfrep = "e_health_selfrep" # Look at the numerosity

database_infos_selfrep_ehis_dep = {
    # original_db_name : (filters, measure_column, prefix, suffix, pattern)
    "hlth_ehis_mh2d" : (f"A......", ["sex", "age", "levels", "lev_limit", "unit"], "svdp-lim", "", ["name", "sex", "age", "level", "lev-lim", "unit"]),
    "hlth_ehis_mh2e" : (f"A......", ["sex", "age", "levels", "isced11", "unit"], "svdp-edu", "", ["name", "sex", "age", "level", "educ", "unit"]),
    "hlth_ehis_mh2i" : (f"A......", ["sex", "age", "levels", "quant_inc", "unit"], "svdp-inc", "", ["name", "sex", "age", "level", "inc", "unit"]),
    "hlth_ehis_mh2u" : (f"A......", ["sex", "age", "levels", "deg_urb", "unit"], "svdp-urb", "", ["name", "sex", "age", "level", "deg-urb", "unit"]),
    "hlth_ehis_mh2c" : (f"A......", ["sex", "age", "lev_perc", "citizen", "unit"], "svdp-citiz", "", ["name", "sex", "age", "level", "citiz", "unit"]),
}

database_infos_selfrep_ehis_bod = {
    "hlth_ehis_pn1e" : (f"A......", ["sex", "age", "levels", "isced11", "unit"], "svbp-edu", "", ["name", "sex", "age", "level", "educ", "unit"]),
    "hlth_ehis_pn1c" : (f"A......", ["sex", "age", "lev_perc", "citizen", "unit"], "svbp-citiz", "", ["name", "sex", "age", "level", "citiz", "unit"]),
    "hlth_ehis_pn1d" : (f"A......", ["sex", "age", "lev_perc", "lev_limit", "unit"], "svbp-lim", "", ["name", "sex", "age", "level", "lev-lim", "unit"]),
}

database_infos_selfrep_silc = {
    "hlth_silc_01" : (f"A......", ["sex", "age", "levels", "wstatus", "unit"], "sph-lab", "", ["name", "sex", "age", "level", "work", "unit"]),
    "hlth_silc_02" : (f"A......", ["sex", "age", "levels", "isced11", "unit"], "sph-edu", "", ["name", "sex", "age", "level", "educ", "unit"]),
    "hlth_silc_10" : (f"A......", ["sex", "age", "levels", "quantile", "unit"], "sph-inc", "", ["name", "sex", "age", "level", "inc", "unit"]),
    "hlth_silc_18" : (f"A......", ["sex", "age", "levels", "deg_urb", "unit"], "sph-urb", "", ["name", "sex", "age", "level", "deg-urb", "unit"]),
    "hlth_silc_24" : (f"A......", ["sex", "age", "lev_perc", "citizen", "unit"], "sph-citiz", "", ["name", "sex", "age", "level", "citiz", "unit"]),
}

health_selfrep_dep_df, dfs_dep = serial_db(db_info=database_infos_selfrep_ehis_dep, 
                                   description=descriptions_selfrep,
                                   keys=keys, 
                                   db_name=db_name_selfrep_dep, 
                                   output_dfs=True)

health_selfrep_bod_df, dfs_bod = serial_db(db_info=database_infos_selfrep_ehis_bod, 
                                   description=descriptions_selfrep,
                                   keys=keys, 
                                   db_name=db_name_selfrep_bod, 
                                   output_dfs=True)


# ------ Connection -------- #
create_table_sql(df=health_selfrep_dep_df, db_name=db_name_selfrep_dep)
create_table_sql(df=health_selfrep_bod_df, db_name=db_name_selfrep_bod)
default_connection(health_selfrep_dep_df, db_name_selfrep_dep)
default_connection(health_selfrep_bod_df, db_name_selfrep_bod)



## Overall perceived social support 
descriptions_socsupp = {
    "ssup-edu": "Overall perceived social support by sex, age and educational attainment level",
    "ssup-urb": "Overall perceived social support by sex, age and degree of urbanisation",
    "ssup-citiz": "Overall perceived social support by sex, age and country of citizenship",
    "ssup-lim": "Overall perceived social support by level of disability (activity limitation), sex and age",
}

db_name_socsupp = "e_health_socsupp"

database_infos_socsupp = {
    # original_db_name : (filters, measure_column, prefix, suffix, pattern)
    "hlth_ehis_ss1e" : (f"A......", ["sex", "age", "lev_perc", "isced11", "unit"], "ssup-edu", "", ["name", "sex", "age", "level", "edu", "unit"]),
    "hlth_ehis_ss1u" : (f"A......", ["sex", "age", "lev_perc", "deg_urb", "unit"], "ssup-urb", "", ["name", "sex", "age", "level", "deg-urb", "unit"]),
    "hlth_ehis_ss1c" : (f"A......", ["sex", "age", "lev_perc", "citizen", "unit"], "ssup-citiz", "", ["name", "sex", "age", "level", "citiz", "unit"]),
    "hlth_ehis_ss1d" : (f"A......", ["sex", "age", "lev_perc", "lev_limit", "unit"], "ssup-lim", "", ["name", "sex", "age", "level", "lev-lim", "unit"]),
}

health_ssup_df, dfs = serial_db(db_info=database_infos_socsupp, 
                                   description=descriptions_socsupp, 
                                   keys=keys, 
                                   db_name=db_name_socsupp, 
                                   output_dfs=True)