import pandas as pd
import glob
from toolbi import default_connection, create_table_sql
from tooldb import update_json

path_pattern = "staticTables/press/*.csv"
dfs = []

for file in glob.glob(path_pattern):
    year = file.split('/')[-1].split('.')[0]
    df = pd.read_csv(f'staticTables/press/{year}.csv', sep=';', decimal=',')
    df = df.rename(columns={'Year (N)': 'time_period', 'Score 2025': 'Score', 'ISO': 'geo'})
    drop_cols = {'Country_EN', 'Country_FR', 'Country_ES', 'Country_AR', 'Country_PT', 'Country_FA', 
                'Rank N-1', 'Rank evolution', 'Zone', 'Situation', 'Score N-1', 'Score evolution'}

    df.drop(columns=drop_cols.intersection(df.columns), inplace=True)
    dfs.append(df)

press_df = pd.concat(dfs, ignore_index=True)
press_df.columns = press_df.columns.str.replace(' ', '-').str.lower()
press_df['time_period'] = pd.to_datetime(press_df['time_period'], format="%Y")
press_df = press_df.sort_values(by='time_period').reset_index(drop=True)

# ------ JSON update -------- #
db_name = 's_press'
pattern = ['name', 'context']
descriptions = {
    'Score': 'Total score between each sub-area', 
    'Rank': 'Ranking between countries participating in the survey', 
    'Political-Context': 'Degree of support and respect for media autonomy and holding politicians accountable, acceptance of journalistic approaches',
    'Economic-Context': 'Economic constraints linked to governmental policies, to non-state actors or to media owners',
    'Legal-Context': 'Degree to which journalists and media are free to work without censorship or judicial sanctions, access information without discrimination, impunity for those responsible for acts of violence against journalists',
    'Social-Context': 'Social constraints resulting from denigration and attacks on the press, cultural constraints, including pressure on journalist',
    'Safety': 'Bodily harm, psychological or emotional distress and professional harm to journalists',
}
update_json(press_df, db_name, pattern, descriptions)

# ------ Connection -------- #
create_table_sql(df=press_df, db_name=db_name)
default_connection(press_df, db_name, db_source="Reporters without Borders")