import socket
import os
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from threading import Thread
import datetime
import time
import re
# Client configuration
BUFFER_SIZE = 1024
CURRENT_DIRECTORY = os.getcwd()
os.makedirs(os.path.join(CURRENT_DIRECTORY, 'downloaded_files'), exist_ok=True)
DOWNLOAD_DIRECTORY = os.path.join(CURRENT_DIRECTORY, 'downloaded_files')
LOG_FILE = 'client_activity.log'

def log(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_message = f"{timestamp} - {message}"
    log_textbox.insert(tk.END, formatted_message + '\n')
    log_textbox.see(tk.END)
    with open(LOG_FILE, 'a') as log_file:
        log_file.write(formatted_message + '\n')
LIST_OF_MAIL = []

def receive_file(filename, server_address):
    try:
        username = username_entry.get()
        # check if the directory exists
        if not os.path.exists(os.path.join(DOWNLOAD_DIRECTORY, username)):
            os.makedirs(os.path.join(DOWNLOAD_DIRECTORY, username))
        file_path = os.path.join(DOWNLOAD_DIRECTORY, username, filename)
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

def request_file(filename):
    try:
        username = username_entry.get()
        # Get server details and filename from the UI
        server_ip = server_ip_entry.get()
        server_port = int(server_port_entry.get())

        if not server_ip or not server_port or not filename:
            messagebox.showwarning("Input Error", "Please enter all required fields.")
            return

        log(f"Requesting file '{filename}' from server {server_ip}:{server_port}...")
        
        # Create UDP socket
        global client_socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Send filename to server
        client_socket.sendto(f"SEND_FILE:{username}:{filename}".encode(), (server_ip, server_port))

        # Receive file contents from server
        receive_file(filename, (server_ip, server_port))

    except Exception as e:
        log(f"Error requesting file: {e}")

def create_email_window():
    email_window = tk.Toplevel(root)
    email_window.title("Email Client")
    email_window.geometry("600x600")

    # Read emails frame
    read_frame = ttk.Frame(email_window)
    read_frame.pack(pady=10)

    read_label = ttk.Label(read_frame, text="Emails:")
    read_label.grid(row=0, column=0, padx=5, pady=5)

    email_listbox = tk.Listbox(read_frame, height=10, width=80)
    email_listbox.grid(row=1, column=0, padx=5, pady=5)
    # click on the email to read the email
    def read_email():
        try:
            username = username_entry.get()
            selected_index = email_listbox.curselection()[0]
            selected_filename = email_listbox.get(selected_index).split(':')[0]
            with open(os.path.join(DOWNLOAD_DIRECTORY, username, selected_filename), 'r') as file:
                content = file.read()
                messagebox.showinfo("Email Content", content)
        except Exception as e:
            log(f"Error reading email: {e}")
    # read the email
    email_listbox.bind("<Double-Button-1>", lambda event: read_email())
    # update the listbox with the current files in the DOWNLOAD_DIRECTORY
    # Function to fetch and display emails
    def fetch_emails():
        try:
            username = username_entry.get()
            # Read email files from the client_files directory
            email_files = os.listdir(os.path.join(DOWNLOAD_DIRECTORY, username))
            email_listbox.delete(0, tk.END)  # Clear the listbox
            for filename in email_files:
                if filename.endswith('.txt'):  # Assuming email files are .txt
                    file_path = os.path.join(DOWNLOAD_DIRECTORY, username, filename)
                    with open(file_path, 'r') as file:
                        log(f"Reading file: {filename}")
                        content = file.readlines()
                        if content:  # Check if the file is not empty
                            subject = content[0].strip()  # Assuming the first line is the title
                            email_listbox.insert(tk.END, f"{filename}: {subject}")
                        else:
                            log(f"File {filename} is empty.")
        except Exception as e:
            log(f"Error fetching emails: {e}")

    # Update the listbox with the current files in the DOWNLOAD_DIRECTORY
    fetch_emails()


    fetch_emails_button = ttk.Button(read_frame, text="Fetch Emails", command=fetch_emails)
    fetch_emails_button.grid(row=2, column=0, padx=5, pady=5)

    # Sending email frame
    send_frame = ttk.Frame(email_window)
    send_frame.pack(pady=10)

    recipient_label = ttk.Label(send_frame, text="Recipient:")
    recipient_label.grid(row=0, column=0, padx=5, pady=5)

    recipient_entry = ttk.Entry(send_frame)
    recipient_entry.grid(row=0, column=1, padx=5, pady=5)

    title_label = ttk.Label(send_frame, text="Email Title:")
    title_label.grid(row=1, column=0, padx=5, pady=5)

    title_entry = ttk.Entry(send_frame)
    title_entry.grid(row=1, column=1, padx=5, pady=5)

    email_content_label = ttk.Label(send_frame, text="Email Content:")
    email_content_label.grid(row=2, column=0, padx=5, pady=5)

    email_entry = tk.Text(send_frame, height=5, width=40)
    email_entry.grid(row=2, column=1, padx=5, pady=5)

    def send_email():
        try:
            username = username_entry.get()
            recipient = recipient_entry.get()
            title = title_entry.get()
            email_content = email_entry.get("1.0", tk.END).strip()
            log (email_content)
            if not recipient or not title or not email_content:
                messagebox.showwarning("Input Error", "Please enter recipient, title, and email content.")
                return

            log(f"Sending email to '{recipient}' with title '{title}'...")

            server_ip = server_ip_entry.get()
            server_port = int(server_port_entry.get())

            # email_message = f"{title}:{email_content}"  # Format of the email
            client_socket.sendto(f"SEND_EMAIL:{username}:{recipient}:{title}:{email_content}".encode(), (server_ip, server_port))
            log("Email sent.")
        except Exception as e:
            log(f"Error sending email: {e}")

    send_email_button = ttk.Button(send_frame, text="Send Email", command=send_email)
    send_email_button.grid(row=3, column=1, padx=5, pady=5)

def create_account():
    try:
        username = username_entry.get()
        password = password_entry.get()

        if not username or not password:
            messagebox.showwarning("Input Error", "Please enter both username and password.")
            return

        log(f"Creating account '{username}'...")

        server_ip = server_ip_entry.get()
        server_port = int(server_port_entry.get())

        global client_socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_socket.sendto(f"CREATE_ACCOUNT:{username}:{password}".encode(), (server_ip, server_port))

        response, _ = client_socket.recvfrom(BUFFER_SIZE)
        log(response.decode())
    except Exception as e:
        log(f"Error creating account: {e}")

def login_account():
    try:
        username = username_entry.get()
        password = password_entry.get()

        if not username or not password:
            messagebox.showwarning("Input Error", "Please enter both username and password.")
            return

        log(f"Logging into account '{username}'...")

        server_ip = server_ip_entry.get()
        server_port = int(server_port_entry.get())

        global client_socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_socket.sendto(f"LOGIN:{username}:{password}".encode(), (server_ip, server_port))

        response, _ = client_socket.recvfrom(BUFFER_SIZE)
        log(response.decode())

        if response.decode() == "Login successful":
            # catch all replies from the server
            while True:
                data, _ = client_socket.recvfrom(BUFFER_SIZE)
                if data.decode() == "END":
                    break
                LIST_OF_MAIL.append(data.decode())
                log(data.decode())
            for filename in LIST_OF_MAIL:
                request_file(filename)
                response, _ = client_socket.recvfrom(BUFFER_SIZE)
                if response.decode() =="END":
                    time.sleep(0.1)
                log(response.decode())

            create_email_window()  # Open the email window on successful login
    except Exception as e:
        log(f"Error logging in: {e}")

# Tkinter UI Setup
root = tk.Tk()
root.title("UDP File Client")
root.geometry("600x600")

# Modern theme
style = ttk.Style()
style.theme_use('clam')

# Server details frame
server_frame = ttk.Frame(root)
server_frame.pack(pady=10)

server_ip_label = ttk.Label(server_frame, text="Server IP:")
server_ip_label.grid(row=0, column=0, padx=5, pady=5)


server_ip_entry = ttk.Entry(server_frame)
server_ip_entry.grid(row=0, column=1, padx=5, pady=5)
server_ip_entry.insert(0, "10.60.236.235")  # Set default IP address

server_port_label = ttk.Label(server_frame, text="Server Port:")
server_port_label.grid(row=1, column=0, padx=5, pady=5)

server_port_entry = ttk.Entry(server_frame)
server_port_entry.grid(row=1, column=1, padx=5, pady=5)
server_port_entry.insert(0, "12345")  # Set default port



# User account frame
user_frame = ttk.Frame(root)
user_frame.pack(pady=10)

# Function to validate email
def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@mail\.com$'
    return re.match(pattern, email) is not None

# Function to handle email input
def handle_email_input(event):
    email = username_entry.get()
    if validate_email(email) == False:
        messagebox.showerror("Error", "Invalid email address. Please use an email ending with @mail.com.")

username_label = ttk.Label(user_frame, text="Email:")
username_label.grid(row=0, column=0, padx=5, pady=5)

username_entry = ttk.Entry(user_frame)
username_entry.grid(row=0, column=1, padx=5, pady=5)



password_label = ttk.Label(user_frame, text="Password:")
password_label.grid(row=1, column=0, padx=5, pady=5)

password_entry = ttk.Entry(user_frame, show='*')
password_entry.grid(row=1, column=1, padx=5, pady=5)

# Buttons for account management
create_account_button = ttk.Button(root, text="Create Account", command=create_account)
create_account_button.pack(pady=5)
create_account_button.bind("<Button-1>", handle_email_input)


login_account_button = ttk.Button(root, text="Login", command=login_account)
login_account_button.pack(pady=5)
# regex to validate email when pressing login
login_account_button.bind("<Button-1>", handle_email_input)

# Log display
log_frame = ttk.Frame(root)
log_frame.pack(pady=10, fill='both', expand=True)

log_label = ttk.Label(log_frame, text="Client Log")
log_label.pack(anchor='w')

log_textbox = tk.Text(log_frame, height=10, width=60)
log_textbox.pack(fill='both', expand=True)

root.mainloop()
