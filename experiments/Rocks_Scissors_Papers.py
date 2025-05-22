
import tkinter as tk
import random
from PIL import Image, ImageTk


class RPSGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Rock-Paper-Scissors")
        self.root.geometry("500x500")
        self.root.resizable(False, False)

        self.choices = ["Rock", "Paper", "Scissors"]

        # Load images
        self.img_size = (120, 120)
        self.images = {}
        self.load_images()

        # Create UI elements
        self.create_widgets()

        # Initialize game state
        self.reset_game()

    def create_widgets(self):
        self.label_info = tk.Label(self.root, text="Choose Rock, Paper, or Scissors:", font=("Arial", 14))
        self.label_info.pack(pady=15)

        self.frame_buttons = tk.Frame(self.root)
        self.frame_buttons.pack(pady=10)
        for choice in self.choices:
            btn = tk.Button(self.frame_buttons, image=self.images[choice],
                            command=lambda c=choice: self.handle_player_choice(c))
            btn.pack(side=tk.LEFT, padx=10)

        self.frame_results = tk.Frame(self.root)
        self.frame_results.pack(pady=10)

        self.label_player_img = tk.Label(self.frame_results)
        self.label_player_img.grid(row=0, column=0, padx=20)
        self.label_vs = tk.Label(self.frame_results, text="VS", font=("Arial", 20, "bold"))
        self.label_vs.grid(row=0, column=1)
        self.label_ai_img = tk.Label(self.frame_results)
        self.label_ai_img.grid(row=0, column=2, padx=20)

        self.label_player = tk.Label(self.root, text="Your choice: None", font=("Arial", 12))
        self.label_player.pack(pady=5)
        self.label_ai = tk.Label(self.root, text="AI choice: None", font=("Arial", 12))
        self.label_ai.pack(pady=5)
        self.label_result = tk.Label(self.root, text="Result: None", font=("Arial", 14, "bold"), fg="blue")
        self.label_result.pack(pady=10)

        self.score_frame = tk.Frame(self.root)
        self.score_frame.pack(pady=10)
        self.wins = 0
        self.losses = 0
        self.draws = 0
        self.rounds_played = 0
        self.label_wins = tk.Label(self.score_frame, text=f"Wins: {self.wins}", font=("Arial", 12), fg="green")
        self.label_wins.pack(side=tk.LEFT, padx=10)
        self.label_losses = tk.Label(self.score_frame, text=f"Losses: {self.losses}", font=("Arial", 12), fg="red")
        self.label_losses.pack(side=tk.LEFT, padx=10)
        self.label_draws = tk.Label(self.score_frame, text=f"Draws: {self.draws}", font=("Arial", 12), fg="orange")
        self.label_draws.pack(side=tk.LEFT, padx=10)

        self.label_rounds_played = tk.Label(self.score_frame, text=f"Rounds Played: {self.rounds_played}",
                                            font=("Arial", 12))
        self.label_rounds_played.pack(side=tk.LEFT, padx=10)

        self.reset_button = tk.Button(self.root, text="Reset Round", command=self.reset_game, state=tk.DISABLED)
        self.reset_button.pack(pady=5)

    def load_images(self):
        """Load images from files."""
        self.images["Rock"] = ImageTk.PhotoImage(Image.open("rock.png").resize(self.img_size))
        self.images["Paper"] = ImageTk.PhotoImage(Image.open("paper.png").resize(self.img_size))
        self.images["Scissors"] = ImageTk.PhotoImage(Image.open("scissors.png").resize(self.img_size))

    def ai_select(self):
        """Randomly select Rock, Paper, or Scissors for AI."""
        return random.choice(self.choices)

    def handle_player_choice(self, player_choice):
        """Handle player's choice and update game state."""
        ai_choice = self.ai_select()
        self.label_player.config(text=f"Your choice: {player_choice}")
        self.label_ai.config(text=f"AI choice: {ai_choice}")

        self.update_game_state(player_choice, ai_choice)

    def update_game_state(self, player_choice, ai_choice):
        """Update the game state based on the choices made."""
        result = self.decide_winner(player_choice, ai_choice)
        color = {"You Win!": "green", "You Lose!": "red", "Draw": "orange"}
        self.label_result.config(text=f"Result: {result}", fg=color.get(result, "blue"))

        # Update scores
        self.update_scores(result)

        # Display choices
        self.label_player_img.config(image=self.images[player_choice])
        self.label_ai_img.config(image=self.images[ai_choice])

        self.disable_buttons()
        self.reset_button.config(state=tk.NORMAL)

        # Update rounds played
        self.rounds_played += 1
        self.update_rounds_played_label()

    def decide_winner(self, player, ai):
        """Decide the winner of the round."""
        if player == ai:
            return "Draw"
        if (player == "Rock" and ai == "Scissors") or \
                (player == "Paper" and ai == "Rock") or \
                (player == "Scissors" and ai == "Paper"):
            return "You Win!"
        else:
            return "You Lose!"

    def update_scores(self, result):
        """Update the score based on the result."""
        if result == "You Win!":
            self.wins += 1
        elif result == "You Lose!":
            self.losses += 1
        else:
            self.draws += 1

        self.update_score_labels()

    def update_score_labels(self):
        """Update the score display labels."""
        self.label_wins.config(text=f"Wins: {self.wins}")
        self.label_losses.config(text=f"Losses: {self.losses}")
        self.label_draws.config(text=f"Draws: {self.draws}")
        self.label_rounds_played.config(text=f"Rounds Played: {self.rounds_played}")

    def disable_buttons(self):
        """Disable choice buttons after a round is played."""
        for child in self.frame_buttons.winfo_children():
            child.config(state=tk.DISABLED)

    def reset_game(self):
        """Reset the game state for a new round."""
        self.label_player.config(text="Your choice: None")
        self.label_ai.config(text="AI choice: None")
        self.label_result.config(text="Result: None", fg="blue")
        self.label_player_img.config(image='')
        self.label_ai_img.config(image='')

        self.enable_buttons()
        self.disable_reset_button()

        # Reset rounds played count
        self.rounds_played = 0
        self.update_rounds_played_label()

    def enable_buttons(self):
        """Enable choice buttons for the next round."""
        for child in self.frame_buttons.winfo_children():
            child.config(state=tk.NORMAL)

    def disable_reset_button(self):
        """Disable the reset button."""
        self.reset_button.config(state=tk.DISABLED)


if __name__ == "__main__":
    root = tk.Tk()
    game = RPSGame(root)
    root.mainloop()
