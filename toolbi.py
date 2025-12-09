import pyodbc
import json
import os.path
import datetime
import re
import pandas as pd
import importlib
from typing import Optional, List, Dict, Any
from urllib.parse import urlparse, parse_qs, unquote
from tooldb import update_db
from sentence_transformers import SentenceTransformer
from itertools import product


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


def generate_chart_rows(
    data: Dict[str, Any],
    db_name: str,
    procedure: int = None,
    forbidden_group: set = None,
    forbidden_other: set = set(),
    delete_single_var_rows: bool = False,
    start_id: int = 1,
    chart_type: str = "",
    category: str = "",
    grouping: Optional[Dict[str, List[str]]] = None,
) -> List[Dict[str, Any]]:
    """
    Generate rows using procedures from the provided `data` dict for the given `db_name`.

    Parameters:
    - data: json file with data to be parsed.
    - db_name: name of the database (present in the first level of the json file) to be selected.
    - procedure: one of the following procedures to create groupings of variables and attributes:
        - 1: Graph for a unique Root bucket and a unique Selection.
        - 2: Graph for a unique Variable and each attribute with each other selection.
        - 3: Graph for a unique Root bucket and all combinations of selections in all attributes (Cartesian product).
    - delete_single_var_rows: it is possible that the procedures create singular lists, if this option is set to
      true, then these rows are not appended.
    - start_id: numeric id from which the rows start to be indexed, it increments only for rows included in the returned list
    - chart_type: the type of chart (hist, line, radar, area, pie) to be used.
    - category: the category of the chart.
    - grouping (optional): dict mapping root name -> list of top-level keys (those present in data[db_name]).
      If provided, this explicit grouping is used. Otherwise grouping is inferred from each top-level key
      by splitting at the first '-' and using the left part as the root (original behaviour).
    - forbidden_group: in procedure 2 these attributes are never going to be used as the fixed list for combinations, 
      while in procedure 3 these attributes will create n different lists filled with Cartesian product of their selections with all other selections.
    - forbidden_other: in procedure 2 these attributes are never going to be used as the changable list for combinations.

    Structure json:
      variable: {attribute1: {selection1, selection2}, attribute2: {selection1, selection2}}
      variable = root + name
    """
    if db_name not in data:
        raise KeyError(f"db_name '{db_name}' not found in data")

    rows: List[Dict[str, Any]] = []
    next_id = int(start_id)

    # Helper: build objects dict for a given list of keys (only keep existing keys)
    def build_objs_for_keys(keys: List[str]) -> Dict[str, Dict[str, List[str]]]:
        objs: Dict[str, Dict[str, List[str]]] = {}
        for key in keys:
            if key not in data[db_name]:
                raise KeyError(f"key '{key}' from grouping not found in data['{db_name}']")
            value = data[db_name][key]
            objs[key] = {}
            for attr, val in value.items():
                if attr == "description":
                    continue
                # ensure string -> split by comma; keep deterministic ordering
                vals = [x.strip() for x in str(val).split(",") if x.strip()]
                objs[key][attr] = vals
        return objs
    
    # Helper to build vars_list for a given mapping of attribute -> chosen value(s)
    def build_vars_list_for_fixed_map(fixed_map: Dict[str, str]) -> List[str]:
        """
        fixed_map: mapping for some attributes (usually the primary attrs). For
        the remaining attributes, iterate all combinations (lexicographic).
        Return a single aggregated vars list (one element per variable name).
        """
        remaining_attrs = [a for a in attr_names if a not in fixed_map]
        remaining_lists = [attr_unique[a] for a in remaining_attrs]

        remaining_combos = list(product(*remaining_lists)) if remaining_lists else [()]

        vars_list: List[str] = []
        # For each remaining-combination (lexicographic), append variables for each object
        for rem_combo in remaining_combos:
            rem_map = dict(zip(remaining_attrs, rem_combo)) if remaining_attrs else {}
            full_map = {**fixed_map, **rem_map}
            for obj_name in objs:
                parts = [obj_name] + [str(full_map[attr]) for attr in attr_names]
                vars_list.append("_".join(parts))
        return vars_list

    if procedure == 1:
        # Build groups per root either from provided grouping or by splitting keys
        groups: Dict[str, Dict[str, Dict[str, List[str]]]] = {}

        if grouping is not None:
            # Validate and build groups according to provided mapping
            # Expect mapping: root -> list of top-level keys
            for root, keys in grouping.items():
                if not isinstance(keys, (list, tuple)):
                    raise TypeError(f"grouping['{root}'] must be a list of keys")
                groups[root] = build_objs_for_keys(list(keys))
        else:
            # Infer grouping by prefix before '-'
            # groups[root][key] = { attr: [vals...] }
            for key, value in data[db_name].items():
                root = key.split('-', 1)[0]
                groups.setdefault(root, {})
                groups[root].setdefault(key, {})
                for attr, val in value.items():
                    if attr == "description":
                        continue
                    groups[root][key][attr] = [x.strip() for x in str(val).split(",") if x.strip()]

        # Iterate per root
        for root, objs in groups.items():
            if not objs:
                continue

            # Collect attribute names from the first object (assume consistent attrs)
            first_obj = next(iter(objs.values()))
            attr_names = list(first_obj.keys())

            # For each attribute, collect unique values across all objects in this root
            attr_unique: Dict[str, List[str]] = {}
            for attr in attr_names:
                vals = set()
                for obj in objs.values():
                    vals.update(obj.get(attr, []))
                # deterministic order
                attr_unique[attr] = sorted(vals)

            # Build Cartesian product of attributes
            combos = list(product(*[attr_unique[attr] for attr in attr_names]))

            for combo in combos:
                combo_dict = dict(zip(attr_names, combo))
                vars_list = []
                for obj_name in objs:
                    var_parts = [obj_name] + [combo_dict[attr] for attr in attr_names]
                    vars_list.append("_".join(var_parts))
                    
                vars_string = "+".join(vars_list)
                row = {
                    "id": next_id,
                    "title": "",
                    "description": "",
                    "db_name": db_name,
                    "vars": vars_string,
                    "chart_type": chart_type,
                    "category": category,
                    "vector_dim": "",
                }
                if not (delete_single_var_rows and len(vars_list) == 1):
                    rows.append(row)
                    next_id += 1

    elif procedure == 2:
        for key, value in data[db_name].items():
            attributes: Dict[str, List[str]] = {}
            for attribute, val in value.items():
                if attribute == "description":
                    continue
                attr_list = [x.strip() for x in str(val).split(",") if x.strip()]
                attributes[attribute] = attr_list

            if not attributes:
                continue

            attr_names = list(attributes.keys())  # preserve original order
            n_attrs = len(attr_names)

            # configuration: never use these as the varying/group attribute
            if not forbidden_group:
                forbidden_group = {"unit"}
            
            preferred_placeholders = ["total", "tot", "t"]

            # Determine placeholder for each forbidden_other attribute based on existing values
            forbidden_placeholder_map: Dict[str, str] = {}
            for forb in forbidden_other:
                # find the attribute in attr_names (case-insensitive)
                matched_attr_name = next((an for an in attr_names if an.lower() == forb.lower()), None)
                if matched_attr_name is None:
                    continue  # attribute not present, skip

                values_lower = [str(v).lower() for v in attributes[matched_attr_name]]
                # pick the first preferred placeholder present in the values
                chosen = next((ph for ph in preferred_placeholders if ph.lower() in values_lower), None)
                if chosen is None:
                    # If none of the preferred placeholders present, skip this attribute
                    continue
                forbidden_placeholder_map[matched_attr_name.lower()] = chosen

            # Generate combinations
            for g in range(n_attrs):
                group_name = attr_names[g]

                # Skip disallowed group attributes
                if group_name.lower() in {x.lower() for x in forbidden_group}:
                    continue

                group_list = attributes[group_name]

                # other indices: exclude group AND forbidden_other
                other_indices = [
                    i for i in range(n_attrs)
                    if i != g and attr_names[i].lower() not in {x.lower() for x in forbidden_other}
                ]
                other_lists = [attributes[attr_names[i]] for i in other_indices]

                other_combinations = list(product(*other_lists)) if other_lists else [()]

                for combo in other_combinations:
                    vars_list = []
                    for group_item in group_list:
                        parts = []
                        combo_idx = 0
                        for i in range(n_attrs):
                            name_lower = attr_names[i].lower()
                            if i == g:
                                parts.append(str(group_item))
                            elif name_lower in forbidden_placeholder_map:
                                # use the determined placeholder (must exist in values)
                                parts.append(forbidden_placeholder_map[name_lower])
                            else:
                                parts.append(str(combo[combo_idx]))
                                combo_idx += 1

                        suffix = "_".join(parts)
                        vars_list.append(f"{key}_{suffix}")

                    vars_string = "+".join(vars_list)
                    row = {
                        "id": next_id,
                        "title": "",
                        "description": "",
                        "db_name": db_name,
                        "vars": vars_string,
                        "chart_type": chart_type,
                        "category": category,
                        "vector_dim": "",
                    }
                    if not (delete_single_var_rows and len(vars_list) == 1):
                        rows.append(row)
                    next_id += 1

    elif procedure == 3:
        # Build groups per root (same grouping logic as proc 1)
        groups: Dict[str, Dict[str, Dict[str, List[str]]]] = {}

        if grouping is not None:
            for root, keys in grouping.items():
                if not isinstance(keys, (list, tuple)):
                    raise TypeError(f"grouping['{root}'] must be a list of keys")
                groups[root] = build_objs_for_keys(list(keys))
        else:
            for key, value in data[db_name].items():
                root = key.split('-', 1)[0]
                groups.setdefault(root, {})
                groups[root].setdefault(key, {})
                for attr, val in value.items():
                    if attr == "description":
                        continue
                    groups[root][key][attr] = [x.strip() for x in str(val).split(",") if x.strip()]

        if not forbidden_group:
            forbidden_group = {"unit"}

        forbidden_primary_lc = {x.lower() for x in (forbidden_group or set())}

        for root, objs in groups.items():
            if not objs:
                continue

            # attribute order is taken from the first object (preserve keys order)
            first_obj = next(iter(objs.values()))
            attr_names = list(first_obj.keys())

            # collect unique sorted values per attribute across objects in the root
            attr_unique: Dict[str, List[str]] = {}
            for attr in attr_names:
                vals = set()
                for obj in objs.values():
                    vals.update(obj.get(attr, []))
                attr_unique[attr] = sorted(vals)

            # determine primary attributes (to split on)
            primary_attrs = [a for a in attr_names if a.lower() in forbidden_primary_lc]

            if not primary_attrs:
                # No forbidden_primary present => single aggregated var-list for the entire cartesian product
                # Build one fixed_map == {} so remaining are all attributes
                vars_list = build_vars_list_for_fixed_map({})
                if not (delete_single_var_rows and len(vars_list) == 1):
                    rows.append({
                        "id": next_id,
                        "title": "",
                        "description": "",
                        "db_name": db_name,
                        "vars": "+".join(vars_list),
                        "chart_type": chart_type,
                        "category": category,
                        "vector_dim": "",
                    })
                    next_id += 1
            else:
                # Split output by the cartesian product of primary attribute values
                primary_value_lists = [attr_unique[a] for a in primary_attrs]
                # Skip root if any primary attribute has no values
                if any(len(lst) == 0 for lst in primary_value_lists):
                    continue

                for prim_values in product(*primary_value_lists):
                    fixed_primary_map = dict(zip(primary_attrs, prim_values))
                    vars_list = build_vars_list_for_fixed_map(fixed_primary_map)
                    if not (delete_single_var_rows and len(vars_list) == 1):
                        rows.append({
                            "id": next_id,
                            "title": "",
                            "description": "",
                            "db_name": db_name,
                            "vars": "+".join(vars_list),
                            "chart_type": chart_type,
                            "category": category,
                            "vector_dim": "",
                        })
                        next_id += 1

    else:
        raise ValueError("Procedure not recognized")

    return rows


def update_chart_rows(
        df:pd.DataFrame, 
        updates:List[str], 
        id_val:int, 
        id_column:str="id", 
        update_columns:List[str]=None, 
        send:bool=True,
        full_update:bool=False,
        vectorization:bool=True,
        dest_table:str="",
        string_in:str="title", 
        vect_out:str="vector_dim", 
        conn_dest:str="connDest.json"
        ):
    """
    Update the newly generated chart rows filling empty rows (default to title and description).
    Then if vectorization is set to true, derive the semantic vector transformation.
    If send is true send the complete new rows to the database in the dest_table.
    """
    mask = df[id_column] >= id_val
    rows_to_update = df.loc[mask]

    if len(rows_to_update) != len(updates):
        raise ValueError(
            f"Mismatch: {len(rows_to_update)} rows but {len(updates)} updates"
        )
    
    if update_columns==None:
        update_columns = ["title", "description"]

    for i, col in enumerate(update_columns):
        df.loc[mask, col] = [u[i] for u in updates]

    if send:
        if vectorization:
            model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        dest = SqlDatasource()
        dest.load(conn_dest)
        dest.connect()
        destination_table = dest.gettable(dest_table)

        rows = df if full_update else df.loc[mask] 

        for _, row in rows.iterrows():
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
    
    return df