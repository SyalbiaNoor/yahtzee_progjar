import tkinter as tk
from tkinter import messagebox, simpledialog
import socket
import threading
import pickle
from gamestate import GameState

# Represent the dots of each die face using ASCII-style visuals
DICE_DOTS = {
    1: ["     ", "  ●  ", "     "],
    2: ["●    ", "     ", "    ●"],
    3: ["●    ", "  ●  ", "    ●"],
    4: ["●   ●", "     ", "●   ●"],
    5: ["●   ●", "  ●  ", "●   ●"],
    6: ["●   ●", "●   ●", "●   ●"]
}

class YahtzeeClientGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Yaht-Z by Group 9")
        self.root.resizable(False, False)

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.room_code = None
        self.player_name = None
        self.gamestate: GameState = None

        self.locked = [False]*5 
        self.dice_buttons = []
        self.score_labels = {}

        self.network_setup()

        self.root.protocol("WM_DELETE_WINDOW", self.cleanup_and_quit)

    def network_setup(self):
        """Dialog for create/join room"""
        self.player_name = simpledialog.askstring("Name", "Enter your name:", parent=self.root)
        res = messagebox.askquestion("Create or Join", "Create new room?\nYes=create, No=join")

        host, port = "localhost", 9009
        self.sock.connect((host, port))

        # Send request to create or join room
        if res == "yes":
            self.sock.sendall(pickle.dumps({"action":"create", "name":self.player_name}))
        else:
            code = simpledialog.askstring("Room Code", "Enter 4-digit room code:", parent=self.root)
            self.sock.sendall(pickle.dumps({"action":"join", "name":self.player_name, "code":code}))

        resp = pickle.loads(self.sock.recv(4096))
        if resp.get("status") in ("created","joined"):
            self.room_code = resp["code"]
            messagebox.showinfo("Room Joined", f"Room code: {self.room_code}")
            threading.Thread(target=self.wait_for_updates, daemon=True).start()
            self.game_ui()
        else:
            messagebox.showerror("Error", resp.get("message","Cannot join room"))
            self.root.destroy()

    def game_ui(self):
        """Builds the main game UI with dice, scores, and labels"""
        self.turn_label = tk.Label(self.root, text="", font=("Arial", 14, "bold"))
        self.turn_label.pack(pady=8)

        self.name_label = tk.Label(self.root, text="", font=("Arial", 11))
        self.name_label.pack(pady=(0, 4))

        # Dice area
        dice_frame = tk.Frame(self.root)
        dice_frame.pack(pady=5)
        for i in range(5):
            btn = tk.Button(dice_frame, text=" ", font=("Courier",12),
                            width=7,height=4,
                            command=lambda i=i: self.toggle_lock(i))
            btn.grid(row=0, column=i, padx=5)
            self.dice_buttons.append(btn)

        # Rolling info
        self.rolls_left_label = tk.Label(self.root, text="", font=('Arial',11))
        self.rolls_left_label.pack(pady=(10,5))
        self.roll_button = tk.Button(self.root, text="Roll", font=("Arial",12,"bold"), width=10, command=self.send_roll)
        self.roll_button.pack(pady=(0,15))

        # Score headers
        header_frame = tk.Frame(self.root)
        header_frame.pack()
        tk.Label(header_frame, text="Category", width=15).grid(row=0, column=0)
        tk.Label(header_frame, text="You", width=10).grid(row=0, column=1)
        tk.Label(header_frame, text="Opponent", width=10).grid(row=0, column=2)

        # Score categories
        self.score_frame = tk.Frame(self.root)
        self.score_frame.pack(pady=5)

        categories = [
            ("ones","Ones"), ("twos","Twos"), ("threes","Threes"), ("fours","Fours"), ("fives","Fives"), ("sixes","Sixes"), ("three_of_kind","3 of a Kind"),
            ("four_of_kind","4 of a Kind"), ("full_house","Full House"), ("small_straight","Sm Straight"), ("large_straight","Lg Straight"), ("yahtzee","Yahtzee"), ("chance","Chance")
        ]

        for i, (key, label) in enumerate(categories):
            tk.Label(self.score_frame, text=label, width=15, anchor='w').grid(row=i, column=0)
            own_lbl = tk.Label(self.score_frame, text="", width=10, relief="groove")
            opp_lbl = tk.Label(self.score_frame, text="", width=10, relief="groove")
            own_lbl.grid(row=i, column=1, padx=2)
            opp_lbl.grid(row=i, column=2, padx=2)
            self.score_labels[key] = (own_lbl, opp_lbl)

        # Info display
        self.info_label = tk.Label(self.root, text="", font=("Arial",11))
        self.info_label.pack(pady=5)

        # Total scoring
        self.subtotal_label = tk.Label(self.root, text="Subtotal: 0", font=("Arial", 10))
        self.subtotal_label.pack()
        self.bonus_label = tk.Label(self.root, text="Bonus: ✘", font=("Arial", 10))
        self.bonus_label.pack()
        self.total_label = tk.Label(self.root, text="Total Score: 0", font=("Arial", 12, "bold"))
        self.total_label.pack(pady=5)

    def wait_for_updates(self):
        """Runs in a separate thread to listen for updates from the server"""
        try:
            while True:
                data = self.sock.recv(4096)
                if not data:
                    raise ConnectionError("Server closed the connection.")
                msg = pickle.loads(data)
                if msg.get("action") == "update":
                    self.gamestate: GameState = msg["game"]
                    self.root.after(0, self.update_display)
        except (ConnectionError, OSError):
            self.root.after(0, lambda: messagebox.showerror("Disconnected", "Connection lost. Server may have closed."))
            self.root.after(0, self.root.destroy)

    def toggle_lock(self, idx):
        """Toggle lock on a die when clicked (only if it's the player's turn and roll is not first roll)"""
        if not self.is_my_turn(): return
        if self.gamestate.scores[self.player_name].dice.get_rolls_remaining() == 3: return
        self.locked[idx] = not self.locked[idx]
        self.update_display()

    def send_roll(self):
        """Send a roll command to the server"""
        if not self.is_my_turn(): return
        self.sock.sendall(pickle.dumps({
            "action":"command","room":self.room_code,
            "player":self.player_name,"command":"roll",
            "keep": self.locked
        }))

    def send_score(self, category):
        """Send a score command to server for a selected category"""
        if not self.is_my_turn(): return
        confirm = messagebox.askyesno("Confirm", f"Use category '{category}'?")
        if not confirm: return
        self.sock.sendall(pickle.dumps({
            "action":"command","room":self.room_code,
            "player":self.player_name,"command":"score",
            "category": category
        }))

        self.locked = [False]*5

    def is_my_turn(self):
        """Check if it's the current player's turn"""
        if self.gamestate is None: return False
        return self.gamestate.current_player() == self.player_name

    def get_die_face(self, v):
        """Convert a die value to its visual string"""
        return "\n".join(DICE_DOTS.get(v, ["     "]*3))

    def update_display(self):
        """Update the UI based on the current game state"""
        g = self.gamestate
        self.turn_label.config(text=f"Room {g.room_code} – You are: {self.player_name}")
        self.name_label.config(
            text=(f"Turn: {g.current_player()} – " + ("Your turn" if self.is_my_turn() else f"Waiting for: {g.current_player()}"))
        )

        # Update dice visuals
        game = g.scores[g.current_player()]
        dice = game.dice.get_dice()
        for i,v in enumerate(dice): self.dice_buttons[i].config(text=self.get_die_face(v), bg="lightblue" if self.locked[i] else "SystemButtonFace")

        self.rolls_left_label.config(text=f"Rolls left: {game.dice.get_rolls_remaining()}")
        self.roll_button.config(state="normal" if self.is_my_turn() and game.can_roll() else "disabled")

        players = list(g.scores.keys())
        if len(players) < 2:
            return

        # Set scores for both players
        opponent = [p for p in players if p != self.player_name][0]
        my_game = g.scores[self.player_name]
        opp_game = g.scores[opponent]
        possible = my_game.get_possible_scores()
        all_scores = my_game.scorecard.get_all_scores()
        opp_scores = opp_game.scorecard.get_all_scores()
        roll_remain = my_game.dice.get_rolls_remaining()

        for key, (my_lbl, opp_lbl) in self.score_labels.items():
            # My score
            if all_scores[key] is not None:
                my_lbl.config(text=str(all_scores[key]), bg="lightgreen", fg="black")
                my_lbl.unbind("<Button-1>")
            elif key in possible and self.is_my_turn() and roll_remain < 3:
                my_lbl.config(text=str(possible[key]), fg="gray", bg="#eef")
                my_lbl.bind("<Button-1>", lambda e, cat=key: self.send_score(cat))
            else:
                my_lbl.config(text="", fg="gray", bg="SystemButtonFace")
                my_lbl.unbind("<Button-1>")

            # Opponent score (read-only)
            if opp_scores[key] is not None:
                opp_lbl.config(text=str(opp_scores[key]), bg="lightgreen", fg="black")
            else:
                opp_lbl.config(text="", bg="SystemButtonFace")

        my_upper = my_game.scorecard.calculate_upper_total()
        my_bonus = my_game.scorecard.calculate_upper_bonus()
        my_total = my_game.get_current_score()

        opp_upper = opp_game.scorecard.calculate_upper_total()
        opp_bonus = opp_game.scorecard.calculate_upper_bonus()
        opp_total = opp_game.get_current_score()

        self.subtotal_label.config(text=f"Subtotal: {my_upper} vs {opp_upper}")
        self.bonus_label.config(text=f"Bonus: {'✔' if my_bonus else '✘'} vs {'✔' if opp_bonus else '✘'}")
        self.total_label.config(text=f"Total Score: {my_total} vs {opp_total}")

        # Show winner if game is over
        if g.winner:
            scores = g.final_scores
            other = [f"{p}: {s}" for p, s in scores.items() if p != g.winner]
            summary = f"{g.winner} wins!\nwith score {scores[g.winner]} vs {other[0]}"
            messagebox.showinfo("Game Over", summary)
            self.root.destroy()

    def cleanup_and_quit(self):
        """Safely close connection and destroy GUI"""
        try:
            self.sock.close()
        except:
            pass
        self.root.destroy()

if __name__=="__main__":
    root = tk.Tk()
    YahtzeeClientGUI(root)
    root.mainloop()
