import pandas as pd
from tools.toolbi import default_connection
from tools.tooldb import clean_stat
from functools import reduce
from tools.tooldb import last_observed_per_group
import tools.tooloecd as to
import config

keys = config.KEYS
countries = config.OECD_COUNTRIES
start_year = config.START_YEAR
end_year = config.END_YEAR

# Current well-being database
wellbeing_df = to.get_oecd_dataset(
    dataset_id= "OECD.WISE.WDP,DSD_HSL@DF_HSL_CWB,1.1",
    filters= f"{countries}.1_1+1_2+1_3+1_3_VER+1_4+2_1+2_2+2_5+3_2+5_1+5_2+6_1+6_1_DEP+6_1_VER+6_2_VER+6_2_DEP+6_2+6_3+6_3_DEP+6_3_VER+6_4+6_4_VER+6_4_DEP+6_5+6_5_DEP+6_5_VER+8_1+8_2+9_3+9_2+11_1.....",
    start_year=2010
)

drop_cols = {'DOMAIN', 'UNIT_MEASURE'}
wellbeing_df = wellbeing_df.loc[wellbeing_df['UNIT_MEASURE'] != 'PT_WG_SAL_M_MEDIAN']
wellbeing_df.drop(columns=drop_cols.intersection(wellbeing_df.columns), inplace=True)
wellbeing_df = wellbeing_df.rename(columns={'REF_AREA': 'geo'})
wellbeing_df = clean_stat(wellbeing_df, keys=keys, columns_to_pivot=['MEASURE', 'AGE', 'SEX', 'EDUCATION_LEV'])
wellbeing_df = wellbeing_df.groupby('geo', group_keys=False).apply(last_observed_per_group, include_groups=False).reset_index()
wellbeing_df['time_period'] = 2024


# Time used database:
# For paid, unpaid work, leisure and perconal care
timespent_df = to.get_oecd_dataset(
    dataset_id= "OECD.WISE.INE,DSD_TIME_USE@DF_TIME_USE,1.0",
    filters= f"{countries}.PAW+PCA+LEI+UPW.M+F+_T"
)

timespent_df = timespent_df.rename(columns={'REF_AREA': 'geo'})
timespent_df['SEX'] = timespent_df['SEX'].astype(str).str.replace("_", "", regex=False)
timespent_df['TIME_PERIOD'] = 2024
timespent_df = clean_stat(timespent_df, keys=['geo', 'TIME_PERIOD'], columns_to_pivot=['MEASURE', 'SEX'])

datasets = [timespent_df, wellbeing_df]
well_df = reduce(lambda left, right: pd.merge(left, right, on=[k.lower() for k in keys], how='outer'), datasets)
well_df = well_df.replace({float('nan'): None})

# ------ Connection -------- #
default_connection(well_df, 'o_wellbeing')