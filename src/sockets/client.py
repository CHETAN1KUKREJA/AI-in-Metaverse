import json
import time
import os

HISTORY_DIR = '../resources/history/'
LOG_SIMULATION_FILE_NAME = 'run'
LOG_SIMULATION_DIR_NAME = 'sim'

class SocketClient:
    def __init__(self, workers_pool, socket, address):
        self.socket = socket
        self.address = address
        self.workers_pool = workers_pool
        self.memory = None
        self.is_running = True
        self.history = []
        
        last_run = 0
        for item in os.listdir(HISTORY_DIR):
            last_run = max(last_run, int(item.split(os.sep)[0].split('_')[-1]))
        
        self.current_sim_dir = HISTORY_DIR + LOG_SIMULATION_DIR_NAME + '_' + str(last_run + 1)
        os.makedirs(self.current_sim_dir, exist_ok=True)
        
        self.current_sim_file = self.current_sim_dir + os.sep + LOG_SIMULATION_FILE_NAME + '_' + self.address

    def _read_until_json(self):
        # Receive data
        data = ""
        while self.is_running:
            chunk = self.socket.recv(1024).decode('utf-8')

            if chunk == "":
                break
            if not chunk:  # Client closed connection
                print("Client disconnected")
                break
            data += chunk

            json_strs = self.data.split("</end/>")
            if len(json_strs) > 0:
                json_list = []
                for json_str in json_strs[:-1]:
                    json_list.append(json.loads(json_str))

                self.data = json_strs[-1]
                return json_list

    def stop_reading(self):
        self.is_running = False
        self.socket.close()

    def start_reading(self):
        print(f"Connected to client at {self.address}, starting to read")

        while self.is_running:
            try:
                request_jsons = self._read_until_json()
                for request_json in request_jsons:
                    print(
                        f"Received request from address: {self.address}"
                    )

                before_process = time.time()
                
                # Process the request and get the response with call, but only ONE time
                # TODO: (check if the json format corresponds to the expected one from the godot team)
                ([call,], [reason,]) = self.workers_pool.process([request_json], [self.memory])
                after_process = time.time()
                
                print(f"========== Request processed ==========")
                print(f"[1] Source address: {self.address}")
                print(f"[2] Processing time: {after_process - before_process}")
                print(f"[3] Generated reason: \n {reason}\n")
                print(f"[4] Generated response: \n {call}")
                print(f"=======================================")
                

                response_json = json.dumps(call) + "</end/>\n"
                self.socket.sendall(response_json.encode("utf-8"))
                    
                # Write to Log
                self.history.append(str(reason) + "\n" +  str(call))
                
                history_str = "\n\n".join(self.history)
                with open(self.current_sim_file, 'w') as f:
                    f.write(history_str)
                

            except Exception as e:
                print(f"Error during reveiving request: {e}")
                print(e.with_traceback())
                break
