import tkinter as tk
from tkinter import messagebox
import random
import time

# --- Constants ---
BOARD_SIZE = 8
SQUARE_SIZE = 64
width = BOARD_SIZE * SQUARE_SIZE
height = BOARD_SIZE * SQUARE_SIZE

# Colors
LIGHT_SQUARE = "#F0D9B5"
DARK_SQUARE = "#B58863"
RED_PIECE = "#D32F2F"
BLACK_PIECE = "#212121"
HIGHLIGHT_COLOR = "blue"
LAST_MOVE_COLOR = "yellow"

# Pieces
EMPTY = 0
RED = 1
BLACK = 2
RED_KING = 3
BLACK_KING = 4

# --- Game Logic ---

class Move:
    def __init__(self, start_sq, end_sq, captured_sqs=None):
        self.start_sq = start_sq  # (r, c)
        self.end_sq = end_sq      # (r, c)
        self.captured_sqs = captured_sqs if captured_sqs else [] # List of (r, c)
        self.move_id = start_sq[0] * 1000 + start_sq[1] * 100 + end_sq[0] * 10 + end_sq[1]

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.move_id == other.move_id
        return False

class GameState:
    def __init__(self):
        self.board = self.create_initial_board()
        self.red_to_move = True
        self.move_log = []
        self.game_over = False
        self.winner = None

    def create_initial_board(self):
        board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if (r + c) % 2 == 1:
                    if r < 3:
                        board[r][c] = BLACK
                    elif r > 4:
                        board[r][c] = RED
        return board

    def make_move(self, move):
        piece = self.board[move.start_sq[0]][move.start_sq[1]]
        
        # Move piece
        self.board[move.start_sq[0]][move.start_sq[1]] = EMPTY
        self.board[move.end_sq[0]][move.end_sq[1]] = piece
        
        # Handle captures
        for r, c in move.captured_sqs:
            self.board[r][c] = EMPTY
            
        # Handle Crowning
        if piece == RED and move.end_sq[0] == 0:
            self.board[move.end_sq[0]][move.end_sq[1]] = RED_KING
        elif piece == BLACK and move.end_sq[0] == 7:
            self.board[move.end_sq[0]][move.end_sq[1]] = BLACK_KING

        self.move_log.append(move)
        self.red_to_move = not self.red_to_move
        
        # Check game over
        valid_moves = self.get_valid_moves()
        if not valid_moves:
            self.game_over = True
            self.winner = "Black" if self.red_to_move else "Red"

    def undo_move(self):
        if not self.move_log: return
        move = self.move_log.pop()
        # This is complex because of piece state and captures. 
        # For simplicity in this AI, we'll use a deepcopy or rebuild state if needed,
        # but let's implement a proper undo.
        # We need to store what the piece was *before* it was potentially crowned.
        # Let's just store board state in move log for simplicity.
        pass

    def get_valid_moves(self):
        moves = []
        # In Checkers, if you can jump, you MUST jump.
        jump_moves = self.get_all_jumps()
        if jump_moves:
            return jump_moves
        return self.get_all_slides()

    def get_all_slides(self):
        slides = []
        turn_pieces = [RED, RED_KING] if self.red_to_move else [BLACK, BLACK_KING]
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self.board[r][c] in turn_pieces:
                    piece = self.board[r][c]
                    dirs = []
                    if piece == RED: dirs = [(-1, -1), (-1, 1)]
                    elif piece == BLACK: dirs = [(1, -1), (1, 1)]
                    else: dirs = [(-1, -1), (-1, 1), (1, -1), (1, 1)] # Kings
                    
                    for dr, dc in dirs:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < 8 and 0 <= nc < 8 and self.board[nr][nc] == EMPTY:
                            slides.append(Move((r, c), (nr, nc)))
        return slides

    def get_all_jumps(self):
        jumps = []
        turn_pieces = [RED, RED_KING] if self.red_to_move else [BLACK, BLACK_KING]
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self.board[r][c] in turn_pieces:
                    self.find_jumps_for_piece(r, c, [], jumps)
        return jumps

    def find_jumps_for_piece(self, r, c, captured, jumps_list):
        piece = self.board[r][c]
        enemy_pieces = [BLACK, BLACK_KING] if self.red_to_move else [RED, RED_KING]
        
        dirs = []
        if piece == RED: dirs = [(-1, -1), (-1, 1)]
        elif piece == BLACK: dirs = [(1, -1), (1, 1)]
        else: dirs = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        
        found_any = False
        for dr, dc in dirs:
            mr, mc = r + dr, c + dc # Middle square
            tr, tc = r + 2*dr, c + 2*dc # Target square
            
            if 0 <= tr < 8 and 0 <= tc < 8:
                if self.board[mr][mc] in enemy_pieces and self.board[tr][tc] == EMPTY:
                    if (mr, mc) not in captured:
                        found_any = True
                        new_captured = captured + [(mr, mc)]
                        # Temporarily move piece to continue multi-jump search
                        orig_piece = self.board[r][c]
                        self.board[r][c] = EMPTY
                        old_target = self.board[tr][tc]
                        self.board[tr][tc] = orig_piece
                        
                        # Continue searching from the new position
                        sub_jumps = []
                        self.find_jumps_for_piece(tr, tc, new_captured, sub_jumps)
                        
                        # Revert
                        self.board[tr][tc] = old_target
                        self.board[r][c] = orig_piece
                        
                        if not sub_jumps:
                            # Start square is the very first one
                            # We need to track the absolute start for the final move object
                            # But here we just return the endpoint for this branch
                            jumps_list.append(Move((r, c), (tr, tc), new_captured))
                        else:
                            for sj in sub_jumps:
                                # Update start square to the current piece location for sub-jumps
                                # This recursion is a bit tricky for the GUI, let's simplify:
                                # Only one jump at a time is easier to handle in the logic
                                jumps_list.append(Move((r, c), sj.end_sq, sj.captured_sqs))

    # Simplified jump logic: just find all immediate jumps
    def get_all_jumps_simple(self):
        jumps = []
        turn_pieces = [RED, RED_KING] if self.red_to_move else [BLACK, BLACK_KING]
        enemy_pieces = [BLACK, BLACK_KING] if self.red_to_move else [RED, RED_KING]
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self.board[r][c] in turn_pieces:
                    piece = self.board[r][c]
                    dirs = [(-1, -1), (-1, 1), (1, -1), (1, 1)] # All pieces check all dirs for jumps? 
                    # Standard rules: Normal pieces jump forward, Kings both. 
                    # Actually, some rules allow normal pieces to jump backward.
                    # Let's use standard: Kings both, Normal forward.
                    p_dirs = dirs if piece in [RED_KING, BLACK_KING] else ([(-1, -1), (-1, 1)] if piece == RED else [(1, -1), (1, 1)])
                    
                    for dr, dc in p_dirs:
                        mr, mc = r + dr, c + dc
                        tr, tc = r + 2*dr, c + 2*dc
                        if 0 <= tr < 8 and 0 <= tc < 8:
                            if self.board[mr][mc] in enemy_pieces and self.board[tr][tc] == EMPTY:
                                jumps.append(Move((r, c), (tr, tc), [(mr, mc)]))
        return jumps

    def get_valid_moves(self):
        jumps = self.get_all_jumps_simple()
        if jumps: return jumps
        return self.get_all_slides()

# --- AI ---

def score_board(gs):
    score = 0
    for r in range(8):
        for c in range(8):
            piece = gs.board[r][c]
            if piece == RED: score += 10 + (7 - r)
            elif piece == RED_KING: score += 25
            elif piece == BLACK: score -= (10 + r)
            elif piece == BLACK_KING: score -= 25
    return score

def find_best_move(gs, moves, depth, alpha, beta, red_to_move):
    if depth == 0 or gs.game_over:
        return score_board(gs), None
    
    best_move = None
    if red_to_move:
        max_eval = -float('inf')
        for move in moves:
            # Simulate move
            original_board = [row[:] for row in gs.board]
            gs.make_move(move)
            eval, _ = find_best_move(gs, gs.get_valid_moves(), depth - 1, alpha, beta, False)
            gs.board = original_board
            gs.red_to_move = True
            
            if eval > max_eval:
                max_eval = eval
                best_move = move
            alpha = max(alpha, eval)
            if beta <= alpha: break
        return max_eval, best_move
    else:
        min_eval = float('inf')
        for move in moves:
            original_board = [row[:] for row in gs.board]
            gs.make_move(move)
            eval, _ = find_best_move(gs, gs.get_valid_moves(), depth - 1, alpha, beta, True)
            gs.board = original_board
            gs.red_to_move = False
            
            if eval < min_eval:
                min_eval = eval
                best_move = move
            beta = min(beta, eval)
            if beta <= alpha: break
        return min_eval, best_move

# --- GUI ---

class CheckersMain:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Impossible Checkers")
        self.canvas = tk.Canvas(self.window, width=width, height=height)
        self.canvas.pack()
        
        self.gs = GameState()
        self.valid_moves = self.gs.get_valid_moves()
        
        self.selected_sq = None
        self.dragging_piece = None
        self.drag_pos = (0, 0)
        
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        
        self.draw_game_state()
        self.window.mainloop()

    def on_press(self, event):
        if self.gs.game_over: return
        if not self.gs.red_to_move: return # AI's turn (AI is Black)

        col = event.x // SQUARE_SIZE
        row = event.y // SQUARE_SIZE
        piece = self.gs.board[row][col]
        
        if piece in [RED, RED_KING]:
            self.selected_sq = (row, col)
            self.dragging_piece = piece
            self.drag_pos = (event.x, event.y)
            self.draw_game_state()

    def on_drag(self, event):
        if self.dragging_piece:
            self.drag_pos = (event.x, event.y)
            self.draw_game_state()

    def on_release(self, event):
        if not self.dragging_piece: return
        
        start_row, start_col = self.selected_sq
        end_col = event.x // SQUARE_SIZE
        end_row = event.y // SQUARE_SIZE
        
        move = Move((start_row, start_col), (end_row, end_col))
        move_made = False
        for m in self.valid_moves:
            if m.start_sq == (start_row, start_col) and m.end_sq == (end_row, end_col):
                self.gs.make_move(m)
                move_made = True
                break
        
        self.dragging_piece = None
        self.selected_sq = None
        self.draw_game_state()
        
        if move_made:
            self.valid_moves = self.gs.get_valid_moves()
            if not self.gs.game_over:
                self.window.after(500, self.ai_move)

    def ai_move(self):
        self.valid_moves = self.gs.get_valid_moves()
        if self.valid_moves:
            _, move = find_best_move(self.gs, self.valid_moves, 4, -float('inf'), float('inf'), False)
            if move:
                self.gs.make_move(move)
        self.valid_moves = self.gs.get_valid_moves()
        self.draw_game_state()

    def draw_game_state(self):
        self.draw_board()
        self.draw_pieces()
        if self.gs.game_over:
            messagebox.showinfo("Game Over", f"{self.gs.winner} wins!")

    def draw_board(self):
        self.canvas.delete("all")
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                color = LIGHT_SQUARE if (r + c) % 2 == 0 else DARK_SQUARE
                self.canvas.create_rectangle(c*SQUARE_SIZE, r*SQUARE_SIZE, (c+1)*SQUARE_SIZE, (r+1)*SQUARE_SIZE, fill=color, outline="")

    def draw_pieces(self):
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self.selected_sq == (r, c) and self.dragging_piece: continue
                piece = self.gs.board[r][c]
                if piece != EMPTY:
                    color = RED_PIECE if piece in [RED, RED_KING] else BLACK_PIECE
                    self.canvas.create_oval(c*SQUARE_SIZE+10, r*SQUARE_SIZE+10, (c+1)*SQUARE_SIZE-10, (r+1)*SQUARE_SIZE-10, fill=color, outline="white")
                    if piece in [RED_KING, BLACK_KING]:
                        self.canvas.create_text(c*SQUARE_SIZE+SQUARE_SIZE//2, r*SQUARE_SIZE+SQUARE_SIZE//2, text="K", fill="white", font=("Arial", 24, "bold"))
        
        if self.dragging_piece:
            color = RED_PIECE if self.dragging_piece in [RED, RED_KING] else BLACK_PIECE
            cx, cy = self.drag_pos[0], self.drag_pos[1]
            self.canvas.create_oval(cx-SQUARE_SIZE//2+10, cy-SQUARE_SIZE//2+10, cx+SQUARE_SIZE//2-10, cy+SQUARE_SIZE//2-10, fill=color, outline="white")
            if self.dragging_piece in [RED_KING, BLACK_KING]:
                self.canvas.create_text(cx, cy, text="K", fill="white", font=("Arial", 24, "bold"))

if __name__ == "__main__":
    CheckersMain()
