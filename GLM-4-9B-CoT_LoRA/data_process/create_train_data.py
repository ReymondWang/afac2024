#coding=utf8
import pandas as pd
import difflib
import json
from tqdm import tqdm

# data_path = '../../CoTPromptEngineer/data/data4cot/cot4train_by_category.xlsx'
data_path = '../data/cot4dev_by_category.xlsx'

class CreateTrainData:
        
    def df_2_json(self,df,json_file):
        print('正在处理',json_file)
        with open(json_file,'w') as m:
            for index, row in tqdm(df.iterrows(),total=df.shape[0]):
                
                input_ = row['cot_prompt_by_category']
                output_ = row['cot_label_by_category']
                                    
                single_data = {"messages":[{"role": "user", "content": input_}, {"role": "assistant", "content": output_}]}
                m.write(json.dumps(single_data,ensure_ascii=False)+'\n')

    def run(self):
        df = pd.read_excel(data_path)
        self.df_2_json(df,'../data/dev.jsonl')

p=CreateTrainData()
p.run()