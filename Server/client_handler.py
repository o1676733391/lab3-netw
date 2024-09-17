class ClientHandler:
    def __init__(self, client_socket):
        self.client_socket = client_socket

    def receive_message(self):
        try:
            message = self.client_socket.recv(1024).decode('utf-8')
            return message
        except Exception as e:
            print(f"Error receiving message: {e}")
            return None

    def send_message(self, message):
        try:
            self.client_socket.sendall(message.encode('utf-8'))
        except Exception as e:
            print(f"Error sending message: {e}")

    def close_connection(self):
        self.client_socket.close()