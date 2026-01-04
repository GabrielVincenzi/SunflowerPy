import pandas as pd
import requests
import csv
import xml.etree.ElementTree as ET
from io import StringIO
from functools import reduce
from tools.tooldb import parse_time_column, update_json, clean_stat
from typing import List, Dict

DECIMAL_POSITIONS = 2
API_BASE = "https://ec.europa.eu/eurostat/api/dissemination"
SDMX = "sdmx/2.1"
NS = {
    'str': 'http://www.sdmx.org/resources/sdmxml/schemas/v2_1/structure',
    'com': 'http://www.sdmx.org/resources/sdmxml/schemas/v2_1/common'
}

def load_eurostat_catalogue():
    '''
    Downloads and parses the Eurostat catalogue of available databases.

    This function sends an HTTP GET request to the Eurostat API endpoint for the full catalogue
    in XML format. If the request is successful, it parses the XML response and returns the root
    element of the parsed XML tree. If the request fails, it prints an error message and returns
    an empty list.

    Returns:
        xml.etree.ElementTree.Element or list: The root element of the parsed XML catalogue if
        successful; otherwise, an empty list.
    '''
    url = f"{API_BASE}/catalogue/toc/xml"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error in the request: {response.status_code}")
        return []

    root = ET.fromstring(response.content)
    return root


def search_eurostat_toc(keyword: str, catalogue: str, lang="en", limit=10):
    '''
    Searches the Eurostat Table of Contents (TOC) XML tree for entries matching a given keyword.

    This function recursively traverses the hierarchical structure of a Eurostat catalogue (in XML format),
    looking for leaf nodes whose title contains the specified keyword (case-insensitive). It collects the
    results up to the specified limit, including the title, code, and hierarchical path for each match.
    The search can be performed in different languages by setting the 'lang' parameter.

    Args:
        keyword (str): The search term to look for in the titles of TOC entries.
        catalogue (str): The root XML node of the Eurostat catalogue to search.
        lang (str, optional): The language code for the titles to search (default is "en").
        limit (int, optional): The maximum number of results to return (default is 10).

    Returns:
        list of dict: A list of dictionaries, each containing the 'Title', 'Code', and 'Path' for a matching entry.
    '''
    ns = {"nt": "urn:eu.europa.ec.eurostat.navtree"}
    results = []

    def recursive_search(node, path):
        nonlocal results
        for child in node:
            if child.tag == f"{{{ns['nt']}}}branch":
                title_elem = child.find(f"nt:title[@language='{lang}']", ns)
                title = title_elem.text if title_elem is not None else ""
                code_elem = child.find("nt:code", ns)
                code = code_elem.text if code_elem is not None else ""
                new_path = path + [f"{code} ({title})"]
                children = child.find("nt:children", ns)
                if children is not None:
                    if recursive_search(children, new_path):
                        return True

            elif child.tag == f"{{{ns['nt']}}}leaf":
                title_elem = child.find(f"nt:title[@language='{lang}']", ns)
                if title_elem is not None and keyword.lower() in title_elem.text.lower():
                    code_elem = child.find("nt:code", ns)
                    code = code_elem.text if code_elem is not None else ""
                    results.append({
                        "Title": title_elem.text,
                        "Code": code,
                        "Path": " > ".join(path)
                    })
                    if len(results) >= limit:
                        return True

        return False

    recursive_search(catalogue, [])
    for r in results:
        print(f"{r['Code']}: {r['Title']} (Path: {r['Path']})")

    return results


def get_eurostat_dataset(dataset_code: str, filters: str = "", start_year: str = None, end_year: str = None, codelist: bool = False) -> pd.DataFrame:
    '''
    Fetches and returns a Eurostat dataset from the official API in CSV format as a pandas.DataFrame, applying optional filters and time range.

    Args:
        dataset_code (str): The Eurostat dataset identifier.
        filters (str, optional): Additional filtering in SDMX key format. Defaults to empty string.
        start_year (str, optional): Minimum year of data to retrieve.
        end_year (str, optional): Maximum year of data to retrieve.
        codelist (bool): Codelist with code and definition for each code.

    Returns:
        pd.DataFrame: The filtered dataset, with unnecessary metadata columns removed. Returns an empty DataFrame on failure.
        codelist (optional): A dictionary for each column with code: description pair.
    '''
    if filters and not filters.startswith("/"):
        filters = f"/{filters}"

    base_url = f"{API_BASE}/{SDMX}/data/{dataset_code}{filters}"
    
    params = {
        "format": "SDMX-CSV",
    }

    if start_year:
        params["startPeriod"] = start_year
    if end_year:
        params["endPeriod"] = end_year

    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        df = pd.read_csv(StringIO(response.text), low_memory=False)

        drop_cols = {'OBS_FLAG', 'CONF_STATUS', 'DATAFLOW', 'LAST UPDATE'}
        df.drop(columns=drop_cols.intersection(df.columns), inplace=True)

        if 'OBSl_VALUE' in df.columns:
            df['OBS_VALUE'] = df['OBS_VALUE'].astype('float64')

        if 'freq' in df.columns and 'TIME_PERIOD' in df.columns:
            df = parse_time_column(df)
        
        if codelist:
            codelist_df = get_eurostat_codelist(df)
            return df, codelist_df
        else:
            return df

    except requests.RequestException as e:
        print(f"Request error: {e}")
        return pd.DataFrame()
    except pd.errors.ParserError as e:
        print(f"CSV parsing error: {e}")
        return pd.DataFrame()
    

def get_eurostat_codelist_dict(dimension_code: str, lang="en"):
    """
    Fetches the Eurostat SDMX codelist for a given dimension
    and returns a dict mapping code -> description.

    Args:
        dimension_code (str): e.g. "unit", "coicop", "geo", "freq"
        lang (str): 2-letter language code ("en" by default)

    Returns:
        Dict[str, str]: mapping from code to label/description
    """
    base_url = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/codelist/ESTAT"
    # The codelist resource is the dimension in uppercase
    resource = dimension_code.upper()

    params = {
        "format": "TSV",
        "lang": lang
    }

    url = f"{base_url}/{resource}/latest"
    resp = requests.get(url, params=params)
    resp.raise_for_status()

    text = resp.text

    # TSV is tab separated: code and label are usually the first two columns
    reader = csv.reader(StringIO(text), delimiter="\t")

    # Typically the first row is header; detect and skip it
    mapping = {}
    for row in reader:
        # Skip header or empty lines
        if not row or row[0].lower() == "code" or row[0].strip() == "":
            continue
        code = row[0]
        label = row[1] if len(row) > 1 else ""
        mapping[code] = label

    return mapping


def get_eurostat_codelist(df, exclude=("geo", "time_period", "OBS_VALUE"), lang="en"):
    """
    Given a Eurostat pandas DataFrame, return a dictionary:
    {
        column_name: { code: description }
    }
    for all Eurostat dimensions in the dataset.

    Args:
        df (pd.DataFrame): Eurostat dataset
        exclude (tuple): columns to ignore
        lang (str): language for labels

    Returns:
        dict
    """
    codelists = {}

    for col in df.columns:
        if col in exclude:
            continue

        try:
            codelist = get_eurostat_codelist_dict(col, lang=lang)

            # Optional: keep only codes actually present in the dataset
            used_codes = set(df[col].dropna().unique())
            codelist = {k: v for k, v in codelist.items() if k in used_codes}

            codelists[col] = codelist

        except Exception as e:
            # Some columns may not have a codelist (or API name mismatch)
            print(f"Skipping '{col}': {e}")

    return codelists


def serial_db(db_info:Dict, description:Dict, keys:List[str], db_name:str, merge_how:str="outer", output_dfs:bool=False):
    dfs = {}
    dbs_list = [db for db in db_info.keys()]

    for db in dbs_list:
        filters, measure_columns, prefix, suffix, pattern = db_info.get(db)
        measure_columns = measure_columns if isinstance(measure_columns, (list, tuple)) else [measure_columns]
        df = get_eurostat_dataset(
            dataset_code=db,
            filters=filters
        )
        for col in measure_columns:
            df[col] = df[col].str.replace('_', '-')
        df = clean_stat(df, keys=keys, columns_to_pivot=measure_columns, prefix=f'{prefix}', suffix=f'{suffix}')

        dfs[db] = df

        update_json(df, db_name, pattern, description)

    final_df = reduce(lambda left, right: pd.merge(left, right, on=[k.lower() for k in keys], how=merge_how), dfs.values())
    final_df = final_df.dropna(axis=1, how='all')

    if output_dfs:
        return final_df, dfs
    else:
        return final_df