import config
from toolworldbank import serial_wb_db, clean_wbstat
from toolbi import create_table_sql, default_connection
from tooldb import update_json

# WORLD BANK Climate Change Knowledge portal
# https://climateknowledgeportal.worldbank.org/download-data
keys = [k.lower() for k in config.KEYS]
countries = "AFG,ALB,DZA,AND,AGO,ARG,ARM,AUS,AUT,AZE,BHS,BHR,BGD,BRB,BLR,BEL,BLZ,BEN,BTN,BOL,BIH,BWA,BRA,BRN,BGR,BFA,BDI,KHM,CMR,CAN,CPV,CAF,TCD,CHL,CHN,COL,COM,COG,CRI,HRV,CUB,CYP,CZE,DNK,DOM,ECU,EGY,SLV,GNQ,ERI,EST,SWZ,ETH,FJI,FIN,FRA,GAB,GMB,GEO,DEU,GHA,GRC,GRD,GTM,GIN,GNB,GUY,HTI,HND,HUN,ISL,IND,IDN,IRN,IRQ,IRL,ISR,ITA,JAM,JPN,JOR,KAZ,KEN,KIR,KOR,KWT,KGZ,LAO,LVA,LBN,LSO,LBR,LBY,LIE,LTU,LUX,MDG,MWI,MYS,MDV,MLI,MLT,MHL,MRT,MUS,MEX,FSM,MDA,MCO,MNG,MNE,MAR,MOZ,MMR,NAM,NPL,NLD,NZL,NIC,NER,NGA,MKD,NOR,OMN,PAK,PLW,PAN,PNG,PRY,PER,PHL,POL,PRT,QAT,ROU,RUS,RWA,KNA,LCA,VCT,WSM,SMR,STP,SAU,SEN,SRB,SYC,SLE,SGP,SVK,SVN,SLB,SOM,ZAF,SSD,ESP,LKA,SDN,SUR,SWE,CHE,SYR,TWN,TJK,TZA,THA,TLS,TGO,TON,TTO,TUN,TUR,TKM,TUV,UGA,UKR,ARE,GBR,USA,URY,UZB,VUT,VEN,VNM,ESH,YEM,ZMB,ZWE"

descriptions = {
    "avg-sup-temp-air": "Average Mean Surface Air Temperature",
    "avgmx-sup-temp-air": "Average Maximum Surface Air Temperature",
    "avgmn-sup-temp-air": "Average Minimum Surface Air Temperature",
    "mx-d-mxtemp": "Maximum of Daily Max-Temperature",
    "avg-1d-prec": "Average Largest 1-Day Precipitation",
    "grow-seas": "Growing Season Length",
    "mx-dryd": "Max Number of Consecutive Dry Days",
    "prec": "Precipitation",
}

data_info = {
    "avg-sup-temp-air": ("cmip6-x0.25", "timeseries", "tas", "timeseries", "annual", "1950-2014,2015-2100", "median,p10,p90", "historical,ssp119,ssp126,ssp245,ssp370,ssp585"),
    "avgmx-sup-temp-air": ("cmip6-x0.25", "timeseries", "tasmax", "timeseries", "annual", "1950-2014,2015-2100", "median,p10,p90", "historical,ssp119,ssp126,ssp245,ssp370,ssp585"),
    "avgmn-sup-temp-air": ("cmip6-x0.25", "timeseries", "tasmin", "timeseries", "annual", "1950-2014,2015-2100", "median,p10,p90", "historical,ssp119,ssp126,ssp245,ssp370,ssp585"),
    "mx-d-mxtemp": ("cmip6-x0.25", "timeseries", "txx", "timeseries", "annual", "1950-2014,2015-2100", "median,p10,p90", "historical,ssp119,ssp126,ssp245,ssp370,ssp585"),
    "avg-1d-prec": ("cmip6-x0.25", "timeseries", "rx1day", "timeseries", "annual", "1950-2014,2015-2100", "median,p10,p90", "historical,ssp119,ssp126,ssp245,ssp370,ssp585"),
    "grow-seas": ("cmip6-x0.25", "timeseries", "gsl", "timeseries", "annual", "1950-2014,2015-2100", "median,p10,p90", "historical,ssp119,ssp126,ssp245,ssp370,ssp585"),
    "mx-dryd": ("cmip6-x0.25", "timeseries", "cdd", "timeseries", "annual", "1950-2014,2015-2100", "median,p10,p90", "historical,ssp119,ssp126,ssp245,ssp370,ssp585"),
    "prec": ("cmip6-x0.25", "timeseries", "pr", "timeseries", "annual", "1950-2014,2015-2100", "median,p10,p90", "historical,ssp119,ssp126,ssp245,ssp370,ssp585"),
}

temp_air_df = serial_wb_db(db_info=data_info, 
                            keys=keys+['model'], 
                            countries=countries,
                            merge_how="outer", 
                            output_json=False,
                            output_dfs=False)

temp_air_hist_df = temp_air_df.query('model == "historical"')
temp_air_hist_df = clean_wbstat(temp_air_hist_df, keys=keys, columns_to_pivot=['model', 'unit'])
temp_air_frc_df = temp_air_df.query('model != "historical"')
temp_air_frc_df = clean_wbstat(temp_air_frc_df, keys=keys, columns_to_pivot=['model', 'unit'])

db_name_hist = 'w_tmp_air_hist'
db_name_frc = 'w_tmp_air_frc'

pattern = ["name", "scenario", "unit"]

update_json(temp_air_hist_df, db_name_hist, pattern, descriptions)
update_json(temp_air_frc_df, db_name_frc, pattern, descriptions)

# ------ Connection -------- #
create_table_sql(df=temp_air_hist_df, db_name=db_name_hist)
default_connection(temp_air_hist_df, db_name_hist)

create_table_sql(df=temp_air_frc_df, db_name=db_name_frc)
default_connection(temp_air_frc_df, db_name_frc)


# IPCC DATA
# https://www.ipcc-data.org