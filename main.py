import argparse
import time
import json
from backend import LangchainLLM, SlotFillingLLM
from backend.communication import start_server


def parse_args():
    parse = argparse.ArgumentParser(description="Action Chain")
    parse.add_argument(
        "--profile",
        default=False,
        action="store_true",
        help="Enable profiling or not.",
    )
    parse.add_argument("--host", type=str, default="localhost", help="Host name of the server")
    parse.add_argument("--port", type=int, default=33455, help="Port of the server")
    args = parse.parse_args()
    return args


if __name__ == "__main__":
    args = parse_args()

    llm = SlotFillingLLM()
    # llm = LangchainLLM()

    def process(input_state):
        if args.profile:
            start_time = time.time()

        call_batch = llm.iterate_step([input_state])

        if args.profile:
            end_time = time.time()
            print(f"Finished in {end_time-start_time:.4f}s")

        return call_batch

    start_server(process, args.host, args.port)
