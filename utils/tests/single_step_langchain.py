
import argparse
import time
import json
from backend.langchain.llm import LLM
from utils.simulation.simulator import Simulator
from input_processing.prompt import get_prompt

def parse_args():
    parse = argparse.ArgumentParser(description="Prompt Engineering")
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

    llm = LLM()
    simulator = Simulator()
    
    if args.profile:
        start_time = time.time()
        
    input_state = simulator.get_agent_input_state()
    print(json.dumps(input_state, indent=4))
    prompt = get_prompt(input_state, "simple_chain")
    print(prompt)
    call_batch = llm.iterate_step(input_jsons=[input_state])
    print(call_batch[0])

    if args.profile:
        end_time = time.time()
        print(f"Finished in {end_time-start_time:.4f}s")