'''
生成纠错训练集和测试集，基于 5460 个训练集数据分割
依赖：err_index.csv true_index.csv train_correct.jsonl
生成：
'''
import random
import pandas as pd
import json

# 错误样本索引 1102
err_index = set(pd.read_csv('err_index.csv').n.tolist())
# 正确样本索引 4358
true_index = pd.read_csv('true_index.csv').n.tolist()
# 乱序
random.shuffle(true_index)
true_index1 = set(true_index[:1102]) # 1
true_index2 = set(true_index[1102:3306]) # 2
true_index3 = set(true_index[3306:]) # 3

# 索引数小于1000，放入dev_c.jsonl
# 索引数大于1000，放入train_c集
with open('train_correct.jsonl', 'r', encoding='utf-8') as f:
    for i,line in enumerate(f):
        if i < 1000:
            with open('dev_c.jsonl', 'a', encoding='utf-8') as f1:
                f1.write(line)
        else:
            if i in err_index:
                with open('train_c1.jsonl', 'a', encoding='utf-8') as f1:
                    f1.write(line)
                with open('train_c2.jsonl', 'a', encoding='utf-8') as f2:
                    f2.write(line)
                with open('train_c3.jsonl', 'a', encoding='utf-8') as f3:
                    f3.write(line)
            else:
                if i in true_index1:
                    with open('train_c1.jsonl', 'a', encoding='utf-8') as f1:
                        f1.write(line)
                elif i in true_index2:
                    with open('train_c2.jsonl', 'a', encoding='utf-8') as f2:
                        f2.write(line)
                else:
                    with open('train_c3.jsonl', 'a', encoding='utf-8') as f3:
                        f3.write(line)


# 合并 train_c1.jsonl train_c2.jsonl train_c3.jsonl
with open('train_c.jsonl', 'w', encoding='utf-8') as f:
    with open('train_c1.jsonl', 'r', encoding='utf-8') as f1:
        for line in f1:
            f.write(line)
    with open('train_c2.jsonl', 'r', encoding='utf-8') as f2:
        for line in f2:
            f.write(line)
    with open('train_c3.jsonl', 'r', encoding='utf-8') as f3:
        for line in f3:
            f.write(line)