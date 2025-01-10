import argparse
import time
import json
from backend import LangchainLLM, SlotFillingLLM
from backend.sockets.server import SocketServer


def parse_args():
    parse = argparse.ArgumentParser(description="Action Chain")
    parse.add_argument(
        "--profile",
        default=False,
        action="store_true",
        help="Enable profiling or not.",
    )
    parse.add_argument("--host", type=str, default="", help="Host name of the server")
    parse.add_argument("--port", type=int, default=33455, help="Port of the server")
    args = parse.parse_args()
    return args


if __name__ == "__main__":
    args = parse_args()

    llm = SlotFillingLLM()
    # llm = LangchainLLM()

    def process(input_state, memory):
        if args.profile:
            start_time = time.time()

        call_batch = llm.iterate_step([input_state])

        if args.profile:
            end_time = time.time()
            print(f"Finished in {end_time-start_time:.4f}s")

        return call_batch

    sv = SocketServer(process, args.host, args.port)
    sv.start_listening()
