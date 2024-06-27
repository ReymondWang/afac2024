"""
本脚本用于使用不同的方式调用大模型推理：
1. openai (API，与模型端分离)
2. transformers (直接运行) 
"""
import openai

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

def openai_inference(prompt:str, model_uid='glm-4-9b-chat', top_p=0.7, temperature=0.6) -> str :
    # Assume that the model is already launched.
    # The api_key can't be empty, any string is OK.
    client = openai.Client(api_key="not empty", base_url="http://localhost:9997/v1")
    return client.chat.completions.create(
        model=model_uid,
        messages=[{"content": prompt,"role": "user",}],
        max_tokens=4096,
        top_p=top_p,
        temperature=temperature
    ).choices[0].message.content


#------------------------------------Transformers------------------------------------#

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
        tokenizer_dir, trust_remote_code=True
    )
    return model, tokenizer

def transformers_inference(prompt:str, model_dir: Union[str,Path], top_p=0.7, temperature=0.6) -> str :

    model, tokenizer = load_model_and_tokenizer(model_dir)
    response,_ = model.chat(tokenizer=tokenizer, query=input, history=[], top_p=top_p, temperature=temperature)
    
    return response
