
from backend.sockets.server import SocketServer
import signal

def process():
    pass

    def _sigint_handler(sig, frame):
        server.stop_server()
        raise SystemExit("Exiting gracefully")

    signal.signal(signal.SIGINT, _sigint_handler)

server = SocketServer(process)
server.start_listening()

    