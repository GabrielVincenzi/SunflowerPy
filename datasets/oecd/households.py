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

# Income distribution database:
# Poverty rate based on disposable income (50% median disposable income) Gini (disposable income)
# P90/P10 disposable income decile ratio
income_df = to.get_oecd_dataset(
    dataset_id= "OECD.WISE.INE,DSD_WISE_IDD@DF_IDD,",
    filters= f"{countries}.A.PG_INC_ DISP+PR_INC_DISP+D9_1_INC_DISP+INC_DISP_GINI._Z.0_TO_1+FCTR+PT_POP._T+Y18T25 +Y41T50+Y51T65+Y_GT65+Y26T40.METH2012.D_CUR._Z+PL_50",
    start_year=2010
)

drop_cols = {'STATISTICAL_OPERATION', 'DEFINITION', 'POVERTY_LINE', 'UNIT_MEASURE'}

income_df.drop(columns=drop_cols.intersection(income_df.columns), inplace=True)
income_df = income_df.rename(columns={'REF_AREA': 'geo'})
income_df['AGE'] = income_df['AGE'].astype(str).str.replace("_", "", regex=False)
income_df = clean_stat(income_df, keys=['geo', 'TIME_PERIOD'], columns_to_pivot=['MEASURE', 'AGE'])

# Wealth distribution database:
# Debt to income ratio
# Mean to median net wealth ratio
# Share of top 1%, 5%, 10% and bottom 40%
wealth_df = to.get_oecd_dataset(
    dataset_id= "OECD.WISE.INE,DSD_WEALTH@DF_WEALTH,",
    filters= f"{countries}.A.M_NW_RATIO+DI_RATIO+SH_BOT40+SH_TOP1+SH_TOP5 +SH_TOP10...",
    start_year=2010
)

drop_cols = {'STATISTICAL_OPERATION', 'THRESHOLD', 'UNIT_MEASURE'}

wealth_df.drop(columns=drop_cols.intersection(wealth_df.columns), inplace=True)
wealth_df = wealth_df.rename(columns={'REF_AREA': 'geo'})
wealth_df = clean_stat(wealth_df, keys=['geo', 'TIME_PERIOD'], columns_to_pivot=['MEASURE'])
for col in wealth_df.select_dtypes(include="object").columns:
    if col not in ["geo"]:   # keep geo as object/string
        wealth_df[col] = pd.to_numeric(wealth_df[col], errors="coerce")


datasets = [income_df, wealth_df]
iw_df = reduce(lambda left, right: pd.merge(left, right, on=[k.lower() for k in keys], how='outer'), datasets)
iw_df = iw_df.sort_values(["geo", "time_period"])
numeric_cols = iw_df.select_dtypes(include="number").columns

iw_df[numeric_cols] = (
    iw_df.groupby("geo")[numeric_cols]
          .apply(lambda g: g.interpolate(method="linear", limit_direction="both"))
          .reset_index(level=0, drop=True)
)

iw_df = iw_df.replace({float('nan'): None})

# ------ Connection -------- #
default_connection(iw_df, 'o_households')