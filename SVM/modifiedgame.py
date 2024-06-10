import tkinter as tk
import random
import joblib
import numpy as np
import warnings

warnings.simplefilter(action='ignore', category=UserWarning)

class MinesweeperAI:
    def __init__(self, root, rows=4, columns=4, mines=3):
        self.root = root
        self.rows = rows
        self.columns = columns
        self.mines = mines
        self.buttons = []
        self.board = []
        self.mine_locations = set()
        self.game_over = False
        self.first_click = True

        self.model = joblib.load("minesweeper_svm_model.pkl")

        self.create_board()
        self.create_buttons()
        self.replay_button()
        self.ai_move_button()

    def create_board(self):
        self.board = [[0 for _ in range(self.columns)] for _ in range(self.rows)]

    def place_mines(self, first_click_r, first_click_c):
        mines_placed = 0
        while mines_placed < self.mines:
            row = random.randint(0, self.rows - 1)
            col = random.randint(0, self.columns - 1)
            if (row, col) != (first_click_r, first_click_c) and self.board[row][col] != -1:
                self.board[row][col] = -1
                self.mine_locations.add((row, col))
                mines_placed += 1
        self.update_counts()

    def create_buttons(self):
        for r in range(self.rows):
            row_buttons = []
            for c in range(self.columns):
                button = tk.Button(self.root, width=2, command=lambda r=r, c=c: self.reveal_cell(r, c))
                button.bind("<Button-3>", lambda event, r=r, c=c: self.flag_cell(r, c))
                button.grid(row=r, column=c)
                row_buttons.append(button)
            self.buttons.append(row_buttons)

    def replay_button(self):
        replay_button = tk.Button(self.root, text="Replay", command=self.reset_game)
        replay_button.grid(row=self.rows, column=0, columnspan=self.columns)

    def ai_move_button(self):
        ai_button = tk.Button(self.root, text="AI Move", command=self.ai_move)
        ai_button.grid(row=self.rows+1, column=0, columnspan=self.columns)

    def update_counts(self):
        for r in range(self.rows):
            for c in range(self.columns):
                if self.board[r][c] == -1:
                    continue
                count = 0
                for i in range(max(0, r - 1), min(self.rows, r + 2)):
                    for j in range(max(0, c - 1), min(self.columns, c + 2)):
                        if self.board[i][j] == -1:
                            count += 1
                self.board[r][c] = count

    def reveal_cell(self, r, c):
        if self.game_over or self.buttons[r][c]["state"] == "disabled" or self.buttons[r][c]["text"] == "F":
            return
        if self.first_click:
            self.first_click = False
            self.place_mines(r, c)

        if self.board[r][c] == -1:
            self.buttons[r][c].config(text="*", bg="red")
            self.game_over = True
            print("You hit a mine!")
            self.reveal_mines()
        else:
            self.buttons[r][c].config(text=str(self.board[r][c]), bg="lightgrey", state="disabled")
            if self.board[r][c] == 0:
                for i in range(max(0, r - 1), min(self.rows, r + 2)):
                    for j in range(max(0, c - 1), min(self.columns, c + 2)):
                        if self.buttons[i][j]["state"] != "disabled":
                            self.reveal_cell(i, j)
            self.check_win()

    def flag_cell(self, r, c):
        if self.game_over or self.buttons[r][c]["state"] == "disabled":
            return
        if self.buttons[r][c]["text"] == "F":
            self.buttons[r][c].config(text="", bg="SystemButtonFace")
        else:
            self.buttons[r][c].config(text="F", bg="yellow")

    def reveal_mines(self):
        for r, c in self.mine_locations:
            self.buttons[r][c].config(text="*", bg="red")

    def check_win(self):
        for r in range(self.rows):
            for c in range(self.columns):
                if self.board[r][c] != -1 and self.buttons[r][c]["state"] != "disabled":
                    return
        print("You won!")
        self.game_over = True

    def reset_game(self):
        self.board = []
        self.buttons = []
        self.mine_locations = set()
        self.game_over = False
        self.first_click = True
        for widget in self.root.winfo_children():
            widget.destroy()
        self.create_board()
        self.create_buttons()
        self.replay_button()
        self.ai_move_button()

    def get_features(self, r, c):
        features = []
        for i in range(max(0, r - 1), min(self.rows, r + 2)):
            for j in range(max(0, c - 1), min(self.columns, c + 2)):
                if i == r and j == c:
                    continue
                features.append(self.board[i][j])
        # uzunlugun 8 oldugunu kontrol et
        while len(features) < 8:
            features.append(-1)
        return features

    def ai_move(self):
        best_move = None
        best_prob = -1

        for r in range(self.rows):
            for c in range(self.columns):
                if self.buttons[r][c]["state"] == "disabled" or self.buttons[r][c]["text"] == "F":
                    continue
                features = self.get_features(r, c)
                features = np.array(features).reshape(1, -1)
                prob = self.model.predict_proba(features)[0][1]
                if prob > best_prob:
                    best_prob = prob
                    best_move = (r, c)

        if best_move:
            self.reveal_cell(best_move[0], best_move[1])

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Minesweeper AI")
    game = MinesweeperAI(root)
    root.mainloop()
