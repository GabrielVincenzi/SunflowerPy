import pandas as pd
from tools.toolbi import default_connection, create_table_sql, chunk_list
from tools.tooldb import clean_stat, update_json, get_eurostat_dataset
from functools import reduce
import config

keys = config.KEYS
countries = config.COUNTRIES
start_year = config.START_YEAR
end_year = config.END_YEAR

# Labour productivity and unit labour costs by industry (NACE Rev.2)
prod_df = get_eurostat_dataset(
    dataset_code="nama_10_lp_a21",
    filters="A.HW+I15+EUR.A+B+B-E+C+D+E+F+G+H+I+M+N+R+S.D1_SAL_HW+RLPR_PER+RLPR_HW+HW_EMP.",
)

# Capital stock based productivity indicators by industry (NACE Rev.2)
ass_df = get_eurostat_dataset(
    dataset_code="nama_10_cp_a21",
    filters="A.N11N+N117N.A+B+C+D+E+F+G+H+I+M+N+R+S.NCS_EMP+NCS_HW+NCS_GVA.I15.IT",
)

cols_to_pivot = ['na_item', 'nace_r2', 'unit']
for col in cols_to_pivot:
    prod_df[col] = prod_df[col].str.replace("_", "-", regex=False)

prod_df = clean_stat(prod_df, keys=keys, columns_to_pivot=cols_to_pivot)

cols_to_pivot = ['na_item', 'nace_r2', 'asset10', 'unit']
for col in cols_to_pivot:
    ass_df[col] = ass_df[col].str.replace("_", "-", regex=False)

ass_df = clean_stat(ass_df, keys=keys, columns_to_pivot=cols_to_pivot)

datasets = [prod_df, ass_df]
productivity_df = reduce(lambda left, right: pd.merge(left, right, on=[k.lower() for k in keys], how='outer'), datasets)
productivity_df = productivity_df.replace({float('nan'): None})

db_name = "e_productivity"
pattern_lab = ['name', 'sector', 'unit']
pattern_ass = ['name', 'sector', 'asset', 'unit']
descriptions = {
    "d1-sal-hw": "Compensation of employees per hour worked by industry (NACE Rev. 2)",
    "rlpr-per": "Real labour productivity per person by industry (NACE Rev. 2) calculated as GDP in volume terms (real) divided by total employees and self-employed",
    "rlpr-hw": "Real labour productivity per hour worked by industry (NACE Rev. 2) calculated as GDP in volume terms (real) divided by total hours worked by employees and self-employed",
    "hw-emp": "Hours worked per employed person by industry (NACE Rev. 2)",
    "ncs-emp": "Net assets per employed person by industry (NACE Rev. 2)",
    "ncs-hw": "Net assets per hour worked by industry (NACE Rev. 2)",
    "ncs-gva": "Net assets to gross value added by industry (NACE Rev. 2)",
}
update_json(prod_df, db_name, pattern_lab, descriptions)
update_json(ass_df, db_name, pattern_ass, descriptions)

# ------ Connection -------- #
create_table_sql(df=productivity_df, db_name=db_name)
default_connection(productivity_df, db_name)