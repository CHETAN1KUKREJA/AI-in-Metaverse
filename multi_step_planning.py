import argparse
import time
import json
from backend.llm import LLM
from simulation.simulator import Simulator


def parse_args():
    parse = argparse.ArgumentParser(description="Action Chain")
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

    llm = LLM("unsloth/Qwen2.5-14B-Instruct-bnb-4bit", "unsloth/Qwen2.5-7B-Instruct-bnb-4bit")
    simulator = Simulator()

    print("############################################")

    for i in range(4):
        if args.profiling:
            start_time = time.time()

        input_state = simulator.get_agent_input_state()
        with open(f"result{i}.json", "w") as fp:
            json.dump(input_state, fp, indent=4)
        call_batch = llm.iterate_step([input_state])
        simulator.update_state(call_batch[0])

        if args.profiling:
            end_time = time.time()
            print(f"Finished in {end_time-start_time:.4f}s")

        print("############################################")
