#coding=utf8
import pandas as pd
import difflib
import json
from tqdm import tqdm

class CreateTrainData:
    def __init__(self) -> None:
        self.standard_name = self.load_standard_name()
        self.prompt='你现在是一个金融领域专家，你需要通过编排api来得到用户query的答案，输出json格式。query是：QUERY \n query中提到的产品标准名可能是：PRODUCT'

    def load_standard_name(self):
        data_stock = pd.read_excel('../raw_data/标准名.xlsx',sheet_name='股票标准名')
        data_fund = pd.read_excel('../raw_data/标准名.xlsx',sheet_name='基金标准名')
        standard_name = data_stock['标准股票名称'].to_list()+data_fund['标准基金名称'].to_list()
        return standard_name
    
    def df_2_json(self,df,json_file):
        print('正在处理',json_file)
        with open(json_file,'w') as m:
            for index, row in tqdm(df.iterrows(),total=df.shape[0]):
                query = row['query']
                products = difflib.get_close_matches(query,self.standard_name,n=50,cutoff=0.0001)
                products_str = '、'.join(products)
                input_ = self.prompt.replace('QUERY',query).replace('PRODUCT',products_str)
                try:
                    output_ = row['label']
                except:
                    output_ = 'mock'
                single_data = {"conversations":[{"role": "user", "content": input_}, {"role": "assistant", "content": output_}]}
                m.write(json.dumps(single_data,ensure_ascii=False)+'\n')

    def run(self):
        df_train = pd.read_excel('../raw_data/train.xlsx')
        df_dev = pd.read_excel('../raw_data/dev.xlsx')
        df_test_a = pd.read_excel('../raw_data/test_a.xlsx')

        self.df_2_json(df_train,'../data/train.json')
        self.df_2_json(df_dev,'../data/dev.json')
        self.df_2_json(df_test_a,'../data/test_a.json')

p=CreateTrainData()
p.run()