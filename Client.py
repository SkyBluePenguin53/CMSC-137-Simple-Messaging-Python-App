import socket
import threading

class Client():
    def __init__(self, max_message_bits) -> None:
        #   Preamble
        #   Initialize client parameters
        self.host = socket.gethostname()
        self.port = 1337
        self.max_message_bits = max_message_bits
        self.separator_token = "<SEP>"
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(f"[*] Connecting to {self.host}:{self.port}...")
        self.server.connect((self.host, self.port))
        print("[+] Connected.")
        self.name = input("Enter your preferred name: ")
    
    # Helper method for listening to server broadcasts
    def _listen(self):
        while True:
            try:
                data = self.server.recv(self.max_message_bits)
                if not data:
                    break
                print("\n" + data.decode())
            except Exception as e:
                print(f"[!] Error: {e}")
                break
        print("Server disconnected. Closing client.")
        self._close_client()
        
    # Helper method to send messages to the server
    def _send(self):
        while True:
            to_send = input()
            if to_send.lower() == '':
                print("Client disconnecting. Attempting to disconnect from server...")
                self._close_client()
                break
            to_send = f"=> {self.name}{self.separator_token}{to_send}"
            self.server.send(to_send.encode())

    def _close_client(self):
        self.server.close()
        #exit()

if __name__ == "__main__":
        instance = Client(2048)

        # Create and start threads for listening to server broadcasts and sending messages
        listen_thread = threading.Thread(target=instance._listen)
        send_thread = threading.Thread(target=instance._send)

        listen_thread.start()
        send_thread.start()

        # Wait for threads to finish
        listen_thread.join()
        send_thread.join()

        # Close the client after threads finish
        instance._close_client()