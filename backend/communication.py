import socket
import json

def start_server(process, host='localhost', port=12345):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(1)
    
    print(f"Server listening on {host}:{port}")
    
    while True:
        # Wait for connection
        client_socket, client_address = server_socket.accept()
        print(f"Connected to client at {client_address}")
        
        while True:
            try:
                # Receive data
                data = ""
                while True:
                    chunk = client_socket.recv(1024).decode('utf-8')
                    if not chunk:  # Client closed connection
                        print("Client disconnected")
                        break
                    data += chunk
                    
                    try:
                        json_data = json.loads(data)
                        break
                    except json.JSONDecodeError:
                        continue
                
                if not chunk:  # Client closed connection
                    break
                
                print(f"Received: {json_data}")
                
                call_batch = process(json_data)
                
                response_json = json.dumps(call_batch) + "\n"
                client_socket.sendall(response_json.encode('utf-8'))
                print(f"Send: {response_json}")
                
            except Exception as e:
                print(f"Error: {e}")
                break
        
        client_socket.close()
