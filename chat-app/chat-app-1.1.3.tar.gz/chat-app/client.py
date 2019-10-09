import getpass
import signal
import socket
import os
import threading

from cryptography.fernet import Fernet

HOME = f"/Users/{getpass.getuser()}"

def signal_handler(sig, frame):
    print("\033[A                             \033[A")
    print("exiting the server...")
    os._exit(1)

def send_messages():
    """
    Sends input to server which
    sends to other clients
    """
        
    def get_input():
        msg = input("")
        if msg != "":
            s.send(bytes(msg, "utf-8"))
        print("\033[A                             \033[A")

    while True:
        ipt = threading.Thread(target=get_input)
        is_writing = threading.Thread(target=get_typing)        

       
def receive_messages(username):
    """
    Constantly reveieves data from
    server and prints to console
    """
    while True:
        data = s.recv(1024).decode("utf-8")
        if data[0] == "1":
            user = data[1:].split(": ")[0] + ": "
            message = data[1:][len(user):]
            if user[:-2] != username:
                print(f"\033[1;34m{user}\033[0m{message}")
            else:  # message was sent by user
                print(f"\033[1;32m{user}\033[0m{message}")
        elif data[0] == "2":
            if "joined the server" in data:
                print(f"\033[32m{data[1:]}\033[0m")
            else:
                print(f"\033[31m{data[1:]}\033[0m")


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
    
        server = input("server: ")
        port = input("port: ")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((server, int(port)))
        print("\033[1;32mSuccessfully connected to the server!\033[0m")   
        
        username = input("username: ")
        s.send(bytes(username, 'utf-8'))    

        sm = threading.Thread(target=send_messages)
        rm = threading.Thread(target=receive_messages, args=[username])
        sm.start()
        rm.start()
    else:
        print('incorrect password')
