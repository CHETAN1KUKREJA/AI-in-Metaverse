from sockets import SocketServer
from llm import WorkersPool

NUMBER_OF_WORKERS = 2
PORT = 33455
HOST = ""

def start_server():
    
    print("========== Initializing Workers ==========")
    workers_pool = WorkersPool(num_workers=NUMBER_OF_WORKERS)
    
    sv = SocketServer(workers_pool, host=HOST, port=PORT)
    
    print(f"========== Server started at \"{HOST}:{PORT}\" ==========")
    sv.start_listening()
    
    

if __name__ == "__main__":
    start_server()
