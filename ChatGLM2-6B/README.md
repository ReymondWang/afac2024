## 数据下载
下载官网数据，放到ptuning/data 下面

## 数据预处理，生成json文件
python create_train_data.py

## 模型训练，产出ckpt

sh ds_train_finetune.sh

## 评测集预测，产出generated_predictions.txt

sh evaluate_finetune.sh

## 数据后处理,产出submit.txt

python pro_eval_data.py