import pandas as pd
from tools.toolbi import default_connection, create_table_sql
from tools.tooldb import clean_stat, update_json
import tools.tooleurostat as et
import config
from functools import reduce

keys = config.KEYS
countries = config.COUNTRIES
start_year = config.START_YEAR
end_year = config.END_YEAR

govexp_df = et.get_eurostat_dataset(
    dataset_code="gov_10a_exp",
    filters=f"A.MIO_EUR+PC_GDP+PC_TOT.S13.GF01+GF0101+GF0104+GF0107+GF02+GF0203+GF03+GF0301+GF0302+GF0303+GF0304+GF04+GF05+GF06+GF07+GF0704+GF08+GF09+GF0901+GF0902+GF0903+GF0904+GF10+GF1001+GF1002+GF1003+GF1004+GF1005+GF1006.TE.",
    start_year=start_year,
    end_year=end_year
)

govtax_df = et.get_eurostat_dataset(
    dataset_code="gov_10a_taxag",
    filters=f"A.MIO_EUR+PC_GDP+PC_TOT.S13.D2+D211+D51+D91.",
    start_year=start_year,
    end_year=end_year
)

govdebt_df = et.get_eurostat_dataset(
    dataset_code="gov_10dd_edpt1",
    filters=f"A.MIO_EUR+PC_GDP.S13.B9+GD+D41PAY.",
    start_year=start_year
)

govexp_df['unit'] = govexp_df['unit'].str.replace('_', '-')
govtax_df['unit'] = govtax_df['unit'].str.replace('_', '-')
govdebt_df["unit"] = govdebt_df["unit"].str.replace("_", "-", regex=False)
govexp_df = clean_stat(govexp_df, keys=keys, columns_to_pivot=['cofog99', 'unit'])
govtax_df = clean_stat(govtax_df, keys=keys, columns_to_pivot=['na_item', 'unit'])
govdebt_df = clean_stat(govdebt_df, keys=keys, columns_to_pivot=['na_item', 'unit'])

datasets = [govexp_df, govtax_df, govdebt_df]
gov_df = reduce(lambda left, right: pd.merge(left, right, on=[k.lower() for k in keys], how='outer'), datasets)
gov_df = gov_df.replace({float('nan'): None})

# ------ JSON update -------- #
db_name = 'e_government'
pattern = ["name", "unit"]
descriptions = {
    "gf01": "Functions relating to government: legislative and executive organs; fiscal affairs; external affairs; the overall functioning of government institutions",
    "gf0101": "Executive and legislative organs: financial and fiscal affairs, external affairs: Subset of GF01 - includes the costs and operations of the central functions of government such as parliaments, courts, financial & fiscal regulation, diplomatic services",
    "gf0104": "Basic research: Government expenditure on basic research under general public services",
    "gf0107": "Public debt transactions: Expenditure related to servicing government’s public debt",
    "gf02": "Defence: COFOG division GF02 - expenditures on military defence, civil defence, etc",
    "gf0203": "Foreign military aid: Expenditure by government in support of foreign military operations or aid",
    "gf03": "Public order and safety: COFOG division GF03 - includes police services, fire protection, law courts, prisons, etc",
    "gf0301": "Police services: Government expenditure on policing (maintaining public law and order)",
    "gf0302": "Fire-protection services: Expenditures for fire prevention, firefighting services",
    "gf0303": "Law courts: Costs associated with judicial system - courts, judiciary",
    "gf0304": "Prisons: Expenditures related to prison services, penal institutions",
    "gf04": "Economic affairs: COFOG division GF04 - economic functions such as general economic & labour affairs, transport, agriculture, energy etc",
    "gf05": "Environmental protection: COFOG division GF05 - includes waste management, pollution abatement, protection of biodiversity etc",
    "gf06": "Housing and community amenities: Functions relating to housing, community development, water supply, street lighting etc",
    "gf07": "Health: COFOG division GF07 - public health, medical services, hospital services etc",
    "gf0704": "Public health: Health functions not elsewhere classified under the health division",
    "gf08": "Recreation, culture and religion: COFOG division GF08 - includes culture, libraries, museums, religious affairs etc",
    "gf09": "Education: COFOG division GF09 - all levels of education, from pre-primary through tertiary, including training etc",
    "gf0901": "Pre-primary and primary education: Government expenditure on pre-primary & primary school levels",
    "gf0902": "Secondary education: Government expenditure on lower and upper secondary (middle/high school) education",
    "gf0903": "Post-secondary non-tertiary education: Education beyond secondary but not at the level of tertiary degree programmes",
    "gf0904": "Tertiary education: Government expenditure on universities, colleges, higher education institutions",
    "gf10": "Social protection: COFOG division GF10 - expenditures on social insurance, assistance, services to families etc",
    "gf1001": "Sickness and disability: Social protection functions relating to sickness and disability benefits",
    "gf1002": "Old age: Social protection: pensions and old-age benefits",
    "gf1003": "Survivors: Social protection: survivors’ benefits (widows, widowers etc)",
    "gf1004": "Family and children: Social protection: benefits for families and children",
    "gf1005": "Unemployment: Social protection: unemployment benefits and related services",
    "gf1006": "Housing, social exclusion not elsewhere classified, etc: Miscellaneous social protection functions such as housing-related benefits, social exclusion, etc",
    "d2": "Taxes on production and imports: Government revenue from taxes on goods and services, excluding VAT",
    "d211": "Taxes on income, profits and capital gains: Government revenue from personal and corporate income taxes",
    "d51": "Social contributions: Revenue from social security contributions paid by employers and employees",
    "d91": "Property income: Government revenue from dividends, interest, rents, and other property income",
    "te": "Total general government expenditure: summed total of general government expenditure across all COFOG functions",
    "b9": "Net lending (+)/net borrowing (-)",
    "gd": "Government consolidated gross debt",
    "d41pay": "Interest, expenditure",
}

update_json(gov_df, db_name, pattern, descriptions)

# ------ Connection -------- #
create_table_sql(df=gov_df, db_name=db_name)
default_connection(gov_df, db_name)