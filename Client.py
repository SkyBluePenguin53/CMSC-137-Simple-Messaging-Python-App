import socket
import tkinter as tk
import threading
from tkinter import Text, Button, simpledialog
import random

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

        #   Use a pop-up dialog to get the user's name
        self.name = self._get_user_name()

        self.queue = []
        self.lock = threading.Lock()
        self.gui = self._GUI()

    #   Helper method to fetch the user's name from GUI
    def _get_user_name(self):
        default_names = self._get_default_names()
        user_name = simpledialog.askstring("*", "Enter your preferred name:")
        if user_name:
            return user_name
        else:
            # If the user closes the dialog without entering a name, provide a random name
            return random.choice(default_names)
    
    #   Helper method to fetch default names from a text file    
    def _get_default_names(self):
        try:
            with open("names.txt", "r") as file:
                return [line.strip() for line in file.readlines()]
        except FileNotFoundError:
            print("Default names file not found.")
            return ["Anonymous"]

    #   Set GUI main loop
    def _GUI(self):
        self.gui = tk.Tk()
        self.gui.title(self.name)
        self.gui.geometry("400x410")

        self.chatlog = Text(self.gui, bg='white')
        self.chatlog.config(state=tk.DISABLED)

        self.send_button = Button(self.gui, bg='black', fg='gold', text="SEND", command=self._send)
        self.textbox = Text(self.gui, bg='white')

        self.chatlog.place(x=6, y=6, width='386', height='370')
        self.textbox.place(x=6, y=380, height=20, width=330)
        self.send_button.place(x=341, y=380, height=20, width=50)

        self.textbox.bind("<KeyRelease-Return>", self._press)

        threading.Thread(target=self._listen, daemon=True).start()

        self.gui.mainloop()

    #   Helper method to associate an event with keypress
    def _press(self, event):
        self._send()

    #   Helper method to update the chatlog
    def _update_chat(self, msg):
        self.chatlog.config(state=tk.NORMAL)
        self.chatlog.insert(tk.END, msg)
        self.chatlog.config(state=tk.DISABLED)
        self.chatlog.yview(tk.END)

    #   Helper method to listen for broadcasts from the server
    def _listen(self):
        while True:
            try:
                data = self.server.recv(self.max_message_bits)
                if data:
                    self._update_chat(data.decode())
            except Exception as e:
                print(f"[!] Error: {e}")
                break
    
    #   Helper method to send messeges to the server
    def _send(self):
        to_send = self.textbox.get("0.0", tk.END)
        to_send = f"=> {self.name}: {to_send}"
        self._update_chat(to_send)
        self.textbox.delete("0.0", tk.END)
        try:
            self.server.send(to_send.encode())
        except Exception as e:
            print(f"[!] Error sending message: {e}")

if __name__ == "__main__":
    instance = Client(2048)

