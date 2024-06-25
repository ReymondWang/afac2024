import os
import difflib
import pandas as pd
import json
from tqdm import tqdm


class ApiSpliter:
    def __init__(self) -> None:
        self.current_path = os.path.dirname(os.path.abspath(__file__))
        self.api_file_path = os.path.join(self.current_path, "../data/api_定义.json")
        self.api_df = pd.read_json(self.api_file_path)
        self.prompt='你现在是一个金融领域专家，你需要通过编排api来得到用户query的答案，输出json格式。query是：QUERY \n query中使用到的api可能是：API'
    
    
    def aggregate(self) -> None:
        """
        将所有的API的分类名称、工具名称、API名称、API描述拼接成一个字符串，方便进行召回。
        整理需要将功能性api与计算型api拆分开。
        """
        self.api_detail_name_arr = []
        self.api_calc_name_arr = []
        for _, row in self.api_df.iterrows():
            if row["category_name"] == "通用":
                api_detail_name = row["tool_name"] + "_" + row["api_name"]
                self.api_calc_name_arr.append(api_detail_name)
            else:
                api_detail_name = row["tool_name"] + "_" + row["api_name"]
                self.api_detail_name_arr.append(api_detail_name)
        
    
    def attach_api_name(self, raw_df, output) -> None:
        print('正在处理',output)
        with open(output,'w') as m:
            for _, row in tqdm(raw_df.iterrows(), total=raw_df.shape[0]):
                query = row['query']
                related_apis = difflib.get_close_matches(query, self.api_detail_name_arr, n=50, cutoff=0.0001)
                related_apis += self.api_calc_name_arr
                related_api_arr = '、'.join(related_apis)
                input_ = self.prompt.replace('QUERY', query).replace('API', related_api_arr)
                try:
                    output_ = row['label']
                    output_ = self.remove_parameters(output_)
                except:
                    output_ = 'mock'
                single_data = {"conversations":[{"role": "user", "content": input_}, {"role": "assistant", "content": output_}]}
                m.write(json.dumps(single_data,ensure_ascii=False)+'\n')
    
    
    def handle_api(self) -> None:
        df_train = pd.read_excel(os.path.join(self.current_path, "../raw_data/train.xlsx"))
        df_dev = pd.read_excel(os.path.join(self.current_path, "../raw_data/dev.xlsx"))
        df_test_a = pd.read_excel(os.path.join(self.current_path, "../raw_data/test_a.xlsx"))
        
        self.aggregate()
        
        self.attach_api_name(df_train, os.path.join(self.current_path, "../data/train_api.json"))
        self.attach_api_name(df_dev, os.path.join(self.current_path, "../data/dev_api.json"))
        self.attach_api_name(df_test_a, os.path.join(self.current_path, "../data/test_a_api.json"))
    
    
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