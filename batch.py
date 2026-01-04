from tools.toolbi import DatasourceTools

# Initialize the Structure of the Data Warehouse
# Create all the tables for Charts, Questions, Database, Categories and Translations
DatasourceTools.execute_modules(['initiators.initiators'])

# Create all the data tables coming from Eurostat, Oecd, WorldBank, National Statistical Institutions
# Create also tables defined from excel static files
# While updating both Data Warehouse and local JSON files for translations and maintenance
modules = [
    'datasets.eurostat.demographic',
    'datasets.eurostat.earnings',
    'datasets.eurostat.employment',
    'datasets.eurostat.income',
    'datasets.eurostat.price',
    'datasets.eurostat.government',
    'datasets.eurostat.macroeconomic',
    'datasets.eurostat.pollutionIndustry',
    'datasets.eurostat.genderViolence',
    'datasets.eurostat.migrations',
    'datasets.eurostat.healthSelfPerc', # 20500 columns

    'datasets.oecd.inflContrib',
    'datasets.oecd.trustSatisf',
    
    'datasets.static.healthSelf',
    'datasets.static.italyUnobservedEcon',
    'datasets.static.press',
    'datasets.static.literacy', 
    'datasets.static.ssp',
]

#DatasourceTools.execute_modules(modules)

# Update categories, database availabilities and translations according to new informations
baseline = [
    'initiators.dbs',
    'initiators.categories',
    'initiators.langs'
]

DatasourceTools.execute_modules(baseline)