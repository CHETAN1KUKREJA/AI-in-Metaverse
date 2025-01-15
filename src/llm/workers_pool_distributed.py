import socket
import json
import threading
from dataclasses import dataclass
from typing import List, Dict, Optional
from threading import Lock, Semaphore, Thread
import time
import traceback
from .slot_filling.llm import LLM


@dataclass
class WorkerInfo:
    host: str
    port: int
    worker_id: int
    is_available: bool = True
    last_heartbeat: float = time.time()


class DistributedWorkerPool:
    def __init__(self, heartbeat_timeout: float = 30.0, server_port: int = 33456):
        self.workers: Dict[str, WorkerInfo] = {}
        self.lock = Lock()
        self.heartbeat_timeout = heartbeat_timeout
        self.empty_sem = None
        self.next_worker_id = 0
        self.server_port = server_port
        self.is_running = True
        self.worker_available_event = threading.Event()

        # Single server socket for all messages
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(("", self.server_port))
        self.server_socket.listen(socket.SOMAXCONN)

        # Single message handling thread
        self.message_thread = Thread(target=self._handle_messages)
        self.message_thread.start()

    def register_worker(self, host: str, port: int, worker_id: int, blocked=True) -> None:
        """Register a new worker in the pool with a specific ID. Replace the old semaphore with a new one."""
        connection_id = f"{host}:{port}"

        def register():
            self.workers[connection_id] = WorkerInfo(host=host, port=port, worker_id=worker_id, is_available=True, last_heartbeat=time.time())
            if self.empty_sem is None:
                self.empty_sem = Semaphore(1)
            else:
                old_sem = self.empty_sem
                self.empty_sem = Semaphore(len(self.workers))
                while True:
                    try:
                        old_sem.release()
                        self.empty_sem.acquire(blocking=False)
                    except (ValueError, threading.BoundedSemaphore.ValueError):
                        break
            self.worker_available_event.set()

            print(f"Registered new worker {worker_id} at {host}:{port}")

        if blocked:
            with self.lock:
                register()
        else:
            register()

    def assign_worker_id(self, blocked=True) -> int:
        """Assign a new unique worker ID."""

        def assign():
            worker_id = self.next_worker_id
            self.next_worker_id += 1
            return worker_id

        if blocked:
            with self.lock:
                return assign()
        else:
            return assign()

    def _handle_single_message(self, client_socket, client_address):
        """Handle message from individual client."""
        try:
            # Read message
            data = ""
            while True:
                chunk = client_socket.recv(1024).decode("utf-8")
                if not chunk:
                    break
                data += chunk
                try:
                    message = json.loads(data)
                    break
                except json.JSONDecodeError:
                    continue

            worker_host = message.get("host")
            worker_port = message.get("port")
            connection_id = f"{worker_host}:{worker_port}"

            if message.get("type") == "registration":
                with self.lock:
                    # Handle registration request
                    exist = False
                    worker_id = None
                    for _, worker in self.workers.items():
                        if worker.host == worker_host and worker.port == worker_port:
                            exist = True
                            worker_id = worker.worker_id
                            break

                    if exist:
                        print(f"Worker ID {worker_id} already exists, keeping ID {worker_id}")
                    else:
                        worker_id = self.assign_worker_id(blocked=False)
                        self.register_worker(worker_host, worker_port, worker_id, blocked=False)
                    response = {"type": "registration_response", "worker_id": worker_id}

            elif message.get("type") == "heartbeat":
                # Handle heartbeat
                worker_id = message.get("worker_id")
                with self.lock:
                    if connection_id in self.workers:
                        if self.workers[connection_id].worker_id == worker_id:
                            self.workers[connection_id].last_heartbeat = time.time()
                            response = {"type": "heartbeat_ack"}
                        else:
                            # Worker ID mismatch, may be cannot reach here
                            response = {"type": "registration_required"}
                            print(f"Worker ID mismatch for {connection_id}")
                    else:
                        # Worker ID not found, may be cannot reach here
                        response = {"type": "registration_required"}
                        print(f"Worker ID not found for {connection_id}")

            client_socket.sendall(json.dumps(response).encode("utf-8"))

        except Exception as e:
            print(f"Error handling message from {client_address}: {e}")
        finally:
            client_socket.close()

    def _handle_messages(self):
        """Main thread that accepts connections and spawns handler threads."""
        while self.is_running:
            try:
                client_socket, client_address = self.server_socket.accept()

                # Spawn a new thread for each client connection
                handler_thread = threading.Thread(target=self._handle_single_message, args=(client_socket, client_address))
                handler_thread.daemon = True
                handler_thread.start()

            except Exception as e:
                print(f"Error accepting connection: {e}")
                if not self.is_running:
                    break

    def get_available_worker(self) -> WorkerInfo:
        """Get an available worker, blocking until one becomes available."""
        while True:
            # timeout necessary because there may be new workers registering
            self.worker_available_event.wait(timeout=1.0)

            current_time = time.time()
            with self.lock:
                for worker_id, worker in self.workers.items():
                    if worker.is_available and current_time - worker.last_heartbeat < self.heartbeat_timeout:
                        worker.is_available = False
                        return worker

            print("No workers available, waiting...")

    def release_worker(self, host: str, port: int) -> None:
        """Mark a worker as available again."""
        worker_id = f"{host}:{port}"
        with self.lock:
            if worker_id in self.workers:
                self.workers[worker_id].is_available = True
                self.workers[worker_id].last_heartbeat = time.time()
                self.worker_available_event.set()

    def stop(self):
        """Stop the message handling thread."""
        self.is_running = False
        self.server_socket.close()
        self.message_thread.join()


class RemoteWorker:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self) -> None:
        """Connect to the remote worker."""
        self.socket.connect((self.host, self.port))

    def process(self, request: dict, memory: Optional[dict]) -> tuple:
        """Send request to remote worker and get response."""
        payload = {"request": request, "memory": memory}
        request_str = json.dumps(payload) + "\n"
        self.socket.sendall(request_str.encode("utf-8"))

        # Read response
        response = ""
        while True:
            chunk = self.socket.recv(1024).decode("utf-8")
            if not chunk:
                break
            response += chunk
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                continue

        raise ConnectionError("Worker connection closed")

    def close(self) -> None:
        """Close the connection to the remote worker."""
        self.socket.close()


class DistributedWorkersPool:
    """Drop-in replacement for the original WorkersPool with distributed capabilities."""

    def __init__(self, registry_host: str = "", registry_port: int = 33455):
        self.worker_pool = DistributedWorkerPool()
        self.registry_host = registry_host
        self.registry_port = registry_port

    def process(self, requests: List[dict], memories: List[Optional[dict]]) -> tuple:
        """Process requests using available distributed workers."""
        # Acquire semaphore (waiting for available worker)
        self.worker_pool.empty_sem.acquire()

        try:
            # May block until a worker is available
            worker_info = self.worker_pool.get_available_worker()

            try:
                worker = RemoteWorker(worker_info.host, worker_info.port)
                worker.connect()

                result = worker.process(requests, memories)
                worker.close()

                return result
            finally:
                self.worker_pool.release_worker(worker_info.host, worker_info.port)
        finally:
            self.worker_pool.empty_sem.release()
