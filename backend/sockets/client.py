import json
import time

class SocketClient():
    def __init__(self, process, socket, address):
        self.socket = socket
        self.address = address
        self.process = process
        
    def _read_until_json(self):
        # Receive data
        data = ""
        while True:
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
        
    def start_reading(self):
        print(f"Connected to client at {self.address}, starting to read")
        
        # PROTOCOL FOR READING:
        # 1. Read until a valid JSON object is received
        # 2. Process the JSON object
        # 3. Send the response as a JSON object
        # 4. Wait for response from GODOT team
        
        while True:
            try:
                request_json = self._read_until_json()
                print(f"Received request from address: {self.address}, request:\n {request_json}")
                
                before_process = time.time()
                call_batch = self.process(request_json)
                after_process = time.time()
                
                print(f"Processed request, sending response: {call_batch}")
                print(f"Processing time: {after_process - before_process}")
                
                response_json = json.dumps(call_batch) + "\n"
                self.socket.sendall(response_json.encode('utf-8'))
                
                response_json = self._read_until_json()
                print(f"Recieved response from GODOT team: {response_json}")
                
            except Exception as e:
                print(f"Error: {e}")
                break
        