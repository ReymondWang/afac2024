import json
import difflib
import pandas as pd 
from .prompt import (fundQuery_cot_prompt,
                    fundSelect_cot_prompt,
                    stockQuery_cot_prompt,
                    stockSelect_cot_prompt,
                    calculation_cot_prompt)
FUND_INQUIRY = 1
FUND_SELECTION = 2
STOCK_INQUIRY = 4
STOCK_SELECTION = 8
PROMPT_MAP = {1:fundQuery_cot_prompt, 2:fundSelect_cot_prompt, 4:stockQuery_cot_prompt, 8:stockSelect_cot_prompt, 0:calculation_cot_prompt}


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


def get_prompt(row,stock_names,fund_names):
    '''
    根据Query、Label生成对应的Prompt
    依赖：原始input(query), type_, products
    '''
    query = row['query']
    # 1. get products 50 if needed
    if row['type_'] & STOCK_INQUIRY:
        products = difflib.get_close_matches(query,stock_names,n=50,cutoff=0.0001)
        query += '\n    query中提到的产品标准名可能是：' + '、'.join(products)
    elif row['type_'] & FUND_INQUIRY:
        products = difflib.get_close_matches(query,fund_names,n=50,cutoff=0.0001)
        query += '\n    query中提到的产品标准名可能是：' + '、'.join(products)
    # 2. get into class prompt
    return PROMPT_MAP[row['type_']].replace('<QUERY>',query)
    

'''
Post Process
'''
def post_process(glm4_output:str):
    '''
    从GLM4输出的带CoT的答案中解析出最终标准Json
    例：
    <output>
        思考过程:
            首先我们可以将该问题分解为以下几个步骤：
                1. query中提出了两个选股条件：上个月的成交金额是将近2986亿，今天收盘时价格是27块84分；
                2. 根据第一个条件，调用 条件选股-成交额(api_0) 获取上个月成交额 等于 2986亿 的股票代码列表;
                3. 根据第二个条件，调用 条件选股-收盘价(api_1) 获取今天收盘价 等于 27.84 的股票代码列表;
                4. 最后，根据问题，需要同时满足以上两个条件，调用 逻辑运算-与运算(api_2) 将以上两个结果取交集，得到最终结果;
                5. 最终输出最终结果，即 api_2 的结果。
        于是最终标准的json格式结果为:
            {"relevant APIs": [{"api_id": "0", "tool_name": "条件选股", "api_name": "成交额", "required_parameters": ["等于", "298600000000.00", "上月"], "rely_apis": []}, {"api_id": "1", "tool_name": "条件选股", "api_name": "收盘价", "required_parameters": ["等于", "27.84", "今日"], "rely_apis": []}, {"api_id": "2", "tool_name": "逻辑运算", "api_name": "与运算", "required_parameters": ["api_0的结果", "api_1的结果"], "rely_apis": ["0", "1"]}], "result": ["api_2的结果"]}
    </output>
    '''
    standard_output = glm4_output.split('于是最终标准的json格式结果为:')[1].strip()
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
    if 'result' not in standard_output:
        print(f'Json格式不正确:result未找到 {standard_output}')
        return None
    return json.dumps(standard_output,ensure_ascii=False)