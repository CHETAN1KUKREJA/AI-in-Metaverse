import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from input_processing import get_processed
import argparse
import time
import json


def parse_args():
    parse = argparse.ArgumentParser(description="Prompt Engineering")
    parse.add_argument(
        "--model",
        type=str,
        default="Qwen/Qwen2.5-7B-Instruct",
        choices=[
            "Qwen/Qwen2.5-14B-Instruct",
            "Qwen/Qwen2.5-7B-Instruct",
            "Qwen/Qwen2.5-3B-Instruct",
        ],
        help="Model to be used.",
    )
    parse.add_argument(
        "--profiling",
        default=False,
        action="store_true",
        help="Enable profiling or not.",
    )
    args = parse.parse_args()
    return args


def process(tokenizer, model, prompt, action_tools):

    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": "What should you do for only one step? Only output the tool call!"},
    ]

    inputs = tokenizer(
        tokenizer.apply_chat_template(
            [messages],
            tools=action_tools,
            add_generation_prompt=True,
            return_tensors="pt",
            tokenize=False,
        )
    )
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

    generated_ids = [
        output[len(input) :] for input, output in zip(input_ids, output_ids)
    ]
    response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)
    return response[0]


if __name__ == "__main__":
    args = parse_args()

    with open("test_json.json") as f:
        input_json = json.load(f)

    prompt, action_tools = get_processed(input_json)
    print(prompt)

    if args.model is not None:
        tokenizer = AutoTokenizer.from_pretrained(args.model, cache_dir="cached_models")

        model = AutoModelForCausalLM.from_pretrained(
            args.model,
            cache_dir="cached_models",
            device_map="auto",
            torch_dtype="auto",
        )
        
        if args.profiling:
            start_time = time.time()
            
        output = process(tokenizer, model, prompt, action_tools)
        print(output + "\n")

        if args.profiling:
            end_time = time.time()
            print(f"Finished in {end_time-start_time:.4f}s")