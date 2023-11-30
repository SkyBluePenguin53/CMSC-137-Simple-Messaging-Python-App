import socket
from threading import Thread
import asyncio

class Server():
    def __init__(self, max_load, max_message_bits) -> None:
        #   Preamble
        #   Initialize server parameters
        self.host = socket.gethostname()
        self.port = 1337
        self.separator_token = "<SEP>"
        self.max_load = max_load
        self.max_message_bits = max_message_bits
        self.client_sockets = set()
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)   #   Allows hot reloading of server, skip waiting for OS to release port
        self.server.bind((self.host, self.port))                            #   Binds server to host and port, telling OS to start server 
        self.exit_event = asyncio.Event()

    #   Helper method for listening to a connection
    #   TODO: Handle [error] exiting socking from client gracefully
    async def _listen(self, conn):
        while True:
            try:
                data = await asyncio.to_thread(conn.recv, self.max_message_bits)
            except Exception as e:
                print(f"[!] Error: {e}")
                self._remove(conn)
            else:
                self._broadcast(data.decode(), conn)

    #   Helper function for sending messages to all sockets in active connections
    def _broadcast(self, message, conn):
        message = message.replace(self.separator_token, ": ")
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
    
    # async def _receive_control_signals(self):
    #     loop = asyncio.get_running_loop()
    #     while not self.exit_event.is_set():
    #         command = await loop.run_in_executor(None, input)

    #         if command.lower() == 'exit':
    #             print("Exiting server...")
    #             self.exit_event.set()
    #         else:
    #             print(f"Unknown command: {command}")
                
    #   Core method, running server instance
    async def _accept_connections(self):
        connection_tasks = []
        #   Listen to a maximum of max_load connections
        self.server.listen(self.max_load)

        print(f"[*] Listening as {self.host}:{self.port}")

        while not self.exit_event.is_set():
            try:
                # The accept() method of a Socket object stores two parameters
                # connection -> socket object of the client
                # address -> IP address of the client
                client_socket, client_address = await asyncio.to_thread(self.server.accept)

                print(f"[+] {client_address} connected.")

                # Maintain a list of active connections to the server
                self.client_sockets.add(client_socket)

                # Spawn a new thread to listen to the requests of the new connection
                task = asyncio.create_task(self._listen(client_socket))
                connection_tasks.append(task)
            except Exception as e:
                print(f"[!] Error: {e}")
        await asyncio.gather(*connection_tasks)

    #   TODO: Diagnose "Exiting server..." inifnite loop (?) -> doesn't really affect execution but still annoying
    async def _run_server(self):
        tasks = [self._accept_connections()]
        await asyncio.gather(*tasks)
        # Make sure to wait for all client connections to be closed
        await asyncio.gather(*(asyncio.to_thread(conn.close) for conn in self.client_sockets))
        self.server.close()

    
if __name__ == "__main__":
    server_instance = Server(1000, 2048)
    asyncio.run(server_instance._run_server())