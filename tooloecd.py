import pandas as pd
import requests
import xml.etree.ElementTree as ET
from io import StringIO
import json

API_BASE = "https://sdmx.oecd.org/public/rest"

def load_oecd_catalogue():
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
    url = f"{API_BASE}/dataflow/all"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error in the request: {response.status_code}")
        return []

    root = ET.fromstring(response.content)
    return root

def get_oecd_dataset(dataset_id: str, filters: str = "", start_year: str = None, end_year: str = None, reading=False) -> pd.DataFrame:
    '''
    Fetches and returns a OECD dataset from the official API in CSV format as a pandas.DataFrame, applying optional filters and time range.

    Args:
        dataset_code (str): The Eurostat dataset identifier.
        filters (str, optional): Additional filtering in SDMX key format. Defaults to empty string. First filter is the FREQ.
        start_year (str, optional): Minimum year of data to retrieve.
        end_year (str, optional): Maximum year of data to retrieve.

    Returns:
        pd.DataFrame: The filtered dataset, with unnecessary metadata columns removed. Returns an empty DataFrame on failure.
    '''
    if filters and not filters.startswith("/"):
        filters = f"/{filters}"

    base_url = f"{API_BASE}/data/{dataset_id}{filters}"
    
    params = {
        "format": "csvfilewithlabels",
        "dimensionAtObservation": "AllDimensions",
        "detail": "DataOnly"
    }

    if start_year:
        params["startPeriod"] = start_year
    if end_year:
        params["endPeriod"] = end_year

    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        df = pd.read_csv(StringIO(response.text), low_memory=False)

        drop_cols = {'STRUCTURE', 'STRUCTURE_ID', 'STRUCTURE_NAME', 'ACTION', 'ADJUSTMENT', 
                     'TRANSFORMATION', 'TIME_HORIZ', 'METHODOLOGY'}
        df.drop(columns=drop_cols.intersection(df.columns), inplace=True)

        if not reading:
            filtered_cols = [col for col in df.columns if not col[-1].islower()]
            df = df[filtered_cols]

        if 'OBSl_VALUE' in df.columns:
            df['OBS_VALUE'] = df['OBS_VALUE'].astype('float64')
        
        return df

    except requests.RequestException as e:
        print(f"Request error: {e}")
        return pd.DataFrame()
    except pd.errors.ParserError as e:
        print(f"CSV parsing error: {e}")
        return pd.DataFrame()