import socket
from threading import Thread
from backend.sockets.client import SocketClient

class SocketServer():
    def __init__(self, process, host = "", port = 33455):
        self.process = process
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(socket.SOMAXCONN)
        self.client_threads = []
        
    
    def start_listening(self, connection_number = socket.SOMAXCONN):
        """
        !THIS FUNCTION IS A BLOCKING FUNCTION!
        Starts listening for incoming connections on the server socket and spawns a new
        thread for each client connection.
        Args:
            connection_number (int, optional): The maximum number of queued connections
                before the server starts to refuse them. Defaults to socket.SOMAXCONN.
        Behavior:
            - Binds the server socket to listen for incoming connections.
            - Accepts new client connections.
            - Creates a SocketClient instance for each connection.
            - Spawns a new thread to handle the client's communication.
            - Continues to listen unless manually stopped.
        Raises:
            OSError: If the socket cannot listen for connections.
        """
        
        print(f"Server is listening on {self.host}:{self.port}")
        
        self.server_socket.listen(connection_number)
        while True:
            (client_socket, client_address) = self.server_socket.accept()
            client = SocketClient(self.process, client_socket, client_address)
        
            # Start a new thread for the client
            thread = Thread(target = client.start_reading)
            thread.start()
            self.client_threads.append(thread)
