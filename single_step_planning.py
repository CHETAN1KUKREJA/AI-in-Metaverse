
import argparse
import time
import json
from backend.llm import LLM

def parse_args():
    parse = argparse.ArgumentParser(description="Prompt Engineering")
    parse.add_argument(
        "--model",
        type=str,
        default="NousResearch/Hermes-3-Llama-3.1-8B",
        choices=[
            "NousResearch/Hermes-3-Llama-3.1-8B",
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


if __name__ == "__main__":
    args = parse_args()

    with open("test_json.json") as f:
        input_json = json.load(f)

    if args.model is not None:
        llm = LLM(args.model)
        
        if args.profiling:
            start_time = time.time()
            
        call_batch = llm.iterate_step([input_json])
        print(call_batch[0])

        if args.profiling:
            end_time = time.time()
            print(f"Finished in {end_time-start_time:.4f}s")