import socket
import threading

class Server():
    def __init__(self, max_load, max_message_bits) -> None:
        #   Preamble
        #   Initialize server parameters
        self.host = socket.gethostname()
        self.port = 1337
        self.max_load = max_load
        self.max_message_bits = max_message_bits
        self.client_sockets = set()
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)   #   Allows hot reloading of server, skip waiting for OS to release port
        self.server.bind((self.host, self.port))                            #   Binds server to host and port, telling OS to start server 
        self.exit_event = False

    # Helper method for listening to a connection
    def _listen(self, conn):
        while True:
            try:
                data = conn.recv(self.max_message_bits)
                if not data:
                    break
            except Exception as e:
                print(f"[!] Error: {e}")
                self._remove(conn)
                break
            else:
                self._broadcast(data.decode(), conn)
    
    #   Helper function for sending messages to all sockets in active connections
    def _broadcast(self, message, conn):
        for client in self.client_sockets:
            try:
                if client != conn:
                    client.send(message.encode())
            except Exception as e:
                print(f"[!] Error: {e}")
                self._remove(conn)
    
    #   Helper function for removing a socket from the active connections     
    def _remove(self, conn):
        try:
            conn.close()
        except Exception as e:
            print(f"[!] Error: {e}")
        finally:
            self.client_sockets.remove(conn)
    
    # Helper method for parsing messages from console to broadcast announcements to clients
    def announce(self):
        while not self.exit_event:
            message = input()
            if message.lower() == '':
                self.shutdown()
                break
            print(server_message := f"=> Server: {message}")
            self._broadcast(server_message, None)
    
    # Core method, running server instance
    def _accept_connections(self):
        connection_threads = []
        self.server.listen(self.max_load)
        print(f"[*] Listening as {self.host}:{self.port}")

        while not self.exit_event:
            try:
                client_socket, client_address = self.server.accept()
                print(f"[+] {client_address} connected.")
                self._broadcast(f"[+] A user has connected.\n", None)
                self.client_sockets.add(client_socket)

                # Spawn a new thread to listen to the requests of the new connection
                thread = threading.Thread(target=self._listen, args=(client_socket,))
                connection_threads.append(thread)
                thread.start()
            except Exception as e:
                print(f"[!] Error: {e}")
                break

        for thread in connection_threads:
            thread.join()

    #   Helper method to shutdown server and close all sockets
    def shutdown(self):
        self.exit_event = True
        for conn in self.client_sockets:
            conn.close()
        self.server.close()
        
if __name__ == "__main__":
        server_instance = Server(1000, 2048)

        # Create and start threads for listening to connections and announcing messages
        accept_thread = threading.Thread(target=server_instance._accept_connections)
        announce_thread = threading.Thread(target=server_instance.announce)

        accept_thread.start()
        announce_thread.start()

        # Wait for threads to finish
        accept_thread.join()
        announce_thread.join()

        # Shutdown the server after threads finish
        server_instance.shutdown()