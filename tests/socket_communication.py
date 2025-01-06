import argparse
import socket
import json

def parse_args():
    parse = argparse.ArgumentParser(description="Action Chain")
    parse.add_argument("--host", type=str, default="localhost", help="Host name of the server")
    parse.add_argument("--port", type=int, default=33455, help="Port of the server")
    args = parse.parse_args()
    return args

def connect_to_server(host='localhost', port=12345):
    # Create socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    return client_socket

def send_and_receive(client_socket, data):
    json_data = json.dumps(data)
    client_socket.sendall(json_data.encode('utf-8'))
    
    # Receive response
    response = ""
    while True:
        chunk = client_socket.recv(1024).decode('utf-8')
        if not chunk:
            break
        if '\n' in chunk:
            response += chunk[:chunk.index('\n')]
            break
        response += chunk
    
    # Parse response
    return json.loads(response)

if __name__ == "__main__":
    args = parse_args()
    
    client_socket = connect_to_server(args.host, args.port)
    
    try:
        with open('sample_agent_input_state/result0.json') as f:
            test_data = json.load(f)
            print(test_data)
            
        response = send_and_receive(client_socket, test_data)
        print(f"Server response: {response}")
            
    finally:
        client_socket.close()