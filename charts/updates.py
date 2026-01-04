
# Updates for the gender_violence database (procedure 1)
updates_gender_violence_p1 = [
    ["General Gender Violence against Women", "Women who have experienced physical and/or psychological violence, threats and sexual violence from a any perpetrator."],
    ["Domestic Gender Violence against Women", "Women who have experienced physical and/or psychological violence, threats and sexual violence from a domestic perpetrator."],
    ["Intimate Gender Violence against Women", "Women who have experienced physical and/or psychological violence, threats and sexual violence from an intimate partner."],
    ["Non Intimate Gender Violence against Women", "Women who have experienced physical and/or psychological violence, threats and sexual violence from a non intimate partner."],
    ["General Gender Violence by occurence", "Women who have experienced violence in adulthood, last 12 months or last 5 years from any perpetrator."],
    ["Domestic Gender Violence by occurence", "Women who have experienced violence in adulthood, last 12 months or last 5 years from a domestic perpetrator."],
    ["Intimate Gender Violence by occurence", "Women who have experienced violence in adulthood, last 12 months or last 5 years from an intimate partner."],
    ["Non Intimate Gender Violence by occurence", "Women who have experienced violence in adulthood, last 12 months or last 5 years from a non intimate partner."],
    ["General Gender Violence by Age", "Women who have experienced violence by age groups from any perpetrator."],
    ["Domestic Gender Violence by Age", "Women who have experienced violence by age groups from a domestic perpetrator."],
    ["Intimate Gender Violence by Age", "Women who have experienced violence by age groups from an intimate partner."],
    ["Non Intimate Gender Violence by Age", "Women who have experienced violence by age groups from a non intimate partner."],
    ["General Gender Violence by Reporting", "Women who have experienced violence by any perpetrator and reported to a close person, health or social service, support service, police or any person."],
    ["Intimate Gender Violence by Reporting", "Women who have experienced violence by an intimate partner and reported to a close person, health or social service, support service, police or any person."],
    ["Non Intimate Gender Violence by Reporting", "Women who have experienced violence by a non intimate partner and reported to a close person, health or social service, support service, police or any person."],
    ["General Gender Violence by Consequences", "Women who have experienced Physical injury, Psychological consequences or have Felt that their life was in danger after violence from any perpetrator."],
    ["Intimate Gender Violence by Consequences", "Women who have experienced Physical injury, Psychological consequences or have Felt that their life was in danger after violence from an intimate partner."],
    ["Non Intimate Gender Violence by Consequences", "Women who have experienced Physical injury, Psychological consequences or have Felt that their life was in danger after violence from a non intimate partner."],
    ["General Gender Violence by Victim limitations", "Women with None, Some, Severe or limited level of disability (activity limitation) who have experienced violence from any perpetrator."],
    ["Domestic Gender Violence by Victim limitations", "Women with None, Some, Severe or limited level of disability (activity limitation) who have experienced violence from a domestic perpetrator."],
    ["Intimate Gender Violence by Victim limitations", "Women with None, Some, Severe or limited level of disability (activity limitation) who have experienced violence from an intimate partner."],
    ["Non Intimate Gender Violence by Victim limitations", "Women with None, Some, Severe or limited level of disability (activity limitation) who have experienced violence from a non intimate partner."],
    ["General Gender Violence by Victim education", "Women with less than primary, primary and lower secondary, upper secondary or tertiary education (ISCED levels 0-2, 3-4, 5-8) who have experienced violence from any perpetrator."],
    ["Domestic Gender Violence by Victim education", "Women with less than primary, primary and lower secondary, upper secondary or tertiary education (ISCED levels 0-2, 3-4, 5-8) who have experienced violence from a domestic perpetrator."],
    ["Intimate Gender Violence by Victim education", "Women with less than primary, primary and lower secondary, upper secondary or tertiary education (ISCED levels 0-2, 3-4, 5-8) who have experienced violence from an intimate partner."],
    ["Non Intimate Gender Violence by Victim education", "Women with less than primary, primary and lower secondary, upper secondary or tertiary education (ISCED levels 0-2, 3-4, 5-8) who have experienced violence from a non intimate partner."],
    ["General Gender Violence by Victim residence", "Women with residence in Cities, Towns or Rural areas who have experienced violence from any perpetrator."],
    ["Domestic Gender Violence by Victim residence", "Women with residence in Cities, Towns or Rural areas who have experienced violence from a domestic perpetrator."],
    ["Intimate Gender Violence by Victim residence", "Women with residence in Cities, Towns or Rural areas who have experienced violence from an intimate partner."],
    ["Non Intimate Gender Violence by Victim residence", "Women with residence in Cities, Towns or Rural areas who have experienced violence from a non intimate partner."],
    ["General Gender Violence by Victim nationality", "Women from EU, Non-EU or Reporting countries except reporting country who have experienced violence from any perpetrator."],
    ["Domestic Gender Violence by Victim nationality", "Women from EU, Non-EU or Reporting countries except reporting country who have experienced violence from a domestic perpetrator."],
    ["Intimate Gender Violence by Victim nationality", "Women from EU, Non-EU or Reporting countries except reporting country who have experienced violence from an intimate partner."],
    ["Non Intimate Gender Violence by Victim nationality", "Women from EU, Non-EU or Reporting countries except reporting country who have experienced violence from a non intimate partner."],
    ["General Gender Violence by relation", "Women who have experienced repeated violence by partner - male or female - non partner or family member."],
    ["Intimate Gender Violence by relation", "Women who have experienced repeated violence by partner - male or female - non partner or family member."],
    ["Non Intimate Gender Violence by relation", "Women who have experienced repeated violence by partner - male or female - non partner or family member."],
    ["Repeated Gender Violence", "Women who have experienced repeated violence At least once a week, less than once a month or at least once a month from any perpetrator."],
    ["Intimate Repeated Gender Violence", "Women who have experienced repeated violence At least once a week, less than once a month or at least once a month from an intimate partner."],
    ["Non Intimate Repeated Gender Violence", "Women who have experienced repeated violence At least once a week, less than once a month or at least once a month from a non intimate partner."],
    ["General Gender Violence by duration", "Women who have experienced repeated violence for less than 1 year, for from 1 to 5 years and for over 5 years from any perpetrator."],
    ["Intimate Gender Violence by duration", "Women who have experienced repeated violence for less than 1 year, for from 1 to 5 years and for over 5 years from an intimate partner."],
    ["Non Intimate Gender Violence by duration", "Women who have experienced repeated violence for less than 1 year, for from 1 to 5 years and for over 5 years from a non intimate partner."],
    ["Intimate Economic Gender Violence by age", "Women who have experienced economic violence (forbidding the respondent to work, controlling the finances of the whole family) by age groups from an intimate partner."],
    ["General Gender Violence by injury occurence", "Women who have experienced injuries after violence in adulthood, last 12 months or last 5 years by any perpetrator."],
]

# rows_out = [row for row in rows_out if row.get("id") not in [85, 86]]
updates_gender_violence_p3 = [
    ["Gender Violence against Women", "Women who have experienced phisical, psychological, sexual violence or threats from domestic, intimate and non intimate perpetrators."],
    ["Gender Violence by occurence", "Women who have experienced violence in adulthood, last 12 months or last 5 years from domestic, intimate and non intimate perpetrators."],
    ["Gender Violence by Age", "Women who have experienced violence by age groups from domestic, intimate and non intimate perpetrators."],
    ["Gender Violence by Reporting", "Women who have experienced violence from domestic, intimate and non intimate perpetrators and reported to a close person, health or social service, support service, police or any person."],
    ["Gender Violence by Consequences", "Women who have experienced Physical injury, Psychological consequences or have Felt that their life was in danger after violence from domestic, intimate and non intimate perpetrators."],
    ["Gender Violence by Victim limitations", "Women with None, Some, Severe or limited level of disability (activity limitation) who have experienced violence from domestic, intimate and non intimate perpetrators."],
    ["Gender Violence by Victim education", "Women with less than primary, primary and lower secondary, upper secondary or tertiary education (ISCED levels 0-2, 3-4, 5-8) who have experienced violence from domestic, intimate and non intimate perpetrators."],
    ["Gender Violence by Victim residence", "Women with residence in Cities, Towns or Rural areas who have experienced violence from domestic, intimate and non intimate perpetrators."],
    ["Gender Violence by Victim nationality", "Women from EU, Non-EU or Reporting countries except reporting country who have experienced violence from domestic, intimate and non intimate perpetrators."],
    ["Gender Violence by relation", "Women who have experienced repeated violence by partner - male or female - non partner or family member."],
    ["Repeated Gender Violence", "Women who have experienced repeated violence At least once a week, less than once a month or at least once a month from domestic, intimate and non intimate perpetrators."],
    ["Gender Violence by duration", "Women who have experienced repeated violence for less than 1 year, for from 1 to 5 years and for over 5 years from domestic, intimate and non intimate perpetrators."],
]

# grouping={"labor": ["emp", "unemp", "inact"]}
updates_employment_p3 = [
    ["Employment by Age, Sex and Education", "Employment by age, sex and education attainments (ISCED)."],
    ["Unemployment by Age, Sex and Education", "Unemployment by age, sex and education attainments (ISCED)."],
    ["Inactivity by Age and Sex", "Inactivity by age and sex."],
]

# grouping_gov= {
#    "general": ["gf01", "gf02", "gf03", "gf04", "gf05", "gf06", "gf07", "gf08", "gf09", "gf10"],
#    "gov_func": ["gf0101", "gf0104", "gf0107"],
#    "order": ["gf0301", "gf0302", "gf0303", "gf0304"],
#    "education": ["gf0901", "gf0902", "gf0903", "gf0904"],
#    "social_protection": ["gf1001", "gf1002", "gf1003", "gf1004", "gf1005", "gf1006"],
#    "taxes": ["d2", "d211", "d51", "d91"],
#}
updates_government_p1 = [
    ["General Public expenditure", "Public expenditure in different sectors in million euros: Functions relating to government (01), Defence (02), Public order and safety (03), Economic affairs (04), Environmental protection (05), Housing and community amenities (06), Health (07), Recreation, culture and religion (08), Education (09) and Social protection (10)."],
    ["General Public expenditure as pct GDP", "Public expenditure in different sectors as percentage of GDP: Functions relating to government (01), Defence (02), Public order and safety (03), Economic affairs (04), Environmental protection (05), Housing and community amenities (06), Health (07), Recreation, culture and religion (08), Education (09) and Social protection (10)."],
    ["General Public expenditure as pct of total", "Public expenditure in different sectors as percentage of total expenditure: Functions relating to government (01), Defence (02), Public order and safety (03), Economic affairs (04), Environmental protection (05), Housing and community amenities (06), Health (07), Recreation, culture and religion (08), Education (09) and Social protection (10)."],
    ["Expenditure in Functions", "Public expenditure in Functions relating to government in million euros: Executive and legislative organs, financial and fiscal affairs, external affairs (0101), Basic research (0104) and Public debt transactions (0107)."],
    ["Expenditure in Functions as pct GDP", "Public expenditure in Functions relating to government as percentage of GDP: Executive and legislative organs, financial and fiscal affairs, external affairs (0101), Basic research (0104) and Public debt transactions (0107)."],
    ["Expenditure in Functions as pct of total", "Public expenditure in Functions relating to government as percentage of total expenditure: Executive and legislative organs, financial and fiscal affairs, external affairs (0101), Basic research (0104) and Public debt transactions (0107)."],
    ["Expenditure in Safety", "Public expenditure in Public order and Safety in million euros: police services (0301), fire protection (0302), law courts (0303), prisons (0304)."],
    ["Expenditure in Safety as pct GDP", "Public expenditure in Public order and Safety as percentage of GDP: police services (0301), fire protection (0302), law courts (0303), prisons (0304)."],
    ["Expenditure in Safety as pct of total", "Public expenditure in Public order and Safety as percentage of total expenditure: police services (0301), fire protection (0302), law courts (0303), prisons (0304)."],
    ["Expenditure in Education", "Public expenditure in Education in million euros: Pre-primary and primary education (0901), Secondary education (0902), Post-secondary non-tertiary education (0903) and Tertiary education (0904)."],
    ["Expenditure in Education as pct GDP", "Public expenditure in Education as percentage of GDP: Pre-primary and primary education (0901), Secondary education (0902), Post-secondary non-tertiary education (0903) and Tertiary education (0904)."],
    ["Expenditure in Education as pct of total", "Public expenditure in Education as percentage of total expenditure: Pre-primary and primary education (0901), Secondary education (0902), Post-secondary non-tertiary education (0903) and Tertiary education (0904)."],
    ["Expenditure in Social protection", "Public expenditure in Social protection in million euros: Sickness and disability, (1001) Old age (1002), Survivors (1003), Family and children (1004), Unemployment (1005), Housing, social exclusion (1006)."],
    ["Expenditure in Social protection as pct GDP", "Public expenditure in Social protection as percentage of GDP: Sickness and disability, (1001) Old age (1002), Survivors (1003), Family and children (1004), Unemployment (1005), Housing, social exclusion (1006)."],
    ["Expenditure in Social protection as pct of total", "Public expenditure in Social protection as percentage of total expenditure: Sickness and disability, (1001) Old age (1002), Survivors (1003), Family and children (1004), Unemployment (1005), Housing, social exclusion (1006)."],
    ["Public Revenues and Taxes", "Public Revenues in million euros from Taxes on production and imports (d2) and more specific Taxes on income, profits and capital gains (d211), Social contributions (d51), Property income like revenue from dividends, interest, rents (d91)."],
    ["Public Revenues and Taxes as pct GDP", "Public Revenues as percentage of GDP from Taxes on production and imports (d2) and more specific Taxes on income, profits and capital gains (d211), Social contributions (d51), Property income like revenue from dividends, interest, rents (d91)."],
    ["Public Revenues and Taxes as pct total", "Public Revenues as percentage of total revenues from Taxes on production and imports (d2) and more specific Taxes on income, profits and capital gains (d211), Social contributions (d51), Property income like revenue from dividends, interest, rents (d91)."],
    ["Expenditure on Interests on Debt in euro", "Expenditure on Interests on Debt in million euro, it is the part of public resources spent to finance past expenditure as debt."],
    ["Expenditure on Interests on Debt in pct GDP", "Expenditure on Interests on Debt as percentage of GDP, it is the part of public resources spent to finance past expenditure as debt."],
    ["Government Debt in euro", "Government consolidated gross debt in euro."],
    ["Government Debt in pct GDP", "Government consolidated gross debt as percentage of GDP."],
    ["Government Lending or Borrowing in euro", "Net lending (+) or Net borrowing (-) in euro: the surplus or deficit in relation to what the country resources are, if they are not enough to cover expenditure, the government needs to borrow, otherwise is able to lend."],
    ["Government Lending or Borrowing in pct GDP", "Net lending (+) or Net borrowing (-) as percentage of GDP: the surplus or deficit in relation to what the country resources are, if they are not enough to cover expenditure, the government needs to borrow, otherwise is able to lend."]
]

# forbidden_other={"educ", "age"},
updates_employment_p3 = [
    ["Employment, Unemp and Inactivity by Age and Sex", "Employment, unemployment and inactivity by age and sex"],
]

# forbidden_other={"educ", "sex"},
updates_employment_p3 = [
    ["Employment, Unemp and Inactivity by Age", "Employment, unemployment and inactivity by age"],
]

# forbidden_other={"educ"},
updates_employment_p3 = [
    ["Employment, Unemp and Inactivity by Age and Sex", "Employment, unemployment and inactivity by age and sex"],
]

# grouping_vars = {
#     "earnings": ["grs-earn", "net-earn", "total-earn", "tax", "soc"],
#     "taxrates": ["taxrt"],
# }
updates_income_p1 = [
    ["Earnings and Contributions One-earning Couple euro", "Earnings, taxes and social contributions in euros for One-earner couple with two children earning 100 percent of the average earning"],
    ["Earnings and Contributions One-earning Couple pps", "Earnings, taxes and social contributions in purchasing parity standard for One-earner couple with two children earning 100 percent of the average earning"],
    ["Earnings and Contributions Two-earning Couple with children and 100 pct average income euro", "Earnings, taxes and social contributions in euros for Two-earner couple with two children, both earning 100 percent of the average earning"],
    ["Earnings and Contributions Two-earning Couple with children and 100 pct average income pps", "Earnings, taxes and social contributions in purchasing parity standard for Two-earner couple with two children, both earning 100 percent of the average earning"],
    ["Earnings and Contributions Two-earning Couple with children and 33 pct average income euro", "Earnings, taxes and social contributions in euros for Two-earner couple with two children, one earning 100 percent and the other 33 percent of the average earning"],
    ["Earnings and Contributions Two-earning Couple with children and 33 pct average income pps", "Earnings, taxes and social contributions in purchasing parity standard for Two-earner couple with two children, one earning 100 percent and the other 33 percent of the average earning"],
    ["Earnings and Contributions Two-earning Couple 100 pct average income euro", "Earnings, taxes and social contributions in euros for Two-earner couple without children, both earning 100 percent of the average earning"],
    ["Earnings and Contributions Two-earning Couple 100 pct average income pps", "Earnings, taxes and social contributions in purchasing parity standard for Two-earner couple without children, both earning 100 percent of the average earning"],
    ["Earnings and Contributions Two-earning Couple 33 pct average income euro", "Earnings, taxes and social contributions in euros for Two-earner couple without children, one earning 100 percent and the other 33 percent of the average earning"],
    ["Earnings and Contributions Two-earning Couple 33 pct average income pps", "Earnings, taxes and social contributions in purchasing parity standard for Two-earner couple without children, one earning 100 percent and the other 33 percent of the average earning"],
    ["Earnings and Contributions Single 100 pct average income euro", "Earnings, taxes and social contributions in euros for Single person without children earning 100 percent of the average earning"],
    ["Earnings and Contributions Single 100 pct average income pps", "Earnings, taxes and social contributions in purchasing parity standard for Single person without children earning 100 percent of the average earning"],
    ["Earnings and Contributions Single 167 pct average income euro", "Earnings, taxes and social contributions in euros for Single person without children earning 167 percent of the average earning"],
    ["Earnings and Contributions Single 167 pct average income pps", "Earnings, taxes and social contributions in purchasing parity standard for Single person without children earning 167 percent of the average earning"],
    ["Earnings and Contributions Single 50 pct average income euro", "Earnings, taxes and social contributions in euros for Single person without children earning 50 percent of the average earning"],
    ["Earnings and Contributions Single 50 pct average income pps", "Earnings, taxes and social contributions in purchasing parity standard for Single person without children earning 50 percent of the average earning"],
    ["Earnings and Contributions Single 67 pct average income euro", "Earnings, taxes and social contributions in euros for Single person without children earning 2/3 of the average earning"],
    ["Earnings and Contributions Single 67 pct average income pps", "Earnings, taxes and social contributions in purchasing parity standard for Single person without children earning 2/3 of the average earning"],
]

updates_income_p2 = [
    ["Gross Earnings for Couples or Single euro", "Gross Earnings in euro for Single and Couples with or without children with 33, 50, 67, 100, 167 percent average income."],
    ["Gross Earnings for Couples or Single pps", "Gross Earnings in purchasing power standard for Single and Couples with or without children with 33, 50, 67, 100, 167 percent average income."],
    ["Net Earnings for Couples or Single euro", "Net Earnings in euro for Single and Couples with or without children with 33, 50, 67, 100, 167 percent average income."],
    ["Net Earnings for Couples or Single pps", "Net Earnings in purchasing power standard for Single and Couples with or without children with 33, 50, 67, 100, 167 percent average income."],
    ["Social Contributions for Couples or Single euro", "Social Contributions in euro for Single and Couples with or without children with 33, 50, 67, 100, 167 percent average income."],
    ["Social Contributions for Couples or Single pps", "Social Contributions in purchasing power standard for Single and Couples with or without children with 33, 50, 67, 100, 167 percent average income."],
    ["Taxes for Couples or Single euro", "Annual Taxes in euro for Single and Couples with or without children with 33, 50, 67, 100, 167 percent average income."],
    ["Taxes for Couples or Single pps", "Annual Taxes in purchasing power standard for Single and Couples with or without children with 33, 50, 67, 100, 167 percent average income."],
    ["Total Earnings for Couples or Single euro", "Total Earnings in euro for Single and Couples with or without children with 33, 50, 67, 100, 167 percent average income."],
    ["Total Earnings for Couples or Single pps", "Total Earnings in purchasing power standard for Single and Couples with or without children with 33, 50, 67, 100, 167 percent average income."],
    ["Average Tax Rates for Couples or Single pps", "Annual average tax rate for Single and Couples with or without children with 33, 50, 67, 100, 167 percent average income."],
]

# grouping_vars = {
#     "general": ["b1gq", "d2", "d3", "p3", "p41", "p61", "p62", "p71", "p72"],
#     "debt": ["f2", "f3", "f31", "f4", "f41", "f42", "gd"],
#     "sector": ["b1g", "d1", "d11", "d12"],
#     "curr-accounts": ["ca", "g", "g1", "g2", "gs", "s"],
#     "fin-accounts": ["eo", "fa", "fa-d-f", "fa-f-f7", "fa-o-f", "fa-p-f"],
#     "flows": ["sa", "sb", "sc", "sd", "se", "sf", "sg", "si"],
# }
# rows_out = [row for row in rows_out if row.get("id") not in [122]]
updates_macroeconomics_p3 = [
    ["Consumption, Imports and Exports as GDP aggregates in euro", "Gross domestic product at market prices (b1gq) with focus on: Taxes on production and imports (d2), subsidies (d3), Final consumption expenditure (p3), individual consumption (p41), Exports of goods (p61) and services (p62), Imports of goods (p71) and services (p72) in million euros."]
    ["Consumption, Imports and Exports as GDP aggregates in pct GDP", "Gross domestic product at market prices (b1gq) with focus on: Taxes on production and imports (d2), subsidies (d3), Final consumption expenditure (p3), individual consumption (p41), Exports of goods (p61) and services (p62), Imports of goods (p71) and services (p72) as percentage of GDP."]
    ["Debt and Loans in euro", "Gross domestic product focus on Debt in currency and deposits (f2), Debt securities (f3) and in particular Short-term (f31) and long-term (f32) debt securities, loans (f4) and in particular short-term (f41) and long-term (f42) loans, Government consolidated gross debt (gd) in million euros."]
    ["Debt and Loans in pct GDP", "Gross domestic product focus on Debt in currency and deposits (f2), Debt securities (f3) and in particular Short-term (f31) and long-term (f32) debt securities, loans (f4) and in particular short-term (f41) and long-term (f42) loans, Government consolidated gross debt (gd) as percentage of GDP."]
    ["GDP Labor Market Aggregated in euro", "Gross Domestic Product aggregates of the labor market: Gross value added (b1g), compensation of employees (d1), wages and salaries (d11) and employers social contributions (d12) in million euros."]
    ["GDP Labor Market Aggregated in pct GDP", "Gross Domestic Product aggregates of the labor market: Gross value added (b1g), compensation of employees (d1), wages and salaries (d11) and employers social contributions (d12) as percentage of GDP."]
    ["Current Accounts in euro", "Balance, Credit and Debt of current (ca) accounts, in particular Goods in current account (g), General merchandise on a balance of payments basis (g1), Net exports of goods under merchanting(g2), Goods and services in current account (gs) and Services in current account (s)."]
    ["Financial Accounts in euro", "financial accounts (fa) and in particular direct investments (fa-d-f), derivatives and employee stock options (fa-f-f7), portfolio investments (fa-p-f) and other investment (fa-o-f). "],
    ["Services in current accounts in euro", "Services in current accounts: manufacturing services on physical inputs owned by others (sa), maintenance and repair services n.i.e. (sb), transport (sc), travel (sd), construction (se), insurance and pension services (sf), financial services (sg), telecommunications, computer, and information services (si) and government goods and services n.i.e. (sl)."]
] 

# grouping_vars = {
#    "pollamount": ["pollamount"],
#    "pollintens": ["pollintens"],
#    "electr-capacity": ["elec-prod-cf", "elec-prod-n9000", "elec-prod-ra100", "elec-prod-ra200", "elec-prod-ra300", "elec-prod-ra410", "elec-prod-ra420", "elec-prod-total", "elec-prod-n9001"],
#}
# forbidden_group={"na_item", "unit"}
updates_pollution_industry_p3 = [
    ["Pollution amount by sector in kg per capita", "Pollution amount in Greenhouse gases C02 equivalent in kilograms per capita by sectors."],
    ["Pollution amount by sector in tonnes", "Pollution amount in Greenhouse gases C02 equivalent in thousand tonnes by sectors."],
    ["Pollution intensity in kg per euro of value added", "Pollution intensity in Greenhouse gases C02 equivalent in kilograms per euro of value added by sectors."],
    ["Pollution intensity in kg per euro of production", "Pollution intensity in Greenhouse gases C02 equivalent in kilograms per euro of output (production) by sectors."],
    ["Electricity production Capacity in MW", "Electricity production capacitiy in MegaWatt for Combustible fuels (cf), Nuclear fuels and other fuels nec (n9000), Hydroelectric (ra100), Geothermal (ra200), Wind (ra300), Solar thermal (ra410) Solar photovoltaic (ra420) and Nuclear fuels (na9001). "],
] 

updates_press_p1 = [
    ["Total Score in the Reporters without Borders publication", "Total score between each sub-category: political, economic, social and legal context, safety."],
    ["Total Rank in the Reporters without Borders publication", "Total Ranking between countries participating in the survey."],
    ["Score for Political Context (Reporters without Borders)", "Political Context: Degree of support and respect for media autonomy and holding politicians accountable, acceptance of journalistic approaches."],
    ["Score for Economic Context (Reporters without Borders)", "Economic Context: Economic constraints linked to governmental policies, to non-state actors or to media owners"],
    ["Score for Legal Context (Reporters without Borders)", "Legal Context: Degree to which journalists and media are free to work without censorship or judicial sanctions, access information without discrimination, impunity for those responsible for acts of violence against journalists."],
    ["Score for Social Context (Reporters without Borders)", "Social Context: Social constraints resulting from denigration and attacks on the press, cultural constraints, including pressure on journalist."],
    ["Score for Safety (Reporters without Borders)", "Safety Context: Bodily harm, psychological or emotional distress and professional harm to journalists."],
] 

#grouping_vars= {
#    "lit-prof-s": ["lit-prof-s"],
#    "lit-prof-a": ["lit-prof-a"],
#    "lit-prof-i": ["lit-prof-i"]
#}
# rows_out = [row for row in rows_out if row.get("id") not in [211, 213, 215]]
updates_literacy_p3 = [
    ["Literacy Proficiency by education and sex", "Adults' mean literacy proficiency, by educational attainment level and gender"],
    ["Literacy Proficiency by education and age", "Adults' mean literacy proficiency, by educational attainment and age group"],
    ["Literacy Proficiency by education and origin", "Adults' mean literacy proficiency, by educational attainment, immigrant background and language spoken at home"],
]

# rows_out = [row for row in rows_out if row.get("id") not in [218]]
updates_literacy_lev_sex_p3 = [
    ["Literacy Proficiency Distribution by education and sex", "Distribution of adults by literacy proficiency levels, by educational attainment and gender"]
]

# rows_out = [row for row in rows_out if row.get("id") not in [219]]
updates_literacy_lev_age_p3 = [
    ["Literacy Proficiency Distribution by education and age", "Distribution of adults by literacy proficiency levels, by educational attainment and age group."]
]

#grouping_vars= {
#    "num-prof-s": ["num-prof-s"],
#    "num-prof-a": ["num-prof-a"],
#    "num-prof-i": ["num-prof-i"]
#}
# rows_out = [row for row in rows_out if row.get("id") not in [219, 221, 223]]
updates = [
    ["Numeracy Proficiency by education and sex", "Adults' mean numeracy proficiency, by educational attainment level and gender"],
    ["Numeracy Proficiency by education and age", "Adults' mean numeracy proficiency, by educational attainment and age group"],
    ["Numeracy Proficiency by education and origin", "Adults' mean numeracy proficiency, by educational attainment, immigrant background and language spoken at home"],
]

# rows_out = [row for row in rows_out if row.get("id") not in [226]]
updates_numeracy_lev_sex_p3 = [
    ["Numeracy Proficiency Distribution by education and sex", "Distribution of adults by numeracy proficiency levels, by educational attainment and gender"]
]

# rows_out = [row for row in rows_out if row.get("id") not in [229]]
updates_numeracy_lev_age_p3 = [
    ["Numeracy Proficiency Distribution by education and age", "Distribution of adults by numeracy proficiency levels, by educational attainment and age group."]
]

# rows_out = [row for row in rows_out if row.get("id") not in [230]]
updates_probsolv_lev_sex_p3 = [
    ["Problem Solving Proficiency Distribution by education and gender", "Distribution of adults by adaptive problem-solving proficiency levels, by educational attainment and gender."]
]

# rows_out = [row for row in rows_out if row.get("id") not in [231]]
updates_probsolv_lev_age_p3 = [
    ["Problem Solving Proficiency Distribution by education and age", "Distribution of adults by adaptive problem-solving proficiency levels, by educational attainment and age."]
]

#grouping_vars= {
#    "pso-prof-s": ["pso-prof-s"],
#    "pso-prof-a": ["pso-prof-a"],
#    "pso-prof-i": ["pso-prof-i"]
#}
# rows_out = [row for row in rows_out if row.get("id") not in [231, 233, 235]]
updates_probsolv_p3 = [
    ["Problem Solving Proficiency by education and sex", "Adults' mean problem solving proficiency, by educational attainment level and gender"],
    ["Problem Solving Proficiency by education and age", "Adults' mean problem solving proficiency, by educational attainment and age group"],
    ["Problem Solving Proficiency by education and origin", "Adults' mean problem solving proficiency, by educational attainment, immigrant background and language spoken at home"],
]

#grouping_vars= {
#    "edu-expst": ["edu-expst"],
#    "stnr": ["stud-enrl"],
#    "nr": ["edu-nwen"],
#    "edu-dnwen": ["edu-dnwen"],
#    "edu-lvl": ["edu-lvl"],
#    "ratios": ["tch-stud1", "tch-stud2"],
#    "out": ["out-lowersec", "out-uppersec"],
#}
updates_schooling_student_p3 = [
    ["Expenditure in Education per Student by program and level", "Annual expenditure on educational institutions per pupil/student based on FTE, by education level and programme orientation"],
    ["Students enrolled by sex, field and level of education", "Pupils and students enrolled by education level, sex and field of education"],
    ["New entrants by sex, field and level of education", "New entrants by education level, programme orientation, sex and field of education"],
    ["Distribution of new entrants by sex, field and level of education", "Distribution of new entrants at education level and programme orientation by sex and field of education"],
    ["Students by education level as pct of total age population", "Pupils and students by education level - as perc of total age population"],
    ["Ratio student to teacher by education level", "Ratio of pupils to teachers and teacher aides and Ratio of pupils and students to teachers and academic staff by education level and programme orientation"],
    ["Out-of-school rate by education level", "Out-of-school rate in population of lower secondary and of upper secondary school age, by sex"],
]

#grouping_vars= {
#    "tch-part": ["tch-part"],
#    "mng-fem": ["mng-fem"],
#    "tch-fem": ["tch-fem"],
#    "tch-pop": ["tch-pop"],
#}
updates_schooling_teacher_p3 = [
    ["Teachers working part-time in pct", "Teachers working part-time - as percent of all teachers, by education level"],
    ["Female school-management personnel in pct", "Female school-management personnel - as perc of total school-management personnel, by education level"],
    ["Female teachers in pct", "Female teachers - as percent of all teachers, by education level"],
    ["Academic staff and teachers by sex, age and field", "Classroom teachers and academic staff by education level, programme orientation, sex and age groups"],
]

#grouping_ssp_energy_p3 = {
#    'ssp1-19': ['ssp1-19'],
#    'ssp1-26': ['ssp1-26'],
#    'ssp1-34': ['ssp1-34'],
#    'ssp1-45': ['ssp1-45'],
#    'ssp1-60': ['ssp1-60'],
#    'ssp1-baseline': ['ssp1-baseline'],
#
#    'ssp2-19': ['ssp2-19'],
#    'ssp2-26': ['ssp2-26'],
#    'ssp2-34': ['ssp2-34'],
#    'ssp2-45': ['ssp2-45'],
#    'ssp2-60': ['ssp2-60'],
#    'ssp2-baseline': ['ssp2-baseline'],
#
#    'ssp3-34': ['ssp3-34'],
#    'ssp3-45': ['ssp3-45'],
#    'ssp3-60': ['ssp3-60'],
#    'ssp3-baseline': ['ssp3-baseline'],
#
#    'ssp4-19': ['ssp4-19'],
#    'ssp4-26': ['ssp4-26'],
#    'ssp4-34': ['ssp4-34'],
#    'ssp4-45': ['ssp4-45'],
#    'ssp4-60': ['ssp4-60'],
#    'ssp4-baseline': ['ssp4-baseline'],
#
#    'ssp5-19': ['ssp5-19'],
#    'ssp5-26': ['ssp5-26'],
#    'ssp5-34': ['ssp5-34'],
#    'ssp5-45': ['ssp5-45'],
#    'ssp5-60': ['ssp5-60'],
#    'ssp5-baseline': ['ssp5-baseline'],
#}
#
#grouping_ssp_energy_p1 = {
#    'ssp': ['ssp1-baseline', 'ssp1-19', 'ssp1-26', 'ssp1-34', 'ssp1-45',
#            'ssp2-baseline', 'ssp2-19', 'ssp2-26', 'ssp2-34', 'ssp2-45', 'ssp2-60',
#            'ssp3-baseline', 'ssp3-34', 'ssp3-45', 'ssp3-60',
#            'ssp4-baseline', 'ssp4-26', 'ssp4-34', 'ssp4-45',
#            'ssp5-baseline', 'ssp5-26', 'ssp5-34', 'ssp5-45', 'ssp5-60',
#            'ssp1-60', 'ssp4-19', 'ssp4-60', 'ssp5-19',
#            ],
#}

updates_ssp_energy_aicme = [
    ["IPCC Scenario SSP1 baseline", "SSP1 (Sustainability - Green Road): A world that prioritizes sustainable development, strong environmental protection, low inequality, and efficient use of resources. Economic growth is inclusive and human well-being improves globally. The baseline assumes no additional climate policies beyond existing trends."],
    ["IPCC Scenario SSP1 19", "SSP1-1.9: A sustainability-focused world that achieves extremely strong climate mitigation. Global CO₂ emissions fall rapidly, reaching net-zero around mid-century. This pathway is consistent with limiting global warming to about 1.5°C. It requires major shifts in energy, land use, and consumption patterns."],
    ["IPCC Scenario SSP1 26", "SSP1-2.6: A sustainable development pathway combined with strong climate policies. Emissions peak early and decline steadily throughout the century. Warming is likely kept close to 2°C above pre-industrial levels. This scenario assumes high international cooperation."],
    ["IPCC Scenario SSP1 34", "SSP1-3.4: Sustainability-oriented development with moderate mitigation efforts. Climate action is present but less ambitious than 2°C-consistent pathways. Global warming reaches intermediate levels. Environmental goals compete with other development priorities."],
    ["IPCC Scenario SSP1 45", "SSP1-4.5: A world striving for sustainability socially and economically, but with relatively weak climate mitigation. Emissions decline slowly or stabilize rather than fall sharply. This results in higher long-term warming."],
    ["IPCC Scenario SSP1 60", "SSP1-6.0: Sustainable development goals are partially achieved, but climate policies remain insufficient. Greenhouse gas emissions stay high throughout the century. This pathway leads to substantial climate change despite social progress."],

    ["IPCC Scenario SSP2 baseline", "SSP2 (Middle of the Road): A future that broadly follows historical trends. Economic growth, population change, and technological progress evolve unevenly. Institutions improve slowly and inequalities persist. Climate action advances incrementally but not decisively."],
    ["IPCC Scenario SSP2 19", "SSP2-1.9: A continuation of current societal trends combined with unexpectedly strong global climate policies. Rapid emissions reductions are achieved despite moderate governance capacity. This pathway is consistent with limiting warming to around 1.5°C."],
    ["IPCC Scenario SSP2 26", "SSP2-2.6: A middle-of-the-road world that implements strong but achievable climate action. Emissions peak soon and decline gradually. Warming is likely limited to around 2°C. International cooperation is present but imperfect."],
    ["IPCC Scenario SSP2 34", "SSP2-3.4: Current development trends continue with partial climate mitigation. Policies reduce emissions growth but do not eliminate it. Warming reaches intermediate levels. Climate risks increase but remain manageable in some regions."],
    ["IPCC Scenario SSP2 45", "SSP2-4.5: The most representative scenario of moderate climate action. Some mitigation policies are implemented, but ambition is limited. Emissions stabilize rather than decline strongly. This results in moderate to high global warming."],
    ["IPCC Scenario SSP2 60", "SSP2-6.0: A world following historical trends with weak climate policies. Fossil fuels remain a major energy source. Emissions remain high throughout the century. This pathway leads to significant climate impacts."],

    ["IPCC Scenario SSP3 baseline", "SSP3 (Regional Rivalry - Rocky Road): A fragmented world with strong nationalism and limited international cooperation. Economic growth is slow and population growth is high in vulnerable regions. Institutions are weak and climate action is minimal."],
    ["IPCC Scenario SSP3 34", "SSP3-3.4: A geopolitically divided world that still achieves some climate mitigation. Emission reductions occur mainly through regional or local efforts. Global coordination is limited. Climate risks remain high in many regions."],
    ["IPCC Scenario SSP3 45", "SSP3-4.5: Regional rivalry constrains effective climate action. Energy systems remain carbon-intensive. Adaptation and mitigation capacities are uneven. This leads to substantial warming and high vulnerability."],
    ["IPCC Scenario SSP3 60", "SSP3-6.0: A highly fragmented world with minimal cooperation on climate change. Emissions continue to rise or stabilize at high levels. Adaptation capacity is low in many regions. Severe climate impacts are widespread."],
 
    ["IPCC Scenario SSP4 baseline", "SSP4 (Inequality - A Road Divided): A world characterized by strong inequalities within and between countries. Wealthy groups have access to advanced technology and protection. Large vulnerable populations face high exposure to climate risks."],
    ["IPCC Scenario SSP4 19", "SSP4 1.9: A deeply unequal world that achieves strong global mitigation. Advanced technologies allow low emissions pathways. However, benefits are concentrated among wealthy regions. Vulnerable populations remain highly exposed."],
    ["IPCC ScenarioSSP4 26", "SSP4-2.6: Climate mitigation is driven by elites and technologically advanced regions. Global warming is limited, but inequality persists. Adaptation capacity varies strongly across populations. Social vulnerability remains high."],
    ["IPCC Scenario SSP4 34", "SSP4-3.4: Uneven mitigation efforts lead to moderate warming. Protected regions cope better with climate change. Poorer regions face disproportionate impacts. Global inequality shapes climate outcomes."],
    ["IPCC Scenario SSP4 45", "SSP4-4.5: Moderate climate action in a highly unequal world. Emissions decline slowly and unevenly. Climate risks are concentrated among vulnerable populations. Adaptation gaps widen."],
    ["SSP4-60", "SSP4 6.0: High inequality combined with weak mitigation. Emissions remain high and warming is severe. Most people lack resources to adapt. Climate impacts exacerbate social divisions."],

    ["IPCC Scenario SSP5 baseline", "SSP5 (Fossil-fuelled Development - Highway): Rapid economic growth driven by energy-intensive lifestyles and fossil fuels. Technological progress is high, but emissions are very large. Environmental concerns are secondary."],
    ["IPCC Scenario SSP5 19", "SSP5-1.9: A fossil-fuel-based world that relies on massive technological intervention. Large-scale carbon capture and removal offset high emissions. Warming is limited to about 1.5°C. This pathway assumes unprecedented technological deployment."],
    ["IPCC Scenario SSP5 26", "SSP5-2.6: Continued economic growth with heavy energy use. Strong mitigation relies on advanced technologies rather than reduced consumption. Emissions decline later in the century. Warming is kept close to 2°C."],
    ["IPCC Scenario SSP5 34", "SSP5-3.4: High-energy development with partial technological mitigation. Emissions remain high for much of the century. Climate impacts increase but are managed technologically. Resource use remains intensive."],
    ["IPCC Scenario SSP5 45", "SSP5-4.5: Fossil-fuel-driven growth with moderate climate controls. Emissions peak late and decline slowly. Warming reaches high levels. Adaptation relies heavily on economic capacity."],
    ["IPCC Scenario SSP5 60", "SSP5-6.0: Continued reliance on fossil fuels with limited mitigation. Economic growth is rapid but emissions stay very high. Climate change becomes severe. Long-term sustainability is compromised."]
]