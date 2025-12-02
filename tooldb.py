import pandas as pd
import numpy as np
import json
import os
import re
from typing import Union, List, Optional, Dict

def clean_stat(
    df: pd.DataFrame,
    keys: Optional[Union[str, List[str]]] = None,
    columns_to_pivot: Union[str, List[str]] = None,
    obs_value: str = None,
    prefix: str =None,
    suffix: str =None
) -> pd.DataFrame:
    """
    Clean and pivot the dataframe.

    Parameters:
    - df: input DataFrame
    - keys: columns to set as index for pivot; default ['geo', 'TIME_PERIOD']
    - columns_to_pivot: column(s) to pivot on
    - obs_value: column where observations reside
    - prefix: to insert into pivot-created column names

    Returns:
    - Cleaned and pivoted DataFrame with lowercase columns.
    """
    if keys is None:
        keys = ['geo', 'TIME_PERIOD']

    if obs_value is None:
        obs_value = 'OBS_VALUE'

    # normalize types
    if isinstance(keys, str):
        keys = [keys]
    if isinstance(columns_to_pivot, str):
        columns_to_pivot = [columns_to_pivot]

    # drop freq if present
    if 'freq' in df.columns:
        df = df.drop(columns=['freq'])

    # pivot
    df = df.pivot(index=keys, columns=columns_to_pivot, values=obs_value)

    # flatten multiindex columns if necessary (e.g. ('y15_24','f') -> 'y15_24_f')
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = ['_'.join(map(str, col)).strip() for col in df.columns.values]

    # reset index so keys become columns
    df = df.reset_index()

    # add prefix to pivot-created columns (i.e., columns after the key columns)
    cols = list(df.columns)
    n_keys = len(keys)
    # if the actual df has fewer columns than keys for any reason, handle safely
    n_keys = min(n_keys, len(cols))
    pivot_cols = cols[n_keys:]

    if prefix and not suffix:
        if not prefix.endswith('-'):
            pref = prefix if prefix.endswith('_') else f"{prefix}_"
        else:
            pref = prefix
        df = df.rename(columns={col: f"{pref}{col}" for col in pivot_cols if not col.startswith(pref)})

    if suffix and not prefix:
        suff = suffix if suffix.startswith('_') else f"_{suffix}"
        df = df.rename(columns={col: f"{col}{suff}" for col in pivot_cols})

    if suffix and prefix:
        if not prefix.endswith('-'):
            pref = prefix if prefix.endswith('_') else f"{prefix}_"
        else:
            pref = prefix
        suff = suffix if suffix.startswith('_') else f"_{suffix}"
        df = df.rename(columns={col: f"{pref}{col}{suff}" for col in pivot_cols})


    # drop rows if all values are NaN
    df = df.dropna(how='all')

    # replace NaN float with None (keeping your original behavior)
    df = df.replace({float('nan'): None})

    # final normalization: lowercase and replace hyphens with underscores
    df.columns = df.columns.str.lower()

    return df


def parse_time_column(df, time_col='TIME_PERIOD', freq_col='FREQ'):
    s = df[time_col].astype(str).str.strip()
    freq = str(df[freq_col].iloc[0]).upper() if freq_col in df.columns else None

    if freq == 'A':  # annual, strings like "2020" or "2020 " 
        # take the first 4 chars (year) and parse
        df[time_col] = pd.to_datetime(s.str[:4], format='%Y', errors='coerce')

    elif freq == 'M':  # monthly, strings like "2020-03" or "2020-03-01"
        # try direct parse (handles YYYY-MM or YYYY-MM-DD)
        df[time_col] = pd.to_datetime(s, errors='coerce')

    elif freq == 'Q':  # quarterly, many possible formats: "2020-Q1", "2020Q1", "2020 Q1"
        # normalize to e.g. "2020Q1"
        q = (s
             .str.replace(r'[-\s]', '', regex=True)   # remove spaces and dashes
             .str.replace(r'([0-9]{4})[qQ]([1-4])$', r'\1Q\2', regex=True)  # ensure YYYYQn
             )

        # Some providers use "2020-Q1" -> we already removed dash -> "2020Q1"
        # Use PeriodIndex to convert quarter -> timestamp (default is start of period)
        try:
            df[time_col] = pd.PeriodIndex(q, freq='Q').to_timestamp()
        except Exception:
            # fallback: try to extract year and quarter numerically
            def q_to_ts(x):
                m = re.match(r'^(?P<y>\d{4})[Qq](?P<q>[1-4])$', x or '')
                if not m:
                    return pd.NaT
                y, qn = int(m.group('y')), int(m.group('q'))
                # map quarter to month (start-of-quarter)
                month = {1:1, 2:4, 3:7, 4:10}[qn]
                return pd.Timestamp(year=y, month=month, day=1)
            df[time_col] = q.apply(q_to_ts)

    elif freq == 'D':  # daily (ISO or other)
        df[time_col] = pd.to_datetime(s, errors='coerce')

    else:
        # fallback: try to parse flexibly
        df[time_col] = pd.to_datetime(s, errors='coerce')

    return df


def update_db(db_name, available_geos, available_periods, db_source):
    columns = ["id","db_name", "available_geos", "available_periods", "db_source"]
    file_path = "dbs/dbsData.csv"
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path)
            if df.empty and len(df.columns) == 0:
                df = pd.DataFrame(columns=columns)
                df.to_csv(file_path, index=False)
        except pd.errors.EmptyDataError:
            df = pd.DataFrame(columns=columns)
            df.to_csv(file_path, index=False)
    else:
        df = pd.DataFrame(columns=columns)
        df.to_csv(file_path, index=False)

    if df.empty:
        next_id = 1
    else:
        next_id = df["id"].max() + 1

    # ------- New row to insert
    new_row = {
        "id": next_id,
        "db_name": db_name,
        "available_geos": available_geos,
        "available_periods": available_periods,
        "db_source": db_source,
    }

    if db_name in df["db_name"].values:
        df = df[df["db_name"] != db_name]
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    else:
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    df.to_csv(file_path, index=False)


def last_observed_per_group(g, keys=None, sort_col:str='time_period'):
    if not keys:
        keys = ['geo', 'time_period']
    indicator_cols = [c for c in g.columns if c not in keys]
    g = g.sort_values(sort_col)
    return g[indicator_cols].apply(lambda s: s.dropna().iloc[-1] if s.dropna().size else np.nan)


def _to_string(seq):
    if seq is None:
        return ""
    seen = set()
    out = []
    for v in seq:
        s = str(v).strip()
        if s == "":
            continue
        if s not in seen:
            seen.add(s)
            out.append(s)
    return ",".join(out)

def _string_to_set(s: str):
    """Convert comma-separated string to a set of trimmed non-empty tokens."""
    if not s:
        return set()
    return {tok.strip() for tok in str(s).split(",") if tok.strip() != ""}

def update_json(df: pd.DataFrame, db_name: str, pattern: List[str], descriptions: Dict[str, str], filename: str = "output.json"):
    """
    Merge metadata extracted from df into filename under db_name.

    - pattern: list like ['name','sex','age','educ'] (first element is variable name)
    - descriptions: dict mapping variable name to description
    - filename: path to JSON file (default 'output.json')
    """
    groups: Dict[str, Dict[str, object]] = {}
    cols = [col for col in df.columns if col not in {'geo', 'time_period'}]

    # Build groups from df columns
    for col in cols:
        tokens = col.split('_')
        if len(tokens) == 0:
            continue
        name = tokens[0]

        # number of fields present in this column (excluding name)
        n_fields = len(tokens) - 1
        expected_fields = pattern[1: 1 + n_fields]  # slice to match tokens length

        # Ensure groups[name] exists and has sets for each field
        if name not in groups:
            groups[name] = {fld: set() for fld in expected_fields}
            # set description from provided descriptions if available
            groups[name]['description'] = descriptions.get(name, "")

        # If this column has more tokens than previously seen for this name,
        # ensure we add any missing field sets (so we don't lose longer columns)
        existing_fields = [k for k in groups[name].keys() if k != 'description']
        if len(expected_fields) > len(existing_fields):
            for fld in expected_fields[len(existing_fields):]:
                groups[name].setdefault(fld, set())

        # Add tokens to corresponding field set
        for i, fld in enumerate(expected_fields):
            token_value = tokens[i + 1] if i + 1 < len(tokens) else ""
            if token_value != "":
                groups[name][fld].add(token_value)

    # Convert sets to comma-separated strings for groups
    for name in list(groups.keys()):
        for patt in list(groups[name].keys()):
            if patt == 'description':
                # keep description string as-is
                continue
            groups[name][patt] = _to_string(groups[name][patt])

    # Load existing JSON (if any)
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {}
    else:
        data = {}

    # Prepare db entry (existing or new)
    existing_db = data.get(db_name, {})

    # Merge groups into existing_db
    for var_name, var_meta in groups.items():
        if var_name not in existing_db:
            # new variable -> add whole meta
            existing_db[var_name] = var_meta.copy()
        else:
            # variable exists -> merge fields
            existing_meta = existing_db[var_name]
            # Merge description: keep existing if present, otherwise use new
            if not existing_meta.get('description'):
                existing_meta['description'] = var_meta.get('description', "")
            # For each field in var_meta (except description), merge sets
            for field, new_val in var_meta.items():
                if field == 'description':
                    continue
                existing_val = existing_meta.get(field, "")
                merged_set = _string_to_set(existing_val) | _string_to_set(new_val)
                existing_meta[field] = _to_string(sorted(merged_set))  # sorted for deterministic order

            existing_db[var_name] = existing_meta

    # Put merged db back into data and write file
    data[db_name] = existing_db
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)