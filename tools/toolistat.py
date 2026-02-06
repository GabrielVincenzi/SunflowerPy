import pandas as pd
import requests
import xml.etree.ElementTree as ET
from io import StringIO

from tools.tooldb import parse_time_column

API_BASE = "https://esploradati.istat.it/SDMXWS/rest"
XML_LANG = "{http://www.w3.org/XML/1998/namespace}lang"

def load_istat_catalogue(provider: str = "IT1") -> dict:
    """
    Returns a dictionary of dataflow ID → (name, version)
    """
    url = f"{API_BASE}/dataflow/{provider}"
    response = requests.get(url)
    response.raise_for_status()
    
    tree = ET.iterparse(StringIO(response.text))

    for _, el in tree:
        _, _, el.tag = el.tag.rpartition('}')

    root = tree.root

    dataflows = []
    for dataflow in root.iter("Dataflow"):
        id = dataflow.get("id")
        version = dataflow.get("version")
        structure_id = [ref.get("id") for ref in dataflow.iter("Ref")][0]

        # iter over names and get the descriptions
        for name in dataflow.findall("Name"):
            lang = name.get("{http://www.w3.org/XML/1998/namespace}lang")
            if lang == "en":
                description_en = name.text
            # if lang == 'it':
            # description_it = name.text

        dataflow_dict = {
            "df_id": id,
            "version": version,
            "df_description": description_en,
            # "description_it": description_it,
            "df_structure_id": structure_id,
        }

        dataflows.append(dataflow_dict)

    dataflows = pd.DataFrame(dataflows)
    
    return dataflows


def _strip_ns_root(xml_text):
    it = ET.iterparse(StringIO(xml_text))
    for _, el in it:
        if "}" in el.tag:
            el.tag = el.tag.rpartition("}")[2]
    return it.root


def get_dimension_values(
    dataflow_id: str,
    dimension: str,
    lang: str = "it",
    dataframe: bool = True,
    agency_id: str = "IT1",
):
    """
    Standalone ISTAT-safe function.
    Given a dataflow id and a dimension id, return the dimension values with labels.
    """

    # Dataflow → Datastructure
    r = requests.get(f"{API_BASE}/dataflow/{agency_id}/{dataflow_id}")
    r.raise_for_status()
    root = _strip_ns_root(r.text)

    ref = root.find(".//Structure/Ref")
    if ref is None:
        raise ValueError("Datastructure reference not found")

    dsd_id = ref.get("id")
    dsd_version = ref.get("version")
    dsd_agency = ref.get("agencyID") or agency_id

    # Datastructure
    dsd_url = f"{API_BASE}/datastructure/{dsd_agency}/{dsd_id}"
    if dsd_version:
        dsd_url += f"/{dsd_version}"

    r = requests.get(dsd_url)
    r.raise_for_status()
    root = _strip_ns_root(r.text)

    # Find dimension → Codelist Ref (IMPORTANT FIX)
    dim = root.find(f".//Dimension[@id='{dimension}']")
    if dim is None:
        raise ValueError(f"Dimension '{dimension}' not found")

    cl_ref = None
    for ref in dim.iter("Ref"):
        if ref.get("class") == "Codelist":
            cl_ref = ref
            break

    if cl_ref is None:
        raise ValueError("Codelist reference not found")

    cl_id = cl_ref.get("id")
    cl_version = cl_ref.get("version")
    cl_agency = cl_ref.get("agencyID") or dsd_agency

    # Codelist
    cl_url = f"{API_BASE}/codelist/{cl_agency}/{cl_id}"
    if cl_version:
        cl_url += f"/{cl_version}"

    r = requests.get(cl_url)
    r.raise_for_status()
    root = _strip_ns_root(r.text)

    rows = []
    for code in root.iter("Code"):
        label = None
        for name in code.findall("Name"):
            if name.get(XML_LANG) == lang:
                label = name.text
                break
        if label is None:
            label = code.findtext("Name")

        rows.append({"code": code.get("id"), "label": label})

    if dataframe:
        return pd.DataFrame(rows)
    return {r["code"]: r["label"] for r in rows}


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