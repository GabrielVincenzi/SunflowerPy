import pandas as pd
from tools.toolbi import default_connection
from tools.tooldb import clean_stat
from functools import reduce
import tools.tooloecd as to
import config

keys = config.KEYS
countries = config.OECD_COUNTRIES
start_year = config.START_YEAR
end_year = config.END_YEAR

# The average rates of employer social security contributions, employee social security contributions, and the total tax-wedge (or wage taxes + SSCs)
# Among single persons with no children
# Who earn 100% of the average wage
# With no special other status (the _Z “not applicable”)
tax_wedge_df = to.get_oecd_dataset(
    dataset_id= "OECD.CTP.TPS,DSD_TAX_WAGES_COMP@DF_TW_COMP,",
    filters= ".AV_R_EMPER_SSC+AV_R_EMPEE_SSC+AV_TW..S_C0.AW100._Z.A",
    start_year="1950"
)

tax_wedge_df = tax_wedge_df.rename(columns={'REF_AREA': 'geo'})
tax_wedge_df = clean_stat(tax_wedge_df, keys=keys, columns_to_pivot=['MEASURE', 'UNIT_MEASURE'])

# Global Revenue Statistics - Comparative tax revenues as Percentage of GDP
revenues_df = to.get_oecd_dataset(
    dataset_id= "OECD.CTP.TPS,DSD_REV_COMP_GLOBAL@DF_RSGLOBAL",
    filters= f"{countries}..S13.T_1110+T_1120+T_1200+T_2100+T_2200+T_2300+T_4100+T_4200+T_4300+T_5100+T_5111+_T..PT_B1GQ+XDC.A",
    start_year="1990",
    end_year="2023"
)

drop_cols = {'MEASURE', 'SECTOR', 'CTRY_SPECIFIC_REVENUE', 'FREQ'}
revenues_df.drop(columns=drop_cols.intersection(revenues_df.columns), inplace=True)
revenues_df = revenues_df.rename(columns={'REF_AREA': 'geo'})
revenues_df = clean_stat(revenues_df, keys=keys, columns_to_pivot=['STANDARD_REVENUE', 'UNIT_MEASURE'])


# This table provides a breakdown of government expenditure according to 
# the Classification of the Functions of Government (COFOG), 
# which shows how much governments spend in areas such as health, education, environmental protection, 
# defence and servicing public debt. 
# In million national currency at current prices.
expenditure_df = to.get_oecd_dataset(
    dataset_id= "OECD.SDD.NAD,DSD_NASEC10@DF_TABLE11,1.1",
    filters= f"A.{countries}.S13...OTE.._T+GF0101+GF0102+GF0103+GF0104+GF0105+GF0106+GF0107+GF0108+GF02+GF0201+GF0202+GF0203+GF0204+GF0205+GF03+GF0301+GF0302+GF0303+GF0304+GF0305+GF0306+GF04+GF0401+GF0402+GF0403+GF0404+GF0405+GF0406+GF0407+GF0408+GF0409+GF05+GF0501+GF0502+GF0503+GF0504+GF0505+GF0506+GF06+GF0601+GF0602+GF0603+GF0604+GF0605+GF0606+GF07+GF0701+GF0702+GF0703+GF0704+GF0705+GF0706+GF08+GF0801+GF0802+GF0803+GF0804+GF0805+GF0806+GF09+GF0901+GF0902+GF0903+GF0904+GF0905+GF0906+GF0907+GF0908+GF10+GF1001+GF1002+GF1003+GF1004+GF1005+GF1006+GF1007+GF1008+GF1009+GF01...V..",
    start_year="1995",
    end_year="2024"
)

drop_cols = {'TRANSACTION', 'SECTOR', 'COUNTERPART_SECTOR', 'ACCOUNTING_ENTRY', 'INSTR_ASSET', 'VALUATION', 'PRICE_BASE', 'TABLE_IDENTIFIER'}
expenditure_df.drop(columns=drop_cols.intersection(expenditure_df.columns), inplace=True)
expenditure_df = expenditure_df.rename(columns={'REF_AREA': 'geo'})
expenditure_df = clean_stat(expenditure_df, keys=keys, columns_to_pivot=['EXPENDITURE', 'UNIT_MEASURE'])

datasets = [revenues_df, tax_wedge_df, expenditure_df]
gov_df = reduce(lambda left, right: pd.merge(left, right, on=[k.lower() for k in keys], how='outer'), datasets)
gov_df = gov_df.replace({float('nan'): None})

# ------ Connection -------- #
default_connection(gov_df, 'o_government')