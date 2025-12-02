import pandas as pd
from toolbi import default_connection
from tooldb import clean_stat
from functools import reduce
import tooloecd as to
import config

keys = config.KEYS
countries = config.COUNTRIES
start_year = config.START_YEAR
end_year = config.END_YEAR

# Repetition rate by level of education, by sex, as percentage of students
school_repetition_rate = to.get_oecd_dataset(
    dataset_id= "OECD.EDU.IMEP,DSD_EAG_UOE_NON_FIN_STUD@DF_UOE_NF_DIST_RPTR,1.0",
    filters= ".ISCED11_1+ISCED11_24+ISCED11_34.RPTR.....A......_T+F+M._T",
    start_year="2015",
    end_year="2023"
)

drop_cols = {'EDUCATION_TYPE', 'INTENSITY', 'EDUCATION_FIELD', 'GRADE', 'FREQ', 
             'ORIGIN', 'DESTINATION', 'INST_TYPE_EDU', 'MOBILITY', 'AGE', 'UNIT_MEASURE'}

school_repetition_rate.drop(columns=drop_cols.intersection(school_repetition_rate.columns), inplace=True)
school_repetition_rate = school_repetition_rate.rename(columns={'REF_AREA': 'geo'})
school_repetition_rate = clean_stat(school_repetition_rate, keys=['geo', 'TIME_PERIOD', 'SEX'], columns_to_pivot=['EDUCATION_LEV'])

new_names = ['rep_rate_prim', 'rep_rate_lower_sec', 'rep_rate_upper_sec']
school_repetition_rate.columns = list(school_repetition_rate.columns[:-3]) + new_names

datasets = [school_repetition_rate]
school_df = reduce(lambda left, right: pd.merge(left, right, on=[k.lower() for k in keys], how='outer'), datasets)
school_df = school_df.replace({float('nan'): None})

# ------ Connection -------- #
default_connection(school_df, 'o_households')