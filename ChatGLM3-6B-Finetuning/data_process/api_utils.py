import pandas as pd
from tqdm import tqdm

def create_api_dict(api_file_path: str):
    api_df = pd.read_json(api_file_path)
    
    start_idx = 100
    api_dict = {}
    api_idx_dict = {}
    for _, row in tqdm(api_df.iterrows(), total=api_df.shape[0]):
        one_api = {
            "global_api_id": str(start_idx), 
            "category_name": row["category_name"], 
            "tool_name": row["tool_name"], 
            "api_name": row["api_name"], 
            "api_description": row["api_description"], 
            "parameters": row["parameters"], 
        }
        api_dict[row["tool_name"] + "_" + row["api_name"]] = one_api
        api_idx_dict[one_api["global_api_id"]] = one_api
        
        start_idx += 1
        
    return api_dict, api_idx_dict
        