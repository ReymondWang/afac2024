## 训练流程

进入本项目目录，训练启动命令如下：

```shell
python finetune_hf.py data ../../../Model/THUDM/chatglm3-6b configs/lora.yaml
```

在lora的结果下再次使用ptuning，训练启动命令如下：
```shell
python finetune_hf.py data ./models/chatglm3-6b-01 configs/ptuning_v2.yaml
```

## 注意
transformer的版本必须时4.40.0，否则微调到evaluation阶段会报错

## 多卡微调

需要使用conda安装mpi4py
```shell
conda install mpi4py 
```

```shell
OMP_NUM_THREADS=1 torchrun --standalone --nnodes=1 --nproc_per_node=6  finetune_hf.py  data  ../../../Model/THUDM/chatglm3-6b  configs/sft.yaml
```

## 模型合并
```shell
python model_export_hf.py ./output/checkpoint-200/ --out-dir ./models/chatglm3-6b-01
```


## DPO在单卡A800上执行
```shell
export PYTORCH_CUDA_ALLOC_CONF="max_split_size_mb:512"
python finetune_dpo.py
```