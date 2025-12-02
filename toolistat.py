import pandas as pd
import requests
import xml.etree.ElementTree as ET
from io import StringIO

from tooldb import parse_time_column

API_BASE = "https://esploradati.istat.it/SDMXWS/rest"
NS = 'http://www.sdmx.org/resources/sdmxml/schemas/v2_1/structure'

def load_istat_catalogue(provider: str = "IT1") -> dict:
    """
    Returns a dictionary of dataflow ID → (name, version)
    """
    url = f"{API_BASE}/dataflow/{provider}?format=sdmx-2.1-structure"
    response = requests.get(url)
    response.raise_for_status()
    
    tree = ET.fromstring(response.content)
    ns = {'str': NS}
    
    dataflows = {}
    for df in tree.findall('.//str:Dataflow', ns):
        flow_id = df.attrib['id']
        version = df.attrib.get('version', '1.0')
        name_el = df.find('.//str:Name', ns)
        name = name_el.text if name_el is not None else flow_id
        dataflows[flow_id] = (name, version)
    return dataflows


def get_istat_dataset(dataset_code: str, filters: str = "", start_year: str = None, end_year: str = None, provider: str = "IT1", version:str=None) -> pd.DataFrame:
    '''
    Fetches and returns a Istat dataset from the official API in CSV format as a pandas.DataFrame, applying optional filters and time range.

    Args:
        dataset_code (str): The Eurostat dataset identifier.
        filters (str, optional): Additional filtering in SDMX key format. Defaults to empty string.
        start_year (str, optional): Minimum year of data to retrieve.
        end_year (str, optional): Maximum year of data to retrieve.

    Returns:
        pd.DataFrame: The filtered dataset, with unnecessary metadata columns removed. Returns an empty DataFrame on failure.
    '''
    if filters and not filters.startswith("/"):
        filters = f"/{filters}"

    if version is None:
        version = "1.0"

    base_url = f"{API_BASE}/data/{provider},{dataset_code},{version}{filters}"
    
    params = {
        "format": "csv",
    }

    if start_year:
        params["startPeriod"] = start_year
    if end_year:
        params["endPeriod"] = end_year

    try:
        response = requests.get(base_url, params=params, timeout=30)
        response.raise_for_status()
        df = pd.read_csv(StringIO(response.text), low_memory=False)

        drop_cols = {col for col in df.columns if "NOTE" in col} | {"OBS_STATUS", "DATAFLOW", "BASE_PER", "UNIT_MEAS", "UNIT_MULT"}
        df.drop(columns=drop_cols.intersection(df.columns), inplace=True)

        if 'OBS_VALUE' in df.columns:
            df['OBS_VALUE'] = df['OBS_VALUE'].astype('float64')

        if 'FREQ' in df.columns and 'TIME_PERIOD' in df.columns:
            df = parse_time_column(df, time_col='TIME_PERIOD', freq_col='FREQ')

        return df

    except requests.RequestException as e:
        print(f"Request error: {e}")
        return pd.DataFrame()
    except pd.errors.ParserError as e:
        print(f"CSV parsing error: {e}")
        return pd.DataFrame()


def get_istat_unique_codelist(codelist_id: str, lang: str = "en", provider: str = "IT1") -> dict[str, str]:
    """
    Fetch an ISTAT SDMX-ML codelist and return its code->label map.

    Args:
        codelist_id: Full SDMX codelist ID (e.g., "CL_115_333_GEOLIV1").
        lang: Preferred label language (ISO code).

    Returns:
        Dict mapping code to label.
    """
    url = f"{API_BASE}/codelist/{provider}/{codelist_id}"
    resp = requests.get(url)
    resp.raise_for_status()

    root = ET.fromstring(resp.content)
    ns = {
        'str': NS,
        'com': 'http://www.sdmx.org/resources/sdmxml/schemas/v2_1/common'
    }

    result = {}
    for code in root.findall('.//str:Code', ns):
        cid = code.get('id')
        names = code.findall('com:Name', ns)
        label = next(
            (n.text for n in names if n.attrib.get('{http://www.w3.org/XML/1998/namespace}lang') == lang),
            names[0].text if names else ''
        )
        if cid:
            result[cid] = label

    return result


def get_istat_codelist(df: pd.DataFrame, dataset_code: str, version: str = "1.0", lang: str = "en") -> dict[str, dict[str, str]]:
    """
    Given an ISTAT DataFrame, fetch only the code->label mappings for dimensions present in the data.

    Args:
        df: pandas DataFrame returned from ISTAT.
        dataset_code: Dataset ID (e.g., "115_333").
        version: Dataset version (e.g., "1.2").
        lang: Preferred label language (ISO code).

    Returns:
        Dict: {dimension: {code: label}}
    """
    url = f"{API_BASE}/datastructure/IT1/{dataset_code}/{version}"
    resp = requests.get(url)
    resp.raise_for_status()

    root = ET.fromstring(resp.content)
    ns = {'str': NS}

    result = {}
    used_columns = set(df.columns)

    for dim in root.findall('.//str:Dimension', ns):
        dim_id = dim.attrib['id']
        if dim_id not in used_columns:
            continue
        cl_ref = dim.attrib.get('codelist')
        if not cl_ref:
            continue
        full_map = get_istat_unique_codelist(cl_ref, lang=lang)
        codes = df[dim_id].dropna().astype(str).unique().tolist()
        result[dim_id] = {code: full_map.get(code, '') for code in codes if code in full_map}

    return result

