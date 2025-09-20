# Zama FHE Demo: FHE Auction Duel – Secret Bidding Game
# Inspired by Zama Concrete & Deberrys auction (github.com/zama-ai/concrete)
# Prerequisite: python3.10 -m pip install -U pip wheel setuptools; python3.10 -m pip install concrete-python --index-url https://pypi.zama.ai/simple
# Run: python3.10 fhe_auction_duel.py

import sys
if sys.version_info.major != 3 or sys.version_info.minor not in [9, 10, 11, 12]:
    print("Error: Requires Python 3.9-3.12. Current version:", sys.version)
    print("Install Python 3.10 and run: python3.10 fhe_auction_duel.py")
    exit(1)

try:
    from concrete import fhe
    FHE_ENABLED = True
    print("FHE loaded successfully!")
except ImportError:
    print("Warning: FHE not available. Using mock mode.")
    print("Install with: python3.10 -m pip install -U pip wheel setuptools")
    print("python3.10 -m pip install concrete-python --index-url https://pypi.zama.ai/simple")
    FHE_ENABLED = False

try:
    import tkinter as tk
    from tkinter import messagebox
    TKINTER_ENABLED = True
except ImportError:
    print("Error: Tkinter not found. Install with: sudo apt-get install -y python3-tk")
    print("Falling back to console mode...")
    TKINTER_ENABLED = False

import random
import time

# FHE or Mock Auction Function
def auction_min(bid1, bid2):
    if FHE_ENABLED:
        compiler = fhe.Compiler(lambda x, y: x if x < y else y, {"bid1": "encrypted", "bid2": "encrypted"})
        inputset = [(i, j) for i in range(1, 21) for j in range(1, 21)]  # Small inputset for speed
        circuit = compiler.compile(inputset)
        circuit.keygen()
        encrypted_bid1, encrypted_bid2 = circuit.encrypt(bid1, bid2)
        encrypted_result = circuit.run(encrypted_bid1, encrypted_bid2)
        return circuit.decrypt(encrypted_result)
    return bid1 if bid1 < bid2 else bid2  # Mock

class AuctionDuel:
    def __init__(self):
        self.opponent_bid = random.randint(1, 100)
        if TKINTER_ENABLED:
            self.root = tk.Tk()
            self.root.title("FHE Auction Duel – Bid Secretly!")
            self.root.geometry("400x300")
            tk.Label(self.root, text=f"Bid 1-100 to win! {'FHE' if FHE_ENABLED else 'Mock'} mode.", font=("Arial", 14)).pack(pady=10)
            self.bid_entry = tk.Entry(self.root)
            self.bid_entry.pack(pady=5)
            tk.Button(self.root, text="Place Secret Bid", command=self.place_bid).pack(pady=10)
            self.status_label = tk.Label(self.root, text="Waiting for opponent...", font=("Arial", 10))
            self.status_label.pack(pady=5)
            self.result_label = tk.Label(self.root, text="", font=("Arial", 12), fg="green")
            self.result_label.pack(pady=10)
        else:
            self.running = True

    def place_bid(self):
        if TKINTER_ENABLED:
            try:
                my_bid = int(self.bid_entry.get())
                if 1 <= my_bid <= 100:
                    self.status_label.config(text="Encrypting & comparing bids...")
                    self.root.update()
                    time.sleep(1)
                    winner_bid = auction_min(my_bid, self.opponent_bid)
                    if my_bid == winner_bid:
                        self.result_label.config(text=f"You won with bid {my_bid}! Opponent: {self.opponent_bid}")
                        messagebox.showinfo("Win!", f"{'FHE' if FHE_ENABLED else 'Mock'} kept bids secret!")
                    else:
                        self.result_label.config(text=f"You lost. Opponent won with {winner_bid} (your bid: {my_bid})")
                        messagebox.showinfo("Lost!", "Try again – bids were hidden!")
                    self.status_label.config(text="New round? Clear and bid again!")
                else:
                    self.status_label.config(text="Bid 1-100 only!", fg="red")
            except ValueError:
                self.status_label.config(text="Enter a number!", fg="red")
        else:
            while self.running:
                try:
                    my_bid = int(input("Enter your bid (1-100, or 0 to quit): "))
                    if my_bid == 0:
                        self.running = False
                        break
                    if 1 <= my_bid <= 100:
                        time.sleep(1)
                        winner_bid = auction_min(my_bid, self.opponent_bid)
                        if my_bid == winner_bid:
                            print(f"You won with bid {my_bid}! Opponent: {self.opponent_bid}")
                        else:
                            print(f"You lost. Opponent won with {winner_bid} (your bid: {my_bid})")
                        print("New round? Enter next bid or 0 to quit.")
                    else:
                        print("Bid 1-100 only!")
                except ValueError:
                    print("Enter a number!")

    def run(self):
        if TKINTER_ENABLED:
            self.root.mainloop()
        else:
            self.place_bid()

if __name__ == "__main__":
    game = AuctionDuel()
    game.run()
