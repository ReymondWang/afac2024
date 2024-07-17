import json
import difflib
import pandas as pd 
from .prompt import *
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


def read_jsonl(file_path) -> list:
    r"""
        将jsonl的文件转化成为列表
        
        Args:
            params (`file_path`):
                文件路径
    """
    
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            data.append(json.loads(line.strip()))
    return pd.DataFrame(data)

def get_type_from_label(label:str):
    '''
    从GLM3输出的json中解析出问题类别
    '''
    try:
        label_d = eval(label)
    except:
        print(f'error in parsing {label}')
        return None
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
    # assert type_ in (FUND_INQUIRY, FUND_SELECTION, STOCK_INQUIRY, STOCK_SELECTION, 0), f'类型重叠： {label}'
    return type_


def get_prompt(row,glm3_output,stock_names,fund_names):
    '''
    根据Query、Label生成对应的Prompt
    依赖：原始input(query), type_, products
    生成两套：一套普通的，一套带有glm3输出的纠错型
    '''
    query = row['query']
    # 1. get products 50 if needed
    if row['type_'] & STOCK_INQUIRY:
        products = difflib.get_close_matches(query,stock_names,n=50,cutoff=0.0001)
        query += '\n    query中提到的产品标准名可能是：' + '、'.join(products)
    elif row['type_'] & FUND_INQUIRY:
        products = difflib.get_close_matches(query,fund_names,n=50,cutoff=0.0001)
        query += '\n    query中提到的产品标准名可能是：' + '、'.join(products)
    res = {}
    res['common_prompt'] = PROMPTS_MAP[row['type_']][1].replace('<QUERY>',query)
    res['correct_prompt'] = PROMPTS_MAP[row['type_']][2].replace('<QUERY>',query)\
        .replace('<GLM3_ANSWER>',f'基础模型给出的答案是：{glm3_output}')
    return res
    
def process_label(label:str):
    '''
    处理label中的一些问题
    '''
    # df["label"] = df["label"].str.replace("\"api_name\": \"查询","\"api_name\": \"")
    # df["label"] = df["label"].str.replace("基金份额类型(A、B、C)","基金份额类型")
    # df["label"] = df["label"].str.replace("每股经营性现资金流","每股经营性现金流")
    label = label.replace("\"api_name\": \"查询","\"api_name\": \"")
    label = label.replace("基金份额类型(A、B、C)","基金份额类型")
    label = label.replace("每股经营性现资金流","每股经营性现金流")
    return label
'''
Post Process
'''
def post_process(glm4_output:str)->str:
    '''
    从GLM4输出的带CoT的答案中解析出最终标准Json
    包含：
        1. 从带有CoT的output中抽取json
    
    '''
    standard_output = glm4_output.split('于是最终标准的json格式结果为:')[1].replace('</output>','').strip()
    # 格式验证
    try:
        standard_output = json.loads(standard_output)
    except:
        print(f'Json格式不正确:解析失败 {standard_output}')
        return None
    
    if 'relevant APIs' not in standard_output:
        print(f'Json格式不正确:relevant APIs未找到 {standard_output}')
        return None
    else:
        for api in standard_output['relevant APIs']:
            if 'tool_name' not in api:
                print(f'Json格式不正确:tool_name未找到 {standard_output}')
                return None                
            if 'api_name' not in api:
                print(f'Json格式不正确:api_name未找到 {standard_output}')
                return None
            if 'required_parameters' not in api:
                print(f'Json格式不正确:required_parameters未找到 {standard_output}')
                return None
            if 'rely_apis' not in api:
                print(f'Json格式不正确:rely_apis未找到 {standard_output}')
                return None
            # 后处理
            if api['tool_name'] in {'基金查询','条件选基','股票查询','条件选股'}:
                api['api_name'] = '查询'+api['api_name']
                if api['tool_name'] == '条件选基' and api['api_name']=='查询基金份额类型':
                    api['api_name'] = '查询基金份额类型(A、B、C)'
                elif api['tool_name'] == '条件选股' and api['api_name']=='查询每股经营性现金流':
                    api['api_name'] = '查询每股经营性现资金流'
    if 'result' not in standard_output:
        print(f'Json格式不正确:result未找到 {standard_output}')
        return None
    
    return json.dumps(standard_output,ensure_ascii=False)