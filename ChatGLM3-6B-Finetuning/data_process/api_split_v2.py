"""
这个版本跟api_split的差别在于，这个版本使用文字而不是编号。
"""

import os
import difflib
import pandas as pd
import json
from tqdm import tqdm
from api_utils import create_api_dict

class ApiSpliter:
    def __init__(self) -> None:
        self.current_path = os.path.dirname(os.path.abspath(__file__))
        self.api_file_path = os.path.join(self.current_path, "../data/api_定义.json")
        self.api_df = pd.read_json(self.api_file_path)
        self.prompt='你现在是一个金融领域专家，你需要根据用户的query编排api，需要使用的api在下面给出。query是：QUERY \n query中使用到的api可能是：API'
        
        
    def aggregate_api_detail(self, api_dict) -> None:
        self.api_detail_arr = []
        self.api_calc_detail_arr = []
        for key in api_dict:
            # 如果添加上description，输入就会过长。不知道是否可以考虑在这里使用RAG技术。
            # api_detail = api_dict[key]["tool_name"] + "_" + api_dict[key]["api_name"] + "_" + api_dict[key]["api_description"]
            api_detail = api_dict[key]["tool_name"] + "_" + api_dict[key]["api_name"]
            
            if api_dict[key]["category_name"] == "通用":
                self.api_detail_arr.append(api_detail)
            else:
                self.api_calc_detail_arr.append(api_detail)
                
                
    def transfer_label_to_api_chain(self, raw_json_str) -> str:
        raw_json = json.loads(raw_json_str)
        related_apis = raw_json["relevant APIs"]
        
        api_id_chain = []
        api_id_to_key = {}
        for related_api in related_apis:
            key = related_api["tool_name"] + "_" + related_api["api_name"]
            api_id_to_key[related_api["api_id"]] = key
            
            rely_apis = related_api["rely_apis"]
            if not rely_apis:
                api_id_chain.append(key)
            else:
                full_api = "("
                
                rely_apis_copy = []
                for api_id in rely_apis:
                    if "," in api_id:
                        for a_id in api_id.split(","):
                            rely_apis_copy.append(a_id)
                    else:
                        rely_apis_copy.append(api_id)
                            
                
                for api_id in rely_apis_copy:
                    if full_api != "(":
                        full_api += ","
                    full_api += api_id_to_key[api_id]
                full_api += ")->"
                full_api += key
                api_id_chain.append(full_api)
        
        return json.dumps(api_id_chain, ensure_ascii=False)
    
    
    def attach_api_name(self, raw_df, api_dict, output) -> None:
        print('正在处理', output)
        with open(output, 'w') as m:
            for _, row in tqdm(raw_df.iterrows(), total=raw_df.shape[0]):
                query = row['query']
                related_apis = difflib.get_close_matches(query, self.api_detail_arr, n=50, cutoff=0.0001)
                related_apis += self.api_calc_detail_arr
                
                related_apis = '、'.join(related_apis)
                input_ = self.prompt.replace('QUERY', query).replace('API', related_apis)
                try:
                    output_ = row['label']
                    output_ = self.transfer_label_to_api_chain(output_)
                except:
                    output_ = 'mock'
                single_data = {"conversations":[{"role": "user", "content": input_}, {"role": "assistant", "content": output_}]}
                m.write(json.dumps(single_data,ensure_ascii=False)+'\n')
                
    
    def handle_api(self) -> None:
        print("--------设置API的映射字典--------")
        api_dict, _ = create_api_dict(self.api_file_path)
        
        self.aggregate_api_detail(api_dict)
        
        df_train = pd.read_excel(os.path.join(self.current_path, "../raw_data/train.xlsx"))
        df_dev = pd.read_excel(os.path.join(self.current_path, "../raw_data/dev.xlsx"))
        # df_test_a = pd.read_excel(os.path.join(self.current_path, "../raw_data/test_a.xlsx"))
        
        self.attach_api_name(df_train, api_dict, os.path.join(self.current_path, "../data/train_api_name.json"))
        self.attach_api_name(df_dev, api_dict, os.path.join(self.current_path, "../data/dev_api_name.json"))
        # self.attach_api_name(df_test_a, api_dict, os.path.join(self.current_path, "../data/test_a_api.json"))
        
        
if __name__ == "__main__":
    apiSpliter = ApiSpliter()
    apiSpliter.handle_api()