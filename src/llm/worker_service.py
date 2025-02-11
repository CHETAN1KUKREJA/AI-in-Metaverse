import socket
import json
from threading import Thread
import time
from src.llm.slot_filling.llm import LLM


class WorkerAgent:
    """Local worker that processes requests using LLM."""

    id_counter = 0

    def __init__(self, w_id):
        self.llm = LLM()
        self.worker_id = w_id

    def process(self, request, memory):
        return self.llm.process(request, memory)


class WorkerService:
    def __init__(self, registry_host: str, registry_port: int, worker_host: int, worker_port: int, heartbeat_diff_time=4.0):
        self.registry_host = registry_host
        self.registry_port = registry_port
        self.worker_host = worker_host
        self.worker_port = worker_port
        self.heartbeat_diff_time = heartbeat_diff_time
        self.worker_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.worker_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.is_running = True
        self.worker = None  # Will be initialized after getting ID from server
        self.assigned_worker_id = None

    def start(self):
        """Start the worker service."""
        # Bind to worker port
        self.worker_socket.bind(("", self.worker_port))
        self.worker_socket.listen(socket.SOMAXCONN)

        # Start heartbeat thread
        heartbeat_thread = Thread(target=self._send_heartbeat)
        heartbeat_thread.daemon = True
        heartbeat_thread.start()
        
        client_socket, _ = self.worker_socket.accept()
        
        # Main service loop
        while self.is_running:
            try:
                self._handle_client(client_socket)
            except Exception as e:
                print(f"Error accepting connection: {e}")

    def _send_heartbeat(self):
        """
        Periodically send heartbeat to registry.
        """
        # First heartbeat serves as registration
        self._register_and_get_id()

        while self.is_running:
            try:
                registry_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                registry_socket.connect((self.registry_host, self.registry_port))

                heartbeat = {
                    "type": "heartbeat",
                    "host": self.worker_host,
                    "port": self.worker_port,
                    "worker_id": self.assigned_worker_id,
                }

                registry_socket.sendall(json.dumps(heartbeat).encode("utf-8"))

                # Wait for acknowledgment
                data = ""
                while True:
                    chunk = registry_socket.recv(4096).decode("utf-8")
                    if not chunk:
                        break
                    data += chunk
                    try:
                        _ = json.loads(data)
                        break
                    except json.JSONDecodeError:
                        continue

                registry_socket.close()
            except Exception as e:
                print(f"Error sending heartbeat: {e}")

            time.sleep(self.heartbeat_diff_time)  # Send heartbeat every 10 seconds

    def _register_and_get_id(self):
        """Register with the server and get assigned worker ID."""
        while self.assigned_worker_id is None and self.is_running:
            try:
                print(f"Registering with server at {self.registry_host}:{self.registry_port}")
                registry_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                registry_socket.connect((self.registry_host, self.registry_port))

                # Send initial registration heartbeat
                heartbeat = {
                    "type": "registration",
                    "host": self.worker_host,
                    "port": self.worker_port,
                }

                print(f"Sending registration heartbeat: {heartbeat}")
                registry_socket.sendall(json.dumps(heartbeat).encode("utf-8"))

                # Wait for registration response with assigned ID
                data = ""
                while True:
                    chunk = registry_socket.recv(4096).decode("utf-8")
                    if not chunk:
                        break
                    data += chunk
                    try:
                        response = json.loads(data)
                        break
                    except json.JSONDecodeError:
                        continue
                print(f"Received registration response: {response}")

                if response["type"] == "registration_response":
                    self.assigned_worker_id = response["worker_id"]
                    print(f"Registered with server. Assigned worker ID: {self.assigned_worker_id}")
                    # Initialize worker agent with assigned ID
                    self.worker = WorkerAgent(self.assigned_worker_id)

                registry_socket.close()
            except Exception as e:
                print(f"Error during registration:\n{e.with_traceback(None)}")
                time.sleep(5)  # Wait before retrying

    def _handle_client(self, client_socket):
        """Handle individual client requests."""
        try:
            # Read request
            data = ""
            while True:
                chunk = client_socket.recv(4096).decode("utf-8")
                
                if not chunk:
                    break
                data += chunk
                try:
                    
                    payload = json.loads(data)
                    break
                except json.JSONDecodeError:
                    continue
            
            
            # Process request using the worker agent
            request = payload["request"]
            memory = payload["memory"]
            response = self.worker.process(request, memory)
            
            # Send response
            response_str = json.dumps(response) + "\n"
           
            client_socket.sendall(response_str.encode("utf-8"))
        except Exception as e:
            print(f"Error handling client: {e}")
            print(e.with_traceback(None))
        # finally:
        #     client_socket.close()

    def stop(self):
        """Stop the worker service."""
        self.is_running = False
        self.worker_socket.close()

