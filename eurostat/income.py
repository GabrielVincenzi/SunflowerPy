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

# Annual net earnings
earnings_df = et.get_eurostat_dataset(
    dataset_code="earn_nt_net",
    filters=f"A.EUR+PPS.NET+TAX+SOC+GRS+TOTAL.P1_NCH_AW50+P1_NCH_AW67+P1_NCH_AW100+P1_NCH_AW167+CPL_CH2_AW100+CPL_CH2_AW100_100+CPL_NCH_AW100_100+CPL_NCH_AW100_33+CPL_CH2_AW100_33.{countries}",
    start_year=start_year,
    end_year=end_year
)

earnings_df["ecase"] = earnings_df["ecase"].str.replace('_', '-')
earnings_df["estruct"] = earnings_df["estruct"].str.replace('_', '-')
earnings_df["currency"] = earnings_df["currency"].str.replace('_', '-')
earnings_df["estruct"] = (earnings_df["estruct"]
                          .str.replace("TOTAL", "TOTAL-EARN", regex=False)
                          .str.replace("NET", "NET-EARN", regex=False)
                          .str.replace("GRS", "GRS-EARN", regex=False))
earnings_df = earnings_df.rename(columns={"currency": "unit"})

# Annual Tax rate
taxrate_df = et.get_eurostat_dataset(
    dataset_code="earn_nt_taxrate",
    filters=f"A.P1_NCH_AW50+P1_NCH_AW67+P1_NCH_AW100+P1_NCH_AW167+CPL_CH2_AW100+CPL_CH2_AW100_100+CPL_NCH_AW100_100+CPL_NCH_AW100_33+CPL_CH2_AW100_33.{countries}",
    start_year=start_year,
    end_year=end_year
)
taxrate_df["ecase"] = taxrate_df["ecase"].str.replace('_', '-')

earnings_df = clean_stat(earnings_df, keys=keys, columns_to_pivot=["estruct", "ecase", "unit"])
taxrate_df = clean_stat(taxrate_df, keys=keys, columns_to_pivot=["ecase"], prefix="taxrt")


datasets = [earnings_df, taxrate_df]
income_df = reduce(lambda left, right: pd.merge(left, right, on=[k.lower() for k in keys], how='outer'), datasets)
income_df = income_df.replace({float('nan'): None})



# ------ JSON update -------- #
db_name = 'e_income'
pattern_earn = ["name", "ecase", "unit"]
pattern_taxrt = ["name", "ecase"]
descriptions = {
    'net-earn': 'Net annual earning',
    'grs-earn': 'Gross annual earning',
    'total-earn': 'Total annual earning',
    'soc': 'Annual social security',
    'tax': 'Annual taxes',
    'taxrt': 'Tax rate',
}
update_json(earnings_df, db_name, pattern_earn, descriptions)
update_json(taxrate_df, db_name, pattern_taxrt, descriptions)

# ------ Connection -------- #
create_table_sql(df=income_df, db_name=db_name)
default_connection(income_df, db_name)