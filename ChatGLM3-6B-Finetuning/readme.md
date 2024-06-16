## 训练流程

进入本项目目录，训练启动命令如下：

```shell
python finetune_hf.py data ../../../Model/THUDM/chatglm3-6b configs/ptuning_v2.yaml
```

## 注意
transformer的版本必须时4.40.0，否则微调到evaluation阶段会报错