import json
import time


class SocketClient:
    def __init__(self, workers_pool, socket, address):
        self.socket = socket
        self.address = address
        self.workers_pool = workers_pool
        self.memory = None
        self.is_running = True

    def _read_until_json(self):
        # Receive data
        data = ""
        while self.is_running:
            chunk = self.socket.recv(1024).decode("utf-8")

            if chunk == "":
                break
            if not chunk:  # Client closed connection
                print("Client disconnected")
                break
            data += chunk

            try:
                _ = json.loads(data)
                break
            except json.JSONDecodeError:
                continue
        return data

    def stop_reading(self):
        self.is_running = False
        self.socket.close()

    def start_reading(self):
        print(f"Connected to client at {self.address}, starting to read")

        while self.is_running:
            try:
                request_str = self._read_until_json()
                print(f"Received request from address: {self.address}\n - Request: {request_str}")

                request_json = json.loads(request_str)

                before_process = time.time()

                # Process the request and get the response with call, but only ONE time
                # TODO: (check if the json format corresponds to the expected one from the godot team)
                ([call], [reason]) = self.workers_pool.process([request_json], [self.memory])
                after_process = time.time()

                print(f"========== Request processed ==========")
                print(f"[1] Source address: {self.address}")
                print(f"[2] Processing time: {after_process - before_process}")
                print(f"[3] Generated reason: \n {reason}\n")
                print(f"[4] Generated response: \n {call}")
                print(f"=======================================")

                response_json = json.dumps(call) + "\n"
                self.socket.sendall(response_json.encode("utf-8"))

            except Exception as e:
                print(f"Error during reveiving request: {e}")
                break
