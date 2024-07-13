MASTER_PORT=$(shuf -n 1 -i 10000-65535)

deepspeed --num_gpus=2 --master_port $MASTER_PORT finetune_dpo.py --deepspeed dpo-config/ds_zero_3.json