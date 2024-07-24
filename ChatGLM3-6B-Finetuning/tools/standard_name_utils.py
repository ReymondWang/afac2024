import json
import pandas as pd
from difflib import get_close_matches

SO_STR = "query中提到的产品标准名可能是："
SPLITOR = "、"

RES_API_KEY = "relevant APIs"
RES_KEY = "result"
RES_TOOL_NAME_KEY = "tool_name"
RES_API_NAME_KEY = "api_name"
RES_PARAM_KEY = "required_parameters"


def get_input_standard_names(input: str) -> list:
    r"""
        从输入的Prompt中获得基金标准名

        Args:
            input (`str`):
                输入的Prompt字符串
    """
    SOS = input.index(SO_STR) + len(SO_STR)
    standard_name_str = input[SOS:]
    standard_name_arr = standard_name_str.split(SPLITOR)
    return standard_name_arr


def optimize_parameters(output: str, fund_standard_name: list, stock_standard_name: list) -> str:
    r"""
        优化LLM模型原始的输出

        Args:
            output (`str`):
                LLM原始输出的结果
            input (`str`):
                输入的Prompt字符串
                
        Result:
            优化后的LLM的输出
    """
    try:
        raw = json.loads(output)
        api_list = raw[RES_API_KEY]
        for api in api_list:
            # api[RES_PARAM_KEY] = reorder(api[RES_PARAM_KEY])
            if api[RES_TOOL_NAME_KEY] == "基金查询" and api[RES_API_NAME_KEY] == "查询代码":
                api[RES_PARAM_KEY] = switch_standard_name(api[RES_PARAM_KEY], fund_standard_name)
            elif api[RES_TOOL_NAME_KEY] == "股票查询" and api[RES_API_NAME_KEY] == "查询代码":
                api[RES_PARAM_KEY] = switch_standard_name(api[RES_PARAM_KEY], stock_standard_name)
                
        raw[RES_API_KEY] = api_list
        return json.dumps(raw, ensure_ascii=False)
    except Exception:
        return output
    
    
def reorder(params: list) -> list:
    r"""
        对调用函数的参数重新排序
        将依赖api的结果按照顺序进行排序，并且放到最前面，其他的参数顺序不变。
        
        Args:
            params (`list`):
                原始函数的参数
        
        Result:
            重新排序以后的参数
    """
    
    if params.count == 1:
        return params
    
    rely_api_res = []
    oth = []
    for param in params:
        if isinstance(param, str) and param.startswith("api_"):
            rely_api_res.append(param)
        else:
            oth.append(param)
            
    rely_api_res.sort()

    return rely_api_res + oth
   
            
def switch_standard_name(raw_list: list, standard_name_list: list) -> list:
    r"""
        将参数中的参数修改为标准名称
        
        Args:
            params (`raw_list`):
                原始函数的参数列表
            params (`standard_name_list`):
                标准名称列表
        
        Result:
            替换以后的参数
    """
    
    res = []
    for raw_item in raw_list:
        if isinstance(raw_item, list):
            res.append(switch_standard_name(raw_item, standard_name_list))
        else:
            if raw_item not in standard_name_list:
                switch_name_list = get_close_matches(raw_item, standard_name_list, n=1)
                if len(switch_name_list) > 0:
                    res.append(switch_name_list[0])
                else:
                    res.append(raw_item)
            else:
                res.append(raw_item)
    return res


def optimize_api_chain(raw_api_chain: str, standard_api: list) -> str:
    r"""
        将原本生成的api_chain解析，纠正语法错误，并且纠正个别的api文字错误。
        
        Args:
            params (`raw_api_chain`):
                原始的api_chain
            params (`standard_api`):
                标准api列表
        
        Result:
            替换以后的api_chain
    """
    if raw_api_chain == None or raw_api_chain == "":
        return raw_api_chain
    
    raw_api_chain = raw_api_chain.replace("[", "").replace("]", "")
    raw_api_list = raw_api_chain.split(", ")
    
    tar_api_list = []
    for raw_api in raw_api_list:
        if "->" in raw_api:
            raw_api_components = raw_api.split("->")
            raw_fore_part = raw_api_components[0]
            raw_back_part = raw_api_components[1]
            
            raw_fore_part = raw_fore_part.replace("(", "").replace(")", "")
            raw_fore_part_list = raw_fore_part.split(",")
            fore_part = "("
            for raw_fore_part in raw_fore_part_list:
                if fore_part != "(":
                    fore_part += ","
                if raw_fore_part in standard_api:
                    fore_part += raw_fore_part
                else:
                    closest_ = get_close_matches(raw_fore_part, standard_api, n=1)
                    if len(closest_) > 0:
                        fore_part += closest_[0]
                    else:
                        fore_part += raw_fore_part
            fore_part += ")"
            
            back_part = ""
            if raw_back_part in standard_api:
                back_part = raw_back_part
            else:
                closest_ = get_close_matches(raw_back_part, standard_api, n=1)
                if len(closest_) > 0:
                    back_part = closest_[0]
                else:
                    back_part = raw_back_part
            
            tar_api_list.append(fore_part + "->" + back_part)
        else:
            if raw_api in standard_api:
                tar_api_list.append(raw_api)
            else:
                closest_ = get_close_matches(raw_api, standard_api, n=1)
                if len(closest_) > 0:
                    tar_api_list.append(closest_[0])
                else:
                    tar_api_list.append(raw_api)
                    
    return json.dumps(tar_api_list, ensure_ascii=False)


def get_standard_api(api_file_path: str) -> list:
    r"""
        读取标准api的文件，返回list。
        
        Args:
            params (`api_file_path`):
                标准api的list
        
        Result:
            标准api列表
    """
    api_df = pd.read_json(api_file_path)
    
    standard_api_list = []
    for _, row in api_df.iterrows():
        standard_api_list.append(row["tool_name"] + "_" + row["api_name"])
        
    return standard_api_list


if __name__ == "__main__":
    test_input = "我想知道国金核心资产A的基金经理是谁，以及他的年化回报率和管理的总规模 \n query中提到的产品标准名可能是：国金核心资产一年持有期混合型证券投资基金C类、国金核心资产一年持有期混合型证券投资基金A类、富国大盘核心资产混合型证券投资基金、国联安核心资产策略混合型证券投资基金、创金合信核心资产混合型证券投资基金C类、创金合信核心资产混合型证券投资基金A类、金鹰核心资源混合型证券投资基金C类、金鹰核心资源混合型证券投资基金A类、金元顺安核心动力混合型证券投资基金、汇安核心资产混合型证券投资基金C类、汇安核心资产混合型证券投资基金A类、富国核心趋势混合型证券投资基金C类、富国核心趋势混合型证券投资基金A类、国投瑞银核心企业混合型证券投资基金、华夏核心资产混合型证券投资基金C类、华夏核心资产混合型证券投资基金A类、国联安核心优势混合型证券投资基金A类、民生加银核心资产股票型证券投资基金C类、民生加银核心资产股票型证券投资基金A类、国联核心成长灵活配置混合型证券投资基金、博时核心资产精选混合型证券投资基金C类、博时核心资产精选混合型证券投资基金A类、创金合信量化核心混合型证券投资基金C类、创金合信量化核心混合型证券投资基金A类、创金合信核心价值混合型证券投资基金C类、创金合信核心价值混合型证券投资基金A类、鑫元核心资产股票型发起式证券投资基金C类、鑫元核心资产股票型发起式证券投资基金A类、海富通消费核心资产混合型证券投资基金C类、海富通消费核心资产混合型证券投资基金A类、富国核心优势混合型发起式证券投资基金C类、富国核心优势混合型发起式证券投资基金A类、光大保德信核心资产混合型证券投资基金C类、光大保德信核心资产混合型证券投资基金A类、交银施罗德核心资产混合型证券投资基金C类、交银施罗德核心资产混合型证券投资基金A类、招商资管核心优势混合型集合资产管理计划C类、招商资管核心优势混合型集合资产管理计划A类、国寿安保核心产业灵活配置混合型证券投资基金、金信核心竞争力灵活配置混合型证券投资基金A类、汇添富大盘核心资产增长混合型证券投资基金C类、汇添富大盘核心资产增长混合型证券投资基金A类、国泰核心价值两年持有期股票型证券投资基金C类、国泰核心价值两年持有期股票型证券投资基金A类、国泰金鹿混合型证券投资基金、国联安核心趋势一年持有期混合型证券投资基金C类、国联安核心趋势一年持有期混合型证券投资基金A类、中金安心回报灵活配置混合型集合资产管理计划C类、中金安心回报灵活配置混合型集合资产管理计划A类、银华全球核心优选证券投资基金"
    # get_input_standard_names(test_input)
    
    test_output = "{\"relevant APIs\": [{\"api_id\": \"0\", \"api_name\": \"查询代码\", \"required_parameters\": [[\"国金核心资一年持有期混合型证券投资基金C类\"]], \"rely_apis\": [], \"tool_name\": \"基金查询\"}, {\"api_id\": \"1\", \"api_name\": \"查询基金经理\", \"required_parameters\": [\"api_1的结果\", \"api_0的结果\"], \"rely_apis\": [\"0\"], \"tool_name\": \"基金查询\"}, {\"api_id\": \"2\", \"api_name\": \"查询基金经理年化回报率\", \"required_parameters\": [\"api_1的结果\"], \"rely_apis\": [\"1\"], \"tool_name\": \"基金查询\"}, {\"api_id\": \"3\", \"api_name\": \"查询基金经理管理规模\", \"required_parameters\": [\"api_1的结果\"], \"rely_apis\": [\"1\"], \"tool_name\": \"基金查询\"}], \"result\": [\"api_1的结果\", \"api_2的结果\", \"api_3的结果\"]}"
    res = optimize_parameters(test_output, test_input)
    print(res)
