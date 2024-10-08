import socket
import threading
import tkinter as tk
from tkinter import simpledialog, scrolledtext

HOST = '10.60.34.209'
PORT = 12345
BUFFER_SIZE = 1024
client_socket = None
client_running = True

# Create client-side GUI
class ChatClient(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('UDP Group Chat')
        self.geometry('400x400')

        # Client name
        self.client_name = ""

        # Create GUI elements
        self.text_area = scrolledtext.ScrolledText(self, state='disabled', wrap='word', width=50, height=15)
        self.text_area.grid(row=0, column=0, padx=10, pady=10, columnspan=2)

        self.message_entry = tk.Entry(self, width=40)
        self.message_entry.grid(row=1, column=0, padx=10, pady=10)
        self.message_entry.bind('<Return>', self.send_message)

        self.send_button = tk.Button(self, text='Send', command=self.send_message)
        self.send_button.grid(row=1, column=1, padx=10, pady=10)

        self.join_button = tk.Button(self, text='Join', command=self.join_chat)
        self.join_button.grid(row=2, column=0, padx=10, pady=10)

        self.leave_button = tk.Button(self, text='Leave', command=self.leave_chat)
        self.leave_button.grid(row=2, column=1, padx=10, pady=10)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Variables for client state
        self.client_connected = False

    def join_chat(self):
        global client_socket, client_running
        if not self.client_connected:
            self.client_name = simpledialog.askstring("Name", "Enter your name")  # Ask for client's name
            if not self.client_name:
                return  # Do nothing if no name is provided
            self.append_message(f"You ({self.client_name}) joined the chat.")
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            client_socket.sendto(f'JOIN:{self.client_name}'.encode(), (HOST, PORT))
            self.client_connected = True
            threading.Thread(target=self.receive_messages, daemon=True).start()

    def leave_chat(self):
        global client_socket, client_running
        if self.client_connected:
            client_socket.sendto(f'LEAVE:{self.client_name}'.encode(), (HOST, PORT))
            self.client_connected = False
            client_socket.close()
            self.append_message(f"You ({self.client_name}) left the chat.")

    def send_message(self, event=None):
        global client_socket
        if self.client_connected and self.message_entry.get().strip():
            message = self.message_entry.get()
            client_socket.sendto(f'SEND:{self.client_name}:{message}'.encode(), (HOST, PORT))
            self.message_entry.delete(0, tk.END)
            self.append_message(f'You: {message}')  # Display message locally

    def receive_messages(self):
        global client_socket
        while self.client_connected:
            try:
                data, _ = client_socket.recvfrom(BUFFER_SIZE)
                message = data.decode()
                if message.startswith('SEND:'):
                    self.append_message(message[5:])
            except Exception as e:
                break

    def append_message(self, message):
        self.text_area.config(state='normal')
        self.text_area.insert(tk.END, message + '\n')
        self.text_area.config(state='disabled')
        self.text_area.yview(tk.END)

    def on_closing(self):
        self.leave_chat()
        self.destroy()

if __name__ == '__main__':
    app = ChatClient()
    app.mainloop()
