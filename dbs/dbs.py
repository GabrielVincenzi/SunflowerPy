import pandas as pd
from toolbi import SqlDatasource

plots_df = pd.read_csv('dbs/dbsData.csv')

# ------ Connection -------- #
dest = SqlDatasource()
dest.load('connDest.json')
dest.connect()

dest.execute('DELETE FROM dbs').commit()

plots_table = dest.gettable('dbs')
plots_table.insertmany(plots_df)
plots_table.commit()

dest.disconnect()