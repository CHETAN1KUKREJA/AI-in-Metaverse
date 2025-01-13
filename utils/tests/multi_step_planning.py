import argparse
import time
import json
from backend import LangchainLLM, SlotFillingLLM
from utils.simulation.simulator import Simulator


def parse_args():
    parse = argparse.ArgumentParser(description="Action Chain")
    parse.add_argument(
        "--profile",
        default=False,
        action="store_true",
        help="Enable profiling or not.",
    )
    parse.add_argument(
        "--output_json",
        default=False,
        action="store_true",
        help="Output the json of each file",
    )
    args = parse.parse_args()
    return args


if __name__ == "__main__":
    args = parse_args()

    llm = SlotFillingLLM()
    # llm = LangchainLLM()
    simulator = Simulator()

    print("############################################")

    for i in range(1):
        if args.profile:
            start_time = time.time()

        input_state = simulator.get_agent_input_state()
        if args.output_json:
            with open(f"result{i}.json", "w") as fp:
                json.dump(input_state, fp, indent=4)
        call_batch = llm.iterate_step([input_state])
        print(call_batch)
        simulator.update_state(call_batch[0])

        if args.profile:
            end_time = time.time()
            print(f"Finished in {end_time-start_time:.4f}s")

        print("############################################")
