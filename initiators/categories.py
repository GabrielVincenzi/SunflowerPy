from tools.toolbi import SqlDatasource

# ------- Connect to Cockroach (dest) -------
dest = SqlDatasource()
dest.load('connDest.json')
dest.connect()

# ------- Fetch distinct categories from charts table -------
result = dest.execute("SELECT DISTINCT category FROM charts")
df_categories = result.fetchframe()
result.commit()

df_categories = df_categories.reset_index().rename(columns={"index": "id"})
df_categories["id"] = df_categories["id"] + 1

# ------- Modify the Category database -------
dest.execute('DELETE FROM categories').commit()

category_table = dest.gettable('categories')
category_table.insertmany(df_categories)
category_table.commit()

dest.disconnect()
