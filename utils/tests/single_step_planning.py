
import argparse
import time
import json
from backend.slot_filling.planer import Planer
from utils.simulation.simulator import Simulator

def parse_args():
    parse = argparse.ArgumentParser(description="Prompt Engineering")
    parse.add_argument(
        "--model",
        type=str,
        default="Qwen/Qwen2.5-14B-Instruct-AWQ",
        choices=[
            "NousResearch/Hermes-3-Llama-3.1-8B",
            "Qwen/Qwen2.5-14B-Instruct",
            "Qwen/Qwen2.5-7B-Instruct",
            "Qwen/Qwen2.5-3B-Instruct",
        ],
        help="Model to be used.",
    )
    parse.add_argument(
        "--profile",
        default=False,
        action="store_true",
        help="Enable profiling or not.",
    )
    args = parse.parse_args()
    return args


if __name__ == "__main__":
    args = parse_args()

    llm = Planer(args.model)
    simulator = Simulator()
    
    if args.profile:
        start_time = time.time()
        
    input_state = simulator.get_agent_input_state()
    # print(json.dumps(input_state, indent=2))
    call_batch = llm.iterate_step([input_state])
    # print(call_batch[0])

    if args.profile:
        end_time = time.time()
        print(f"Finished in {end_time-start_time:.4f}s")