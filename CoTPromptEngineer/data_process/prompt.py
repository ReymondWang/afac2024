cot_prompt = '''
以下是业务背景
<背景>
    你现在是一个金融领域专家。我们计划做一个智能查询系统，系统中有一系列原子化api，系统负责在接收用户的提问后，通过一系列的api调用生成答案。目前我们人工收集了一些列问题和json格式标准答案（该答案包括：1. 问题对应的api调用链，2.需要输出的结果），目前苦恼于从问题到标准答案的思维链逻辑不是很清晰。希望你借助金融知识和自身强大的理解力，结合问题和标准答案，给出由问题一步步得到该答案的一个完整思考过程(注意：输出的思考过程本身不应包含对标准答案的解读（如：不应出现“根据提供的标准答案”等类似的字眼），因为逻辑上来说，先有思考过程后有答案)。

    API描述：
        所有原子化api共有基金、股票、通用三个大类（category_name）,其中基金和股票大类下分别有基金查询、条件选基和股票查询、条件选股四个小类（tool_name）,通用大类下有数值计算、逻辑运算两个小类。每个小类下有多个api，每个api有特定的输入和输出。以下是各小类中所有可用的api及简要说明：
        基金查询：(查询某基金的以下指标)
            api有：
                代码,类型,规模,晨星评级,蚂蚁评级,申购费率,成立年限,开放类型,申购状态,蚂蚁金选标识,风险等级,基金经理类型,基金经理,基金公司,
                基金经理从业年限,基金经理管理规模,基金经理年化回报率,持股估值,持股集中度,持股热门度,持股换手率,机构占比,单一持有人占比,
                重仓股票,重仓行业,持仓风格,基金公司是否自购,是否可投沪港深,近一年买入持有6个月历史盈利概率,近3年买入持有1年历史盈利概率,
                近5年买入持有1年历史盈利概率,近期收益率,近期收益率同类排名,近期年化收益率,近期年化收益率同类排名,近期超大盘收益率,近期创新高次数,
                近期最大回撤,近期最大回撤同类排名,近期波动率同类排名,近期最长解套天数,近期跟踪误差,近期夏普比率同类排名,近期卡玛比率同类排名,
                近期信息比率同类排名,年度收益率,近期指数增强,年度最大回撤,基金事后分类,基金资产打分,基金募集类型,投组区域,基金份额类型,
                申购最小起购金额,分红方式,赎回状态,是否支持定投,单位净值同步日期,单位净值,基金经理任职期限,近期夏普率,
                投资市场,板块,行业,聚类行业,管理费率,销售服务费率,托管费率,认购费率,赎回费率,分红年度,权益登记日,除息日,派息日,红利再投日,每十份收益单位派息（元）
            说明：
                1. 名称为“代码”的api，输入基金名称，返回基金代码；
                2. 其他api名称为指标名称，参数为基金代码（个别带有"近期","年度"关键字的api有第二参数：时间），返回相应指标值。
        条件选基：(根据以下指标选择基金，返回基金代码列表)
            api与基金查询类api名称相同（一一对应）
            说明：
                1. 本类中名称为“代码”的api，输入基金代码，查询该基金详细信息;
                2. 其余api输入运算符（如“>” “<” “=” "包括"等）和指标（如“规模”），输出符合该指标对应条件的基金列表。
                3. 类似，个别带有"近期","年度"关键字的api有第三参数：时间。
        股票查询：
            api有：
                代码,开盘价,最高价,最低价,当前价,收盘价,成交量,成交额,涨停价,跌停价,涨跌额,涨跌幅,主力资金流入,主力资金流出,主力资金净流入,总流入,总流出,
                换手率,每股收益,静态市盈率,总市值,振幅,流通市值,每股收益ttm,市盈率ttm,净资产收益率,每股净资产,每股经营性现金流,毛利率,净利率,净利润,
                净利润同比增长,营业收入,营收同比增长,投资收入,营业利润,营业利润同比增长,扣非净利润,流动资产,总资产,短期负债,总负债,股东权益,净经营性现金流,净投资性现金流,净融资性现金流,银行资本充足率,流通股本,总股本,高管名称
            说明：
                类比与基金查询类api。其中第一行除了"代码"以外的api，都支持第二参数：时间。
        条件选股类：
            api与股票查询类api名称相同（一一对应），说明类比条件选基。
        数值计算类(4个)：
            加法计算,减法计算,乘法计算,除法计算
        逻辑运算类(2个)：
            与运算,或运算

    query特点：
        每个query主要分为四类，分别是基金查询、条件选基、股票查询、条件选股，每个query用到的api仅限于本类中api和通用api。 另外有极个别的问题（主要是简单的投入金额计算）不属于这四类，只用到了通用api。

    行业背景知识&Tips（可以辅助你分析解决问题）：
        1. 基金规模和基金经理管理规模是两个不同的概念，基金规模是指某一支基金的规模，而基金经理管理规模是指某个基金经理管理的基金规模。
        2. 基金申购指购买已经发行的基金份额，认购指初次发行的基金。
        3. 基金中的主要费用包括：
            申购时有申购费，持有期间有基金管理费，赎回时有赎回费(因持有时长不同，费率不同),其他还有销售服务费等
            注意：金额*相关费率=相关费用（!注意乘数是金额而不是份额，给出份额时应通过份额*净值计算出金额） 
        4. 通过名称区分股票和基金Tips:
            包含 "单位净值" "C"  "ETF" "LOF" "夏普" "最大回撤" 等字眼多是基金类问题
            包含"开盘价" "收盘价" "市值" "资金流向" "市盈率" "营业"等多是股票类问题
            不好区分股票还是基金时，如果 只有两三个字，一般是股票，如果描述有很多字（超过四个），一般是基金； 也可以结合query和上面的api判断，有些指标只有基金有，有些只有股票有。
        5. 如无特殊说明，计算收益(率)统一使用收盘价计算
        6. 涉及到市盈率，一般指的是静态市盈率；动态市盈率指的是市盈率ttm
        7. 注意区分价值与成本，当前的价值是当前的价格*份额，成本是（购买时的价格*份额-费用）
        8. 当用户给出某个基金产品或股票名称时，第一步要首先把它转化成代码，然后再进行后续操作，因为我们的其他api都只能根据代码去查而不是名称。
        9. 只能选用上文中"所有可用的api"中的api，不能捏造；
        2. 切题，避免无关的api调用（比如问基金经理管理规模就不要查询基金规模了）。
</背景>

以下是一些简单示例，帮助你更好得理解和解决问题
<示例>
示例1(基金查询)：
    问题：
        query是：我如果3个月前用5000块买了国投瑞银锐意改革C，然后又在1个月前购买了1000块，那么我现在总共赚了多少钱呢？ 问题中提到的产品标准名可能是：国投瑞银锐意改革灵活配置混合型证券投资基金C类、国投瑞银锐意改革灵活配置混合型证券投资基金A类、国投瑞银瑞福深证100指数分级证券投资基金、国投瑞银瑞福深证100指数证券投资基金(LOF)、国投瑞银瑞福深证100指数分级证券投资基金之进取级基金份额、国投瑞银瑞福深证100指数分级证券投资基金之优先级基金份额、国投瑞银瑞和沪深300指数分级证券投资基金
        标准答案是：{"relevant APIs": [{"api_id": "0", "api_name": "代码", "required_parameters": [["国投瑞银锐意改革灵活配置混合型证券投资基金C类"]], "rely_apis": [], "tool_name": "基金查询"}, {"api_id": "1", "api_name": "近期收益率", "required_parameters": ["api_0的结果", "3个月"], "rely_apis": ["0"], "tool_name": "基金查询"}, {"api_id": "2", "api_name": "乘法计算", "required_parameters": ["api_1的结果", "5000"], "rely_apis": ["1"], "tool_name": "数值计算"}, {"api_id": "3", "api_name": "近期收益率", "required_parameters": ["api_0的结果", "1个月"], "rely_apis": ["0"], "tool_name": "基金查询"}, {"api_id": "4", "api_name": "乘法计算", "required_parameters": ["api_3的结果", "1000"], "rely_apis": ["3"], "tool_name": "数值计算"}, {"api_id": "5", "api_name": "加法计算", "required_parameters": ["api_2的结果", "api_4的结果"], "rely_apis": ["2", "4"], "tool_name": "数值计算"}], "result": ["api_5的结果"]}
    回答：
        思考过程：
            首先可以确定这是一个基金查询类任务，我们可以将该问题分解为以下几个步骤：
                1. 首先确定基金名称，query中的基金标准名应该是“国投瑞银锐意改革灵活配置混合型证券投资基金C类”；
                2. 根据基金名称查询基金的代码，调用 基金查询-代码(api_0) 获取基金代码;
                3. 有两次购买行为，问总共赚了多少钱，可以根据基金代码分别查询3个月和1个月的得出这两次购买基金的收益率，然后分别乘上相应的金额得出两次的收益，最后将二者相加即可。
                    3.1 首先查询3个月的近期收益率，调用 基金查询-近期收益率(api_1) 获取最近三个月的收益率;
                    3.2 调用 乘法计算(api_2)，将3个月的近期收益率乘以 5000 元，得出三个月前购买的这笔收益;
                    3.3 再查询1个月的近期收益率，调用 基金查询-近期收益率(api_1) 获取最近一个月的收益率;
                    3.4 调用 乘法计算(api_4)，将1个月的近期收益率乘以 1000 元，得出一个月前购买的这笔收益;
                    3.5 调用 加法计算(api_5)，将三个月前购买的基金收益和一个月前购买的基金收益相加，得出总收益;
                4. 最终输出总收益，即 api_5 的结果。
                
示例2(条件选股)：
    问题：
        query是：上个月的成交金额是将近2986亿吧，还有就是今天收盘时价格是27块84分的股票，我想知道都有哪些？问题中提到的产品标准名可能是：富达传承6个月持有期股票型证券投资基金C类、富达传承6个月持有期股票型证券投资基金A类、大成睿裕六个月持有期股票型证券投资基金C类、大成睿裕六个月持有期股票型证券投资基金A类、中泰研究精选6个月持有期股票型证券投资基金C类、中泰研究精选6个月持有期股票型证券投资基金A类、招商科技动力3个月滚动持有股票型证券投资基金C类、招商科技动力3个月滚动持有股票型证券投资基金A类、中航量化阿尔法六个月持有期股票型证券投资基金C类、中航量化阿尔法六个月持有期股票型证券投资基金A类,
        标准答案是：{"relevant APIs": [{"api_id": "0", "tool_name": "条件选股", "api_name": "成交额", "required_parameters": ["等于", "2986156499.47", "上月"], "rely_apis": []}, {"api_id": "1", "tool_name": "条件选股", "api_name": "收盘价", "required_parameters": ["等于", "27.84", "今日"], "rely_apis": []}, {"api_id": "2", "tool_name": "逻辑运算", "api_name": "与运算", "required_parameters": ["api_0的结果", "api_1的结果"], "rely_apis": ["0", "1"]}], "result": ["api_2的结果"]}
    回答：
        思考过程:
            首先可以确定这是一个条件选股类任务，我们可以将该问题分解为以下几个步骤：
                1. query中提出了两个选股条件：上个月的成交金额是将近2986亿，今天收盘时价格是27块84分；
                2. 根据第一个条件，调用 条件选股-成交额(api_0) 获取上个月成交额 等于 2986亿 的股票代码列表;
                3. 根据第二个条件，调用 条件选股-收盘价(api_1) 获取今天收盘价 等于 27.84 的股票代码列表;
                4. 最后，根据问题，需要同时满足以上两个条件，调用 逻辑运算-与运算(api_2) 将以上两个结果取交集，得到最终结果;
                5. 最终输出最终结果，即 api_2 的结果。
</示例>

接下来是你需要完成的任务
<任务>
    问题：
        query是：<QUERY>
        标准答案是：<LABEL>
    回答：
        思考过程：
'''

cot_prompt_train = '''
以下是业务背景
<背景>
    你现在是一个金融领域专家。我们有一个查询系统，系统中有一系列原子化api，你负责在接收用户的提问后，通过详细分析问题，编排api来得到用户query的答案，为了保证逻辑的严谨性，你需要将问题一步步拆解，写出思考过程，最后给出json格式的标准答案。

    API描述：
        所有原子化api共有基金、股票、通用三个大类（category_name）,其中基金和股票大类下分别有基金查询、条件选基和股票查询、条件选股四个小类（tool_name）,通用大类下有数值计算、逻辑运算两个小类。每个小类下有多个api，每个api有特定的输入和输出。以下是各小类中所有可用的api及简要说明：
        基金查询：(查询某基金的以下指标)
            api有：
                代码,类型,规模,晨星评级,蚂蚁评级,申购费率,成立年限,开放类型,申购状态,蚂蚁金选标识,风险等级,基金经理类型,基金经理,基金公司,
                基金经理从业年限,基金经理管理规模,基金经理年化回报率,持股估值,持股集中度,持股热门度,持股换手率,机构占比,单一持有人占比,
                重仓股票,重仓行业,持仓风格,基金公司是否自购,是否可投沪港深,近一年买入持有6个月历史盈利概率,近3年买入持有1年历史盈利概率,
                近5年买入持有1年历史盈利概率,近期收益率,近期收益率同类排名,近期年化收益率,近期年化收益率同类排名,近期超大盘收益率,近期创新高次数,
                近期最大回撤,近期最大回撤同类排名,近期波动率同类排名,近期最长解套天数,近期跟踪误差,近期夏普比率同类排名,近期卡玛比率同类排名,
                近期信息比率同类排名,年度收益率,近期指数增强,年度最大回撤,基金事后分类,基金资产打分,基金募集类型,投组区域,基金份额类型,
                申购最小起购金额,分红方式,赎回状态,是否支持定投,单位净值同步日期,单位净值,基金经理任职期限,近期夏普率,
                投资市场,板块,行业,聚类行业,管理费率,销售服务费率,托管费率,认购费率,赎回费率,分红年度,权益登记日,除息日,派息日,红利再投日,每十份收益单位派息（元）
            说明：
                1. 名称为“代码”的api，输入基金名称，返回基金代码；
                2. 其他api名称为指标名称，参数为基金代码（个别带有"近期","年度"关键字的api有第二参数：时间），返回相应指标值。
        条件选基：(根据以下指标选择基金，返回基金代码列表)
            api与基金查询类api名称相同（一一对应）
            说明：
                1. 本类中名称为“代码”的api，输入基金代码，查询该基金详细信息;
                2. 其余api输入运算符（如“>” “<” “=” "包括"等）和指标（如“规模”），输出符合该指标对应条件的基金列表。
                3. 类似，个别带有"近期","年度"关键字的api有第三参数：时间。
        股票查询：
            api有：
                代码,开盘价,最高价,最低价,当前价,收盘价,成交量,成交额,涨停价,跌停价,涨跌额,涨跌幅,主力资金流入,主力资金流出,主力资金净流入,总流入,总流出,
                换手率,每股收益,静态市盈率,总市值,振幅,流通市值,每股收益ttm,市盈率ttm,净资产收益率,每股净资产,每股经营性现金流,毛利率,净利率,净利润,
                净利润同比增长,营业收入,营收同比增长,投资收入,营业利润,营业利润同比增长,扣非净利润,流动资产,总资产,短期负债,总负债,股东权益,净经营性现金流,净投资性现金流,净融资性现金流,银行资本充足率,流通股本,总股本,高管名称
            说明：
                类比与基金查询类api。其中第一行除了"代码"以外的api，都支持第二参数：时间。
        条件选股类：
            api与股票查询类api名称相同（一一对应），说明类比条件选基。
        数值计算类(4个)：
            加法计算,减法计算,乘法计算,除法计算
        逻辑运算类(2个)：
            与运算,或运算

    query特点：
        每个query主要分为四类，分别是基金查询、条件选基、股票查询、条件选股，每个query用到的api仅限于本类中api和通用api。 另外有极个别的问题（主要是简单的投入金额计算）不属于这四类，只用到了通用api。

    行业背景知识&Tips（可以辅助你分析解决问题）：
        1. 基金规模和基金经理管理规模是两个不同的概念，基金规模是指某一支基金的规模，而基金经理管理规模是指某个基金经理管理的基金规模。
        2. 基金申购指购买已经发行的基金份额，认购指初次发行的基金。
        3. 基金中的主要费用包括：
            申购时有申购费，持有期间有基金管理费，赎回时有赎回费(因持有时长不同，费率不同),其他还有销售服务费等
            注意：金额*相关费率=相关费用（!注意乘数是金额而不是份额，给出份额时应通过份额*净值计算出金额） 
        4. 通过名称区分股票和基金Tips:
            包含 "单位净值" "C"  "ETF" "LOF" "夏普" "最大回撤" 等字眼多是基金类问题
            包含"开盘价" "收盘价" "市值" "资金流向" "市盈率" "营业"等多是股票类问题
            不好区分股票还是基金时，如果 只有两三个字，一般是股票，如果描述有很多字（超过四个），一般是基金； 也可以结合query和上面的api判断，有些指标只有基金有，有些只有股票有。
        5. 如无特殊说明，计算收益(率)统一使用收盘价计算
        6. 涉及到市盈率，一般指的是静态市盈率；动态市盈率指的是市盈率ttm
        7. 注意区分价值与成本，当前的价值是当前的价格*份额，成本是（购买时的价格*份额-费用）
        8. 当用户给出某个基金产品或股票名称时，第一步要首先把它转化成代码，然后再进行后续操作，因为我们的其他api都只能根据代码去查而不是名称。
        9. 只能选用上文中"所有可用的api"中的api，不能捏造；
        2. 切题，避免无关的api调用（比如问基金经理管理规模就不要查询基金规模了）。
</背景>

<示例>
示例1(基金查询)：
    问题：
        query是：我如果3个月前用5000块买了国投瑞银锐意改革C，然后又在1个月前购买了1000块，那么我现在总共赚了多少钱呢？ 问题中提到的产品标准名可能是：国投瑞银锐意改革灵活配置混合型证券投资基金C类、国投瑞银锐意改革灵活配置混合型证券投资基金A类、国投瑞银瑞福深证100指数分级证券投资基金、国投瑞银瑞福深证100指数证券投资基金(LOF)、国投瑞银瑞福深证100指数分级证券投资基金之进取级基金份额、国投瑞银瑞福深证100指数分级证券投资基金之优先级基金份额、国投瑞银瑞和沪深300指数分级证券投资基金
    回答：
        思考过程：
            首先可以确定这是一个基金查询类任务，我们可以将该问题分解为以下几个步骤：
                1. 首先确定基金名称，query中的基金标准名应该是“国投瑞银锐意改革灵活配置混合型证券投资基金C类”；
                2. 根据基金名称查询基金的代码，调用 基金查询-代码(api_0) 获取基金代码;
                3. 有两次购买行为，问总共赚了多少钱，可以根据基金代码分别查询3个月和1个月的得出这两次购买基金的收益率，然后分别乘上相应的金额得出两次的收益，最后将二者相加即可。
                    3.1 首先查询3个月的近期收益率，调用 基金查询-近期收益率(api_1) 获取最近三个月的收益率;
                    3.2 调用 乘法计算(api_2)，将3个月的近期收益率乘以 5000 元，得出三个月前购买的这笔收益;
                    3.3 再查询1个月的近期收益率，调用 基金查询-近期收益率(api_1) 获取最近一个月的收益率;
                    3.4 调用 乘法计算(api_4)，将1个月的近期收益率乘以 1000 元，得出一个月前购买的这笔收益;
                    3.5 调用 加法计算(api_5)，将三个月前购买的基金收益和一个月前购买的基金收益相加，得出总收益;
                4. 最终输出总收益，即 api_5 的结果。
        于是最终的json格式标准结果为:
            {"relevant APIs": [{"api_id": "0", "api_name": "代码", "required_parameters": [["国投瑞银锐意改革灵活配置混合型证券投资基金C类"]], "rely_apis": [], "tool_name": "基金查询"}, {"api_id": "1", "api_name": "近期收益率", "required_parameters": ["api_0的结果", "3个月"], "rely_apis": ["0"], "tool_name": "基金查询"}, {"api_id": "2", "api_name": "乘法计算", "required_parameters": ["api_1的结果", "5000"], "rely_apis": ["1"], "tool_name": "数值计算"}, {"api_id": "3", "api_name": "近期收益率", "required_parameters": ["api_0的结果", "1个月"], "rely_apis": ["0"], "tool_name": "基金查询"}, {"api_id": "4", "api_name": "乘法计算", "required_parameters": ["api_3的结果", "1000"], "rely_apis": ["3"], "tool_name": "数值计算"}, {"api_id": "5", "api_name": "加法计算", "required_parameters": ["api_2的结果", "api_4的结果"], "rely_apis": ["2", "4"], "tool_name": "数值计算"}], "result": ["api_5的结果"]}
                
示例2(条件选股)：
    问题：
        query是：上个月的成交金额是将近2986亿吧，还有就是今天收盘时价格是27块84分的股票，我想知道都有哪些？问题中提到的产品标准名可能是：富达传承6个月持有期股票型证券投资基金C类、富达传承6个月持有期股票型证券投资基金A类、大成睿裕六个月持有期股票型证券投资基金C类、大成睿裕六个月持有期股票型证券投资基金A类、中泰研究精选6个月持有期股票型证券投资基金C类、中泰研究精选6个月持有期股票型证券投资基金A类、招商科技动力3个月滚动持有股票型证券投资基金C类、招商科技动力3个月滚动持有股票型证券投资基金A类、中航量化阿尔法六个月持有期股票型证券投资基金C类、中航量化阿尔法六个月持有期股票型证券投资基金A类,
    回答：
        思考过程:
            首先可以确定这是一个条件选股类任务，我们可以将该问题分解为以下几个步骤：
                1. query中提出了两个选股条件：上个月的成交金额是将近2986亿，今天收盘时价格是27块84分；
                2. 根据第一个条件，调用 条件选股-成交额(api_0) 获取上个月成交额 等于 2986亿 的股票代码列表;
                3. 根据第二个条件，调用 条件选股-收盘价(api_1) 获取今天收盘价 等于 27.84 的股票代码列表;
                4. 最后，根据问题，需要同时满足以上两个条件，调用 逻辑运算-与运算(api_2) 将以上两个结果取交集，得到最终结果;
                5. 最终输出最终结果，即 api_2 的结果。
        于是最终标准的json格式结果为:
            {"relevant APIs": [{"api_id": "0", "tool_name": "条件选股", "api_name": "成交额", "required_parameters": ["等于", "2986156499.47", "上月"], "rely_apis": []}, {"api_id": "1", "tool_name": "条件选股", "api_name": "收盘价", "required_parameters": ["等于", "27.84", "今日"], "rely_apis": []}, {"api_id": "2", "tool_name": "逻辑运算", "api_name": "与运算", "required_parameters": ["api_0的结果", "api_1的结果"], "rely_apis": ["0", "1"]}], "result": ["api_2的结果"]}
</示例>

接下来是你需要完成的任务
<任务>
    问题：
        query是：<QUERY>
    回答：
        思考过程：
            （参考示例格式给出思考过程）
        于是最终标准的json格式是结果为：
            （json格式结果）
'''