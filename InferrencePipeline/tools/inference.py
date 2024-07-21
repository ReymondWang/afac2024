from pathlib import Path
from typing import Union
from peft import AutoPeftModelForCausalLM, PeftModelForCausalLM
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    PreTrainedModel,
    PreTrainedTokenizer,
    PreTrainedTokenizerFast,
)

ModelType = Union[PreTrainedModel, PeftModelForCausalLM]
TokenizerType = Union[PreTrainedTokenizer, PreTrainedTokenizerFast]

def _resolve_path(path: Union[str, Path]) -> Path:
    return Path(path).expanduser().resolve()

def load_model_and_tokenizer(model_dir: Union[str, Path]) -> tuple[ModelType, TokenizerType]:
    model_dir = _resolve_path(model_dir)
    if (model_dir / 'adapter_config.json').exists():
        model = AutoPeftModelForCausalLM.from_pretrained(
            model_dir, trust_remote_code=True, device_map='auto'
        )
        tokenizer_dir = model.peft_config['default'].base_model_name_or_path
    else:
        model = AutoModelForCausalLM.from_pretrained(
            model_dir, trust_remote_code=True, device_map='auto'
        )
        tokenizer_dir = model_dir
    tokenizer = AutoTokenizer.from_pretrained(
        tokenizer_dir, trust_remote_code=True,
        encode_special_tokens=True, use_fast=False
    )
    return model, tokenizer

def glm3_inference(input:str, model: ModelType, tokenizer: TokenizerType, top_p=0.7, temperature=0.6) -> str :

    response,_ = model.chat(tokenizer=tokenizer, query=input, history=[], top_p=top_p, temperature=temperature, max_length=2048)
    
    return response

def glm4_inference(input_:dict, model: ModelType, tokenizer: TokenizerType, top_p=0.8, temperature=0.8) -> str:
    
    messages = [input_] # {'role':'user','content':'...'}
    
    inputs = tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=True,
            return_tensors="pt"
        ).to(model.device)
    
    generate_kwargs = {
            "input_ids": inputs,
            "max_new_tokens": 1024,
            "do_sample": True,
            "top_p": top_p,
            "temperature": temperature,
            "repetition_penalty": 1.2,
            "eos_token_id": model.config.eos_token_id,
        }
    
    outputs = model.generate(**generate_kwargs)
    response = tokenizer.decode(outputs[0][len(inputs[0]):], skip_special_tokens=True).strip()
    return response