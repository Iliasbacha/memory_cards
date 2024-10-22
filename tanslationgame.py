import tkinter as tk
from tkinter import messagebox
import random

# List of English words and their French translations
word_pairs = [
    ("dog", "chien"),
    ("cat", "chat"),
    ("apple", "pomme"),
    ("house", "maison"),
    ("car", "voiture"),
    ("book", "livre")
]

class TranslationGame:
    def __init__(self, root):
        self.root = root
        self.root.title("French Translation Game")

        # Initialize game variables
        self.player_name = ""
        self.score = 0
        self.round = 0
        
        # Create name entry screen
        self.name_frame = tk.Frame(root)
        self.name_frame.pack(pady=20)

        self.name_label = tk.Label(self.name_frame, text="Enter your name:", font=("Arial", 16))
        self.name_label.pack()

        self.name_entry = tk.Entry(self.name_frame, font=("Arial", 16))
        self.name_entry.pack(pady=10)

        self.start_button = tk.Button(self.name_frame, text="Start Game", command=self.start_game, font=("Arial", 14))
        self.start_button.pack(pady=10)

    def start_game(self):
        """Start the game after entering the player's name."""
        self.player_name = self.name_entry.get().strip()
        if not self.player_name:
            messagebox.showwarning("Input Error", "Please enter a valid name.")
            return
        
        self.name_frame.pack_forget()  # Hide name entry frame
        self.setup_game()

    def setup_game(self):
        """Set up the game interface."""
        random.shuffle(word_pairs)
        self.current_word = None

        # UI Elements
        self.word_label = tk.Label(self.root, text="Translate this word:", font=("Arial", 16))
        self.word_label.pack(pady=10)

        self.word_display = tk.Label(self.root, text="", font=("Arial", 20), fg="blue")
        self.word_display.pack(pady=10)

        self.translation_entry = tk.Entry(self.root, font=("Arial", 16))
        self.translation_entry.pack(pady=10)

        self.submit_button = tk.Button(self.root, text="Submit", command=self.check_translation, font=("Arial", 14))
        self.submit_button.pack(pady=10)

        self.feedback_label = tk.Label(self.root, text="", font=("Arial", 16))
        self.feedback_label.pack(pady=10)

        self.score_label = tk.Label(self.root, text=f"Score: {self.score}", font=("Arial", 16))
        self.score_label.pack(pady=10)

        self.next_button = tk.Button(self.root, text="Next", command=self.next_word, font=("Arial", 14), state="disabled")
        self.next_button.pack(pady=10)

        self.next_word()

    def next_word(self):
        """Move to the next word in the game."""
        self.translation_entry.delete(0, tk.END)
        self.feedback_label.config(text="")
        self.next_button.config(state="disabled")
        
        if self.round < len(word_pairs):
            self.current_word = word_pairs[self.round]
            self.word_display.config(text=self.current_word[0])  # Show English word
            self.round += 1
        else:
            messagebox.showinfo("Game Over", f"Game over, {self.player_name}! Your final score is {self.score}.")
            self.root.quit()

    def check_translation(self):
        """Check if the entered translation is correct."""
        user_input = self.translation_entry.get().strip().lower()
        correct_translation = self.current_word[1]

        if user_input == correct_translation:
            self.score += 1
            self.feedback_label.config(text="Correct!", fg="green")
        else:
            self.feedback_label.config(text=f"Incorrect. The correct word was '{correct_translation}'", fg="red")

        # Update score display
        self.score_label.config(text=f"Score: {self.score}")
        self.next_button.config(state="normal")

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    game = TranslationGame(root)
    root.mainloop()
