
import argparse
import time
import json
from backend.summarizer import Summarizer
from simulation.simulator import Simulator

def parse_args():
    parse = argparse.ArgumentParser(description="Prompt Engineering")
    parse.add_argument(
        "--model",
        type=str,
        default="Qwen/Qwen2.5-3B-Instruct",
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

    llm = Summarizer(args.model)
    
    if args.profiling:
        start_time = time.time()
        
    input = r"""
Given your current status and the available actions, the best next step would be to go to the market. Although the market is currently closed, you can still move there to see if it opens soon or if you can find any other opportunities n
earby. Here’s the plan:                                                                                                                                                                                                                     
                                                                                                                                                                                                                                            
1. **go to the market**: Since the market is 2.8 units away, this is a feasible action that will allow you to check the situation there.

Let's proceed with this action.
""".strip()
        
    call_batch = llm.iterate_step([input])

    if args.profiling:
        end_time = time.time()
        print(f"Finished in {end_time-start_time:.4f}s")