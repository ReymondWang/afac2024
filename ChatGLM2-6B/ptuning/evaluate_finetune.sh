STEP=100
NUM_GPUS=1

torchrun --standalone --nnodes=1 --nproc-per-node=$NUM_GPUS main.py \
    --do_predict \
    --validation_file data/test_a.json \
    --test_file data/test_a.json \
    --overwrite_cache \
    --prompt_column input \
    --response_column output \
    --model_name_or_path ./output/checkpoint-$STEP  \
    --output_dir ./output/checkpoint-$STEP \
    --overwrite_output_dir \
    --max_source_length 1024 \
    --max_target_length 1024 \
    --per_device_eval_batch_size 16 \
    --predict_with_generate \
    --fp16_full_eval
