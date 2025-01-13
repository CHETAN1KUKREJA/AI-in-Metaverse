from sockets import SocketServer
from models import WorkersPool

NUMBER_OF_WORKERS = 2
PORT = 33455
HOST = ""

if __name__ == "__main__":
    workers_pool = WorkersPool(num_workers=NUMBER_OF_WORKERS)

    sv = SocketServer(workers_pool, host=HOST, port=PORT)
    sv.start_listening()
