import json
import time

class SocketClient():
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
            chunk = self.socket.recv(1024).decode('utf-8')
            if not chunk:  # Client closed connection
                print("Client disconnected")
                break
            data += chunk
                    
            try:
                json_data = json.loads(data)
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
                request_json = self._read_until_json()
                print(f"Received request from address: {self.address}, request:\n {request_json}")
                
                before_process = time.time()
                call_batch = self.workers_pool.process(request_json, self.memory)
                after_process = time.time()
                
                print(f"Processed request, sending response: {call_batch}")
                print(f"Processing time: {after_process - before_process}")
                
                response_json = json.dumps(call_batch) + "\n"
                self.socket.sendall(response_json.encode('utf-8'))
                
            except Exception as e:
                print(f"Error: {e}")
                break
        