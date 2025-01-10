import argparse
import time
import json
from backend import LangchainLLM, SlotFillingLLM
from backend.sockets.server import SocketServer
from backend.workers_pool import WorkersPool


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

    workers_pool = WorkersPool(num_workers=1)

    # start_server(process, args.host, args.port)
    sv = SocketServer(workers_pool, None, args.port)
    sv.start_listening()
