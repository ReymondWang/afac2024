## 训练流程

进入本项目目录，训练启动命令如下：

```shell
python3 train_qlora.py \
--train_args_json QLoRA.json \
--model_name_or_path ../../Model/THUDM/chatglm3-6b \
--train_data_path data/train.json \
--eval_data_path data/dev.json \
--lora_rank 4 \
--lora_dropout 0.05 \
--compute_dtype fp32
```