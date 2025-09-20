# Zama FHE Demo: Guess the Secret Score Game with GUI & Multiplayer
# Inspired by Zama Concrete docs (github.com/zama-ai/concrete)
# Prerequisite: Run in Codespaces – dependencies auto-installed
# Run: python fhe_game_demo.py single

from concrete import fhe  # Import from concrete-python
import tkinter as tk
from tkinter import messagebox
import socket
import random

# FHE Comparison Function
def compare_scores(guess, secret):
    return 1 if guess < secret else 0  # 1 = lower, 0 = higher/equal

# Compile FHE circuit
compiler = fhe.Compiler(compare_scores, {"guess": "encrypted", "secret": "encrypted"})
inputset = [(i, j) for i in range(11) for j in range(11)]  # Input set for 0-10
circuit = compiler.compile(inputset)
circuit.keygen()  # Generate keys

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
                encrypted_guess, encrypted_secret = circuit.encrypt(guess, self.secret_score)
                encrypted_result = circuit.run(encrypted_guess, encrypted_secret)
                result = circuit.decrypt(encrypted_result)
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
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(('localhost', 12345))
            sock.send(str(self.entry.get()).encode())
            feedback = sock.recv(1024).decode()
            self.feedback_label.config(text=feedback)
            sock.close()
        except:
            messagebox.showerror("Error", "Server not running! Run server mode first.")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    import sys
    mode = sys.argv[1] if len(sys.argv) > 1 else "single"
    if mode == "server":
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('localhost', 12345))
        server.listen(1)
        conn, addr = server.accept()
        guess = int(conn.recv(1024).decode())
        encrypted_guess, encrypted_secret = circuit.encrypt(guess, random.randint(0, 10))
        encrypted_result = circuit.run(encrypted_guess, encrypted_secret)
        result = circuit.decrypt(encrypted_result)
        feedback = "Lower!" if result == 1 else "Higher or Equal!"
        conn.send(feedback.encode())
        conn.close()
        print("Server done – FHE comparison complete!")
    else:
        game = FHEGame(mode)
        game.run()
