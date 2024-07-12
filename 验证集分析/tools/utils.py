import pandas as pd
from IPython.display import display, HTML

def get_features(label:str,prefix:str) -> pd.Series:
    features = {}
    features[f'{prefix}_api_list'] = []
    features[f'{prefix}_api_params'] = []
    features[f'{prefix}_api_num'] = 0
    features[f'{prefix}_result'] = []
    try:
        label_d = eval(label)
    except:
        print(f'error in parsing {label}')
        res = pd.Series(features).astype(str)
        res.loc[f'{prefix}_api_num'] = 0
        return res
    for api in label_d['relevant APIs']:
        features[f'{prefix}_api_list'].append(str((api['tool_name'],api['api_name'])))
        features[f'{prefix}_api_params'].append(str(api['required_parameters']))
        features[f'{prefix}_api_num'] += 1
    try:
        features[f'{prefix}_result'] = ','.join([res[:-3] for res in label_d['result']])
    except:
        features[f'{prefix}_result'] = None
        print(label_d['result'])
    features[f'{prefix}_api_list'] = '<br>'.join(features[f'{prefix}_api_list'])
    features[f'{prefix}_api_params'] = '<br>'.join(features[f'{prefix}_api_params'])
    # features[f'{prefix}_result'] = label_d['result']
    return pd.Series(features)

def disp(df, cols_width=[]):
    
    # 将DataFrame转换为HTML
    html = df.to_html(escape=False)
    if cols_width:
        assert len(cols_width) == df.shape[1], "列宽度列表的长度必须与DataFrame的列数相等"
        cols_width = [4] + cols_width 
        # 构建<colgroup>标签字符串以指定列宽度
        colgroup = "<colgroup>" + "".join([f'<col style="width: {width}px;">' for width in cols_width]) + "</colgroup>"
        # 将<colgroup>标签插入到<table>标签之后
        html = html.replace('<table border="1" class="dataframe">', '<table border="1" class="dataframe">' + colgroup)
    
    # 显示带有自定义列宽度的DataFrame
    return display(HTML(html))


def compare_lists(a:list, b:list):
    i, j = 0, 0 
    result_a, result_b = [], []
    
    while i < len(a) and j < len(b):
        if a[i] == b[j]:
            result_a.append(a[i])
            result_b.append(b[j])
            i += 1
            j += 1
        elif a[i] != b[j]:
            # 检查b中是否存在与a[i]相等的元素
            found_in_b = False
            for k in range(j, len(b)):
                if a[i] == b[k]:
                    found_in_b = True
                    break
            if found_in_b:  # b中多出了 j->k
                result_a.append(a[i])
                result_b.append(f'<span style="color: red">{"<br>".join(b[j:k])}</span>')
                i += 1
                j = k
            else: 
                if len(a)-i > len(b)-j: # a 多
                    result_a.append(f'<span style="color: green">{a[i]}</span>')
                    i += 1
                else :
                    result_b.append(f'<span style="color: red">{b[j]}</span>')
                    result_a.append(f'<span style="color: green">{a[i]}</span>')
                    i += 1
                    j += 1 

    
    # 处理剩余的元素
    while i < len(a):
        result_a.append(f'<span style="color: green">{a[i]}</span>')
        i += 1
    while j < len(b):
        result_b.append(f'<span style="color: red">{b[j]}</span>')
        j += 1
    
    return result_a, result_b

def highlight_differences(row,col_a,col_b):
    
    a_list = row[col_a].split('<br>')
    b_list = row[col_b].split('<br>')

    a_list,b_list = compare_lists(a_list,b_list)
    return pd.Series({col_a:'<br>'.join(a_list),col_b:'<br>'.join(b_list)})

FUND_INQUIRY = 1
FUND_SELECTION = 2
STOCK_INQUIRY = 4
STOCK_SELECTION = 8

def get_type_from_json(label:str):
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
        if api['tool_name'] == '基金查询':
            type_ |= FUND_INQUIRY
        elif api['tool_name'] == '条件选基':
            type_ |= FUND_SELECTION
        elif api['tool_name'] == '股票查询':
            type_ |= STOCK_INQUIRY
        elif api['tool_name'] == '条件选股':
            type_ |= STOCK_SELECTION
    return type_
    


if __name__=='__main__':
    # compare_lists示例
    a = ["('股票查询', '查询代码')","('股票查询', '查询当前价')","('数值计算', '乘法计算')"]
    b = ["('股票查询', '查询代码')","('股票查询', '查询收盘价')","('股票查询', '查询收盘价')",
         "('数值计算', '乘法计算')","('数值计算', '加法计算')"]
    result_a, result_b = compare_lists(a, b)
    from IPython.display import display, HTML
    display(HTML(f"A: {result_a}"))
    display(HTML(f"B: {result_b}"))

    # disp测试
    # 示例使用
    data = {'A': [1, 2, 3], 'B': [4, 5, 6], 'C': [7, 8, 9]}
    df = pd.DataFrame(data)
    disp(df, cols_width=[50, 100, 150])