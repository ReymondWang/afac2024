import pandas as pd
from numpy.random import choice
from prompt import cot_prompt

import os; print(os.getcwd())
train_df = pd.read_csv('../data/data4cot/train_cot.csv')

n = 100
sample = choice(train_df.index, n, replace=False)
for i in sample:
    query = train_df.loc[i, 'query_with_products']
    label = train_df.loc[i, 'label']
    prompt = cot_prompt.replace('<QUERY>', query).replace('<LABEL>', label)
    with open(f'samples/{i}.txt', 'w') as f:
        f.write(prompt)
