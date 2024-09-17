import socket
import threading

def receive_messages(client_socket):
    while True:
        try:
            response = client_socket.recv(1024)
            if not response:
                break
            message = response.decode('utf-8')
            if message.startswith("Client-"):
                print('\n' + message)
            else:
                print('\nServer:', message)
        except ConnectionResetError:
            break

def send_message_to_server(host='127.0.0.1', port=65432):
    # Prompt for client name
    client_name = input("Enter your name: ")

    # Create a TCP/IP socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        # Connect the socket to the server's address and port
        client_socket.connect((host, port))
        
        print("Connected to the server. Type your messages below:")
        
        # Start a thread to receive messages from the server
        threading.Thread(target=receive_messages, args=(client_socket,)).start()
        
        while True:
            # Read message from console
            message = input("You: ")
            
            # Prepend client name to the message
            full_message = f"Client-{client_name}: {message}"
            
            # Send the message
            client_socket.sendall(full_message.encode('utf-8'))

if __name__ == "__main__":
    send_message_to_server()