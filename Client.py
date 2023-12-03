import socket
import tkinter as tk
from tkinter import Text, Button
import threading

""" class GUI(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Simple Tkinter GUI")

        self.label = tk.Label(self, text="Enter your name:")
        self.label.pack(pady=10)

        self.name_entry = tk.Entry(self)
        self.name_entry.pack(pady=10)

        self.greet_button = tk.Button(self, text="Greet", command=self.greet)
        self.greet_button.pack(pady=10)

        self.quit_button = tk.Button(self, text="Quit", command=self.quit)
        self.quit_button.pack(pady=10)
        self.mainloop()

    def greet(self):
        name = self.name_entry.get() """
        

class Client:
    def __init__(self, max_message_bits) -> None:
        self.chatlog = self.textbox = None
        self.host = socket.gethostname()
        self.port = 1337
        self.max_message_bits = max_message_bits
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(f"[*] Connecting to {self.host}:{self.port}...")
        self.server.connect((self.host, self.port))
        print("[+] Connected.")
        self.name = input("Enter your preferred name: ")
        self.queue = []
        self.lock = threading.Lock()
        self.gui = self.GUI()

    def GUI(self):
        self.gui = tk.Tk()
        self.gui.title("OG Server")
        self.gui.geometry("400x410")

        self.chatlog = Text(self.gui, bg='white')
        self.chatlog.config(state=tk.DISABLED)

        self.send_button = Button(self.gui, bg='black', fg='gold', text="SEND", command=self._send)
        self.textbox = Text(self.gui, bg='white')

        self.chatlog.place(x=6, y=6, width='386', height='370')
        self.textbox.place(x=6, y=380, height=20, width=330)
        self.send_button.place(x=341, y=380, height=20, width=50)

        self.textbox.bind("<KeyRelease-Return>", self.press)

        threading.Thread(target=self._listen, daemon=True).start()

        # Periodically check for new messages and update the chat log
        #self.gui.after(100, self.check_for_messages)

        self.gui.mainloop()

    def press(self, event):
        self._send()

    def update_chat(self, msg):
        self.chatlog.config(state=tk.NORMAL)
        self.chatlog.insert(tk.END, msg)
        self.chatlog.config(state=tk.DISABLED)
        self.chatlog.yview(tk.END)

    """ def check_for_messages(self):
        with self.lock:
            for msg in self.queue:
                self.update_chat(msg)
            self.queue.clear()
        self.gui.after(100, self.check_for_messages) """

    def _listen(self):
        while True:
            try:
                data = self.server.recv(self.max_message_bits)
                if data:
                    #print("\n" + data.decode())
                    """ with self.lock:
                        self.queue.append(data) """
                    self.update_chat(data)
            except Exception as e:
                print(f"[!] Error: {e}")
                break

    def _send(self):
        to_send = self.textbox.get("0.0", tk.END)
        if to_send.lower() == '':
            print("Client disconnecting. Attempting to disconnect from the server...")
            self._close_client()
        else:
            to_send = f"=> {self.name}: {to_send}"
            """ with self.lock:
                self.queue.append(to_send) """
            self.update_chat(to_send)
            self.textbox.delete("0.0", tk.END)
            try:
                self.server.send(to_send.encode())
            except Exception as e:
                print(f"[!] Error sending message: {e}")

    def _close_client(self):
        self.server.close()

if __name__ == "__main__":
    instance = Client(2048)
