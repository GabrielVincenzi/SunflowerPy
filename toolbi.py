import pyodbc
import json
import os.path
import datetime
import re
import pandas as pd
import importlib
from typing import Optional, List
from urllib.parse import urlparse, parse_qs, unquote
from tooldb import update_db
from sentence_transformers import SentenceTransformer


class DatasourceTable:
    def __init__(self, tablename: str, datasource) -> None:
        self.datasource = datasource
        self.cursor = datasource._connection.cursor()

        # Normalize schema and table name
        if '.' in tablename:
            schema, tname = tablename.split('.')
        else:
            schema, tname = 'public', tablename

        if tname.startswith('"') and tname.endswith('"'):
            tname = tname[1:-1]
        if schema.startswith('"') and schema.endswith('"'):
            schema = schema[1:-1]

        self.tablename = f'{schema}."{tname}"'  # quote table name for CockroachDB

        # Fetch column names from information_schema
        qry = datasource.execute(
            """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = :schema
              AND table_name = :table
            ORDER BY ordinal_position
            """,
            {'schema': schema, 'table': tname}
        )
        self.columns = qry.fetchall()
        qry.close()

        self._sql_insert = ''
        self._insert_columns = []

    def _createsql_insert(self, params: list[dict[str, object]] | pd.DataFrame) -> None:
        # Determine columns to insert based on input data
        self._insert_columns = []

        sample = params[0] if isinstance(params, list) else params.columns

        for c in self.columns:
            if c['column_name'] in sample:
                self._insert_columns.append(c['column_name'])

        quoted_columns = [f'"{col}"' for col in self._insert_columns]
        placeholders = ", ".join(["?"] * len(self._insert_columns))
        self._sql_insert = f'INSERT INTO {self.tablename} ({", ".join(quoted_columns)}) VALUES ({placeholders})'
        #print(f"Sample: {sample}")
        #print(f"Database columns: {self.columns}")
        #print(self._insert_columns)
        #print(self._sql_insert)


    def commit(self) -> None:
        self.cursor.commit()

    def close(self) -> None:
        self.cursor.close()

    def insertone(self, params: dict[str, object]) -> None:
        self.insertmany([params])

    def insertmany(self, params: list[dict[str, object]] | pd.DataFrame) -> None:
        # Empty check
        if isinstance(params, list):
            if not params:
                return
        else:  # DataFrame
            if params.empty:
                return

        # Prepare insert SQL if not already prepared
        if not self._sql_insert:
            self._createsql_insert(params)

        args = []

        if isinstance(params, list):
            for row in params:
                args.append([row[k] for k in self._insert_columns])
        else:  # DataFrame
            params = params.reset_index(drop=True)
            for _, row in params.iterrows():
                args.append([row[k] for k in self._insert_columns])

        # Execute insert
        self.cursor.executemany(self._sql_insert, args)


class DatasourceCursor:
    def __init__(self, cursor: pyodbc.Cursor) -> None:
        self.cursor = cursor
        if cursor.description is not None:
            self.field_map = [col[0] for col in cursor.description]

    def close(self) -> None:
        self.cursor.close()

    def commit(self) -> None:
        self.cursor.commit()
        
    def fetchone(self) -> dict[str, object]|None:
        result = {}
        row = self.cursor.fetchone()
        if row is None:
            return None
        i = 0
        for name in self.field_map:
            result[name] = row[i]
            i += 1
        return result
    
    def fetchall(self) -> list[dict[str, object]]:
        result = []
        while (row := self.fetchone()) is not None:
            result.append(row)
        return result
    
    def fetchframe(self) -> pd.DataFrame:
        return pd.DataFrame(self.fetchall())
            
class SqlDatasource:
    def __init__(self) -> None:
        self.database_url = ""

    def load(self, filename):
        if os.path.exists(filename):
            with open(filename, "r") as fs:
                conf = json.load(fs)
            self.database_url = conf["DATABASE_URL"]

    def connect(self):
        parsed = urlparse(self.database_url)
        user = unquote(parsed.username or "")
        pwd = unquote(parsed.password or "")
        host = parsed.hostname or ""
        port = parsed.port or 26257
        db = parsed.path.lstrip("/") or "defaultdb"
        qs = parse_qs(parsed.query)
        sslmode = qs.get("sslmode", ["require"])[0]
        sslrootcert = unquote(qs.get("sslrootcert", [""])[0]) or None

        driver_name = "PostgreSQL Unicode"  # must match odbcinst -q -d

        dsn = (
            f"DRIVER={{{driver_name}}};"
            f"SERVER={host};PORT={port};DATABASE={db};"
            f"UID={user};PWD={pwd};sslmode={sslmode};"
        )
        if sslrootcert:
            dsn += f"sslrootcert={sslrootcert};"

        self._connection = pyodbc.connect(dsn, timeout=30)
        return self._connection

    def disconnect(self) -> None:
        if self._connection is not None:
            self._connection.close()
            self._connection = None

    def execute(self, sql: str, parameters: Optional[dict[str, object]] = None, wildcards: Optional[dict[str, str]] = None) -> DatasourceCursor:
        # Apply wildcards first
        if wildcards:
            for wld, val in wildcards.items():
                sql = sql.replace('@' + wld, val)

        # Handle named parameters
        if parameters:
            # Find :param placeholders
            matches = re.findall(r'[:]\w+', sql)
            args = [parameters[m[1:]] for m in matches]
            # Replace :param with ?
            sql = re.sub(r'[:]\w+', r'?', sql)
            cursor = self._connection.execute(sql, args)
        else:
            cursor = self._connection.execute(sql)

        return DatasourceCursor(cursor)
    
    def gettable(self, tablename: str) -> DatasourceTable:
        return DatasourceTable(tablename, self)


class DatasourceTools:
    FILENAME = 'parameters.json'
    COMPANYNAME = ''

    @staticmethod
    def execute_modules(modules):
        for m in modules:
            DatasourceTools.write_log('Start execution of ' + m)
            try:
                importlib.import_module(m)
            except Exception as e:
                DatasourceTools.write_log('Error ' + str(e) + ' in ' + m)
            DatasourceTools.write_log('Execution of ' + m + ' terminated')

    @staticmethod
    def write_log(message):
        fs = open('batch.log', 'a')
        fs.write(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' ' + message + '\n')
        fs.close()

    @staticmethod
    def load_json():
        conf = {}

        if os.path.exists(DatasourceTools.FILENAME):
            fs = open(DatasourceTools.FILENAME, "r")
            conf = json.load(fs)
            fs.close()
       
        return conf
    
    @staticmethod
    def save_json(conf):
        dump = json.dumps(conf, indent=2)
        fs = open(DatasourceTools.FILENAME, "w")
        fs.write(dump)
        fs.close()        

    @staticmethod
    def get_date(key):
        conf = DatasourceTools.load_json()
        if DatasourceTools.COMPANYNAME in conf:
            conf = conf[DatasourceTools.COMPANYNAME]
            if key in conf:
                return datetime.datetime.strptime(conf[key], '%Y-%m-%d').date()
            
    def set_date(key, dt):
        conf = DatasourceTools.load_json()
        if DatasourceTools.COMPANYNAME not in conf:
            conf[DatasourceTools.COMPANYNAME] = {}

        conf[DatasourceTools.COMPANYNAME][key] = datetime.date.strftime(dt, '%Y-%m-%d')
        DatasourceTools.save_json(conf)


def default_connection(df_to_insert, db_name:str, db_source:str=None, geo_col:str="geo", time_period_col:str="time_period", period_type:str="Y", db_update:bool=True):
    if db_update:
        db_source = (
            "eurostat" if db_name.lower().startswith("e_")
            else "oecd" if db_name.lower().startswith("o_")
            else db_source  # keep the inputted one
        )
        periods = sorted(
            df_to_insert[time_period_col]
            .dropna()
            .dt.to_period(period_type)
            .astype(str)
            .unique()
        )
        available_periods = f"{periods[0]}+{periods[-1]}" if periods else ""
        available_geos = "+".join(df_to_insert[geo_col].unique())
        update_db(db_name, available_geos, available_periods, db_source)

    dest = SqlDatasource()
    dest.load('connDest.json')
    dest.connect()

    dest.execute(f'DELETE FROM {db_name}').commit()

    default_table = dest.gettable(db_name)
    default_table.insertmany(df_to_insert)
    default_table.commit()

    dest.disconnect()


def send_df(df:pd.DataFrame, dest_table:str, file_path, new_rows:dict=None, by_row:bool=True, 
                vectorization:bool=True, string_in:str="title", vect_out:str="vector_dim", conn_dest:str="connDest.json"):
    if vectorization:
        model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    dest = SqlDatasource()
    dest.load(conn_dest)
    dest.connect()
    destination_table = dest.gettable(dest_table)

    if new_rows:
        df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
        df.to_csv(file_path, index=False)

    rows = new_rows if by_row else df.to_dict(orient="records")

    for row in rows:
        if vectorization:
            embs = model.encode(row[string_in],
                                convert_to_numpy=True,
                                batch_size=64,
                                normalize_embeddings=True)
            vals = embs.tolist()
            vec_str = "[" + ",".join(f"{float(x):.10f}" for x in vals) + "]"   # e.g. "[0.012345,-0.023456,...]"
            row[vect_out] = vec_str

        destination_table.insertone(row)

    destination_table.commit()
    dest.disconnect()
                      
def _quote_ident(name: str) -> str:
    """
    Safely quote a Postgres identifier using double quotes.
    Internal double quotes are doubled per SQL standard.
    """
    if name is None:
        raise ValueError("Identifier name cannot be None")
    # strip leading/trailing whitespace to avoid accidental problems
    nm = str(name).strip()
    escaped = nm.replace('"', '""')
    return f'"{escaped}"'


def create_table_sql(
    df: object,
    db_name: str,
    *,
    dest= "connDest.json",
    canonical_geo: str = "geo",
    geo_type: str = "VARCHAR(10) NOT NULL",
    canonical_time: str = "time_period",
    time_type: str = "TIMESTAMP NOT NULL",
    default_col_type: str = "FLOAT8 NULL",
) -> str:
    """
    Build a CREATE TABLE IF NOT EXISTS SQL statement.

    Parameters
    ----------
    columns_or_df : Iterable[str] or object with .columns (like pandas.DataFrame)
        Source of column names. If it's a DataFrame, its .columns will be used.
    db_name : str
        Unquoted table name to create.
    canonical_geo : str
        Name of canonical geo column to always include (default "geo").
    geo_type : str
        SQL type for geo column (default "VARCHAR(10) NOT NULL").
    canonical_time : str
        Name of canonical time column to always include (default "time_period").
    time_type : str
        SQL type for canonical time column (default "TIMESTAMP NOT NULL").
    default_col_type : str
        Default SQL type for other columns (default "FLOAT8 NULL").
    type_map : mapping
        Optional dict mapping column_name (exact) -> SQL type string to override default.

    Returns
    -------
    str
        CREATE TABLE IF NOT EXISTS ... SQL text
    """
    # extract column names
    cols: List[str] = []
    cols = df.columns

    unique_cols = [c for c in cols if c.strip().lower() != canonical_geo.lower()]
    unique_cols = [c for c in unique_cols if c.strip().lower() != canonical_time.lower()]

    # Now build column definitions
    col_defs: List[str] = []
    # canonical geo and time first (order matters for readability)
    col_defs.append(f"{_quote_ident(canonical_geo)} {geo_type}")
    col_defs.append(f"{_quote_ident(canonical_time)} {time_type}")

    for c in unique_cols:
        lower = c.strip().lower()
        # skip canonical geo/time
        if lower in (canonical_geo.lower(), canonical_time.lower()):
            continue
        col_defs.append(f"{_quote_ident(c)} {default_col_type}")

    # Compose CREATE TABLE SQL
    quoted_table = _quote_ident(db_name)
    pk = f'PRIMARY KEY ({_quote_ident(canonical_geo)}, {_quote_ident(canonical_time)})'

    sql_lines = [f"CREATE TABLE IF NOT EXISTS {quoted_table} ("]
    # add column lines with commas; last column before PK will have a comma as we add PK afterward
    for cd in col_defs:
        sql_lines.append(f"    {cd},")
    sql_lines.append(f"    {pk}")
    sql_lines.append(");")
    sql_text = "\n".join(sql_lines)
    
    # Execute using dest; be defensive about API surface
    try:
        dest = SqlDatasource()
        dest.load('connDest.json')
        dest.connect()

        dest.execute(sql_text).commit()
        dest.disconnect()
    except Exception as exc:
        return sql_text, {"executed": False, "message": str(exc)}
    