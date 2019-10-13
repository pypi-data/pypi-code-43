import getpass
import os
import signal
import socket
import subprocess
import sys
import threading

from cryptography.fernet import Fernet

HOME = f"/Users/{getpass.getuser()}"

def signal_handler(sig, frame):
    os._exit(1)

# message statuses (each is first byte of message):
# 1 - message received
# 2 - someone joined/left the server

def handle_client_message(clientsocket, address):
    """
    Send recieved message back to 
    client and also print to console
    """
    n_messages = 0
    username = ""
    while True:
        msg = clientsocket.recv(1024)
        if msg != b'':
            if n_messages == 0:
                username = msg.decode("utf-8")
                msg = "2" + username + " has joined the server!"
                for c in clientsockets[:-1]:
                    c.send(bytes(msg, "utf-8"))
            else:
                msg = f"1{username}: " + msg.decode("utf-8")
                for c in clientsockets:
                    c.send(bytes(msg, "utf-8"))

            n_messages += 1
        else:
            clientsocket.close()
            clientsockets.remove(clientsocket)
            addresses.remove(address)
            print(f"Connection for {address} has been severed")
            for c in clientsockets:
                c.send(bytes("2" + username + " has left the server", "utf-8"))
            break

def create_connections():
    """
    Constantly look for clients to connect with
    """
    while True:
        clientsocket, address = s.accept()
        print(f"Connection from {address} has been established!")
        clientsockets.append(clientsocket)
        addresses.append(address)
        hcm = threading.Thread(target=handle_client_message, args=(clientsocket, address))
        hcm.start()

if __name__ == "__main__":

    signal.signal(signal.SIGINT, signal_handler)
    
    os.system("stty -echo")
    password = input("Password: ")
    os.system("stty echo")
    print()
    
    with open(f"{HOME}/.chat-app.key", "rb") as f:
        key = f.read()
    
    fernet = Fernet(key)
    
    # read encrypted message
    with open(f'{HOME}/.chat-app-user-secrets', 'rb') as f:
        encrypted = f.read()

    if password == fernet.decrypt(encrypted).decode("utf-8"):

        ip = subprocess.check_output(
                "ifconfig | grep \"...\....\..\....\" | cut -d ' ' -f2",
                shell=True).decode("utf-8")[:-1] 
        port = input("port: ")

        # create socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((ip, int(port)))
        s.listen(5)
        
        print("Server successfully created")
 
        # client info
        clientsockets = []
        addresses = []

        create_connections()
    else:
        print('\033[1;31mincorrect password\033[0m')
