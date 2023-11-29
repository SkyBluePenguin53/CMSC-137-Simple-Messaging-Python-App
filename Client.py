import socket
from threading import Thread

#   Get computer IP address
host = socket.gethostname()
#   Set gateway
port = 1337
separator_token = "<SEP>"


#   initialize TCP socket
s = socket.socket()
print(f"[*] Connecting to {host}:{port}...")
#   Connects to a server
s.connect((host, port))
print("[+] Connected.")

name = input("Enter your preferred name: ")
   
def listen():
    while True:
        data = s.recv(1024).decode()
        print("\n" + data)
        
t = Thread(target = listen)
t.daemon = True
t.start()

while True:
    # input message we want to send to the server
    to_send =  input()
    # a way to exit the program
    if to_send.lower() == '[exit]':
        break
    to_send = f"=> {name}{separator_token}{to_send}"
    # finally, send the message
    s.send(to_send.encode())

# close the socket
s.close()