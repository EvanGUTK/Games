import tkinter as tk
import random
import os

class Game2048:
    def __init__(self, master):
        self.master = master
        self.master.title("2048 Game")
        self.master.geometry("600x700")  # Fixed size for consistent layout
        self.master.configure(bg="#faf8ef")
        self.grid_size = 4
        self.score = 0
        self.high_score = self.load_high_score()
        self.board = [[0] * self.grid_size for _ in range(self.grid_size)]
        self.game_over_flag = False
        self.init_ui()
        self.restart_game()

    def load_high_score(self):
        if os.path.exists("highscore.txt"):
            with open("highscore.txt", "r") as file:
                return int(file.read().strip())
        return 0

    def save_high_score(self):
        with open("highscore.txt", "w") as file:
            file.write(str(self.high_score))

    def init_ui(self):
        self.header = tk.Frame(self.master, bg="#faf8ef", padx=20, pady=10)
        self.header.pack()

        self.title_label = tk.Label(self.header, text="2048", font=("Arial", 40, "bold"), bg="#faf8ef", fg="#776e65")
        self.title_label.grid(row=0, column=0, columnspan=2)

        self.score_frame = tk.Frame(self.header, bg="#bbada0", padx=20, pady=10)
        self.score_frame.grid(row=1, column=0, padx=5)
        self.score_label = tk.Label(self.score_frame, text=f"Score:\n{self.score}", font=("Arial", 16), bg="#bbada0", fg="#f9f6f2", justify="center")
        self.score_label.pack()

        self.high_score_frame = tk.Frame(self.header, bg="#bbada0", padx=20, pady=10)
        self.high_score_frame.grid(row=1, column=1, padx=5)
        self.high_score_label = tk.Label(self.high_score_frame, text=f"Best:\n{self.high_score}", font=("Arial", 16), bg="#bbada0", fg="#f9f6f2", justify="center")
        self.high_score_label.pack()

        self.grid_canvas = tk.Canvas(self.master, width=560, height=560, bg="#bbada0", highlightthickness=0)
        self.grid_canvas.pack(pady=20)

        self.cell_size = 140  # Fixed cell size for consistent layout
        self.cell_backgrounds = []
        self.cell_texts = []

        for i in range(self.grid_size):
            row_backgrounds = []
            row_texts = []
            for j in range(self.grid_size):
                x0, y0 = j * self.cell_size + 10, i * self.cell_size + 10
                x1, y1 = x0 + self.cell_size - 20, y0 + self.cell_size - 20

                # Background layer
                background = self.grid_canvas.create_rectangle(x0, y0, x1, y1, fill="#cdc1b4", outline="")
                row_backgrounds.append(background)

                # Text layer
                text = self.grid_canvas.create_text((x0 + x1) // 2, (y0 + y1) // 2, text="", font=("Arial", 24, "bold"), fill="#776e65")
                row_texts.append(text)

            self.cell_backgrounds.append(row_backgrounds)
            self.cell_texts.append(row_texts)

        self.restart_button = tk.Button(self.master, text="New Game", command=self.restart_game, font=("Arial", 14), bg="#8f7a66", fg="#f9f6f2", padx=10, pady=5)
        self.restart_button.pack(pady=10)

        self.master.bind("<Up>", lambda event: self.move("up"))
        self.master.bind("<Down>", lambda event: self.move("down"))
        self.master.bind("<Left>", lambda event: self.move("left"))
        self.master.bind("<Right>", lambda event: self.move("right"))

    def restart_game(self):
        self.board = [[0] * self.grid_size for _ in range(self.grid_size)]
        self.score = 0
        self.game_over_flag = False
        self.spawn_tile()
        self.spawn_tile()
        self.update_ui()

    def spawn_tile(self):
        empty_cells = [(i, j) for i in range(self.grid_size) for j in range(self.grid_size) if self.board[i][j] == 0]
        if empty_cells:
            i, j = random.choice(empty_cells)
            self.board[i][j] = random.choice([2, 4])

    def update_ui(self):
        self.score_label.config(text=f"Score:\n{self.score}")
        self.high_score_label.config(text=f"Best:\n{self.high_score}")
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                value = self.board[i][j]
                color, text_color = self.get_tile_colors(value)

                # Update background layer
                self.grid_canvas.itemconfig(self.cell_backgrounds[i][j], fill=color)

                # Update text layer
                self.grid_canvas.itemconfig(self.cell_texts[i][j], text=str(value) if value else "", fill=text_color)

        if not self.can_move() and not self.game_over_flag:
            self.game_over_flag = True
            self.show_game_over()

    def get_tile_colors(self, value):
        colors = {
            0: ("#cdc1b4", "#776e65"),
            2: ("#ffffff", "#000000"),  # White background, black text
            4: ("#f5f5dc", "#8b4513"),  # Super light brown, darker brown text
            8: ("#f2b179", "#ffffff"),  # Orange background, white text
            16: ("#f59563", "#ffffff"),  # Darker orange background, white text
            32: ("#f67c5f", "#ffffff"),  # Redder orange background, white text
            64: ("#f65e3b", "#ffffff"),  # Almost red background, white text
            128: ("#edcf72", "#ffffff"),  # Yellow background, white text
        }
        # For tiles > 128, use yellow background and white text
        if value > 128:
            return ("#edcf72", "#ffffff")
        return colors.get(value, ("#3c3a32", "#f9f6f2"))

    def move(self, direction):
        if self.game_over_flag:
            return

        original_board = [row[:] for row in self.board]
        if direction == "up":
            self.board = self.merge(self.transpose(self.board))
        elif direction == "down":
            self.board = self.merge(self.transpose(self.board[::-1]))[::-1]
        elif direction == "left":
            self.board = self.merge(self.board)
        elif direction == "right":
            self.board = [row[::-1] for row in self.merge([row[::-1] for row in self.board])]

        if self.board != original_board:
            self.spawn_tile()
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()
        self.update_ui()

    def merge(self, board):
        merged_board = []
        for row in board:
            new_row = [value for value in row if value != 0]
            for i in range(1, len(new_row)):
                if new_row[i] == new_row[i - 1]:
                    new_row[i - 1] *= 2
                    self.score += new_row[i - 1]
                    new_row[i] = 0
            new_row = [value for value in new_row if value != 0]
            merged_board.append(new_row + [0] * (self.grid_size - len(new_row)))
        return merged_board

    def transpose(self, board):
        return [list(row) for row in zip(*board)]

    def can_move(self):
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if self.board[i][j] == 0:
                    return True
                if i < self.grid_size - 1 and self.board[i][j] == self.board[i + 1][j]:
                    return True
                if j < self.grid_size - 1 and self.board[i][j] == self.board[i][j + 1]:
                    return True
        return False

    def show_game_over(self):
        game_over_popup = tk.Toplevel(self.master)
        game_over_popup.title("Game Over")
        tk.Label(game_over_popup, text="Game Over!", font=("Arial", 20), bg="#faf8ef", fg="#776e65").pack(pady=10)
        tk.Label(game_over_popup, text=f"Final Score: {self.score}", font=("Arial", 14), bg="#faf8ef", fg="#776e65").pack(pady=5)
        tk.Label(game_over_popup, text=f"Best: {self.high_score}", font=("Arial", 14), bg="#faf8ef", fg="#776e65").pack(pady=5)
        tk.Button(game_over_popup, text="New Game", command=lambda: [self.restart_game(), game_over_popup.destroy()], font=("Arial", 12), bg="#8f7a66", fg="#f9f6f2", padx=10, pady=5).pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    game = Game2048(root)
    root.mainloop()
