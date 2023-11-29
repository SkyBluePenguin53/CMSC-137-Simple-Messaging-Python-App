import socket
from threading import Thread

class Server():
    def __init__(self, max_load) -> None:
        #   Preamble
        #   Initialize server parameters
        self.host = socket.gethostname()
        self.port = 1337
        self.separator_token = "<SEP>"
        self.max_load = max_load
        self.max_message_bits = 2048
        self.client_sockets = set()
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)   #   Allows hot reloading of server, skip waiting for OS to release port
        self.server.bind((self.host, self.port))                            #   Binds server to host and port, telling OS to start server 
        self._exit_flag = False
        self._run_server()

    #   Helper method for listening to a connection
    #   TODO: Handle [error] exiting socking from client gracefully
    def _listen(self, conn):
        while True:
            try:
                data = conn.recv(self.max_message_bits).decode()
            except Exception as e:
                print(f"[!] Error: {e}")
                self.client_sockets.remove(conn)
                print(self.client_sockets)
            else:
                self._broadcast(data, conn)

    #   Helper function for sending messages to all sockets in active connections
    def _broadcast(self, message, conn):
        message = message.replace(self.separator_token, ": ")
        for client in self.client_sockets:
            try:
                client.send(message.encode())
            except Exception as e:
                print(f"[!] Error: {e}")
                self._remove(conn)
    
    #   Helper function for removing a socket from the active connections     
    def _remove(self, conn):
        try:
            conn.close()
        except:
            pass    ##  TODO: add proper error handling if conn.close() unexpectedly fails
        finally:
            self.client_sockets.remove(conn)
    
    def _console_input(self):
        while True:
            command = input()
            if command.lower() == 'exit':
                print("Exiting server...")
                self._exit_server()
                break
            else:
                print(f"Unknown command: {command}")
                
    #   Core method, running server instance
    def _run_server(self):
        #   Listen to a maximum of max_load connections
        self.server.listen(self.max_load)

        print(f"[*] Listening as {self.host}:{self.port}")
        
        console_thread = Thread(target=self._console_input)
        console_thread.daemon = True
        console_thread.start()

        try:
            while not self._exit_flag:
                # The accept() method of a Socket object stores two parameters
                # connection -> socket object of the client
                # address -> IP address of the client
                client_socket, client_address = self.server.accept()

                if self._exit_flag:
                    break  # Exit the loop if the exit flag is set

                print(f"[+] {client_address} connected.")

                # Maintain a list of active connections to the server
                self.client_sockets.add(client_socket)

                # Spawn a new thread to listen to the requests of the new connection
                client_thread = Thread(target=self._listen, args=(client_socket,))

                # Daemon threads end whenever the main thread ends
                client_thread.daemon = True

                client_thread.start()

        except Exception as e:
            print(f"[!] Error: {e}")

        # Call the exit method to close remaining connections and sockets
        self._exit_server()
    
    ##  TODO: Call this method when exiting server frontend
    ##  FIX: Handling closed sockets
    def _exit_server(self):
        self._exit_flag = True
        #   Close all sockets in client_sockets
        if len(self.client_sockets) > 0:
            for conn in self.client_sockets:
                conn.close()
        # close server socket
        self.server.close()

instance = Server(1000)