import socket
import threading

clients = []

def handle_client(connection, client_address):
    print('Connected by', client_address)
    while True:
        try:
            data = connection.recv(1024)
            if not data:
                break
            print('Received from client:', data.decode('utf-8'))
            broadcast(data, connection)
        except ConnectionResetError:
            break
    connection.close()
    clients.remove(connection)
    print('Disconnected by', client_address)

def broadcast(message, sender_connection=None):
    for client in clients:
        if client != sender_connection:
            try:
                client.sendall(message)
            except:
                client.close()
                clients.remove(client)

def handle_server_input():
    while True:
        message = input("Server: ")
        broadcast(message.encode('utf-8'))

def start_server(host='127.0.0.1', port=65432):
    # Create a TCP/IP socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        # Bind the socket to the address and port
        server_socket.bind((host, port))
        
        # Listen for incoming connections
        server_socket.listen()
        print(f'Server is listening on {host}:{port}')
        
        # Start a thread to handle server input
        threading.Thread(target=handle_server_input, daemon=True).start()
        
        while True:
            # Accept a connection
            connection, client_address = server_socket.accept()
            clients.append(connection)
            threading.Thread(target=handle_client, args=(connection, client_address)).start()

if __name__ == "__main__":
    start_server()