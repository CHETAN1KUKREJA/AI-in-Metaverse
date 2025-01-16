import argparse
import time
import json
from src.llm.slot_filling.planer import Planer
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
        "--input_state",
        type=str,
        help="Input json state.",
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

    try:
        llm = Planer(args.model)
        if args.input_state is None:
            simulator = Simulator()
            input_state = simulator.get_agent_input_state()
        else:
            with open(args.input_state, "r") as fp:
                input_state = json.load(fp)

        if args.profile:
            start_time = time.time()

        # print(json.dumps(input_state, indent=2))
        call_batch = llm.iterate_step([input_state])
        print(call_batch[0])

        if args.profile:
            end_time = time.time()
            print(f"Finished in {end_time-start_time:.4f}s")
    finally:
        del llm