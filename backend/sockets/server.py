import socket
from threading import Thread
import sys
from backend.sockets.client import SocketClient

class SocketServer():
    def __init__(self, process, host = "", port = 33455):
        self.process = process
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(socket.SOMAXCONN)
        self.client_threads = []
        self.is_listening = True
        
    def stop_server(self):
        """
        Stops the server from listening for new connections.
        Behavior:
            - Closes the server socket.
            - Sets the is_listening flag to False.
            - Joins all client threads.
        """
        print("Server is stopping")
        
        self.is_listening = False
        
        for thread in self.client_threads:
            thread.kill()   
        
        self.server_socket.close()
        for client in self.clients:
            client.stop_reading()
        
    
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
        try:
            while self.is_listening:
                (client_socket, client_address) = self.server_socket.accept()
                client = SocketClient(self.process, client_socket, client_address)
           
                # Start a new thread for the client
                thread = Thread(target = client.start_reading)
                thread.start()
                self.client_threads.append(thread)
        except:
            raise SystemExit("Stopping server")
