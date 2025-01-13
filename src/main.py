from sockets.server import SocketServer
from models.workers_pool import WorkersPool

NUMBER_OF_WORKERS = 2
PORT = 33455
HOST = ""

if __name__ == "__main__":
    workers_pool = WorkersPool(num_workers=2)

    sv = SocketServer(workers_pool, host=HOST, port=PORT)
    sv.start_listening()
