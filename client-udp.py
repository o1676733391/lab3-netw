import socket
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from threading import Thread

# Client configuration
BUFFER_SIZE = 1024
# get the current working directory
CURRENT_DIRECTORY = os.getcwd()
# make directory for the client files
os.makedirs(os.path.join(CURRENT_DIRECTORY, 'client_files'), exist_ok=True)
# set the download directory
DOWNLOAD_DIRECTORY = os.path.join(CURRENT_DIRECTORY, 'client_files')

def receive_file(filename, server_address):
    try:
        file_path = os.path.join(DOWNLOAD_DIRECTORY, filename)
        os.makedirs(DOWNLOAD_DIRECTORY, exist_ok=True)
        log(f"Saving file to: {file_path}")  # Debug: show where the file will be saved

        with open(file_path, 'wb') as file:
            while True:
                data, _ = client_socket.recvfrom(BUFFER_SIZE)
                
                # Check if the server sent the end signal
                if data.decode() == "END":
                    log("End of file transmission.")
                    break
                
                if data.decode() == "File not found":
                    log("File not found on the server.")
                    break
                
                log(f"Received packet: {data[:50]}...")  # Show first 50 bytes of the received packet
                file.write(data)
        
        log(f"Finished receiving file: {filename}")
    except Exception as e:
        log(f"An error occurred: {e}")

def request_file():
    try:
        # Get server details and filename from the UI
        server_ip = server_ip_entry.get()
        server_port = int(server_port_entry.get())
        filename = file_entry.get()

        if not server_ip or not server_port or not filename:
            messagebox.showwarning("Input Error", "Please enter all required fields.")
            return

        log(f"Requesting file '{filename}' from server {server_ip}:{server_port}...")
        
        # Create UDP socket
        global client_socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Send filename to server
        client_socket.sendto(filename.encode(), (server_ip, server_port))

        # Receive file contents from server
        receive_file(filename, (server_ip, server_port))

    except Exception as e:
        log(f"Error requesting file: {e}")

def log(message):
    log_textbox.insert(tk.END, message + '\n')
    log_textbox.see(tk.END)  # Auto-scroll to the bottom

# Initialize the UI
root = tk.Tk()
root.title("UDP File Client")

# Server IP entry
server_ip_label = tk.Label(root, text="Server IP:")
server_ip_label.pack()

server_ip_entry = tk.Entry(root)
server_ip_entry.pack()

# Server port entry
server_port_label = tk.Label(root, text="Server Port:")
server_port_label.pack()

server_port_entry = tk.Entry(root)
server_port_entry.pack()

# File name entry
file_label = tk.Label(root, text="File Name:")
file_label.pack()

file_entry = tk.Entry(root)
file_entry.pack()

# Request file button
request_file_button = tk.Button(root, text="Request File", command=lambda: Thread(target=request_file).start())
request_file_button.pack()

# Create a log display
log_label = tk.Label(root, text="Client Status")
log_label.pack()

log_textbox = tk.Text(root, height=15, width=50)
log_textbox.pack()

# Start the Tkinter main loop
root.mainloop()

