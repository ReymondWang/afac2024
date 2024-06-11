PRE_SEQ_LEN=128
LR=2e-2
NUM_GPUS=4

torchrun --standalone --nnodes=1 --nproc_per_node=$NUM_GPUS main.py \
    --do_train \
    --train_file ./data/train.json \
    --validation_file ./data/dev.json \
    --preprocessing_num_workers 10 \
    --prompt_column input \
    --response_column output \
    --overwrite_cache \
    --model_name_or_path /mnt3/zhaomu.ldc/chatglm2-6b \
    --output_dir output/ \
    --overwrite_output_dir \
    --max_source_length 1024 \
    --max_target_length 1024 \
    --per_device_train_batch_size 16 \
    --per_device_eval_batch_size 1 \
    --gradient_accumulation_steps 16 \
    --predict_with_generate \
    --max_steps 200 \
    --logging_steps 100 \
    --save_steps 200 \
    --learning_rate $LR \
    --pre_seq_len $PRE_SEQ_LEN \
    # --quantization_bit 4

