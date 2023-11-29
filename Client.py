import socket
import asyncio
from threading import Thread
from aioconsole import ainput

class Client():
    def __init__(self) -> None:
        #   Preamble
        #   Initialize client parameters
        self.host = socket.gethostname()
        self.port = 1337
        self.max_message_bits = 2048
        self.separator_token = "<SEP>"
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(f"[*] Connecting to {self.host}:{self.port}...")
        self.server.connect((self.host, self.port))
        print("[+] Connected.")
        self.name = input("Enter your preferred name: ")
        
        self._run_client()
    
    #   Helper method for listening to server broadcasts
    async def _listen(self):
        while True:
            try:
                data = await asyncio.to_thread(self.server.recv, self.max_message_bits)     #   Receive messages from server asynchronously
                if not data:
                    break
                print("\n" + data.decode())
            except ConnectionAbortedError:
                print("Server disconnected. Closing client.")
                self._close_client()
                break
    
    #   Helper method to send messages to the server
    async def _send(self):
        while True:
            to_send = await ainput()    #   Asynchronous equivalent to input()
            if to_send.lower() == '[exit]':
                self._close_client()
                break
            to_send = f"=> {self.name}{self.separator_token}{to_send}"
            self.server.send(to_send.encode())

    #   Core method to run both listen and send at the same time asynchronously
    def _run_client(self):
        #   Use asynchronous looping to listen for and send messages at the same time
        loop = asyncio.get_event_loop()
        tasks = [self._listen(), self._send()]
        loop.run_until_complete(asyncio.gather(*tasks))

    def _close_client(self):
        self.server.close()

instance = Client()
