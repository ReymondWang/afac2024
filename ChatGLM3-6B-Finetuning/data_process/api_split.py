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
        self.prompt='你现在是一个金融领域专家，你需要根据用户的query编排api，需要使用的api以id==具体功能的形式在下面给出，预测中只需要给出id。query是：QUERY \n query中使用到的api可能是：API'
    
    
    def aggregate_api_detail(self, api_dict) -> None:
        self.api_detail_arr = []
        self.api_calc_detail_arr = []
        for key in api_dict:
            # api_detail = api_dict[key]["tool_name"] + "_" + api_dict[key]["api_name"] + "_" + api_dict[key]["api_description"]
            api_detail = api_dict[key]["tool_name"] + "_" + api_dict[key]["api_name"]
            
            if api_dict[key]["category_name"] == "通用":
                self.api_detail_arr.append(api_detail)
            else:
                self.api_calc_detail_arr.append(api_detail)
    
    
    def transfer_label_to_global_api_id(self, raw_json_str, api_dict) -> str:
        raw_json = json.loads(raw_json_str)
        related_apis = raw_json["relevant APIs"]
        
        api_id_chain = []
        api_id_to_global = {}
        for related_api in related_apis:
            key = related_api["tool_name"] + "_" + related_api["api_name"]
            global_api_id = api_dict[key]["global_api_id"]
            api_id_to_global[related_api["api_id"]] = global_api_id
            
            rely_apis = related_api["rely_apis"]
            if not rely_apis:
                api_id_chain.append(global_api_id)
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
                    full_api += api_id_to_global[api_id]
                full_api += ")->"
                full_api += global_api_id
                api_id_chain.append(full_api)
        
        return json.dumps(api_id_chain, ensure_ascii=False)


    def attach_api_name(self, raw_df, api_dict, output) -> None:
        print('正在处理', output)
        with open(output, 'w') as m:
            for _, row in tqdm(raw_df.iterrows(), total=raw_df.shape[0]):
                query = row['query']
                related_apis = difflib.get_close_matches(query, self.api_detail_arr, n=50, cutoff=0.0001)
                related_apis += self.api_calc_detail_arr
                
                related_api_with_ids = []
                for api in related_apis:
                    api_arr = api.split("_")
                    global_api_id = api_dict[api_arr[0] + "_" + api_arr[1]]["global_api_id"]
                    related_api_with_ids.append(global_api_id + "==" + api)
                
                related_api_with_ids = '、'.join(related_api_with_ids)
                input_ = self.prompt.replace('QUERY', query).replace('API', related_api_with_ids)
                try:
                    output_ = row['label']
                    output_ = self.transfer_label_to_global_api_id(output_, api_dict)
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
        df_test_a = pd.read_excel(os.path.join(self.current_path, "../raw_data/test_a.xlsx"))
        
        self.attach_api_name(df_train, api_dict, os.path.join(self.current_path, "../data/train_api.json"))
        self.attach_api_name(df_dev, api_dict, os.path.join(self.current_path, "../data/dev_api.json"))
        self.attach_api_name(df_test_a, api_dict, os.path.join(self.current_path, "../data/test_a_api.json"))
    
    
    def remove_parameters(self, raw_json_str) -> str:
        raw_json = json.loads(raw_json_str)
        related_apis = raw_json["relevant APIs"]
        for related_api in related_apis:
            del related_api["required_parameters"]
        return json.dumps(raw_json, ensure_ascii=False)
    
    
    def get_fund_and_general_api(self):
        sub_api_df = self.api_df.query("category_name == '基金' | category_name == '通用'")
        
        json_records = sub_api_df.to_json(orient="records", force_ascii=False)
        json_list = json.loads(json_records)
        
        save_path = os.path.join(self.current_path, "../data/fund_api_定义.json")
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(json_list, f, ensure_ascii=False, indent=4)
        
    
    def test(self) -> None:
        print(self.api_df.head())
        
if __name__ == "__main__":
    apiSpliter = ApiSpliter()
    apiSpliter.handle_api()