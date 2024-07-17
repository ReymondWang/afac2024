task_cot_generate = '''\
你现在是一个金融领域专家。我们计划做一个智能查询系统，系统中有一系列原子化api，系统负责在接收用户的提问后，通过一系列的api调用生成答案。目前我们人工收集了一系列问题和json格式标准答案（该答案包括：1. 问题对应的api调用链，2.需要输出的结果）想要进一步通过思维链（CoT）二次纠错提升正确率。希望你借助金融知识和自身强大的理解力，结合问题和标准答案，给出由问题一步步得到该答案的一个完整思考过程(注意：输出的思考过程本身不应包含对标准答案的解读（如：不应出现“根据提供的标准答案”等类似的字眼），因为逻辑上来说，先有思考过程后有答案)；这将用于我们的模型训练。
'''
task_cot_generate_with_correct = '''\
你现在是一个金融领域专家。我们计划做一个智能查询系统，系统中有一系列原子化api，系统负责在接收用户的提问后，通过一系列的api调用生成答案。目前我们：
        1. 人工收集了一系列问题和json格式标准答案（该答案包括：1. 问题对应的api调用链，2.需要输出的结果）；
        2. 训练了一个基础的端到端大模型可以直接输出类似的答案，但正确率只有60%左右。
    想要进一步通过思维链（CoT）和基础模型答案二次纠错提升正确率。希望你借助金融知识和自身强大的理解力完成以下任务以生成更全面的训练数据来提升模型的正确率：
        1. 结合问题和标准答案，给出由问题一步步得到该答案的一个完整思考过程(注意：输出的思考过程本身不应包含对标准答案的解读（如：不应出现“根据提供的标准答案”等类似的字眼），因为逻辑上来说，先有思考过程后有答案)；
        2. 基于1的思考过程判断基础模型答案的正确性，如有错误，指出错误原因。
'''

task_inference = '''\
你现在是一个金融领域专家，负责在接收用户的提问(query)后，通过详细分析问题，编排api来得到用户query的答案，为了保证逻辑的严谨性，你需要将问题一步步拆解，写出思考过程，最后给出json格式的标准答案。
'''

task_inference_with_correct = '''\
你现在是一个金融领域专家，负责在接收用户的提问(query)后，通过详细分析问题，编排api来得到用户query的答案，为了保证逻辑的严谨性，你需要将问题一步步拆解，写出思考过程，最后给出json格式的标准答案。另外，我们有一个训练好的大模型也会给出答案（只有最终答案），其完全正确的概率只有60%左右，仅用于参考。
'''
common_api_description = '''\
数值计算类(4个)：
                名称：加法计算,减法计算,乘法计算,除法计算
                说明：输入两个数值，做相应计算
            逻辑运算类(2个)：
                名称：与运算,或运算
                说明：输入两个列表，分别是做交集和并集
'''

fund_apis = '''\
类型,规模,晨星评级,蚂蚁评级,申购费率,成立年限,开放类型,申购状态,蚂蚁金选标识,风险等级,基金经理类型,基金经理,基金公司,
                    基金经理从业年限,基金经理管理规模,基金经理年化回报率,持股估值,持股集中度,持股热门度,持股换手率,机构占比,单一持有人占比,
                    重仓股票,重仓行业,持仓风格,基金公司是否自购,是否可投沪港深,近一年买入持有6个月历史盈利概率,近3年买入持有1年历史盈利概率,
                    近5年买入持有1年历史盈利概率,近期收益率,近期收益率同类排名,近期年化收益率,近期年化收益率同类排名,近期超大盘收益率,近期创新高次数,
                    近期最大回撤,近期最大回撤同类排名,近期波动率同类排名,近期最长解套天数,近期跟踪误差,近期夏普比率同类排名,近期卡玛比率同类排名,
                    近期信息比率同类排名,年度收益率,近期指数增强,年度最大回撤,基金事后分类,基金资产打分,基金募集类型,投组区域,基金份额类型,
                    申购最小起购金额,分红方式,赎回状态,是否支持定投,单位净值同步日期,单位净值,基金经理任职期限,近期夏普率,
                    投资市场,板块,行业,聚类行业,管理费率,销售服务费率,托管费率,认购费率,赎回费率,分红年度,权益登记日,除息日,派息日,红利再投日,每十份收益单位派息（元）
'''
stock_apis = '''\
开盘价,最高价,最低价,当前价,收盘价,成交量,成交额,涨停价,跌停价,涨跌额,涨跌幅,主力资金流入,主力资金流出,主力资金净流入,总流入,总流出,
                    换手率,每股收益,静态市盈率,总市值,振幅,流通市值,每股收益ttm,市盈率ttm,净资产收益率,每股净资产,每股经营性现金流,毛利率,净利率,净利润,
                    净利润同比增长,营业收入,营收同比增长,投资收入,营业利润,营业利润同比增长,扣非净利润,流动资产,总资产,短期负债,总负债,股东权益,净经营性现金流,净投资性现金流,净融资性现金流,银行资本充足率,流通股本,总股本,高管名称
'''

fundQuery_api_description = '''\
基金查询类api:
                名称：
                    代码,<FUND_APIS>
                说明：
                    1. 名称为“代码”的api，输入基金名称列表，返回对应的基金代码列表，当用户提到一支基金的名称，一定要先通过这个api将名称转化为代码再查询，因为其他查询api都接受代码而不是名称；
                    2. 其他api名称为指标名称，参数为基金代码列表（个别带有"近期","年度"关键字的api有第二参数：时间），返回相应指标值。
            <COMMON_API_DESC>
'''.replace('<FUND_APIS>',fund_apis).replace('<COMMON_API_DESC>',common_api_description)

fundSelect_api_description = '''\
条件选基类api: 
                名称：
                    <FUND_APIS>
                说明：
                    1. 这些api输入运算符（如“大于” “小于” “等于” "包括"等）和指标（如“规模”），输出符合该指标对应条件的基金名称列表。
                    2. 个别带有"近期","年度"关键字的api有第三参数：时间。
            <COMMON_API_DESC>
'''.replace('<FUND_APIS>',fund_apis).replace('<COMMON_API_DESC>',common_api_description)

stockQuery_api_description = f'''\
股票查询类api:
                名称：
                    代码,<STOCK_APIS>
                说明：
                    1. 这些api输入股票代码，返回相应指标值，当用户提到股票的名称，一定要先通过这个api将名称转化为代码再查询，因为其他查询api都接受代码而不是名称；
                    2. 个别带有"近期","年度"关键字的api有第二参数：时间。
            <COMMON_API_DESC>
'''.replace('<STOCK_APIS>',stock_apis).replace('<COMMON_API_DESC>',common_api_description)

stockSelect_api_description = f'''\
条件选股类api: 
                名称：
                    <STOCK_APIS>
                说明：
                    1. 这些api输入运算符（如“大于” “小于” “等于” "包括"等）和指标（如“规模”），输出符合该指标对应条件的股票代码列表。
                    2. 个别带有"近期","年度"关键字的api有第三参数：时间。
            <COMMON_API_DESC>
'''.replace('<STOCK_APIS>',stock_apis).replace('<COMMON_API_DESC>',common_api_description)

fund_tips = '''\
行业背景知识&Tips（可以辅助你分析解决问题）：
        1. 基金规模和基金经理管理规模是两个不同的概念，基金规模是指某一支基金的规模，而基金经理管理规模是指某个基金经理管理的基金规模。
        2. 基金申购指购买已经发行的基金份额，认购指初次发行的基金。
        3. 基金中的主要费用包括：
            申购时有申购费，持有期间有基金管理费，赎回时有赎回费(因持有时长不同，费率不同),其他还有销售服务费等
            注意：金额*相关费率=相关费用（!注意乘数是金额而不是份额，给出份额时应通过份额*净值计算出金额） 
        4. 注意区分价值与成本，当前的价值是当前的价格*份额，成本是（购买时的价格*份额-费用）
        5. 只能选用上文中"所有可用的api"中的api，不能捏造；
        6. 切题，避免无关的api调用（比如问基金经理管理规模就不要查询基金规模了）。
'''

stock_tips = '''\
行业背景知识&Tips（可以辅助你分析解决问题）：
        1. 如无特殊说明，计算收益(率)统一使用收盘价计算
        2. 涉及到市盈率，一般指的是静态市盈率；动态市盈率指的是市盈率ttm
        3. 只能选用上文中"所有可用的api"中的api，不能捏造
        4. 切题，避免无关的api调用
'''

standard_json_format = '''\
最终答案中的json格式为（其中tool_name为api类别，api_id从0开始依次递增）：
        {"relevant APIs": [{"api_id": "0", "api_name": "...", "required_parameters": [...], "rely_apis": [...], "tool_name": "..."},...],"result": ["api_5的结果"]}
'''

examples = {
    'fundQuery':{
        'query':"我如果3个月前用5000块买了国投瑞银锐意改革C，然后又在1个月前购买了1000块，那么我现在总共赚了多少钱呢？\n        问题中提到的产品标准名可能是：国投瑞银锐意改革灵活配置混合型证券投资基金C类、国投瑞银锐意改革灵活配置混合型证券投资基金A类、国投瑞银瑞福深证100指数分级证券投资基金、国投瑞银瑞福深证100指数证券投资基金(LOF)、国投瑞银瑞福深证100指数分级证券投资基金之进取级基金份额、国投瑞银瑞福深证100指数分级证券投资基金之优先级基金份额、国投瑞银瑞和沪深300指数分级证券投资基金",
        'answer':'{"relevant APIs": [{"api_id": "0", "api_name": "代码", "required_parameters": [["国投瑞银锐意改革灵活配置混合型证券投资基金C类"]], "rely_apis": [], "tool_name": "基金查询"}, {"api_id": "1", "api_name": "近期收益率", "required_parameters": ["api_0的结果", "3个月"], "rely_apis": ["0"], "tool_name": "基金查询"}, {"api_id": "2", "api_name": "乘法计算", "required_parameters": ["api_1的结果", "5000"], "rely_apis": ["1"], "tool_name": "数值计算"}, {"api_id": "3", "api_name": "近期收益率", "required_parameters": ["api_0的结果", "1个月"], "rely_apis": ["0"], "tool_name": "基金查询"}, {"api_id": "4", "api_name": "乘法计算", "required_parameters": ["api_3的结果", "1000"], "rely_apis": ["3"], "tool_name": "数值计算"}, {"api_id": "5", "api_name": "加法计算", "required_parameters": ["api_2的结果", "api_4的结果"], "rely_apis": ["2", "4"], "tool_name": "数值计算"}], "result": ["api_5的结果"]}',
        'cot':"""我们可以将该问题分解为以下几个步骤：
            1. 首先确定基金名称，query中的基金标准名应该是“国投瑞银锐意改革灵活配置混合型证券投资基金C类”；
            2. 根据基金名称查询基金的代码，调用 基金查询-代码(api_0) 获取基金代码；
            3. 有两次购买行为，问总共赚了多少钱，可以根据基金代码分别查询3个月和1个月的得出这两次购买基金的收益率，然后分别乘上相应的金额得出两次的收益，最后将二者相加即可：
                3.1 首先查询3个月的近期收益率，调用 基金查询-近期收益率(api_1) 获取最近三个月的收益率；
                3.2 调用 乘法计算(api_2)，将3个月的近期收益率乘以 5000 元，得出三个月前购买的这笔收益；
                3.3 再查询1个月的近期收益率，调用 基金查询-近期收益率(api_1) 获取最近一个月的收益率；
                3.4 调用 乘法计算(api_4)，将1个月的近期收益率乘以 1000 元，得出一个月前购买的这笔收益；
                3.5 调用 加法计算(api_5)，将三个月前购买的基金收益和一个月前购买的基金收益相加，得出总收益。
            4. 最终输出总收益，即 api_5 的结果。
            """,
        'glm3_answer': '{"relevant APIs": [{"api_id": "0", "api_name": "代码", "required_parameters": [["国投瑞银锐意改革灵活配置混合型证券投资基金C类"]], "rely_apis": [], "tool_name": "基金查询"}, {"api_id": "1", "api_name": "近期收益率", "required_parameters": ["api_0的结果", "3个月"], "rely_apis": ["0"], "tool_name": "基金查询"}, {"api_id": "2", "api_name": "乘法计算", "required_parameters": ["api_1的结果", "5000"], "rely_apis": ["1"], "tool_name": "数值计算"}, {"api_id": "3", "api_name": "近期收益率", "required_parameters": ["api_0的结果", "1个月"], "rely_apis": ["0"], "tool_name": "基金查询"}, {"api_id": "4", "api_name": "乘法计算", "required_parameters": ["api_3的结果", "1000"], "rely_apis": ["3"], "tool_name": "数值计算"}, {"api_id": "5", "api_name": "加法计算", "required_parameters": ["api_2的结果", "api_4的结果"], "rely_apis": ["2", "4"], "tool_name": "数值计算"}]',
        'correction':'基础模型给出的答案不正确，json格式不完整，没有result。'
    },
    'stockQuery':{
        'query':"""你现在是一个金融领域专家，你需要通过编排api来得到用户query的答案，输出json格式。query是：我打算用100万元买三羊马的股票，如果按照三羊马的最高价来计算，我能买多少股呢？\n        问题中提到的产品标准名可能是：三羊马、万马股份 等""",
        'answer':'{"relevant APIs": [{"api_id": "0", "api_name": "代码", "required_parameters": [["三羊马"]], "rely_apis": [], "tool_name": "股票查询"}, {"api_id": "1", "api_name": "最高价", "required_parameters": ["api_0的结果", "今日"], "rely_apis": ["0"], "tool_name": "股票查询"}, {"api_id": "2", "api_name": "除法计算", "required_parameters": ["1000000", "api_1的结果"], "rely_apis": ["1"], "tool_name": "数值计算"}], "result": ["api_2的结果"]}',
        'cot':"""对于该任务，我们可以分为以下步骤：
            1. 根据问题中提到的股票名称“三羊马”，我们需要将其转换为股票代码，以便后续查询；
            2. 调用 股票查询-代码(api_0) 获取“三羊马”的股票代码；
            3. 获取股票代码后，调用 股票查询-最高价(api_1) 获取今日“三羊马”的最高价；
            4. 根据问题，用户打算用100万元购买股票，我们需要计算在最高价下能购买多少股；
            5. 调用 数值计算-除法计算(api_2)，将100万元除以最高价，计算出能购买的股票数量；
            6. 最终输出能购买的股票数量，即 api_2 的结果。'}
            """,
        'glm3_answer':'{"relevant APIs": [{"api_id": "0", "api_name": "查询代码", "required_parameters": [["三羊马"]], "rely_apis": [], "tool_name": "股票查询"}, {"api_id": "1", "api_name": "查询最高价", "required_parameters": ["api_0的结果", "今日"], "rely_apis": ["0"], "tool_name": "股票查询"}, {"api_id": "2", "api_name": "除法计算", "required_parameters": ["1000000", "api_1的结果"], "rely_apis": ["1"], "tool_name": "数值计算"}, {"api_id": "3", "api_name": "乘法计算", "required_parameters": ["api_2的结果", "api_1的结果"], "rely_apis": ["1", "2"], "tool_name": "数值计算"}], "result": ["api_3的结果"]}',
        'correction':'基础模型给出的答案有误：用户问题要求给出能买多少股，在api_2调用后（总金额除以最高价）就已经得出了股数，不需要再做乘法计算。'
    },
    'fundSelect':{
        'query':"""你能帮我找找哪些基金今年的收益率超过了大盘，收益率是12.11%，而且它们是在2013年9月25日成立的吗？""",
        'answer':'{"relevant APIs": [{"api_id": "0", "tool_name": "条件选基", "api_name": "近期超大盘收益率", "required_parameters": ["等于", "0.1211", "今年来"], "rely_apis": []}, {"api_id": "1", "tool_name": "条件选基", "api_name": "成立年限", "required_parameters": ["等于", "20130925.0"], "rely_apis": []}, {"api_id": "2", "tool_name": "逻辑运算", "api_name": "与运算", "required_parameters": ["api_0的结果", "api_1的结果"], "rely_apis": ["0", "1"]}], "result": ["api_2的结果"]}',
        'cot':'''对于本任务，我们可以将该问题分为以下几个步骤：
            1. 问题提出了两个选基条件：今年的收益率超出大盘的收益率12.11%，以及基金是在2013年9月25日成立的；
            2. 根据第一个条件，调用 条件选基-近期超大盘收益率(api_0) 获取今年超出大盘收益率12.11%的基金名称列表；
            3. 根据第二个条件，调用 条件选基-成立年限(api_1) 获取成立日期等于2013年9月25日的基金名称列表；
            4. 最后，根据问题，需要同时满足以上两个条件，调用 逻辑运算-与运算(api_2) 将以上两个结果取交集，得到最终结果；
            5. 最终输出最终结果，即 api_2 的结果。''',
        'glm3_answer':'{"relevant APIs": [{"api_id": "0", "tool_name": "条件选基", "api_name": "近期收益率", "required_parameters": ["等于", "0.1211", "今年来"], "rely_apis": []}, {"api_id": "1", "tool_name": "条件选基", "api_name": "成立年限", "required_parameters": ["等于", "20130925.0"], "rely_apis": []}, {"api_id": "2", "tool_name": "逻辑运算", "api_name": "与运算", "required_parameters": ["api_0的结果", "api_1的结果"], "rely_apis": ["0", "1"]}], "result": ["api_2的结果"]}',
        'correction':'基础模型给出的答案有误：用户问题第一个条件是 今年的收益率超过大盘12.11%的基金，应当调用近期超大盘收益率，而不是近期收益率。'
    },
    'stockSelect':{
        'query':"""上个月的成交金额是将近2986亿吧，还有就是今天收盘时价格是27块84分的股票，我想知道都有哪些？""",
        'answer':'{"relevant APIs": [{"api_id": "0", "tool_name": "条件选股", "api_name": "成交额", "required_parameters": ["等于", "298600000000.00", "上月"], "rely_apis": []}, {"api_id": "1", "tool_name": "条件选股", "api_name": "收盘价", "required_parameters": ["等于", "27.84", "今日"], "rely_apis": []}, {"api_id": "2", "tool_name": "逻辑运算", "api_name": "与运算", "required_parameters": ["api_0的结果", "api_1的结果"], "rely_apis": ["0", "1"]}], "result": ["api_2的结果"]}',
        'cot':'''首先我们可以将该问题分解为以下几个步骤：
                1. query中提出了两个选股条件：上个月的成交金额是将近2986亿，今天收盘时价格是27块84分；
                2. 根据第一个条件，调用 条件选股-成交额(api_0) 获取上个月成交额 等于 2986亿 的股票代码列表；
                3. 根据第二个条件，调用 条件选股-收盘价(api_1) 获取今天收盘价 等于 27.84 的股票代码列表；
                4. 最后，根据问题，需要同时满足以上两个条件，调用 逻辑运算-与运算(api_2) 将以上两个结果取交集，得到最终结果;
                5. 最终输出最终结果，即 api_2 的结果。
        ''',
        'glm3_answer':'{"relevant APIs": [{"api_id": "0", "tool_name": "条件选股", "api_name": "成交额", "required_parameters": ["等于", "298600000000.00", "上月"], "rely_apis": []}, {"api_id": "1", "tool_name": "条件选股", "api_name": "收盘价", "required_parameters": ["等于", "27.84", "今日"], "rely_apis": []}, {"api_id": "2", "tool_name": "逻辑运算", "api_name": "与运算", "required_parameters": ["api_0的结果", "api_1的结果"], "rely_apis": ["0", "1"]}], "result": ["api_2的结果"]}',
        'correction':'基础模型给出的答案正确'
    },
    'common':{
        'query':"""假设三个月前我用了100000元买了日上，我一直没有卖，现在我手上的这股票相比三个月前涨了30%，那我现在手上总共有多少的资金""",
        'answer':'{"relevant APIs": [{"api_id": "0", "api_name": "加法计算", "required_parameters": ["30%", "100%"], "rely_apis": [], "tool_name": "数值计算"}, {"api_id": "1", "api_name": "乘法计算", "required_parameters": ["api_0的结果", "100000"], "rely_apis": ["0"], "tool_name": "数值计算"}], "result": ["api_2的结果"]}',
        'cot':'''用户投入的资金是100000元，现在涨了30%，需要现在计算总资金：
                1. 首先调用计算涨了30%后，现在总资金的相对值：调用 加法计算(api_0) 将 100% 加上30% 的涨幅，得到现在的总资金的相对值;
                2. 再调用 乘法计算(api_1) 将 api_0输出的相对值 乘以100000元，得到现在真实的总资金；
                3. 最终输出最终结果，即 api_1 的结果。''',
        'glm3_answer':'{"relevant APIs": [{"api_id": "0", "api_name": "加法计算", "required_parameters": ["30%", "100%"], "rely_apis": [], "tool_name": "数值计算"}, {"api_id": "1", "api_name": "乘法计算", "required_parameters": ["api_0的结果", "100000"], "rely_apis": ["0"], "tool_name": "数值计算"}], "result": ["api_2的结果"]}',
        'correction':'基础模型给出的答案正确'
    }
}


cot_generate_prompt = '''
<任务>
    <TASK>
    API描述：
        所有可用的api名称：
            <API_DESC>
    <TIPS>
</任务>

<示例>
    问题：
        query是：<QUERY_DEMO>
        标准答案是：<ANSWER_DEMO>
    回答：
        思考过程：
            <COT_DEMO>
</示例>

接下来是你需要回答的问题
问题：
    query是：<QUERY>
    标准答案是：<ANSWER>
回答：
    思考过程：
'''
cot_generate_fund_query_prompt = (cot_generate_prompt.replace('<TASK>', task_cot_generate)
                                    .replace('<API_DESC>', fundQuery_api_description)
                                    .replace('<TIPS>', fund_tips)
                                    .replace('<QUERY_DEMO>', examples['fundQuery']['query'])
                                    .replace('<ANSWER_DEMO>', examples['fundQuery']['answer'])
                                    .replace('<COT_DEMO>', examples['fundQuery']['cot']))
cot_generate_fund_select_prompt = (cot_generate_prompt.replace('<TASK>', task_cot_generate)
                                    .replace('<API_DESC>', fundSelect_api_description)
                                    .replace('<TIPS>', fund_tips)
                                    .replace('<QUERY_DEMO>', examples['fundSelect']['query'])
                                    .replace('<ANSWER_DEMO>', examples['fundSelect']['answer'])
                                    .replace('<COT_DEMO>', examples['fundSelect']['cot']))
cot_generate_stock_query_prompt = (cot_generate_prompt.replace('<TASK>', task_cot_generate)
                                    .replace('<API_DESC>', stockQuery_api_description)
                                    .replace('<TIPS>', stock_tips)
                                    .replace('<QUERY_DEMO>', examples['stockQuery']['query'])
                                    .replace('<ANSWER_DEMO>', examples['stockQuery']['answer'])
                                    .replace('<COT_DEMO>', examples['stockQuery']['cot']))
cot_generate_stock_select_prompt = (cot_generate_prompt.replace('<TASK>', task_cot_generate)
                                    .replace('<API_DESC>', stockSelect_api_description)
                                    .replace('<TIPS>', stock_tips)
                                    .replace('<QUERY_DEMO>', examples['stockSelect']['query'])
                                    .replace('<ANSWER_DEMO>', examples['stockSelect']['answer'])
                                    .replace('<COT_DEMO>', examples['stockSelect']['cot']))
cot_generate_common_prompt = (cot_generate_prompt.replace('<TASK>', task_cot_generate)
                                    .replace('<API_DESC>', common_api_description)
                                    .replace('<TIPS>', '')
                                    .replace('<QUERY_DEMO>', examples['common']['query'])
                                    .replace('<ANSWER_DEMO>', examples['common']['answer'])
                                    .replace('<COT_DEMO>', examples['common']['cot']))

cot_inference_prompt = '''
<任务>
    <TASK>
    API描述：
        所有可用的api名称：
            <API_DESC>
    <TIPS>
    <STANDARD_FORMAT>
</任务>

<示例>
    <query>
        <QUERY_DEMO>
        <GLM3_ANSWER_DEMO>
    </query>
    <output>
        思考过程：
            <COT_DEMO>
        于是最终的json格式标准结果为:
            <ANSWER_DEMO>
    </output>
</示例>

<query>
    <QUERY>
    <GLM3_ANSWER>
</query>
'''
fund_query_prompt = (cot_inference_prompt.replace('<TASK>', task_inference)
                                    .replace('<API_DESC>', fundQuery_api_description)
                                    .replace('<TIPS>', fund_tips)
                                    .replace('<STANDARD_FORMAT>', standard_json_format)
                                    .replace('<QUERY_DEMO>', examples['fundQuery']['query'])
                                    .replace('<ANSWER_DEMO>', examples['fundQuery']['answer'])
                                    .replace('<COT_DEMO>', examples['fundQuery']['cot']))
fund_select_prompt = (cot_inference_prompt.replace('<TASK>', task_inference)
                                    .replace('<API_DESC>', fundSelect_api_description)
                                    .replace('<TIPS>', fund_tips)
                                    .replace('<STANDARD_FORMAT>', standard_json_format)
                                    .replace('<QUERY_DEMO>', examples['fundSelect']['query'])
                                    .replace('<ANSWER_DEMO>', examples['fundSelect']['answer'])
                                    .replace('<COT_DEMO>', examples['fundSelect']['cot']))
stock_query_prompt = (cot_inference_prompt.replace('<TASK>', task_inference)
                                    .replace('<API_DESC>', stockQuery_api_description)
                                    .replace('<TIPS>', stock_tips)
                                    .replace('<STANDARD_FORMAT>', standard_json_format)
                                    .replace('<QUERY_DEMO>', examples['stockQuery']['query'])
                                    .replace('<ANSWER_DEMO>', examples['stockQuery']['answer'])
                                    .replace('<COT_DEMO>', examples['stockQuery']['cot']))
stock_select_prompt = (cot_inference_prompt.replace('<TASK>', task_inference)
                                    .replace('<API_DESC>', stockSelect_api_description)
                                    .replace('<TIPS>', stock_tips)
                                    .replace('<STANDARD_FORMAT>', standard_json_format)
                                    .replace('<QUERY_DEMO>', examples['stockSelect']['query'])
                                    .replace('<ANSWER_DEMO>', examples['stockSelect']['answer'])
                                    .replace('<COT_DEMO>', examples['stockSelect']['cot']))
common_prompt = (cot_inference_prompt.replace('<TASK>', task_inference)
                                    .replace('<API_DESC>', common_api_description)
                                    .replace('<TIPS>', '')
                                    .replace('<STANDARD_FORMAT>', standard_json_format)
                                    .replace('<QUERY_DEMO>', examples['common']['query'])
                                    .replace('<ANSWER_DEMO>', examples['common']['answer'])
                                    .replace('<COT_DEMO>', examples['common']['cot']))

fund_query_prompt_with_correct = (fund_query_prompt.replace('<GLM3_ANSWER_DEMO>','基础模型答案是：'+examples['fundQuery']['glm3_answer'])
                                  .replace(task_inference,task_inference_with_correct))
fund_select_prompt_with_correct = (fund_select_prompt.replace('<GLM3_ANSWER_DEMO>','基础模型答案是：'+examples['fundSelect']['glm3_answer'])
                                   .replace(task_inference,task_inference_with_correct))
stock_query_prompt_with_correct = (stock_query_prompt.replace('<GLM3_ANSWER_DEMO>','基础模型答案是：'+examples['stockQuery']['glm3_answer'])
                                   .replace(task_inference,task_inference_with_correct))
stock_select_prompt_with_correct = (stock_select_prompt.replace('<GLM3_ANSWER_DEMO>','基础模型答案是：'+examples['stockSelect']['glm3_answer'])
                                    .replace(task_inference,task_inference_with_correct))
common_prompt_with_correct = (common_prompt.replace('<GLM3_ANSWER_DEMO>','基础模型答案是：'+examples['common']['glm3_answer'])
                              .replace(task_inference,task_inference_with_correct))

fund_query_prompt = fund_query_prompt.replace('<GLM3_ANSWER_DEMO>','').replace('<GLM3_ANSWER>','')
fund_select_prompt = fund_select_prompt.replace('<GLM3_ANSWER_DEMO>','').replace('<GLM3_ANSWER>','')
stock_query_prompt = stock_query_prompt.replace('<GLM3_ANSWER_DEMO>','').replace('<GLM3_ANSWER>','')
stock_select_prompt = stock_select_prompt.replace('<GLM3_ANSWER_DEMO>','').replace('<GLM3_ANSWER>','')
common_prompt = common_prompt.replace('<GLM3_ANSWER_DEMO>','').replace('<GLM3_ANSWER>','')
