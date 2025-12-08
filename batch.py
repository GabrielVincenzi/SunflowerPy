from toolbi import DatasourceTools

#DatasourceTools.execute_modules(['initiators.initiators'])

modules = [
    #'eurostat.demographic',
    'eurostat.earnings',
    #'eurostat.employment',
    #'eurostat.government',
    #'eurostat.macroeconomic',
    #'eurostat.pollutionIndustry',
    #'eurostat.genderViolence',
    #'eurostat.migrations',
    #'eurostat.healthSelfPerc', # 20500 columns

    #'oecd.inflContrib',

    #'static.healthSelf',
    #'static.italyUnobservedEcon',
    #'static.press',
    #'static.literacy', 
    #'static.ssp',
]

DatasourceTools.execute_modules(modules)

baseline = [
    'dbs.dbs',
    'charts.charts'
]

#DatasourceTools.execute_modules(baseline)