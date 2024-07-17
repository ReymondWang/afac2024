""" 
本脚本用于生成训练GLM-4 CoT专用数据集，包括 train 和 dev
本步骤是在GLM-3调用生成label的基础上
主要生成这些东西：
    1. 用于访问外部大模型生成CoT的Prompt (cot_generate_xxx_prompt)
    2. 嵌入外部模型CoT的label (cot_label)
    3. 用于训练的输入prompt (cot_input)
    4. 融入glm3输出的纠错型prompt (cot_correct_input)
"""
import pandas as pd
import difflib
import json
from tqdm import tqdm
from prompt import *
from openai import OpenAI
import pandas as pd
# import os; api_key = os.getenv('DEEPSEEK_API')
api_key = 'sk-b75d2229e28a49dd9f4c1caf4293345c'
print(api_key)

FUND_INQUIRY = 1
FUND_SELECTION = 2
STOCK_INQUIRY = 4
STOCK_SELECTION = 8
PROMPTS_MAP = {
    0:[cot_generate_common_prompt,common_prompt,common_prompt_with_correct],
    1:[cot_generate_fund_query_prompt,fund_query_prompt,fund_query_prompt_with_correct],
    2:[cot_generate_fund_select_prompt,fund_select_prompt,fund_select_prompt_with_correct],
    4:[cot_generate_stock_query_prompt,stock_query_prompt,stock_query_prompt_with_correct],
    8:[cot_generate_stock_select_prompt,stock_select_prompt,stock_select_prompt_with_correct],
}

def get_type_from_label(label:str)->int:
    '''
    从label中解析出类型，label可以是原始label，也可以是glm3输出的label
    '''
    try:
        label_d = eval(label)
    except:
        print(f'error in parsing {label}')
        return 0
    api_list = label_d['relevant APIs']
    type_ = 0
    for api in api_list:
        if 'tool_name' not in api:
            print(f'error in parsing {api}')
            continue
        if api['tool_name'] == '基金查询' and api['api_name'] != '查询代码':    # 个别仅仅查询了代码，不算查询（无效）
            type_ |= FUND_INQUIRY
        elif api['tool_name'] == '条件选基':
            type_ |= FUND_SELECTION
        elif api['tool_name'] == '股票查询' and api['api_name'] != '查询代码':
            type_ |= STOCK_INQUIRY
        elif api['tool_name'] == '条件选股':
            type_ |= STOCK_SELECTION
    if type_ not in PROMPTS_MAP:
        print(f'error in parsing {label}: type:{type_}')
        return 0
    return type_

    
class CreateTrainData:
    def __init__(self):
        # self.standard_name = self.load_standard_name()
        # self.prompt='你现在是一个金融领域专家，你需要通过编排api来得到用户query的答案，输出json格式。query是：QUERY \n query中提到的产品标准名可能是：PRODUCT'
        self.client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        self.load_standard_name()

    def load_standard_name(self):
        self.stock_names = pd.read_excel('../data/data-0520/标准名.xlsx',sheet_name='股票标准名')['标准股票名称'].to_list()
        self.fund_names = pd.read_excel('../data/data-0520/标准名.xlsx',sheet_name='基金标准名')['标准基金名称'].to_list()

    def get_type(self,df):
        if 'label' not in df.columns:
            print('no label found in DataFrame')
            raise ValueError 
        else:
            df['type_'] = df['label'].apply(get_type_from_label)
    
    def get_products(self,df):
        print('正在召回产品标准名')
        df['products'] = None
        df['query_with_products'] = df['query']
        for index,row in tqdm(df.iterrows(),total=df.shape[0]):
            if row['type_'] & STOCK_INQUIRY:
                products = difflib.get_close_matches(row['query'],self.stock_names,n=50,cutoff=0.0001)
                df.at[index,'products'] = products
                df.at[index,'query_with_products'] += '\n    query中提到的产品标准名可能是：' + '、'.join(products)
                # print(f'index: {index}, query: {row["query"]}\nproducts: {products}\nnew_query: {df.at[index,"query_with_products"]}')
            if row['type_'] & FUND_INQUIRY:
                products = difflib.get_close_matches(row['query'],self.fund_names,n=50,cutoff=0.0001)
                df.at[index,'products'] = products
                df.at[index,'query_with_products'] += '\n    query中提到的产品标准名可能是：' + '、'.join(products)
    
    def process_label(self,df):
        '''
        处理label中的一些问题
        '''
        df["label"] = df["label"].str.replace("\"api_name\": \"查询","\"api_name\": \"")
        df["label"] = df["label"].str.replace("基金份额类型(A、B、C)","基金份额类型")
        df["label"] = df["label"].str.replace("每股经营性现资金流","每股经营性现金流")
    
    def get_cot_generate_prompt(self,df):
        df['cot_generate_prompt'] = df.apply(
            lambda x: PROMPTS_MAP[x['type_']][0].replace('<QUERY>',x['query_with_products'])\
                .replace('<ANSWER>',x['label']),axis=1)
    
    def get_cot_label(self,df):
        print('正在生成CoT的label')
        df['cot'] = ''
        df['cot_label'] = ''
        for index,row in tqdm(df.iterrows(),total=df.shape[0]):
            messages = [{"role": "user", "content": row['cot_generate_prompt']}]
            response = self.client.chat.completions.create(model="deepseek-chat", messages=messages, max_tokens=4096)   
            output = response.choices[0].message.content
            if output.strip()[:4]!='思考过程':
                output =  '思考过程：\n    ' + output
            df.at[index,'cot'] = output 
            cot_label = output +' \n于是最终标准的json格式结果为:\n    ' + row['label']
            cot_label = cot_label.replace('\n','\n    ')
            cot_label = '<output>\n    ' + cot_label + '\n</output>'
            df.at[index,'cot_label'] = cot_label
            if index%100==0:
                df.to_excel(f'{index}.xlsx')
     
    def get_cot_input(self,df):
        df['cot_input'] = df.apply(lambda x: PROMPTS_MAP[x['type_']][1].replace('<QUERY>',x['query_with_products']),axis=1)
    
    def get_glm3_label(self,df):
        '''
        调用GLM3生成label
        '''
        pass
    
    def get_cot_correct_input(self,df):
        # 先调GLM3生成GLM3_label
        pass

    def process_df(self,df,test=False):
        if not test:
            # self.get_glm3_label(df)
            self.get_type(df)
            self.get_products(df)
            self.process_label(df)
            self.get_cot_input(df)
            # self.get_cot_correct_input(df)
            self.get_cot_generate_prompt(df)
            self.get_cot_label(df)  # 这一步最耗时
        else: # 推理前加工的流程
            self.get_glm3_label(df) # 用glm3_label作为label
            self.get_type(df)
            self.get_products(df)
            self.process_label(df)
            self.get_cot_input(df)
            self.get_cot_correct_input(df)
        return df

    def df_2_json(self,df,json_file,input_col,output_col):
        print('正在处理',json_file)
        with open(json_file,'w') as m:
            for index,row in tqdm(df.iterrows(),total=df.shape[0]):
                input_ = row[input_col]
                output_ = row[output_col]
                single_data = {'input':input_,'output':output_}
                m.write(json.dumps(single_data,ensure_ascii=False)+'\n')
                
    def run(self):
        df_train = pd.read_excel('../data/data-0520/train.xlsx')
        df_dev = pd.read_excel('../data/data-0520/dev.xlsx')
        # df_test_a = pd.read_excel('../data/data-0520/test_a.xlsx')
        
        self.process_df(df_train)
        df_train.to_excel('./train.xlsx')
        # self.process_df(df_dev)
        # df_dev.to_excel('./dev.xlsx')

        self.df_2_json(df_train,'../data/json_data/train_cot.json',input_col='cot_input',output_col='cot_label')
        self.df_2_json(df_dev,'../data/json_data/dev_cot.json',input_col='cot_input',output_col='cot_label')
        # self.df_2_json(df_test_a,'../data/json_data/test_a.json')

p=CreateTrainData()
p.run()
