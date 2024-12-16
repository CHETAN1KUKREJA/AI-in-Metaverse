
import argparse
import time
import json
from backend.llm import LLM
from simulation.simulator import Simulator

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

    llm = LLM(args.model)
    simulator = Simulator()
    
    if args.profiling:
        start_time = time.time()
        
    for i in range(3):
        input_state = simulator.get_agent_input_state()
        call_batch = llm.iterate_step([input_state])
        print(call_batch[0])
        simulator.update_state(json.loads(call_batch[0]))

    if args.profiling:
        end_time = time.time()
        print(f"Finished in {end_time-start_time:.4f}s")