import socket
import tkinter as tk
import threading
from tkinter import Text, Button

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
        self.connected_users = {}
        self.first_time_send = True
        self.gui = self._GUI()
        
    def _GUI(self):
        self.gui = tk.Tk()
        self.gui.title("Server")
        self.gui.geometry("400x360")
        self.gui.eval('tk::PlaceWindow . center')

        self.chatlog = Text(self.gui, bg='white', width=200, height=20)
        self.chatlog.config(state=tk.DISABLED)
        self.chatlog.pack(side = tk.TOP, padx=5, pady=5)

        self.send_button = Button(self.gui, bg='black', fg='white', text="SEND", command=self.announce)
        self.send_button.pack(side = tk.RIGHT, padx=5, pady=5)
        
        self.textbox = Text(self.gui, bg='white', width=200, height=1)
        self.textbox.pack(side = tk.LEFT, padx=5, pady=5)
        self.textbox.focus_set()
        
        self.textbox.bind("<Return>", self._press)
        
        # Create and start threads for listening to connections and announcing messages
        accept_thread = threading.Thread(target=self._accept_connections, daemon = True)
        announce_thread = threading.Thread(target=self._press, daemon = True)

        accept_thread.start()
        announce_thread.start()

        self.gui.mainloop()
    
    #   Updates the tkinter Text as chatlog
    def _update_chat(self, msg):
        self.chatlog.config(state=tk.NORMAL)
        self.chatlog.insert(tk.END, msg)
        self.chatlog.config(state=tk.DISABLED)
        self.chatlog.yview(tk.END)

    #   Helper method to associate an event with keypress
    def _press(self, event=None):
        #   Prevents the thread to immediately execute the function after running 
        self.announce() if not self.first_time_send else setattr(self, 'first_time_send', False)
        #   Prevents a newline bug in the console log
        return 'break'

            

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
        message = message.encode()
        self._update_chat(message)
        for client in self.client_sockets:
            try:
                if client != conn:
                    client.send(message)
            except Exception as e:
                print(f"[!] Error: {e}")
                self._remove(conn)
    
    #   Helper function for removing a socket from the active connections     
    def _remove(self, conn):
        try:
            name = self.connected_users[conn]
            del self.connected_users[conn]
            self._broadcast(f"[-] {name} has disconnected.\n", None)
            conn.close()
        except Exception as e:
            print(f"[!] Error: {e}")
        finally:
            self.client_sockets.remove(conn)
    
    # Helper method for parsing messages from console to broadcast announcements to clients
    def announce(self):
        #while not self.exit_event:
        message = self.textbox.get("0.0", tk.END)
        self.textbox.delete("0.0", tk.END)
        server_message = f"[O] Server: {message}"
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
                #self._broadcast(f"[+] A user has connected.\n", None)
                self.client_sockets.add(client_socket)
                
                client_handling = threading.Thread(target=self.client_name, args=(client_socket,))
                connection_threads.append(client_handling)
                client_handling.start()

                # Spawn a new thread to listen to the requests of the new connection
                thread = threading.Thread(target=self._listen, args=(client_socket,))
                connection_threads.append(thread)
                thread.start()
            except Exception as e:
                print(f"[!] Error: {e}")
                break

        for thread in connection_threads:
            thread.join()
            
    def client_name(self, client_socket):
        # Receive data from the client (name)
        name = client_socket.recv(2048).decode()
        self.connected_users.update({client_socket: name})
        self._broadcast(f"[+] Welcome to the chat, {name}!\n", None)

    #   Helper method to shutdown server and close all sockets
    def shutdown(self):
        self.exit_event = True
        for conn in self.client_sockets:
            conn.close()
        self.server.close()
        
if __name__ == "__main__":
    server_instance = Server(1000, 2048)