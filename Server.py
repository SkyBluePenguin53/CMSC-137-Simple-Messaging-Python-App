import socket
from threading import Thread

#   Get computer IP address
host = socket.gethostname()
#   Set gateway
port = 1337
separator_token = "<SEP>"


#   Initialize list/set of all connected client's sockets
client_sockets = set()
#   Create TCP socket
s = socket.socket()
#   Reusable port
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#   Looks for any incoming connections
s.bind((host, port))
#   Five clients, one server
s.listen(5)

print(f"[*] Listening as {host}:{port}")


def listen(conn):
    while True:
        try:
            data = conn.recv(1024).decode()
        except Exception as e:
            print(f"[!] Error: {e}")
            client_sockets.remove(conn)
        else:
            data = data.replace(separator_token,": ")
        for client_socket in client_sockets:
            client_socket.send(data.encode())

while True:
    #   Keep listening for new connections always
    client_socket, client_address = s.accept()
    print(f"[+] {client_address} connected.")
    # add the new connected client to connected sockets
    client_sockets.add(client_socket)
    # start a new thread that listens for each client's messages
    t = Thread(target=listen, args=(client_socket,))
    # make the thread daemon so it ends whenever the main thread ends
    t.daemon = True
    # start the thread
    t.start()

# close client sockets
for conn in client_sockets:
    conn.close()
# close server socket
s.close()