
import pandas as pd
from prompt import cot_prompt_train
train_df = pd.read_csv('./train_cot.csv')

train_df['cot_label'] = train_df.cot + '\n\t\t于是最终标准的json格式结果为:\n\t\t\t' + train_df.label
train_df['cot_prompt'] = train_df.query_with_products.apply(lambda query:cot_prompt_train.replace('<QUERY>',query))
train_df[['cot_prompt','cot_label']].to_excel('cot4train.xlsx')
# for backward compatibility, you can still use `https://api.deepseek.com/v1` as `base_url`.
print(client.models.list())
