import tkinter as tk
from tkinter import messagebox
import random
import time
import copy

# --- Constants ---
ROWS = 6
COLS = 7
EMPTY = 0
PLAYER = 1
AI = 2

WINDOW_LENGTH = 4
EMPTY_SCORE = 0
PLAYER_SCORE = 1
AI_SCORE = 2

# Colors
BOARD_COLOR = "#0000FF"  # Blue
EMPTY_COLOR = "#FFFFFF"  # White
PLAYER_COLOR = "#FF0000" # Red
AI_COLOR = "#FFFF00"     # Yellow

# AI Difficulty (Depth)
DEPTH = 4

class Connect4:
    def __init__(self, root):
        self.root = root
        self.root.title("Connect 4 - Human vs AI")
        self.board = [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]
        self.turn = PLAYER
        self.game_over = False

        self.setup_ui()

    def setup_ui(self):
        self.canvas = tk.Canvas(self.root, width=COLS * 100, height=ROWS * 100, bg=BOARD_COLOR)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.handle_click)

        self.status_label = tk.Label(self.root, text="Your Turn (Red)", font=("Arial", 16))
        self.status_label.pack()

        self.restart_button = tk.Button(self.root, text="Restart", command=self.reset_game)
        self.restart_button.pack()

        self.draw_board()

    def draw_board(self):
        self.canvas.delete("all")
        for r in range(ROWS):
            for c in range(COLS):
                color = EMPTY_COLOR
                if self.board[r][c] == PLAYER:
                    color = PLAYER_COLOR
                elif self.board[r][c] == AI:
                    color = AI_COLOR
                
                # Draw circles (offset by 5 for padding)
                # In our internal board, [0][0] is top-left, but for Connect4, 
                # row 5 is the bottom. We'll draw row 0 at the top.
                self.canvas.create_oval(c * 100 + 10, r * 100 + 10, (c + 1) * 100 - 10, (r + 1) * 100 - 10, fill=color, outline="black")

    def handle_click(self, event):
        if self.game_over or self.turn != PLAYER:
            return

        col = event.x // 100
        if self.is_valid_location(self.board, col):
            row = self.get_next_open_row(self.board, col)
            self.drop_piece(self.board, row, col, PLAYER)

            if self.winning_move(self.board, PLAYER):
                self.draw_board()
                self.status_label.config(text="PLAYER 1 WINS!")
                self.game_over = True
                messagebox.showinfo("Game Over", "You win!")
            elif self.is_board_full(self.board):
                self.draw_board()
                self.status_label.config(text="DRAW!")
                self.game_over = True
                messagebox.showinfo("Game Over", "It's a draw!")
            else:
                self.turn = AI
                self.status_label.config(text="AI's Turn (Yellow)...")
                self.draw_board()
                self.root.after(500, self.ai_move)

    def ai_move(self):
        if self.game_over:
            return

        # Use Minimax with Alpha-Beta pruning to find the best move
        col, _ = self.minimax(self.board, DEPTH, -float('inf'), float('inf'), True)
        
        if col is not None and self.is_valid_location(self.board, col):
            row = self.get_next_open_row(self.board, col)
            self.drop_piece(self.board, row, col, AI)

            if self.winning_move(self.board, AI):
                self.draw_board()
                self.status_label.config(text="AI WINS!")
                self.game_over = True
                messagebox.showinfo("Game Over", "AI wins!")
            elif self.is_board_full(self.board):
                self.draw_board()
                self.status_label.config(text="DRAW!")
                self.game_over = True
                messagebox.showinfo("Game Over", "It's a draw!")
            else:
                self.turn = PLAYER
                self.status_label.config(text="Your Turn (Red)")
                self.draw_board()

    def reset_game(self):
        self.board = [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]
        self.turn = PLAYER
        self.game_over = False
        self.status_label.config(text="Your Turn (Red)")
        self.draw_board()

    # --- Logic Helpers ---
    def is_valid_location(self, board, col):
        return board[0][col] == EMPTY

    def get_next_open_row(self, board, col):
        for r in range(ROWS-1, -1, -1):
            if board[r][col] == EMPTY:
                return r

    def drop_piece(self, board, row, col, piece):
        board[row][col] = piece

    def winning_move(self, board, piece):
        # Check horizontal
        for c in range(COLS - 3):
            for r in range(ROWS):
                if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
                    return True
        # Check vertical
        for c in range(COLS):
            for r in range(ROWS - 3):
                if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
                    return True
        # Check positively sloped diagonals
        for c in range(COLS - 3):
            for r in range(ROWS - 3):
                if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
                    return True
        # Check negatively sloped diagonals
        for c in range(COLS - 3):
            for r in range(3, ROWS):
                if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
                    return True
        return False

    def is_board_full(self, board):
        return all(board[0][c] != EMPTY for c in range(COLS))

    def get_valid_locations(self, board):
        valid_locations = []
        for col in range(COLS):
            if self.is_valid_location(board, col):
                valid_locations.append(col)
        return valid_locations

    # --- AI Algorithm (Minimax with Alpha-Beta Pruning) ---
    def evaluate_window(self, window, piece):
        score = 0
        opp_piece = PLAYER if piece == AI else AI

        if window.count(piece) == 4:
            score += 100000
        elif window.count(piece) == 3 and window.count(EMPTY) == 1:
            score += 100
        elif window.count(piece) == 2 and window.count(EMPTY) == 2:
            score += 10

        if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
            score -= 80  # Penalize if opponent is close to winning

        return score

    def score_position(self, board, piece):
        score = 0

        # Score center column (give a slight advantage for center control)
        center_array = [board[r][COLS//2] for r in range(ROWS)]
        center_count = center_array.count(piece)
        score += center_count * 3

        # Score Horizontal
        for r in range(ROWS):
            row_array = board[r]
            for c in range(COLS - 3):
                window = row_array[c:c+WINDOW_LENGTH]
                score += self.evaluate_window(window, piece)

        # Score Vertical
        for c in range(COLS):
            col_array = [board[r][c] for r in range(ROWS)]
            for r in range(ROWS - 3):
                window = col_array[r:r+WINDOW_LENGTH]
                score += self.evaluate_window(window, piece)

        # Score Positively Sloped Diagonal
        for r in range(ROWS - 3):
            for c in range(COLS - 3):
                window = [board[r+i][c+i] for i in range(WINDOW_LENGTH)]
                score += self.evaluate_window(window, piece)

        # Score Negatively Sloped Diagonal
        for r in range(ROWS - 3):
            for c in range(COLS - 3):
                window = [board[r+3-i][c+i] for i in range(WINDOW_LENGTH)]
                score += self.evaluate_window(window, piece)

        return score

    def is_terminal_node(self, board):
        return self.winning_move(board, PLAYER) or self.winning_move(board, AI) or self.is_board_full(board)

    def minimax(self, board, depth, alpha, beta, maximizingPlayer):
        valid_locations = self.get_valid_locations(board)
        is_terminal = self.is_terminal_node(board)
        
        if depth == 0 or is_terminal:
            if is_terminal:
                if self.winning_move(board, AI):
                    return (None, 10000000000000)
                elif self.winning_move(board, PLAYER):
                    return (None, -10000000000000)
                else: # Game is over, no more valid moves
                    return (None, 0)
            else: # Depth is zero
                return (None, self.score_position(board, AI))

        if maximizingPlayer:
            value = -float('inf')
            column = random.choice(valid_locations)
            for col in valid_locations:
                row = self.get_next_open_row(board, col)
                b_copy = copy.deepcopy(board)
                self.drop_piece(b_copy, row, col, AI)
                new_score = self.minimax(b_copy, depth-1, alpha, beta, False)[1]
                if new_score > value:
                    value = new_score
                    column = col
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return column, value

        else: # Minimizing player (Human)
            value = float('inf')
            column = random.choice(valid_locations)
            for col in valid_locations:
                row = self.get_next_open_row(board, col)
                b_copy = copy.deepcopy(board)
                self.drop_piece(b_copy, row, col, PLAYER)
                new_score = self.minimax(b_copy, depth-1, alpha, beta, True)[1]
                if new_score < value:
                    value = new_score
                    column = col
                beta = min(beta, value)
                if alpha >= beta:
                    break
            return column, value

if __name__ == "__main__":
    root = tk.Tk()
    game = Connect4(root)
    root.mainloop()
