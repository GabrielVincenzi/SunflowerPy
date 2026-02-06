import pyodbc
import json
import os.path
import datetime
import re
import pandas as pd
import importlib
from typing import Optional, List, Dict, Tuple, Any, Iterable, Union
from urllib.parse import urlparse, parse_qs, unquote
from tools.tooldb import update_db
from sentence_transformers import SentenceTransformer
from itertools import product
import uuid


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


def title_to_uuid(title: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, title))

def load_json(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def chunk_list(lst, size=4):
    return [lst[i:i+size] for i in range(0, len(lst), size)]

def default_connection(df_to_insert, db_name:str, db_source:str=None, geo_col:str="geo", time_period_col:str="time_period", period_type:str="Y", db_update:bool=True, period_list:bool=False):
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
        if period_list:
            available_periods = "+".join(periods) if periods else ""
        else:
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
    geo_type: str = "VARCHAR(50) NOT NULL",
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
        SQL type for geo column (default "VARCHAR(50) NOT NULL").
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
    other_placeholder: List[str] = [],
    delete_single_var_rows: bool = False,
    chart_type: str = "",
    category: str = "",
    grouping: Optional[Dict[str, List[str]]] = None,
    control_db: bool = False,
    db_to_control: str = "",
    conn_file: str = "connDest.json",
) -> List[Dict[str, Any]]:
    """
    Generate rows using procedures from the provided `data` dict for the given `db_name`.

    Parameters:
    - data: json file with data to be parsed.
    - db_name: name of the database (present in the first level of the json file) to be selected.
    - procedure: one of the following procedures to create groupings of variables and attributes:
        - 1: Graph for a unique Root bucket and a unique selection combination.
        - 2: Graph for a unique Variable and each attribute with each other selection.
        - 3: Graph for a unique Root bucket and all combinations of selections in all attributes (Cartesian product).
        - 4: Graph for a unique variable and a unique attribute with all its selections in case of trailing attributes (after description).
    - delete_single_var_rows: it is possible that the procedures create singular lists, if this option is set to
      true, then these rows are not appended.
    - chart_type: the type of chart (hist, line, radar, area, pie) to be used.
    - category: the category of the chart.
    - grouping (optional): dict mapping root name -> list of top-level keys (those present in data[db_name]).
      If provided, this explicit grouping is used. Otherwise grouping is inferred from each top-level key
      by splitting at the first '-' and using the left part as the root (original behaviour).
    - forbidden_group: in procedure 2 these attributes are never going to be used as the fixed list for combinations, 
      while in procedure 3 these attributes will create n different lists filled with Cartesian product of their selections with all other selections.
    - forbidden_other: in procedure 2 these attributes are never going to be used as the changeable list for combinations, so only totals are used
      and the same in procedure 3 where only totals will be used.
    - other_placeholder: in procedure 2 these selection is used to define the totals of a given attribute to use as the filling selection if 
      there are forbidden_other attributes. Input a string in the list for each forbidden_other attribute.
    - control_db: if True, only variables that exist as columns in `db_to_control` will be kept.
    - db_to_control: the table (or object) name to query for column names.
    - conn_file: path to connection JSON used by SqlDatasource().load(...)

    Structure json:
      variable: {attribute1: {selection1, selection2}, attribute2: {selection1, selection2}}
      variable = root + name
    """
    if db_name not in data:
        raise KeyError(f"db_name '{db_name}' not found in data")

    rows: List[Dict[str, Any]] = []

    # --- DB control: fetch column names once (if requested) ---
    db_column_map: Dict[str, str] = {}

    if control_db:
        if not db_to_control:
            db_to_control = db_name

        dest = SqlDatasource()
        dest.load(conn_file)
        dest.connect()

        db_cntr = dest.gettable(db_to_control)
        dest.disconnect()

        # lower-case lookup → real DB column name
        db_column_map = {
            row["column_name"].strip().lower(): row["column_name"].strip()
            for row in db_cntr.columns
            if "column_name" in row and row["column_name"]
        }

        if not db_column_map:
            raise RuntimeError(
                f"No columns found for table '{db_to_control}'"
            )

    # Helper: Efficient filtering
    def filter_vars_by_db(vars_list: List[str]) -> List[str]:
        """Filter + normalize vars using DB column names (O(1) lookup)."""
        if not control_db:
            return vars_list

        return [
            db_column_map[v.lower()]
            for v in vars_list
            if v.lower() in db_column_map
        ]

    # Helper: build objects dict for a given list of keys (only keep existing keys)
    def build_objs_for_keys(keys: List[str]) -> Tuple[Dict[str, Dict[str, List[str]]], Dict[str, List[str]]]:
        objs: Dict[str, Dict[str, List[str]]] = {}
        orders: Dict[str, List[str]] = {}
        for key in keys:
            if key not in data[db_name]:
                raise KeyError(f"key '{key}' from grouping not found in data['{db_name}']")
            value = data[db_name][key]
            objs[key] = {}
            orders[key] = []
            for attr, val in value.items():
                orders[key].append(attr)
                if attr == "description":
                    continue
                vals = [x.strip() for x in str(val).split(",") if x.strip()]
                objs[key][attr] = vals
        return objs, orders

    # Helper to find trailing attributes (those appearing after "description" in the original ordering)
    def trailing_attrs_for_order(attr_order: List[str]) -> List[str]:
        if "description" in attr_order:
            idx = attr_order.index("description")
            # attributes after description
            return [a for a in attr_order[idx + 1:] if a != "description"]
        return []

    # Helper to build vars_list for a given mapping of attribute -> chosen value(s)
    def build_vars_list_for_fixed_map(fixed_map: Dict[str, str]) -> List[str]:
        vars_list: List[str] = []

        for obj_name, obj_attrs in objs.items():
            # Only attributes that THIS variable actually has
            valid_attrs = [a for a in attr_names if a in obj_attrs]

            remaining_attrs = [a for a in valid_attrs if a not in fixed_map]
            remaining_lists = [obj_attrs[a] for a in remaining_attrs]

            remaining_combos = list(product(*remaining_lists)) if remaining_lists else [()]

            for rem_combo in remaining_combos:
                rem_map = dict(zip(remaining_attrs, rem_combo))
                parts = [obj_name]

                for attr in valid_attrs:
                    if attr in fixed_map:
                        parts.append(str(fixed_map[attr]))
                    else:
                        parts.append(str(rem_map[attr]))

                vars_list.append("_".join(parts))

        return vars_list


    if procedure == 1:
        # Build groups per root either from provided grouping or by splitting keys
        groups: Dict[str, Dict[str, Dict[str, List[str]]]] = {}
        groups_orders: Dict[str, Dict[str, List[str]]] = {}

        if grouping is not None:
            for root, keys in grouping.items():
                if not isinstance(keys, (list, tuple)):
                    raise TypeError(f"grouping['{root}'] must be a list of keys")
                objs, orders = build_objs_for_keys(list(keys))
                groups[root] = objs
                groups_orders[root] = orders
        else:
            for key, value in data[db_name].items():
                root = key.split('-', 1)[0]
                groups.setdefault(root, {})
                groups[root].setdefault(key, {})
                groups_orders.setdefault(root, {})
                groups_orders[root].setdefault(key, list(value.keys()))
                for attr, val in value.items():
                    if attr == "description":
                        continue
                    groups[root][key][attr] = [x.strip() for x in str(val).split(",") if x.strip()]

        # Iterate per root
        for root, objs in groups.items():
            if not objs:
                continue

            # Attribute order from first object
            first_key = next(iter(objs.keys()))
            first_obj = objs[first_key]
            order_for_first = groups_orders.get(root, {}).get(first_key, list(first_obj.keys()))
            trailing_attrs = trailing_attrs_for_order(order_for_first)
            attr_names = [a for a in list(first_obj.keys()) if a not in trailing_attrs]

            # collect unique sorted values per attribute across objects in the root
            attr_unique: Dict[str, List[str]] = {}
            for attr in attr_names:
                vals = set()
                for obj in objs.values():
                    vals.update(obj.get(attr, []))
                attr_unique[attr] = sorted(vals)

            # Build Cartesian product of attributes (excluding trailing)
            combos = list(product(*[attr_unique[attr] for attr in attr_names]))

            for combo in combos:
                combo_dict = dict(zip(attr_names, combo))
                vars_list = []
                for obj_name in objs:
                    var_parts = [obj_name] + [combo_dict[attr] for attr in attr_names]
                    vars_list.append("_".join(var_parts))

                # filter & normalize against DB if requested
                filtered = filter_vars_by_db(vars_list)
                if not filtered:
                    continue

                vars_string = "+".join(filtered)
                row = {
                    "chart_id": "",
                    "title": "",
                    "description": "",
                    "db_name": db_name,
                    "vars": vars_string,
                    "chart_type": chart_type,
                    "category": category,
                    "vector_dim": "",
                }
                if not (delete_single_var_rows and len(filtered) == 1):
                    rows.append(row)

    elif procedure == 2:
        for key, value in data[db_name].items():
            # Determine original attribute order for this variable
            original_order = list(value.keys())
            trailing_attrs = trailing_attrs_for_order(original_order)

            # Build attributes dict excluding description (we keep all attributes values accessible,
            # but we'll exclude trailing_attrs from cartesian use)
            attributes: Dict[str, List[str]] = {}
            for attribute, val in value.items():
                if attribute == "description":
                    continue
                attr_list = [x.strip() for x in str(val).split(",") if x.strip()]
                attributes[attribute] = attr_list

            if not attributes:
                continue

            # Exclude trailing attributes from the attributes used for combinations
            # Keep original order for the remaining attributes
            attr_names_all = [a for a in list(attributes.keys())]  # preserve original order
            attr_names = [a for a in attr_names_all if a not in trailing_attrs]
            n_attrs = len(attr_names)

            # configuration: never use these as the varying/group attribute
            if not forbidden_group:
                forbidden_group = {"unit"}

            preferred_placeholders = ["total", "tot", "t", "all"] + other_placeholder

            # Determine placeholder for each forbidden_other attribute based on existing values
            forbidden_placeholder_map: Dict[str, str] = {}
            for forb in forbidden_other:
                matched_attr_name = next((an for an in attr_names if an.lower() == forb.lower()), None)
                if matched_attr_name is None:
                    continue  # attribute not present or was trailing, skip

                values_lower = [str(v).lower() for v in attributes[matched_attr_name]]
                chosen = next((ph for ph in preferred_placeholders if ph.lower() in values_lower), None)
                if chosen is None:
                    continue
                forbidden_placeholder_map[matched_attr_name.lower()] = chosen

            if n_attrs == 0:
                continue

            # Prepare lists for other attributes when a group is chosen
            for g in range(n_attrs):
                group_name = attr_names[g]

                # Skip disallowed group attributes
                if group_name.lower() in {x.lower() for x in forbidden_group}:
                    continue

                group_list = attributes[group_name]

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
                            elif (
                                    name_lower in forbidden_placeholder_map
                                    and attr_names[i] in attributes   # attribute exists for this variable
                                ):
                                    parts.append(forbidden_placeholder_map[name_lower])
                            else:
                                parts.append(str(combo[combo_idx]))
                                combo_idx += 1

                        suffix = "_".join(parts)
                        vars_list.append(f"{key}_{suffix}")

                    # filter & normalize
                    filtered = filter_vars_by_db(vars_list)
                    if not filtered:
                        continue

                    vars_string = "+".join(filtered)
                    row = {
                        "chart_id": "",
                        "title": "",
                        "description": "",
                        "db_name": db_name,
                        "vars": vars_string,
                        "chart_type": chart_type,
                        "category": category,
                        "vector_dim": "",
                    }
                    if not (delete_single_var_rows and len(filtered) == 1):
                        rows.append(row)

            # trailing attributes skipped here (procedure 4 will handle)

    elif procedure == 3:
        # Build groups per root (same grouping logic as proc 1) but we capture attribute orders
        groups: Dict[str, Dict[str, Dict[str, List[str]]]] = {}
        groups_orders: Dict[str, Dict[str, List[str]]] = {}

        if grouping is not None:
            for root, keys in grouping.items():
                if not isinstance(keys, (list, tuple)):
                    raise TypeError(f"grouping['{root}'] must be a list of keys")
                objs, orders = build_objs_for_keys(list(keys))
                groups[root] = objs
                groups_orders[root] = orders
        else:
            for key, value in data[db_name].items():
                root = key.split('-', 1)[0]
                groups.setdefault(root, {})
                groups[root].setdefault(key, {})
                groups_orders.setdefault(root, {})
                groups_orders[root].setdefault(key, list(value.keys()))
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

            first_key = next(iter(objs.keys()))
            first_obj = objs[first_key]
            order_for_first = groups_orders.get(root, {}).get(first_key, list(first_obj.keys()))
            trailing_attrs = trailing_attrs_for_order(order_for_first)

            # Build attr_names excluding trailing attributes
            attr_names = [a for a in list(first_obj.keys()) if a not in trailing_attrs]

            # collect unique sorted values per attribute across objects in the root, but only for attr_names
            attr_unique: Dict[str, List[str]] = {}
            for attr in attr_names:
                vals = set()
                for obj in objs.values():
                    vals.update(obj.get(attr, []))
                attr_unique[attr] = sorted(vals)

            # Apply forbidden_other placeholders logic
            preferred_placeholders = ["total", "tot", "t", "all"] + other_placeholder
            forbidden_placeholder_map: Dict[str, str] = {}

            for forb in (forbidden_other or []):
                matched_attr = next((a for a in attr_names if a.lower() == forb.lower()), None)
                if matched_attr is None:
                    continue

                values_lower = [str(v).lower() for v in attr_unique.get(matched_attr, [])]
                chosen = next((ph for ph in preferred_placeholders if any(ph.lower() in vl for vl in values_lower)), None)

                if chosen is None:
                    continue

                forbidden_placeholder_map[matched_attr] = chosen
                attr_unique[matched_attr] = [chosen]

            primary_attrs = [a for a in attr_names if a.lower() in forbidden_primary_lc]

            if not primary_attrs:
                fixed_map = {}
                for a, ph in forbidden_placeholder_map.items():
                    if any(a in obj for obj in objs.values()):
                        fixed_map[a] = ph

                # NOTE: build_vars_list_for_fixed_map uses outer-scope `objs` and `attr_names`, which
                # will be those defined here. That's consistent with original code behaviour.
                vars_list = build_vars_list_for_fixed_map(fixed_map)
                filtered = filter_vars_by_db(vars_list)
                if filtered and not (delete_single_var_rows and len(filtered) == 1):
                    rows.append({
                        "chart_id": "",
                        "title": "",
                        "description": "",
                        "db_name": db_name,
                        "vars": "+".join(filtered),
                        "chart_type": chart_type,
                        "category": category,
                        "vector_dim": "",
                    })
            else:
                primary_value_lists = [attr_unique[a] for a in primary_attrs]
                if any(len(lst) == 0 for lst in primary_value_lists):
                    continue

                for prim_values in product(*primary_value_lists):
                    fixed_primary_map = dict(zip(primary_attrs, prim_values))
                    for a, ph in forbidden_placeholder_map.items():
                        if any(a in obj for obj in objs.values()):
                            fixed_primary_map[a] = ph

                    vars_list = build_vars_list_for_fixed_map(fixed_primary_map)
                    filtered = filter_vars_by_db(vars_list)
                    if filtered and not (delete_single_var_rows and len(filtered) == 1):
                        rows.append({
                            "chart_id": "",
                            "title": "",
                            "description": "",
                            "db_name": db_name,
                            "vars": "+".join(filtered),
                            "chart_type": chart_type,
                            "category": category,
                            "vector_dim": "",
                        })

    elif procedure == 4:
        # For each variable (top-level key), detect attributes after 'description'
        # and output a separate row for each trailing attribute
        for key, value in data[db_name].items():
            original_order = list(value.keys())
            trailing = trailing_attrs_for_order(original_order)
            if not trailing:
                continue

            for ta in trailing:
                if ta not in value:
                    continue
                vals = [x.strip() for x in str(value[ta]).split(",") if x.strip()]
                if not vals:
                    continue

                singular_vars = [f"{key}_{v}" for v in vals]

                # filter & normalize
                filtered = filter_vars_by_db(singular_vars)
                if delete_single_var_rows and len(filtered) == 1:
                    continue
                if not filtered:
                    continue

                rows.append({
                    "chart_id": "",
                    "title": "",
                    "description": f"singular vars for trailing attribute '{ta}' of {key}",
                    "db_name": db_name,
                    "vars": "+".join(filtered),
                    "chart_type": chart_type,
                    "category": category,
                    "vector_dim": "",
                })

    else:
        raise ValueError("Procedure not recognized")

    return rows



def update_chart_rows(
    rows_out=None,
    updates=None,
    json_charts="library/charts.json",
    json_texts="library/charts_text.json",
    lang="en",
    full_migration: bool = False,
    send: bool = True,
    vectorization: bool = True,
    vect_out: str = "vector_dim",
    dest_table_chart: str = "charts",
    dest_table_text: str = "charts_text",
    conn_dest: str = "connDest.json",
    overwrite_existing: bool = True,
    ret_data: bool = False,
):
    """
    full_migration = True
        - Uses dataset
        - Writes to charts + charts_text
        - No dependency on rows_out / updates

    full_migration = False
        - Uses rows_out + updates
        - Writes to charts + charts_text
        - Vectorization allowed
    """

    # ---------- Input enforcement ----------
    if full_migration:
        if rows_out is None:
            raise ValueError("full_migration=True requires rows_out")

        rows = rows_out.to_dict(orient="records")

    else:
        if rows_out is None or updates is None:
            raise ValueError("full_migration=False requires rows_out and updates")
        if len(rows_out) != len(updates):
            raise ValueError(
                f"Mismatch: {len(rows_out)} rows but {len(updates)} updates"
            )
        rows = []
        for row, (title, description) in zip(rows_out, updates):
            r = row.copy()
            r["title"] = title
            r["description"] = description
            rows.append(r)

    # ---------- Load JSON ----------
    data = load_json(json_charts)
    data_text = load_json(json_texts)
    text_rows = []

    # ---------- DB setup ----------
    if send:
        dest = SqlDatasource()
        dest.load(conn_dest)
        dest.connect()
        charts_table = dest.gettable(dest_table_chart)
        charts_text_table = dest.gettable(dest_table_text)

        if vectorization:
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer(
                "sentence-transformers/all-MiniLM-L6-v2"
            )

    # ---------- Process rows ----------
    for row in rows:
        title = str(row.get("title", "")).strip()
        description = str(row.get("description", "")).strip()
        category = str(row.get("category", "")).strip()

        if not title:
            continue

        chart_id = title_to_uuid(title)
        row["chart_id"] = chart_id

        # ---- JSON metadata ----
        json_chart = {
            "chart_id": chart_id,
            "db_name": row.get("db_name", ""),
            "category": category,
            "chart_type": row.get("chart_type", ""),
            "vars": row.get("vars", "")
        }

        json_text = {
            "title": title,
            "description": description,
            "category": category
        }

        if chart_id not in data:
            data[chart_id] = json_chart
        elif overwrite_existing:
            data[chart_id].update(json_chart)

        if chart_id not in data_text:
            data_text[chart_id] = json_text
        elif overwrite_existing:
            data_text[chart_id].update(json_text)

        # ---- charts_text rows ----
        text_rows.append({
            "chart_id": chart_id,
            "text_category": "title",
            "lang": lang,
            "text_input": title
        })

        text_rows.append({
            "chart_id": chart_id,
            "text_category": "category",
            "lang": lang,
            "text_input": category
        })

        if description:
            text_rows.append({
                "chart_id": chart_id,
                "text_category": "description",
                "lang": lang,
                "text_input": description
            })

        # ---- charts table ----
        if send:
            db_row = row.copy()

            if vectorization:
                vect_input = f"{title}: {description}"
                embs = model.encode(
                    vect_input,
                    convert_to_numpy=True,
                    batch_size=64,
                    normalize_embeddings=True
                )
                db_row[vect_out] = "[" + ",".join(
                    f"{float(x):.10f}" for x in embs
                ) + "]"

            charts_table.insertone(db_row)

    # ---------- Commit DB ----------
    if send:
        charts_table.commit()

        if text_rows:
            df_text = pd.DataFrame(
                text_rows,
                columns=["chart_id", "text_category", "lang", "text_input"]
            )
            charts_text_table.insertmany(df_text)
            charts_text_table.commit()

        dest.disconnect()

    # ---------- Write JSON ----------
    with open(json_charts, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    with open(json_texts, "w", encoding="utf-8") as f:
        json.dump(data_text, f, indent=4, ensure_ascii=False)

    if ret_data:
        return data


def update_db_from_json(
    json_charts="library/charts.json",
    json_texts="library/charts_text.json",
    update_charts=True,
    update_texts=True,
    vectorization=True,
    vect_out="vector_dim",
    dest_table_chart="charts",
    dest_table_text="charts_text",
    conn_dest="connDest.json",
):
    """
    Update DB using charts.json and charts_text.json.

    Parameters
    ----------
    update_charts : bool
        If True, updates charts table and computes vectors
    update_texts : bool
        If True, updates charts_text table
    """

    if not update_charts and not update_texts:
        raise ValueError("Nothing to update: both update_charts and update_texts are False")
    
    if update_texts and len(json_texts.split(".")[0].split("_")) >= 3:
        lang = json_texts.split(".")[0].split("_")[-1]
    else:
        lang = "en"

    # ---------- Load JSON ----------
    charts_data = load_json(json_charts)
    texts_data = load_json(json_texts)

    # ---------- DB setup ----------
    dest = SqlDatasource()
    dest.load(conn_dest)
    dest.connect()

    charts_table = dest.gettable(dest_table_chart) if update_charts else None
    charts_text_table = dest.gettable(dest_table_text) if update_texts else None

    # ---------- Vector model ----------
    if update_charts and vectorization:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

    chart_rows = []
    text_rows = []

    # ---------- Iterate by chart_id ----------
    chart_ids = set(charts_data.keys()) | set(texts_data.keys())

    for chart_id in chart_ids:
        chart_meta = charts_data.get(chart_id, {})
        text_meta = texts_data.get(chart_id, {})

        title = str(text_meta.get("title", "")).strip()
        description = str(text_meta.get("description", "")).strip()
        category = str(text_meta.get("category", "")).strip()

        # ---------- charts table ----------
        if update_charts and chart_meta:
            row = {
                "chart_id": chart_id,
                "db_name": chart_meta.get("db_name", ""),
                "category": chart_meta.get("category", ""),
                "chart_type": chart_meta.get("chart_type", ""),
                "vars": chart_meta.get("vars", ""),
            }

            if vectorization:
                vect_input = f"{title}: {description}".strip()
                if vect_input:
                    emb = model.encode(
                        vect_input,
                        convert_to_numpy=True,
                        normalize_embeddings=True
                    )
                    row[vect_out] = "[" + ",".join(f"{float(x):.10f}" for x in emb) + "]"

            chart_rows.append(row)

        # ---------- charts_text table ----------
        if update_texts and title:
            text_rows.append({
                "chart_id": chart_id,
                "text_category": "title",
                "lang": lang,
                "text_input": title,
            })

            text_rows.append({
                "chart_id": chart_id,
                "text_category": "category",
                "lang": lang,
                "text_input": category
            })

            if description:
                text_rows.append({
                    "chart_id": chart_id,
                    "text_category": "description",
                    "lang": lang,
                    "text_input": description,
                })

    # ---------- DB writes ----------
    if update_charts and chart_rows:
        df_charts = pd.DataFrame(chart_rows)
        charts_table.insertmany(df_charts)
        charts_table.commit()

    if update_texts and text_rows:
        df_texts = pd.DataFrame(text_rows)
        charts_text_table.insertmany(df_texts)
        charts_text_table.commit()

    dest.disconnect()


def update_mobile_from_json(
    json_app="library/mobile_app.json",
    dest_table_app="translations",
    conn_dest="connDest.json",
):
    """
    Update DB using mobile_app.json for each language needed
    """
    
    if len(json_app.split(".")[0].split("_")) >= 3:
        lang = json_app.split(".")[0].split("_")[-1]
    else:
        lang = "en"

    # ---------- Load JSON ----------
    app_data = load_json(json_app)

    # ---------- DB setup ----------
    dest = SqlDatasource()
    dest.load(conn_dest)
    dest.connect()

    deletion = f"""DELETE FROM public.{dest_table_app} WHERE "lang" ='{lang}'"""
    dest.execute(deletion).commit()
    app_table = dest.gettable(dest_table_app)
    row = {"lang": lang, "payload": json.dumps(app_data)}

    app_table.insertone(row)
    app_table.commit()
    dest.disconnect()


def update_questions_and_choices(
    questions: list[dict],
    choices: list[dict],
    json_questions="library/questions.json",
    json_choices="library/choices.json",
    conn_dest="connDest.json",
    overwrite_existing: bool = True,
    send: bool = True,
    ret_data: bool = False,
):
    """
    Update questions and choices in JSON + database.
    Automatically assigns IDs to questions and ensures choices use the correct question_id.
    """

    # ---------- Load JSON ----------
    if os.path.exists(json_questions):
        with open(json_questions, "r", encoding="utf-8") as f:
            json_q = json.load(f)
    else:
        json_q = {}

    if os.path.exists(json_choices):
        with open(json_choices, "r", encoding="utf-8") as f:
            json_a = json.load(f)
    else:
        json_a = {}

    # ---------- DB setup ----------
    if send:
        dest = SqlDatasource()
        dest.load(conn_dest)
        dest.connect()

        q_table = dest.gettable("questions")
        a_table = dest.gettable("choices")

        # Fetch the current max ID in questions table
        res = q_table.datasource.execute("SELECT MAX(id) as max_id FROM questions").fetchone()
        max_qid = res["max_id"] if res and res["max_id"] is not None else 0
    else:
        max_qid = max([int(k) for k in json_q.keys()], default=0)

    # ---------- QUESTIONS ----------
    qid_map = {}  # map question object -> assigned DB id

    for q in questions:
        qid = q.get("id")
        if qid is None:
            max_qid += 1
            qid = max_qid
            q["id"] = qid

        qid_map[id(q)] = qid
        key = str(qid)

        # Update JSON
        if key not in json_q or overwrite_existing:
            json_q[key] = q.copy()

        # Insert into DB
        if send:
            q_table.insertone(q)

    # ---------- CHOICES ----------
    for a in choices:
        # Assign question_id if missing
        if "question_id" not in a or a["question_id"] is None:
            if len(questions) == 1:
                a["question_id"] = qid_map[id(questions[0])]
            else:
                raise ValueError(
                    "Choice missing 'question_id' and cannot auto-assign when multiple questions provided"
                )

        aid = a.get("id")
        if aid is None:
            aid = max([int(k) for k in json_a.keys()], default=0) + 1
            a["id"] = aid

        key = str(aid)

        # Update JSON
        if key not in json_a or overwrite_existing:
            json_a[key] = a.copy()

        # Insert into DB
        if send:
            a_table.insertone(a)

    # ---------- Commit DB ----------
    if send:
        q_table.commit()
        a_table.commit()
        dest.disconnect()

    # ---------- Write JSON ----------
    with open(json_questions, "w", encoding="utf-8") as f:
        json.dump(json_q, f, indent=4, ensure_ascii=False)

    with open(json_choices, "w", encoding="utf-8") as f:
        json.dump(json_a, f, indent=4, ensure_ascii=False)

    if ret_data:
        return json_q, json_a
