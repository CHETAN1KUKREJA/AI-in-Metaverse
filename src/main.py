from sockets import SocketServer
from llm import DistributedWorkersPool

NUMBER_OF_WORKERS = 2
PORT = 33455
HOST = ""


def start_server():

    print("========== Initializing Workers ==========")
    workers_pool = DistributedWorkersPool()

    sv = SocketServer(workers_pool, host=HOST, port=PORT)

    print(f'========== Server started at "{HOST}:{PORT}" ==========')
    sv.start_listening()


if __name__ == "__main__":
    start_server()

# python src/main.py
# python src/llm/worker_service.py --registry-host localhost --registry-port 33456 --worker-port 33457