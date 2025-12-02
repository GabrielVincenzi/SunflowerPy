import pandas as pd
from toolbi import default_connection
from tooldb import clean_stat, update_json
from functools import reduce
import tooloecd as to
import config

keys = config.KEYS
countries = config.OECD_COUNTRIES

# Trust, security and dignity database:
# Trust in national, local government, civil service, court, legislature
# Personal data usage, political efficiency, transparency, participation, majority strenght
trust_df = to.get_oecd_dataset(
    dataset_id= "OECD.GOV.GIP,DSD_GOV_INT@DF_GOV_TDG_2025,1.0",
    filters= f"A.{countries}......",
    start_year=2021,
)

drop_cols = {'CATEGORY', 'EDITION', 'SECTOR', 'UNIT_MEASURE'}

trust_df.drop(columns=drop_cols.intersection(trust_df.columns), inplace=True)
trust_df = trust_df.rename(columns={'REF_AREA': 'geo'})
trust_df['MEASURE'] = trust_df['MEASURE'].str.replace('_', '-')
trust_df = clean_stat(trust_df, keys=keys, columns_to_pivot=['MEASURE', 'SCALE'])


# Satisfaction with public services database:
# Satisfaction with education, healthcare, administration,
# NEET, PISA reading and math, affordable civil justice, free justice
satisf_df = to.get_oecd_dataset(
    dataset_id= "OECD.GOV.GIP,DSD_GOV_INT@DF_GOV_SPS_2025,1.0",
    filters= f"A.{countries}.CS_HC+CS_ES+TRUST_S_AS+THE_POP+RE_Y_NEET+PEE_PISA_R+PEE_PISA_M+AJ_AACJ+EFJ_RLCJ_FGI.....",
    start_year=2018,
)

drop_cols = {'CATEGORY', 'EDITION', 'SECTOR', 'UNIT_MEASURE', 'SCALE'}

satisf_df.drop(columns=drop_cols.intersection(satisf_df.columns), inplace=True)
satisf_df = satisf_df.rename(columns={'REF_AREA': 'geo'})
satisf_df = clean_stat(satisf_df, keys=keys, columns_to_pivot=['MEASURE'])
satisf_df[satisf_df.columns[2:]] = satisf_df.groupby("geo")[satisf_df.columns[2:]].ffill()
satisf_df = satisf_df.query('time_period == 2024')
satisf_df['time_period'] = 2023
satisf_df.columns = [
    col.replace('_', '-') + '_%' if col not in [k.lower() for k in keys] else col for col in satisf_df.columns
]

datasets = [trust_df, satisf_df]
feel_df = reduce(lambda left, right: pd.merge(left, right, on=[k.lower() for k in keys], how='outer'), datasets)
feel_df = feel_df.replace({float('nan'): None})


# ------ JSON update -------- #
db_name = 'o_trust_satisf'
pattern = ['name', 'scale']
descriptions = {
    'trust-ng': 'Trust in national government',
    'trust-dat': 'Personal data used for legitimate purposes',
    'trust-pol': 'National policy would be changed if majority expressed view against it',
    'trust-pe-ext': 'Political efficacy, confident that political system allows them to have a say',
    'trust-pe-int': 'Political efficacy, confident in own ability to participate in politics',
    'trust-le': 'Trust legislature',
    'trust-lg': 'Trust in local government',
    'trust-cs': 'Trust in civil service',
    'trust-cl': 'Trust in courts and legal system',
}
update_json(trust_df, db_name, pattern, descriptions)

pattern = ['name', 'unit']
descriptions = {
    'aj-aacj': 'People can access and afford civil justice',
    'cs-es': 'Satisfaction with education system',
    'cs-hc': 'Satisfaction with healthcare system',
    'efj-rlcj-fgi': 'Civil justice is free of improper government influence',
    'pee-pisa-m': 'PISA mean score in mathematics',
    'pee-pisa-r': 'PISA mean score in reading',
    're-y-neet': 'Young people not in education, employment or training',
    'the-pop': 'Total health expenditures per capita',
    'trust-s-as': 'Satisfaction with administrative services',
}
update_json(satisf_df, db_name, pattern, descriptions)

# ------ Connection -------- #
default_connection(feel_df, 'o_trust_satisf', db_source='OECD')