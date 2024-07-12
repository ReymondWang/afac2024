## 新发现
无复合问题，四类问题分界清晰, 极个别问题只需要通用api(7/5460 3/1092)

| n | query | api_list | api_num | category |
| - | ----- | -------- | ------- | -------- |
|147|	    我十年前一次性投入了1万块钱买了金鹰信息产业A，并且每年增加千元的投资，现在总共投入了多少钱？|	[(数值计算, 乘法计算), (数值计算, 加法计算)]	| 2	api_1	| 0  |
|953|	    我想知道如果1年前用2000元买了华宝成长基金，然后每个月再定投500元，现在一共投入了多少钱	|[(数值计算, 乘法计算), (数值计算, 加法计算)]	| 2	api_1	| 0 |
|1929|	我今天花20000买了招商招旭D，而且我知道其申购费率为2%，我现在想知道我真正投入的购买本金是多少？	|[(数值计算, 乘法计算), (数值计算, 加法计算)]	| 2	api_1	| 0 |
|2385|	我5年前一次性买入1000块汇丰晋信丰盈C基金，然后定期每半年再买500块，我现在总共投入了多少钱	|[(数值计算, 乘法计算), (数值计算, 乘法计算), (数值计算, 加法计算)]	| 3	api_2	| 0 |
|4248|	我如果1年前用500块买广发东财大数据A，之后每月定投200块，到现在为止我总共投入了多少钱	|[(数值计算, 乘法计算), (数值计算, 加法计算)]	| 2	api_1	| 0 |
|4660|	我准备通过一次性投资和定期投资相结合的方式购买创金合信专精特新A，一次性投入5000元，然后每个月定投500元，那么一年后我的投入总额是多少？|	[(数值计算, 乘法计算), (数值计算, 加法计算)]	| 2	api_1	| 0 |
|5451|	如果我5年前用1000块买建信新兴市场C，并且每年投入1000块，那么现在我总共投入了多少钱？	|[(数值计算, 乘法计算), (数值计算, 加法计算)]	| 2	api_1	| 0 |


### 思路
    先训练一个小模型，应该可以高概率准确分类，在每一类中 
        a. Cot learning with GLM-4
        b. 多个 ChatGLM3 全参数

---
## 已完成
- product名字召回概况分析 `data_process/训练集生成.ipynb`
    
    | 召回百分比  | 召回截止数 |
    | --------  | -------- |
    |   75%     |   2      |
    |   90%     |  10      |
    |   95%     |  20      |
    |   99%     |  41      |
    |   99.9%   |  47      |
    |   max     |  49      |

- 前处理：将label 中的 api_name 统一化：
    - 去掉 `查询`
    - 对齐（先对比train中的数据）
        - 条件选基中：基金份额类型(A、B、C) => 基金份额类型
        - 股票查询中：增加 银行资本充足率
        - 条件选股中：查询每股经营性现资金流 => 查询每股经营性现金流
- 利用DeepSeekV2(性价比最高)基于原始Prompt+Label+背景+FewShot,生成CoT
    - 用到的prompt为 `prompt.py` 中的 **cot_prompt**
- 训练基生成
    - prompt采用 `prompt.py` 中的 **cot_prompt_train**
    - lable使用上一步得到的CoT+原始label
---
## TODO
- 后处理
    - 拼接思考过程与json
    - 对齐回退

