# Zama FHE Demo: Guess the Secret Score Game with GUI & Multiplayer
# Inspired by Zama Concrete docs (github.com/zama-ai/concrete)
# Run: pip install concrete-compiler; python fhe_game_demo.py (server) or client mode

from concrete import fhe
import tkinter as tk
from tkinter import messagebox
import socket
import threading
import random

# FHE Comparison Function
@fhe.compiler({"guess": "encrypted", "secret": "encrypted"})
def compare_scores(guess, secret):
    return 1 if guess < secret else 0  # 1 = guess lower, 0 = higher/equal

compiled_compare = compare_scores.compile((5, 5))  # Compile for 0-10 range

class FHEGame:
    def __init__(self, mode="single"):
        self.mode = mode
        self.secret_score = random.randint(0, 10)
        self.root = tk.Tk()
        self.root.title("Zama FHE Game: Guess the Secret Score!")
        self.root.geometry("300x200")
        tk.Label(self.root, text="Guess 0-10 (FHE keeps it secret!)", font=("Arial", 12)).pack(pady=10)
        self.entry = tk.Entry(self.root)
        self.entry.pack(pady=5)
        tk.Button(self.root, text="Guess", command=self.make_guess).pack(pady=5)
        self.feedback_label = tk.Label(self.root, text="", font=("Arial", 10), fg="blue")
        self.feedback_label.pack(pady=5)
        if mode == "multi":
            tk.Button(self.root, text="Connect to Friend", command=self.connect_multi).pack(pady=5)

    def make_guess(self):
        try:
            guess = int(self.entry.get())
            if 0 <= guess <= 10:
                encrypted_guess = fhe.encrypt(guess, compiled_compare)
                encrypted_secret = fhe.encrypt(self.secret_score, compiled_compare)
                result = compiled_compare(encrypted_guess, encrypted_secret)
                feedback = "Lower!" if result == 1 else "Higher or Equal!"
                self.feedback_label.config(text=feedback)
                if guess == self.secret_score:
                    messagebox.showinfo("Win!", f"Correct! Secret: {self.secret_score}\nFHE protected it!")
                    self.root.quit()
            else:
                self.feedback_label.config(text="0-10 only!", fg="red")
        except ValueError:
            self.feedback_label.config(text="Enter a number!", fg="red")

    def connect_multi(self):
        # Simple multiplayer: Connect to server for Player 2's secret
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(('localhost', 12345))  # Assume server running
            # Send guess, receive encrypted result (simplified)
            sock.send(str(self.entry.get()).encode())
            feedback = sock.recv(1024).decode()
            self.feedback_label.config(text=feedback)
            sock.close()
        except:
            messagebox.showerror("Error", "Server not running! Run server mode first.")

    def run(self):
        self.root.mainloop()

# Run as Server (for Multiplayer)
if __name__ == "__main__":
    import sys
    mode = sys.argv[1] if len(sys.argv) > 1 else "single"
    if mode == "server":
        # Simple server for Player 2's secret
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('localhost', 12345))
        server.listen(1)
        conn, addr = server.accept()
        guess = int(conn.recv(1024).decode())
        encrypted_guess = fhe.encrypt(guess, compiled_compare)
        encrypted_secret = fhe.encrypt(random.randint(0, 10), compiled_compare)
        result = compiled_compare(encrypted_guess, encrypted_secret)
        feedback = "Lower!" if result == 1 else "Higher or Equal!"
        conn.send(feedback.encode())
        conn.close()
        print("Server done – FHE comparison complete!")
    else:
        game = FHEGame(mode)
        game.run()
