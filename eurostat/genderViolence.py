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

db_name = 'e_gender_violence'

# missed the cross table: gbv_ipv_frq, gbv_any_cnqv
descriptions = {}

descriptions["gbv_ipv_type"] = {
    'vtype-phy': 'Women who have experienced Physical violence',
    'vtype-thrt': 'Women who have experienced Threats violence',
    'vtype-psy': 'Women who have experienced Psychological violence',
    'vtype-phy-sx': 'Women who have experienced Physical or sexual violence',
    'vtype-phy-thrt-nsx': 'Women who have experienced Physical (including threats and not sexual) violence',
    'vtype-phy-thrt-sx': 'Women who have experienced Physical (including threats) or sexual violence',
    'vtype-psy-phy-thrt-sx': 'Women who have experienced Psychological, physical (including threats) or sexual violence',
    'vtype-psy-thrt': 'Women who have experienced Psychological or threats violence',
}

descriptions["gbv_ipv_occ"] = {
    'voccur-adlh': 'Women who have experienced violence in adulthood',
    'voccur-m12': 'Women who have experienced violence in last 12 months',
    'voccur-y5': 'Women who have experienced violence in last 5 years',
}

descriptions["gbv_ipv_age"] = {
    'vage-y18-29': 'Women from 18 to 29 years who have experienced violence',
    'vage-y18-74': 'Women from 18 to 74 years who have experienced violence',
    'vage-y30-44': 'Women from 30 to 44 years who have experienced violence',
    'vage-y45-64': 'Women from 45 to 64 years who have experienced violence',
    'vage-y65-74': 'Women from 65 to 74 years who have experienced violence',
}

descriptions["gbv_ipv_rp"] = {
    'vrp-clsper': 'Women who have experienced violence and reported to Close person',
    'vrp-hlth-soc': 'Women who have experienced violence and reported to Health or social service',
    'vrp-supp': 'Women who have experienced violence and reported to Support service',
    'vrp-polc': 'Women who have experienced violence and reported to Police',
    'vrp-any': 'Women who have experienced violence and reported to Any person or service',
    'vrp-hlth-soc-supp-polc': 'Women who have experienced violence and reported to Health, social or support service or police',
}

descriptions["gbv_ipv_cnq"] = {
    'veff-inj': 'Women who have experienced Physical injury after violence',
    'veff-psy': 'Women who have experienced Psychological consequences after violence',
    'veff-inj-psy': 'Women who have experienced Physical injury or psychological consequences after violence',
    'veff-life-dng': 'Women who have Felt that their life was in danger after violence',
}

descriptions["gbv_ipv_lim"] = {
    'vlmt-some': 'Women with Some level of disability (activity limitation) who have experienced violence',
    'vlmt-total': 'Women who have experienced violence',
    'vlmt-ltd-nsev-none': 'Women Limited but not severely or not limited at all (activity limitation) who have experienced violence',
    'vlmt-sev': 'Women with Severe level of disability (activity limitation) who have experienced violence',
    'vlmt-sm-sev': 'Women with Some or severe level of disability (activity limitation) who have experienced violence',
    'vlmt-none': 'Women with no disability (activity limitation) who have experienced violence',
}

descriptions["gbv_ipv_ed"] = {
    'veduc-ed0-2': 'Women with Less than primary, primary and lower secondary education (levels 0-2) who have experienced violence',
    'veduc-ed3-4': 'Women with Upper secondary and post-secondary non-tertiary education (levels 3 and 4) who have experienced violence',
    'veduc-ed5-8': 'Women with Tertiary education (levels 5-8) who have experienced violence',
}

descriptions["gbv_ipv_du"] = {
    'vurb-deg1': 'Women with residence in Cities who have experienced violence',
    'vurb-deg2': 'Women with residence in Towns and suburbs who have experienced violence ',
    'vurb-deg3': 'Women with residence in Rural areas who have experienced violence',
}

descriptions["gbv_ipv_cob"] = {
    'vbrth-eu-for': 'Women from EU-countries except reporting country who have experienced violence',
    'vbrth-neu-for': 'Women from Non-EU countries nor reporting country (aggregate changing according to the context) who have experienced violence',
    'vbrth-nat': 'Women from Reporting country who have experienced violence',
}

descriptions["gbv_ipv_rtog"] = {
    'vperp-iptn-tgt': 'Women who have experienced repeated violence by Intimate partner while being together - male or female',
    'vperp-iptn-sep': 'Women who have experienced repeated violence by Intimate partner after separation - male or female',
}

descriptions["gbv_ipv_roft"] = {
    'vfreq-ge1w': 'Women who have experienced repeated violence At least once a week',
    'vfreq-lt1m': 'Women who have experienced repeated violence Less than once a month',
    'vfreq-ge1m': 'Women who have experienced repeated violence At least once a month',
}

descriptions["gbv_ipv_rdur"] = {
    'vdur-y-lt1': 'Women who have experienced repeated violence for Less than 1 year',
    'vdur-y1-5': 'Women who have experienced repeated violence for From 1 to 5 years',
    'vdur-y-gt5': 'Women who have experienced repeated violence for Over 5 years',
}

descriptions["gbv_ipv_ecage"] = {
    'vecon-age-y18-29': 'Women From 18 to 29 years who have experienced economic violence (forbidding the respondent to work, controlling the finances of the whole family)',
    'vecon-age-y18-74': 'Women From 18 to 74 years who have experienced economic violence (forbidding the respondent to work, controlling the finances of the whole family)',
    'vecon-age-y30-44': 'Women From 30 to 44 years who have experienced economic violence (forbidding the respondent to work, controlling the finances of the whole family)',
    'vecon-age-y45-64': 'Women From 45 to 64 years who have experienced economic violence (forbidding the respondent to work, controlling the finances of the whole family)',
    'vecon-age-y65-74': 'Women From 65 to 74 years who have experienced economic violence (forbidding the respondent to work, controlling the finances of the whole family)',
}

descriptions["gbv_npv_type"] = {
    'vtype-rape': 'Women who have experienced Rape violence',
    'vtype-sx': 'Women who have experienced Sexual violence',
}

descriptions["gbv_npv_perp"] = {
    'vperp-nptn': 'Women who have experienced violence by Non-partner - male or female',
    'vperp-nptn-m': 'Women who have experienced violence by Non-partner - male',
    'vperp-nptn-f': 'Women who have experienced violence by Non-partner - female',
    'vperp-fam-rel': 'Women who have experienced violence by Family member or relative - male or female',
    'vperp-fam-rel-m': 'Women who have experienced violence by Family member or relative - male',
    'vperp-knw': 'Women who have experienced violence by Any known - male or female',
    'vperp-knw-m': 'Women who have experienced violence by Any known - male',
    'vperp-knw-oth': 'Women who have experienced violence by Other known (non-family or relative) - male or female',
    'vperp-knw-oth-m': 'Women who have experienced violence by Other known (non-family or relative) - male',
    'vperp-strng': 'Women who have experienced violence by Stranger - male or female',
    'vperp-strng-m': 'Women who have experienced violence by Stranger - male',
}

descriptions["gbv_any_injocc"] = {
    'vinj-adlh': 'Women who have experienced violence in adulthood',
    'vinj-m12': 'Women who have experienced violence in last 12 months',
    'vinj-y5': 'Women who have experienced violence in last 5 years',
}

descriptions["gbv_any_perp"] = {
    'vperp-perp1': 'Women who have experienced violence by One perpetrator type',
    'vperp-perp-multi': 'Women who have experienced violence by Multiple perpetrator types',
}

database_infos = {
    # original_db_name : (filters, measure_column, prefix, suffix, pattern)
    "gbv_any_type" : ("A...", "violence", "type", "any-perp", ['name', 'bywho', 'unit']),
    "gbv_any_occ" : ("A...", "occur", "occur", "any-perp", ['name', 'bywho', 'unit']),
    "gbv_any_age" : ("A...", "age", "age", "any-perp", ['name', 'bywho', 'unit']),
    "gbv_any_rp" : ("A...", "pers_serv", "rp", "any-perp", ['name', 'bywho', 'unit']),
    "gbv_any_cnq" : ("A...", "effect", "eff", "any-perp", ['name', 'bywho', 'unit']),
    "gbv_any_lim" : ("A...", "lev_limit", "lmt", "any-perp", ['name', 'bywho', 'unit']),
    "gbv_any_ed" : ("A...", "isced11", "educ", "any-perp", ['name', 'bywho', 'unit']),
    "gbv_any_du" : ("A...", "deg_urb", "urb", "any-perp", ['name', 'bywho', 'unit']),
    "gbv_any_cob" : ("A...", "c_birth", "brth", "any-perp", ['name', 'bywho', 'unit']),
    "gbv_any_perp" : ("A...", "perp", "perp", "any-perp", ['name', 'bywho', 'unit']),
    "gbv_any_roft" : ("A...", "frequenc", "freq", "any-perp", ['name', 'bywho', 'unit']),
    "gbv_any_rdur" : ("A...", "duration", "dur", "any-perp", ['name', 'bywho', 'unit']),
    "gbv_any_injocc" : ("A...", "occur", "inj", "any-perp", ['name', 'bywho', 'unit']),

    "gbv_ipv_type" : ("A...", "violence", "type", "intim-part", ['name', 'bywho', 'unit']),
    "gbv_ipv_occ" : ("A...", "occur", "occur", "intim-part", ['name', 'bywho', 'unit']),
    "gbv_ipv_age" : ("A...", "age", "age", "intim-part", ['name', 'bywho', 'unit']),
    "gbv_ipv_rp" : ("A...", "pers_serv", "rp", "intim-part", ['name', 'bywho', 'unit']),
    "gbv_ipv_cnq" : ("A...", "effect", "eff", "intim-part", ['name', 'bywho', 'unit']),
    "gbv_ipv_lim" : ("A...", "lev_limit", "lmt", "intim-part", ['name', 'bywho', 'unit']),
    "gbv_ipv_ed" : ("A...", "isced11", "educ", "intim-part", ['name', 'bywho', 'unit']),
    "gbv_ipv_du" : ("A...", "deg_urb", "urb", "intim-part", ['name', 'bywho', 'unit']),
    "gbv_ipv_cob" : ("A...", "c_birth", "brth", "intim-part", ['name', 'bywho', 'unit']),
    "gbv_ipv_rtog" : ("A...", "perp", "perp", "intim-part", ['name', 'bywho', 'unit']),
    "gbv_ipv_roft" : ("A...", "frequenc", "freq", "intim-part", ['name', 'bywho', 'unit']),
    "gbv_ipv_rdur" : ("A...", "duration", "dur", "intim-part", ['name', 'bywho', 'unit']),
    "gbv_ipv_ecage" : ("A...", "age", "econ-age", "intim-part", ['name', 'bywho', 'unit']),

    "gbv_npv_type" : ("A...", "violence", "type", "nonint-part", ['name', 'bywho', 'unit']),
    "gbv_npv_occ" : ("A...", "occur", "occur", "nonint-part", ['name', 'bywho', 'unit']),
    "gbv_npv_age" : ("A...", "age", "age", "nonint-part", ['name', 'bywho', 'unit']),
    "gbv_npv_rp" : ("A...", "pers_serv", "rp", "nonint-part", ['name', 'bywho', 'unit']),
    "gbv_npv_cnq" : ("A...", "effect", "eff", "nonint-part", ['name', 'bywho', 'unit']),
    "gbv_npv_lim" : ("A...", "lev_limit", "lmt", "nonint-part", ['name', 'bywho', 'unit']),
    "gbv_npv_ed" : ("A...", "isced11", "educ", "nonint-part", ['name', 'bywho', 'unit']),
    "gbv_npv_du" : ("A...", "deg_urb", "urb", "nonint-part", ['name', 'bywho', 'unit']),
    "gbv_npv_cob" : ("A...", "c_birth", "brth", "nonint-part", ['name', 'bywho', 'unit']),
    "gbv_npv_perp" : ("A...", "perp", "perp", "nonint-part", ['name', 'bywho', 'unit']),
    "gbv_npv_roft" : ("A...", "frequenc", "freq", "nonint-part", ['name', 'bywho', 'unit']),
    "gbv_npv_rdur" : ("A...", "duration", "dur", "nonint-part", ['name', 'bywho', 'unit']),

    "gbv_dv_type" : ("A...", "violence", "type", "domest-perp", ['name', 'bywho', 'unit']),
    "gbv_dv_occ" : ("A...", "occur", "occur", "domest-perp", ['name', 'bywho', 'unit']),
    "gbv_dv_age" : ("A...", "age", "age", "domest-perp", ['name', 'bywho', 'unit']),
    "gbv_dv_lim" : ("A...", "lev_limit", "lmt", "domest-perp", ['name', 'bywho', 'unit']),
    "gbv_dv_ed" : ("A...", "isced11", "educ", "domest-perp", ['name', 'bywho', 'unit']),
    "gbv_dv_du" : ("A...", "deg_urb", "urb", "domest-perp", ['name', 'bywho', 'unit']),
    "gbv_dv_cob" : ("A...", "c_birth", "brth", "domest-perp", ['name', 'bywho', 'unit']),
}

# Gender violence databases divided between different types of perpetrators and other
# dimensions such as occurence, degree of urbanization, education, injuries, etc.
viol_dfs = {}
dbs_list = [db for db in database_infos.keys()]

for i, db in enumerate(dbs_list):
    filters, measure_columns, prefix, suffix, pattern = database_infos.get(db)
    measure_columns = measure_columns if isinstance(measure_columns, (list, tuple)) else [measure_columns]
    df = et.get_eurostat_dataset(
        dataset_code=db,
        filters=filters
    )

    for col in measure_columns:
        df[col] = df[col].str.replace('_', '-')
    df = clean_stat(df, keys=keys, columns_to_pivot=measure_columns, prefix=f'v{prefix}-', suffix=f'{suffix}_%')

    viol_dfs[i+1] = df

    if db in descriptions:
        update_json(df, db_name, pattern, descriptions[db])
    else:
        update_json(df, db_name, pattern, descriptions)

gv_df = reduce(lambda left, right: pd.merge(left, right, on=["geo", "time_period"], how="outer"), viol_dfs.values())


# More Genderviolence indicators on sexual harassment at work, stalking, violence in childhood
# and awareness of support services
db_name_spec = 'e_gender_violence_spec'
descriptions = {}

#descriptions["gbv_shw_comm"] = {
#    'v-sp-cmn-vcmn': 'Very common Perception of Women as victims/non-victims of sexual harassment at work',
#    'v-sp-cmn-fcmn': 'Fairly common Perception of Women as victims/non-victims of sexual harassment at work',
#    'v-sp-cmn-nvcmn': 'Not very common Perception of Women as victims/non-victims of sexual harassment at work',
#    'v-sp-cmn-ncmn': 'Not common at all Perception of Women as victims/non-victims of sexual harassment at work',
#}

descriptions["gbv_shw_occ"] = {
    'v-sp-occur-adlh': 'Women who have experienced stalking or sexual harassment at work in adulthood',
    'v-sp-occur-m12': 'Women who have experienced stalking or sexual harassment at work in last 12 months',
    'v-sp-occur-y5': 'Women who have experienced stalking or sexual harassment at work in last 5 years',
}

descriptions["gbv_shw_age"] = {
    'v-sp-age-y18-29': 'Women from 18 to 29 years who have experienced stalking or sexual harassment at work',
    'v-sp-age-y18-74': 'Women from 18 to 74 years who have experienced stalking or sexual harassment at work',
    'v-sp-age-y30-44': 'Women from 30 to 44 years who have experienced stalking or sexual harassment at work',
    'v-sp-age-y45-64': 'Women from 45 to 64 years who have experienced stalking or sexual harassment at work',
    'v-sp-age-y65-74': 'Women from 65 to 74 years who have experienced stalking or sexual harassment at work',
}

descriptions["gbv_shw_rp"] = {
    'v-sp-rp-nofcl-wrk': 'Women who have experienced sexual harassment and reported to Unofficial (colleague, close person or someone else)',
    'v-sp-rp-any': 'Women who have experienced sexual harassment and reported to Any person or service',
    'v-sp-rp-ofcl-wrk': 'Women who have experienced sexual harassment and reported to Official body (support/health/social service or police or officials at work)',
}

descriptions["gbv_shw_perp"] = {
    'v-sp-perp-cw-m': 'Women who have experienced sexual harassment by Co-worker - male',
    'v-sp-perp-boss-m': 'Women who have experienced violsexual harassment at workence by Boss - male',
    'v-sp-perp-oth-w-m': 'Women who have experienced violsexual harassment at workence by Other work-related - male',
    'v-sp-perp-perp-m': 'Women who have experienced violsexual harassment at workence by Perpetrators - male',
}

descriptions["gbv_shw_frq"] = {
    'v-sp-freq-t1': 'Women who have experienced sexual harassment Once (one time)',
    'v-sp-freq-rpt': 'Women who have experienced sexual harassment Repeated',
}

descriptions["gbv_shw_type"] = {
    'v-sp-type-sxh-wrk': 'Women who have experienced sexual harassment at work',
    'v-sp-type-msg': 'Women who have experienced Violence using messaging apps',
    'v-sp-type-sm': 'Women who have experienced Violence using social media',
    'v-sp-type-otl': 'Women who have experienced Violence using online tools',
    'v-sp-type-notl': 'Women who have experienced Violence not using online tools',
}

descriptions["gbv_shw_snwage"] = {
    'v-sp-snwage-y18-29': 'Women from 18 to 29 years who have experienced sexual harassment via social network and messages',
    'v-sp-snwage-y18-74': 'Women from 18 to 74 years who have experienced sexual harassment via social network and messages',
    'v-sp-snwage-y30-44': 'Women from 30 to 44 years who have experienced sexual harassment via social network and messages',
    'v-sp-snwage-y45-64': 'Women from 45 to 64 years who have experienced sexual harassment via social network and messages',
    'v-sp-snwage-y65-74': 'Women from 65 to 74 years who have experienced sexual harassment via social network and messages',
}

descriptions["gbv_st_rp"] = {
    'v-sp-rp-polc': 'Women who have experienced stalking and reported to Police',
    'v-sp-rp-supp-leg': 'Women who have experienced stalking and reported to Legal or victim support service',
    'v-sp-rp-supp-polc': 'Women who have experienced stalking and reported to Support service or police',
}

descriptions["gbv_st_perp"] = {
    'v-sp-perp-perp-f': 'Women who have experienced stalking by Perpetrators - female',
    'v-sp-perp-perp': 'Women who have experienced stalking by Perpetrators - male or female',
    'v-sp-perp-perp-m': 'Women who have experienced stalking by Perpetrators - male',
    'v-sp-perp-iptn': 'Women who have experienced stalking by Intimate partner - male or female',
    'v-sp-perp-nptn': 'Women who have experienced stalking by Non-partner - male or female',
    'v-sp-perp-nptn-m': 'Women who have experienced stalking by Non-partner - male',
    'v-sp-perp-nptn-f': 'Women who have experienced stalking by Non-partner - female',
}

descriptions["gbv_st_cnq"] = {
    'v-sp-eff-chg-tlf-cl-snw': 'Women who have experienced stalking and consequently Changed telephone number/email address or closed social network',
    'v-sp-eff-impl-prot': 'Women who have experienced stalking and consequently Implemented protecting measures (eg changed going out or usual route or taking with knife, pepper spray etc)',
    'v-sp-eff-mov-res-chg-wrk': 'Women who have experienced stalking and consequently Moved to another residence or changed working or studying',
}

descriptions["gbv_awr_serv"] = {
    'vawr': 'Women as victims/non-victims of violence, by awareness of the existence of support services',
}

descriptions["gbv_awr_leg"] = {
    'vawr-aid': 'Women as victims/non-victims of violence, by awareness of free legal aid',
}

descriptions["gbv_ch_age"] = {
    'v-ch-age-y18-29': 'Women from 18 to 29 years who have experienced sexual violence during childhood',
    'v-ch-age-y18-74': 'Women from 18 to 74 years who have experienced sexual violence during childhood',
    'v-ch-age-y30-44': 'Women from 30 to 44 years who have experienced sexual violence during childhood',
    'v-ch-age-y45-64': 'Women from 45 to 64 years who have experienced sexual violence during childhood',
    'v-ch-age-y65-74': 'Women from 65 to 74 years who have experienced sexual violence during childhood',
}

descriptions["gbv_ch_perp"] = {
    'v-ch-perp-perp': 'Women who have experienced sexual violence during childhood by Perpetrators - male or female',
    'v-ch-perp-perp-m': 'Women who have experienced sexual violence during childhood by Perpetrators - male',
    'v-ch-perp-fam-rel': 'Women who have experienced sexual violence during childhood by Family member or relative - male or female',
    'v-ch-perp-knw': 'Women who have experienced sexual violence during childhood by Any known - male or female',
    'v-ch-perp-knw-oth': 'Women who have experienced sexual violence during childhood by Other known (non-family or relative) - male or female',
    'v-ch-perp-strng': 'Women who have experienced sexual violence during childhood by Stranger - male or female',
}

descriptions["gbv_ch_rp"] = {
    'v-ch-rp-any': 'Women who have experienced violence during childhood and reported to Any person or service',
    'v-ch-rp-ofcl-sch': 'Women who have experienced violence during childhood and reported to Official body (support/health/social service or police or someone in school)',
    'v-ch-rp-nofcl-sch': 'Women who have experienced violence during childhood and reported to Unofficial (friends, family member or someone else)',
}

descriptions["gbv_ch_ph"] = {
    'v-ch-phpar-mot': 'Women who have experienced physical violence during childhood committed by the Mother',
    'v-ch-phpar-fat': 'Women who have experienced physical violence during childhood committed by the Father',
    'v-ch-phpar-par': 'Women who have experienced physical violence during childhood committed by Parents',
}

descriptions["gbv_ch_ps"] = {
    'v-ch-pspar-mot': 'Women who have experienced psychological violence during childhood committed by the Mother',
    'v-ch-pspar-fat': 'Women who have experienced psychological violence during childhood committed by the Father',
    'v-ch-pspar-par': 'Women who have experienced psychological violence during childhood committed by Parents',
}

descriptions["gbv_ch_phps"] = {
    'v-ch-pshpar-mot': 'Women who have experienced physical or psychological violence during childhood committed by the Mother',
    'v-ch-pshpar-fat': 'Women who have experienced physical or psychological violence during childhood committed by the Father',
    'v-ch-pshpar-par': 'Women who have experienced physical or psychological violence during childhood committed by Parents',
}

descriptions["gbv_ch_vbp"] = {
    'v-ch-vbp-mot': 'Women who have witnessed violence between parents during childhood committed by the Mother',
    'v-ch-vbp-fat': 'Women who have witnessed violence between parents during childhood committed by the Father',
    'v-ch-vbp-par': 'Women who have witnessed violence between parents during childhood committed by Parents',
}

database_infos = {
    # original_db_name : (filters, measure_column, prefix, suffix, pattern)
    "gbv_shw_type" : ("A...", "violence", "-sp-type-", "harass-atwork", ['name', 'bywho', 'unit']),
    "gbv_shw_occ" : ("A...", "occur", "-sp-occur-", "harass-atwork", ['name', 'bywho', 'unit']),
    "gbv_shw_age" : ("A...", "age", "-sp-age-", "harass-atwork", ['name', 'bywho', 'unit']),
    "gbv_shw_rp" : ("A...", "pers_serv", "-sp-rp-", "harass-atwork", ['name', 'bywho', 'unit']),
    "gbv_shw_perp" : ("A...", "perp", "-sp-perp-", "harass-atwork", ['name', 'bywho', 'unit']),
    "gbv_shw_frq" : ("A...", "frequenc", "-sp-freq-", "harass-atwork", ['name', 'bywho', 'unit']),
    "gbv_shw_snwage" : ("A...", "age", "-sp-snwage-", "harass-atwork", ['name', 'bywho', 'unit']),

    "gbv_st_occ" : ("A...", "occur", "-sp-occur-", "stalk", ['name', 'bywho', 'unit']),
    "gbv_st_age" : ("A...", "age", "-sp-age-", "stalk", ['name', 'bywho', 'unit']),
    "gbv_st_rp" : ("A...", "pers_serv", "-sp-rp-", "stalk", ['name', 'bywho', 'unit']),
    "gbv_st_perp" : ("A...", "perp", "-sp-perp-", "stalk", ['name', 'bywho', 'unit']),
    "gbv_st_cnq" : ("A...", "effect", "-sp-eff-", "stalk", ['name', 'bywho', 'unit']),

    "gbv_awr_serv" : ("A....", ['yn_vict', 'yn_awr'], "awr", "", ['name', 'vict', 'awr', 'unit']),
    "gbv_awr_leg" : ("A....", ['yn_vict', 'yn_awr'], "awr-aid", "", ['name', 'vict', 'awr', 'unit']),

    "gbv_ch_age" : ("A...", "age", "-ch-age-", "inchildhood", ['name', 'when', 'unit']),
    "gbv_ch_rp" : ("A...", "pers_serv", "-ch-rp-", "inchildhood", ['name', 'when', 'unit']),
    "gbv_ch_perp" : ("A...", "perp", "-ch-perp-", "inchildhood", ['name', 'when', 'unit']),
    "gbv_ch_ph" : ("A...", "perp", "-ch-phpar-", "inchildhood", ['name', 'when', 'unit']),
    "gbv_ch_ps" : ("A...", "perp", "-ch-pspar-", "inchildhood", ['name', 'when', 'unit']),
    "gbv_ch_phps" : ("A...", "perp", "-ch-pshpar-", "inchildhood", ['name', 'when', 'unit']),
    "gbv_ch_vbp" : ("A....", ["perp", "violence"], "-ch-vbp-", "inchildhood", ['name', 'when', 'type', 'unit']),
}

viol_spec_dfs = {}
dbs_spec_list = [db for db in database_infos.keys()]

for i, db in enumerate(dbs_spec_list):
    filters, measure_columns, prefix, suffix, pattern = database_infos.get(db)
    measure_columns = measure_columns if isinstance(measure_columns, (list, tuple)) else [measure_columns]
    df = et.get_eurostat_dataset(
        dataset_code=db,
        filters=filters
    )
    for col in measure_columns:
        df[col] = df[col].str.replace('_', '-')
    df = clean_stat(df, keys=keys, columns_to_pivot=measure_columns, prefix=f'v{prefix}', suffix=f'{suffix}_%')

    viol_spec_dfs[i+1] = df

    if db in descriptions:
        update_json(df, db_name_spec, pattern, descriptions[db])
    else:
        update_json(df, db_name_spec, pattern, descriptions)

gv_spec_df = reduce(lambda left, right: pd.merge(left, right, on=["geo", "time_period"], how="outer"), viol_spec_dfs.values())

# ------ Connection -------- #
create_table_sql(df=gv_df, db_name=db_name)
create_table_sql(df=gv_spec_df, db_name=db_name_spec)
default_connection(gv_df, db_name, db_source='Eurostat')
default_connection(gv_spec_df, db_name_spec, db_source='Eurostat')