import pandas as pd
import requests
import json
from functools import reduce
from tools.tooldb import update_json
from typing import List, Dict


def get_wb_data(
        model:str,
        type:str,
        variable:str,
        product:str,
        aggregation:str,
        periods:str,
        unit:str,
        sub_models:str,
        countries:str,
        var_name:str=None):
    if var_name is None:
        var_name = variable

    base_url = "https://cckpapi.worldbank.org/api/v1/"
    url = f"{base_url}{model}_{type}_{variable}_{product}_{aggregation}_{periods}_{unit}_{sub_models}_ensemble_all_mean/{countries}?_format=json"
        
    try :
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        data = json.loads(response.text)
        d = data['data']
        rows = []
        for period, a_models in d.items():          
            for unit, b_models in a_models.items():             
                for model, sub_data in b_models.items():
                    df = pd.DataFrame(sub_data).reset_index().rename(columns={'index': 'time_period'})
                    melted = df.melt(id_vars='time_period', var_name='geo', value_name='value')

                    # Attach identifying columns
                    melted['model'] = model
                    melted['period'] = period
                    melted['unit'] = unit

                    rows.append(melted)

            df = pd.concat(rows, ignore_index=True)
            df = df.rename(columns={'value': var_name})
            df = df[['time_period', 'period', 'geo', 'model', 'unit', var_name]]
            if 'period' in df.columns:
                df = df.drop(columns=['period'])

    except requests.RequestException as e:
        print(f"Request error: {e}")
        return pd.DataFrame()
    return df

def serial_wb_db(db_info:Dict, keys:List[str], countries:str, description:Dict=None, pattern=None, db_name:str=None, merge_how:str="outer", output_json:bool=True, output_dfs:bool=False):
    dfs = {}
    dbs_list = [db for db in db_info.keys()]

    for var_name in dbs_list: 
        model, type, variable, product, aggregation, periods, unit, sub_models, = db_info.get(var_name)
        df = get_wb_data(
                model=model,
                type=type,   
                variable=variable,
                product=product,
                aggregation=aggregation,
                periods=periods,
                unit=unit,
                sub_models=sub_models,
                countries=countries,
                var_name=var_name)
        
        df['model'] = df['model'].str.replace('_', '-')

        dfs[var_name] = df

        if output_json:
            update_json(df, db_name, pattern, description)

    final_df = reduce(lambda left, right: pd.merge(left, right, on=[k.lower() for k in keys] + ['unit'], how=merge_how), dfs.values())
    final_df = final_df.dropna(axis=1, how='all')

    if output_dfs:
        return final_df, dfs
    else:
        return final_df
    

def clean_wbstat(df:pd.DataFrame, keys:str, columns_to_pivot:List, aggfunc:str='first'):
    value_vars = [c for c in df.columns if c not in keys + columns_to_pivot]

    wide = df.pivot_table(
            index=keys,
            columns=columns_to_pivot,
            values=value_vars,
            aggfunc=aggfunc
        )

    if isinstance(wide.columns, pd.MultiIndex):
        wide.columns = [
            f"{val}_{model}_{unit}" for val, model, unit in wide.columns
        ]
    else:
        wide.columns.name = None

    # reset index back to columns
    wide = wide.reset_index()

    return wide