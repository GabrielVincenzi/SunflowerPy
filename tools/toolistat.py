import pandas as pd
import requests
import xml.etree.ElementTree as ET
from io import StringIO

from tools.tooldb import parse_time_column

API_BASE = "https://esploradati.istat.it/SDMXWS/rest"

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


def get_available_values(id:str):
    """Return a dictionary with available values for each dimension in the DataSet instance"""
    url = f"{API_BASE}/availableconstraint/{id}/?references=all&detail=full"

    response = requests.get(url)
    response.raise_for_status()
    if response.text == 'No available data found for the requested query':
        raise ValueError(f'No available data found for the requested query (dataset {id})')
    
    tree = ET.iterparse(StringIO(response.text))

    for _, el in tree:
        _, _, el.tag = el.tag.rpartition('}')

    root = tree.root

    dimensions_values = {}
    for dimension in root.iter("Codelist"):
        dimension_id = dimension.get("id")

        values = {}
        value_id_l, value_descr_l = [], []

        for value in dimension.iter("Code"):
            value_id = value.get("id")
            value_descr = [name.text for name in value.findall("Name")][1]
            value_id_l.append(value_id)
            value_descr_l.append(value_descr)

        values["values_ids"] = value_id_l
        values["values_description"] = value_descr_l
        dimensions_values[dimension_id] = values

    #for dimension_id in list(dimensions_values.keys()):
    #    dimension = self.get_dimension_name(dimension_id)
    #    dimensions_values[dimension] = dimensions_values.pop(dimension_id)

    return dimensions_values

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