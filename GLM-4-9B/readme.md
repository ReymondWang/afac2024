## 训练流程

进入本项目目录，训练启动命令如下：

```shell
python finetune.py data ../../../Model/THUDM/glm-4-9b-chat configs/lora.yaml
```

从保存检查点继续训练，命令如下：

```shell
python finetune.py data ../../../Model/THUDM/glm-4-9b-chat configs/lora.yaml yes
```