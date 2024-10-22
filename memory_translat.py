import tkinter as tk
from tkinter import simpledialog, messagebox
from wonderwords import RandomWord
from googletrans import Translator
import random
import sqlite3
from nltk.corpus import words as nltk_words
import nltk
from langdetect import detect
nltk.download('words')

translator = Translator()
random_word = RandomWord()

class MemoryGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Memory Card Game")
        self.root.geometry("600x600")
        self.root.resizable(True, True)
        self.root.configure(bg='lightblue')
        
        self.players = []
        self.current_player_index = 0
        self.difficulty = "easy"
        self.grid_size = 4
        self.scores = {}

        # Setup SQLite database (in-memory)
        self.conn = sqlite3.connect(':memory:')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE word_pairs (original TEXT PRIMARY KEY, translation TEXT)''')

        self.setup_menu()

    def setup_menu(self):
        menu_frame = tk.Frame(self.root, bg='lightblue')
        menu_frame.pack(pady=20)

        # Player Name Input
        tk.Label(menu_frame, text="Enter Player Names (comma separated):", bg='lightblue').grid(row=0, column=0, padx=10, pady=5)
        self.player_name_entry = tk.Entry(menu_frame)
        self.player_name_entry.grid(row=0, column=1, padx=10, pady=5)

        # Difficulty Selection
        tk.Label(menu_frame, text="Select Difficulty:", bg='lightblue').grid(row=1, column=0, padx=10, pady=5)
        self.difficulty_var = tk.StringVar(value="easy")
        tk.OptionMenu(menu_frame, self.difficulty_var, "easy", "medium", "hard").grid(row=1, column=1, padx=10, pady=5)

        # Grid Size Selection
        tk.Label(menu_frame, text="Select Grid Size:", bg='lightblue').grid(row=2, column=0, padx=10, pady=5)
        self.grid_size_var = tk.IntVar(value=4)
        tk.OptionMenu(menu_frame, self.grid_size_var, 4, 6, 8).grid(row=2, column=1, padx=10, pady=5)

        # Start Game Button
        tk.Button(menu_frame, text="Start Game", command=self.start_game).grid(row=3, column=0, columnspan=2, pady=20)

    def start_game(self):
        player_names = self.player_name_entry.get()
        if not player_names:
            messagebox.showerror("Error", "Please enter player names.")
            return
        self.players = [name.strip() for name in player_names.split(",")]
        self.scores = {player: 0 for player in self.players}
        self.difficulty = self.difficulty_var.get()
        self.grid_size = self.grid_size_var.get()

        self.words = self.generate_word_pairs()
        if not self.words:
            return
        self.setup_game_board()

    def generate_word_pairs(self):
        word_list = nltk_words.words()
        word_pairs = []
        num_pairs = (self.grid_size ** 2) // 2

        while len(word_pairs) < num_pairs:
            word = random_word.word()
            if word.lower() not in word_list:
                continue

            # Validate the language of the generated word
            if detect(word) != 'en':
                continue
            
            try:
                translated_word = translator.translate(word, src='en', dest='fr').text.lower()
            except Exception as e:
                continue  # Skip words that cause translation errors
            
            # Ensure words are unique to avoid mixing languages incorrectly
            if all(word.lower() != w1 and translated_word != w2 for w1, w2 in word_pairs):
                word_pairs.append((word.lower(), translated_word))
                self.cursor.execute('INSERT INTO word_pairs (original, translation) VALUES (?, ?)', (word.lower(), translated_word))

        self.conn.commit()
        random.shuffle(word_pairs)
        return word_pairs

    def setup_game_board(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        board_frame = tk.Frame(self.root, bg='lightblue')
        board_frame.pack(expand=True, fill='both')

        cards = [pair[0] for pair in self.words for _ in range(2)]
        random.shuffle(cards)

        self.buttons = []
        self.card_values = {}  # Dictionary to store the card values by their position
        index = 0
        for i in range(self.grid_size):
            row = []
            for j in range(self.grid_size):
                position = f"{i},{j}"
                btn = tk.Button(board_frame, text="?", bg='skyblue', fg='red', command=lambda b=(i, j): self.reveal_card(b))
                btn.grid(row=i, column=j, padx=5, pady=5, sticky='nsew')
                board_frame.grid_rowconfigure(i, weight=1)
                board_frame.grid_columnconfigure(j, weight=1)
                row.append(btn)
                self.card_values[(i, j)] = cards[index]
                index += 1
            self.buttons.append(row)
        self.conn.commit()

        self.revealed = []
        self.input_entry = tk.Entry(self.root)
        self.input_entry.pack(pady=10)
        self.submit_button = tk.Button(self.root, text="Submit Translation", command=self.check_translation)
        self.submit_button.pack(pady=5)
        self.update_turn_label()
        self.update_score_label()

    def reveal_card(self, button_pos):
        i, j = button_pos
        button = self.buttons[i][j]

        if button.cget("text") == "?" and len(self.revealed) < 2:
            card_value = self.card_values[(i, j)]
            button.config(text=card_value)
            self.revealed.append((button, card_value))

            if len(self.revealed) == 2:
                self.prompt_for_translation()

    def prompt_for_translation(self):
        (btn1, val1), (btn2, val2) = self.revealed
        if val1 == val2:
            # Prompt player for translation
            correct_translation = self.get_correct_translation(val1)
            user_translation = simpledialog.askstring("Translation", f"Enter the translation for '{val1}':")
            if user_translation and user_translation.lower() == correct_translation:
                btn1.config(state="disabled", bg="lightgreen")
                btn2.config(state="disabled", bg="lightgreen")
                self.scores[self.players[self.current_player_index]] += 1
                self.revealed = []
            else:
                messagebox.showinfo("Incorrect", f"Incorrect! The correct translation is '{correct_translation}'.")
                btn1.config(bg="lightcoral")
                btn2.config(bg="lightcoral")
                self.root.after(1000, self.hide_cards)
        else:
            self.root.after(1000, self.hide_cards)

        self.update_score_label()

    def get_correct_translation(self, word):
        self.cursor.execute('SELECT translation FROM word_pairs WHERE original = ?', (word,))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        return ""

    def hide_cards(self):
        if len(self.revealed) == 2:
            btn1, _ = self.revealed[0]
            btn2, _ = self.revealed[1]
            btn1.config(text="?", bg="skyblue", fg='red')
            btn2.config(text="?", bg="skyblue", fg='red')
        self.revealed = []
        self.next_player()

    def next_player(self):
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        self.update_turn_label()

    def update_turn_label(self):
        if hasattr(self, 'turn_label'):
            self.turn_label.destroy()
        self.turn_label = tk.Label(self.root, text=f"Current Turn: {self.players[self.current_player_index]}", bg='lightblue')
        self.turn_label.pack(pady=5)

    def update_score_label(self):
        if hasattr(self, 'score_label'):
            self.score_label.destroy()
        score_text = "  |  ".join([f"{player}: {score}" for player, score in self.scores.items()])
        self.score_label = tk.Label(self.root, text=f"Scores: {score_text}", bg='lightblue')
        self.score_label.pack(pady=5)

    def end_game(self):
        final_scores = "\n".join([f"{player}: {score}" for player, score in self.scores.items()])
        messagebox.showinfo("Game Over", f"Final Scores:\n{final_scores}")

if __name__ == "__main__":
    root = tk.Tk()
    game = MemoryGame(root)
    root.mainloop()
