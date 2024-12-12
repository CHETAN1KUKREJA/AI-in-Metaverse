import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from prompt.base import get_prompt
import argparse
import time
import json


def parse_args():
    parse = argparse.ArgumentParser(description="Prompt Engineering")
    parse.add_argument(
        "--model",
        type=str,
        default=None,
        choices=["unsloth/Llama-3.3-70B-Instruct-bnb-4bit", "meta-llama/Meta-Llama-3.1-8B-Instruct", "katanemo/Arch-Function-3B"],
        help="Model to be used.",
    )
    parse.add_argument(
        "--profiling",
        default=False,
        action="store_true",
        help="Enable profiling or not.",
    )
    parse.add_argument(
        "--input-json",
        type=str,
        help="The input json file",
    )
    parse.add_argument(
        "--prompt-mode",
        type=str,
        default="guided_chain",
        choices=["simple_chain", "guided_chain", "deep_guided_chain"],
        help="The mode of prompt",
    )
    args = parse.parse_args()
    return args


def process(tokenizer, model, prompt):

    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": ""},
    ]

    inputs = tokenizer(tokenizer.apply_chat_template([messages], add_generation_prompt=True, return_tensors="pt", tokenize=False))
    input_ids = torch.tensor(inputs["input_ids"]).to(model.device)
    attn_mask = torch.tensor(inputs["attention_mask"]).to(model.device)

    output_ids = model.generate(
        input_ids,
        attention_mask=attn_mask,
        max_new_tokens=2048,
        do_sample=True,
        top_p=0.9,
        temperature=0.6,
    )

    generated_ids = [output[len(input) :] for input, output in zip(input_ids, output_ids)]
    response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)
    return response[0]


if __name__ == "__main__":
    args = parse_args()

    with open(args.input_json) as f:
        input_json = json.load(f)

    prompt = get_prompt(input_json, args.prompt_mode)
    print(prompt)

    if args.model is not None:
        if args.profiling:
            start_time = time.time()

        tokenizer = AutoTokenizer.from_pretrained(args.model, cache_dir="cached_models")

        if "70B" in args.model:
            quantization_config = BitsAndBytesConfig(load_in_4bit=True)
            model = AutoModelForCausalLM.from_pretrained(
                args.model,
                cache_dir="cached_models",
                device_map="auto",
                torch_dtype="auto",
                quantization_config=quantization_config,
            )
        else:
            model = AutoModelForCausalLM.from_pretrained(
                args.model,
                cache_dir="cached_models",
                device_map="auto",
                torch_dtype="auto",
            )

        print(process(tokenizer, model, prompt))

        if args.profiling:
            end_time = time.time()
            print(f"Finished in {end_time-start_time:.4f}s")
