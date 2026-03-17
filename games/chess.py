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
HIGHLIGHT_COLOR = "#BBCB48"  # Yellow-ish green for selected/last move
CHECK_COLOR = "#E55342"      # Red for check

# Pieces
EMPTY = "."
PAWN = "P"
KNIGHT = "N"
BISHOP = "B"
ROOK = "R"
QUEEN = "Q"
KING = "K"

# Sides
WHITE = "w"
BLACK = "b"

# Unicode Pieces
UNICODE_PIECES = {
    "wP": "♙", "wN": "♘", "wB": "♗", "wR": "♖", "wQ": "♕", "wK": "♔",
    "bP": "♟", "bN": "♞", "bB": "♝", "bR": "♜", "bQ": "♛", "bK": "♚"
}

# Values for AI
PIECE_VALUES = {
    PAWN: 100, KNIGHT: 320, BISHOP: 330, ROOK: 500, QUEEN: 900, KING: 20000
}

# Position Tables (Simplified from Sunfish/Stockfish concepts)
pst = {
    PAWN: (
        0,  0,  0,  0,  0,  0,  0,  0,
        50, 50, 50, 50, 50, 50, 50, 50,
        10, 10, 20, 30, 30, 20, 10, 10,
        5,  5, 10, 25, 25, 10,  5,  5,
        0,  0,  0, 20, 20,  0,  0,  0,
        5, -5,-10,  0,  0,-10, -5,  5,
        5, 10, 10,-20,-20, 10, 10,  5,
        0,  0,  0,  0,  0,  0,  0,  0
    ),
    KNIGHT: (
        -50,-40,-30,-30,-30,-30,-40,-50,
        -40,-20,  0,  0,  0,  0,-20,-40,
        -30,  0, 10, 15, 15, 10,  0,-30,
        -30,  5, 15, 20, 20, 15,  5,-30,
        -30,  0, 15, 20, 20, 15,  0,-30,
        -30,  5, 10, 15, 15, 10,  5,-30,
        -40,-20,  0,  5,  5,  0,-20,-40,
        -50,-40,-30,-30,-30,-30,-40,-50
    ),
    BISHOP: (
        -20,-10,-10,-10,-10,-10,-10,-20,
        -10,  0,  0,  0,  0,  0,  0,-10,
        -10,  0,  5, 10, 10,  5,  0,-10,
        -10,  5,  5, 10, 10,  5,  5,-10,
        -10,  0, 10, 10, 10, 10,  0,-10,
        -10, 10, 10, 10, 10, 10, 10,-10,
        -10,  5,  0,  0,  0,  0,  5,-10,
        -20,-10,-10,-10,-10,-10,-10,-20
    ),
    ROOK: (
        0,  0,  0,  0,  0,  0,  0,  0,
        5, 10, 10, 10, 10, 10, 10,  5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        0,  0,  0,  5,  5,  0,  0,  0
    ),
    QUEEN: (
        -20,-10,-10, -5, -5,-10,-10,-20,
        -10,  0,  0,  0,  0,  0,  0,-10,
        -10,  0,  5,  5,  5,  5,  0,-10,
        -5,  0,  5,  5,  5,  5,  0, -5,
        0,  0,  5,  5,  5,  5,  0, -5,
        -10,  5,  5,  5,  5,  5,  0,-10,
        -10,  0,  5,  0,  0,  0,  0,-10,
        -20,-10,-10, -5, -5,-10,-10,-20
    ),
    KING: (
        -30,-40,-40,-50,-50,-40,-40,-30,
        -30,-40,-40,-50,-50,-40,-40,-30,
        -30,-40,-40,-50,-50,-40,-40,-30,
        -30,-40,-40,-50,-50,-40,-40,-30,
        -20,-30,-30,-40,-40,-30,-30,-20,
        -10,-20,-20,-20,-20,-20,-20,-10,
        20, 20,  0,  0,  0,  0, 20, 20,
        20, 30, 10,  0,  0, 10, 30, 20
    )
}

# --- Game Logic ---

class GameState:
    def __init__(self):
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            [EMPTY] * 8, [EMPTY] * 8, [EMPTY] * 8, [EMPTY] * 8,
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]
        self.white_to_move = True
        self.move_log = []
        self.white_king_location = (7, 4)
        self.black_king_location = (0, 4)
        self.checkmate = False
        self.stalemate = False
        # Castling rights
        self.current_castling_right = CastleRights(True, True, True, True)
        self.castle_rights_log = [CastleRights(True, True, True, True)]

    def make_move(self, move):
        self.board[move.start_row][move.start_col] = EMPTY
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.move_log.append(move)  # Log the move
        self.white_to_move = not self.white_to_move  # Swap players
        
        # Update King's location if moved
        if move.piece_moved == "wK":
            self.white_king_location = (move.end_row, move.end_col)
        elif move.piece_moved == "bK":
            self.black_king_location = (move.end_row, move.end_col)

        # Castling Move
        if move.is_castle_move:
            if move.end_col - move.start_col == 2:  # Kingside
                self.board[move.end_row][move.end_col - 1] = self.board[move.end_row][move.end_col + 1] # Move Rook
                self.board[move.end_row][move.end_col + 1] = EMPTY
            else:  # Queenside
                self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 2] # Move Rook
                self.board[move.end_row][move.end_col - 2] = EMPTY
        
        # Update Castling Rights - whenever a rook or king moves
        self.update_castle_rights(move)
        self.castle_rights_log.append(CastleRights(self.current_castling_right.wks, self.current_castling_right.bks, 
                                                   self.current_castling_right.wqs, self.current_castling_right.bqs))

    def undo_move(self):
        if len(self.move_log) != 0:
            move = self.move_log.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            self.white_to_move = not self.white_to_move
            
            # Update King's location
            if move.piece_moved == "wK":
                self.white_king_location = (move.start_row, move.start_col)
            elif move.piece_moved == "bK":
                self.black_king_location = (move.start_row, move.start_col)
            
            # Undo Castling Move
            if move.is_castle_move:
                if move.end_col - move.start_col == 2:  # Kingside
                    self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 1]
                    self.board[move.end_row][move.end_col - 1] = EMPTY
                else:  # Queenside
                    self.board[move.end_row][move.end_col - 2] = self.board[move.end_row][move.end_col + 1]
                    self.board[move.end_row][move.end_col + 1] = EMPTY

            # Undo Castling Rights
            self.castle_rights_log.pop()
            new_rights = self.castle_rights_log[-1]
            self.current_castling_right = CastleRights(new_rights.wks, new_rights.bks, new_rights.wqs, new_rights.bqs)
            
            self.checkmate = False
            self.stalemate = False

    def update_castle_rights(self, move):
        if move.piece_moved == "wK":
            self.current_castling_right.wks = False
            self.current_castling_right.wqs = False
        elif move.piece_moved == "bK":
            self.current_castling_right.bks = False
            self.current_castling_right.bqs = False
        elif move.piece_moved == "wR":
            if move.start_row == 7:
                if move.start_col == 0:  # Left Rook
                    self.current_castling_right.wqs = False
                elif move.start_col == 7:  # Right Rook
                    self.current_castling_right.wks = False
        elif move.piece_moved == "bR":
            if move.start_row == 0:
                if move.start_col == 0:  # Left Rook
                    self.current_castling_right.bqs = False
                elif move.start_col == 7:  # Right Rook
                    self.current_castling_right.bks = False

    def get_valid_moves(self):
        # 1. Generate all pseudo-legal moves
        temp_en_passant_possible = False # Placeholder if we add en passant
        moves = self.get_all_possible_moves()
        
        # 2. Filter moves that leave king in check
        if self.white_to_move:
            self.get_castle_moves(self.white_king_location[0], self.white_king_location[1], moves)
        else:
            self.get_castle_moves(self.black_king_location[0], self.black_king_location[1], moves)
            
        for i in range(len(moves) - 1, -1, -1): # Go backwards to remove
            self.make_move(moves[i])
            self.white_to_move = not self.white_to_move # Switch back to see if *current* player is in check
            if self.in_check():
                moves.remove(moves[i])
            self.white_to_move = not self.white_to_move
            self.undo_move()
            
        if len(moves) == 0:
            if self.in_check():
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False
            
        return moves

    def in_check(self):
        if self.white_to_move:
            return self.square_under_attack(self.white_king_location[0], self.white_king_location[1])
        else:
            return self.square_under_attack(self.black_king_location[0], self.black_king_location[1])

    def square_under_attack(self, r, c):
        self.white_to_move = not self.white_to_move # Switch to opponent's POV
        opp_moves = self.get_all_possible_moves()
        self.white_to_move = not self.white_to_move # Switch back
        for move in opp_moves:
            if move.end_row == r and move.end_col == c:
                return True
        return False

    def get_all_possible_moves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn == "w" and self.white_to_move) or (turn == "b" and not self.white_to_move):
                    piece = self.board[r][c][1]
                    if piece == "P": self.get_pawn_moves(r, c, moves)
                    elif piece == "R": self.get_rook_moves(r, c, moves)
                    elif piece == "N": self.get_knight_moves(r, c, moves)
                    elif piece == "B": self.get_bishop_moves(r, c, moves)
                    elif piece == "Q": self.get_queen_moves(r, c, moves)
                    elif piece == "K": self.get_king_moves(r, c, moves)
        return moves

    def get_pawn_moves(self, r, c, moves):
        if self.white_to_move: # White moves up (-1)
            if self.board[r-1][c] == EMPTY: # 1 sq move
                moves.append(Move((r, c), (r-1, c), self.board))
                if r == 6 and self.board[r-2][c] == EMPTY: # 2 sq move
                    moves.append(Move((r, c), (r-2, c), self.board))
            if c-1 >= 0: # Capture left
                if self.board[r-1][c-1][0] == "b":
                    moves.append(Move((r, c), (r-1, c-1), self.board))
            if c+1 <= 7: # Capture right
                if self.board[r-1][c+1][0] == "b":
                    moves.append(Move((r, c), (r-1, c+1), self.board))
        else: # Black moves down (+1)
            if self.board[r+1][c] == EMPTY:
                moves.append(Move((r, c), (r+1, c), self.board))
                if r == 1 and self.board[r+2][c] == EMPTY:
                    moves.append(Move((r, c), (r+2, c), self.board))
            if c-1 >= 0:
                if self.board[r+1][c-1][0] == "w":
                    moves.append(Move((r, c), (r+1, c-1), self.board))
            if c+1 <= 7:
                if self.board[r+1][c+1][0] == "w":
                    moves.append(Move((r, c), (r+1, c+1), self.board))

    def get_rook_moves(self, r, c, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1)) # up, left, down, right
        enemy_color = "b" if self.white_to_move else "w"
        for d in directions:
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    if end_piece == EMPTY:
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                    elif end_piece[0] == enemy_color:
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                        break
                    else:
                        break # Friendly piece
                else:
                    break

    def get_knight_moves(self, r, c, moves):
        knight_moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        enemy_color = "b" if self.white_to_move else "w"
        for m in knight_moves:
            end_row = r + m[0]
            end_col = c + m[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece == EMPTY or end_piece[0] == enemy_color:
                    moves.append(Move((r, c), (end_row, end_col), self.board))

    def get_bishop_moves(self, r, c, moves):
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemy_color = "b" if self.white_to_move else "w"
        for d in directions:
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    if end_piece == EMPTY:
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                    elif end_piece[0] == enemy_color:
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                        break
                    else:
                        break
                else:
                    break

    def get_queen_moves(self, r, c, moves):
        self.get_rook_moves(r, c, moves)
        self.get_bishop_moves(r, c, moves)

    def get_king_moves(self, r, c, moves):
        king_moves = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
        enemy_color = "b" if self.white_to_move else "w"
        for i in range(8):
            end_row = r + king_moves[i][0]
            end_col = c + king_moves[i][1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece == EMPTY or end_piece[0] == enemy_color:
                    moves.append(Move((r, c), (end_row, end_col), self.board))

    def get_castle_moves(self, r, c, moves):
        if self.square_under_attack(r, c):
            return # Can't castle out of check
        if (self.white_to_move and self.current_castling_right.wks) or \
           (not self.white_to_move and self.current_castling_right.bks):
            self.get_kingside_castle_moves(r, c, moves)
        if (self.white_to_move and self.current_castling_right.wqs) or \
           (not self.white_to_move and self.current_castling_right.bqs):
            self.get_queenside_castle_moves(r, c, moves)

    def get_kingside_castle_moves(self, r, c, moves):
        if self.board[r][c+1] == EMPTY and self.board[r][c+2] == EMPTY:
            if not self.square_under_attack(r, c+1) and not self.square_under_attack(r, c+2):
                moves.append(Move((r, c), (r, c+2), self.board, is_castle_move=True))

    def get_queenside_castle_moves(self, r, c, moves):
        if self.board[r][c-1] == EMPTY and self.board[r][c-2] == EMPTY and self.board[r][c-3] == EMPTY:
            if not self.square_under_attack(r, c-1) and not self.square_under_attack(r, c-2):
                moves.append(Move((r, c), (r, c-2), self.board, is_castle_move=True))

class CastleRights:
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs

class Move:
    def __init__(self, start_sq, end_sq, board, is_castle_move=False):
        self.start_row = start_sq[0]
        self.start_col = start_sq[1]
        self.end_row = end_sq[0]
        self.end_col = end_sq[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]
        self.move_id = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col
        self.is_castle_move = is_castle_move
        
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.move_id == other.move_id
        return False

    def get_chess_notation(self):
        return self.get_rank_file(self.start_row, self.start_col) + self.get_rank_file(self.end_row, self.end_col)

    def get_rank_file(self, r, c):
        cols_to_files = {0: "a", 1: "b", 2: "c", 3: "d", 4: "e", 5: "f", 6: "g", 7: "h"}
        rows_to_ranks = {0: "8", 1: "7", 2: "6", 3: "5", 4: "4", 5: "3", 6: "2", 7: "1"}
        return cols_to_files[c] + rows_to_ranks[r]

# --- AI ---
def find_best_move(game_state, valid_moves):
    global next_move
    next_move = None
    random.shuffle(valid_moves) # Shuffle to add variety if scores are equal
    find_move_nega_max_alpha_beta(game_state, valid_moves, 3, -float("inf"), float("inf"), 1 if game_state.white_to_move else -1)
    return next_move

def find_move_nega_max_alpha_beta(game_state, valid_moves, depth, alpha, beta, turn_multiplier):
    global next_move
    if depth == 0:
        return turn_multiplier * score_board(game_state)
    
    max_score = -float("inf")
    for move in valid_moves:
        game_state.make_move(move)
        next_moves = game_state.get_valid_moves()
        score = -find_move_nega_max_alpha_beta(game_state, next_moves, depth - 1, -beta, -alpha, -turn_multiplier)
        game_state.undo_move()
        if score > max_score:
            max_score = score
            if depth == 3: # Root depth
                next_move = move
        if max_score > alpha:
            alpha = max_score
        if alpha >= beta:
            break
    return max_score

def score_board(game_state):
    if game_state.checkmate:
        if game_state.white_to_move:
            return -20000
        else:
            return 20000
    if game_state.stalemate:
        return 0
    
    score = 0
    for r in range(len(game_state.board)):
        for c in range(len(game_state.board[r])):
            square = game_state.board[r][c]
            if square != EMPTY:
                piece_type = square[1]
                piece_color = square[0]
                
                # Material Score
                base_val = PIECE_VALUES[piece_type]
                
                # Positional Score
                pos_table = pst[piece_type]
                if piece_color == "w":
                    # Flip index for white because table is defined for black/mirrored
                    pos_val = pos_table[r*8 + c]
                else:
                    # Mirror row for black
                    pos_val = pos_table[(7-r)*8 + c]

                if piece_color == "w":
                    score += base_val + pos_val
                else:
                    score -= base_val + pos_val
    return score

# --- GUI ---
class ChessMain:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Impossible Chess")
        self.canvas = tk.Canvas(self.window, width=width, height=height)
        self.canvas.pack()
        
        self.gs = GameState()
        self.valid_moves = self.gs.get_valid_moves()
        self.move_made = False 
        self.load_images() 
        
        self.selected_sq = None  # (row, col)
        self.dragging_piece = None # piece string
        self.drag_pos = (0, 0) # (x, y)
        
        self.game_over = False
        self.player_one = True # Human = White
        self.player_two = False # AI = Black

        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        
        self.draw_game_state()
        self.window.mainloop()

    def load_images(self):
        self.font_size = 48

    def on_press(self, event):
        if self.game_over: return
        if not ((self.gs.white_to_move and self.player_one) or (not self.gs.white_to_move and self.player_two)):
            return

        col = event.x // SQUARE_SIZE
        row = event.y // SQUARE_SIZE
        piece = self.gs.board[row][col]
        
        # Only allow picking up own pieces
        turn_color = "w" if self.gs.white_to_move else "b"
        if piece != EMPTY and piece[0] == turn_color:
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
        
        # Basic bounds check
        if 0 <= end_row < 8 and 0 <= end_col < 8:
            move = Move((start_row, start_col), (end_row, end_col), self.gs.board)
            # Check if it's a valid move (including special moves like castle)
            move_found = False
            for m in self.valid_moves:
                if move == m:
                    self.gs.make_move(m)
                    self.move_made = True
                    move_found = True
                    break
        
        self.dragging_piece = None
        self.selected_sq = None
        self.draw_game_state()
        
        if self.move_made:
            self.valid_moves = self.gs.get_valid_moves()
            self.move_made = False
            self.window.update()
            # AI Move if it's AI's turn
            if not self.game_over and not ((self.gs.white_to_move and self.player_one) or (not self.gs.white_to_move and self.player_two)):
                self.window.after(100, self.ai_move)

    def ai_move(self):
        self.valid_moves = self.gs.get_valid_moves()
        if not self.game_over:
            ai_move = find_best_move(self.gs, self.valid_moves)
            if ai_move is None and len(self.valid_moves) > 0:
                ai_move = random.choice(self.valid_moves)
            if ai_move:
                self.gs.make_move(ai_move)
                self.move_made = True
                self.draw_game_state()

        if self.move_made:
            self.valid_moves = self.gs.get_valid_moves()
            self.move_made = False

    def draw_game_state(self):
        self.draw_board()
        self.draw_pieces()
        self.highlight_squares()
        
        if self.gs.checkmate:
            self.game_over = True
            winner = "Black" if self.gs.white_to_move else "White"
            self.window.after(200, lambda: messagebox.showinfo("Game Over", f"{winner} wins by Checkmate!"))
        elif self.gs.stalemate:
            self.game_over = True
            self.window.after(200, lambda: messagebox.showinfo("Game Over", "Stalemate!"))

    def draw_board(self):
        colors = [LIGHT_SQUARE, DARK_SQUARE]
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                color = colors[((r+c) % 2)]
                self.canvas.create_rectangle(c*SQUARE_SIZE, r*SQUARE_SIZE, (c+1)*SQUARE_SIZE, (r+1)*SQUARE_SIZE, fill=color, outline="")

    def highlight_squares(self):
        # Highlight last move
        if len(self.gs.move_log) > 0:
            last_move = self.gs.move_log[-1]
            self.highlight_square(last_move.start_row, last_move.start_col, "yellow")
            self.highlight_square(last_move.end_row, last_move.end_col, "yellow")
        
        # Highlight selected square
        if self.selected_sq:
            self.highlight_square(self.selected_sq[0], self.selected_sq[1], "blue")

    def highlight_square(self, r, c, color):
        self.canvas.create_rectangle(c*SQUARE_SIZE, r*SQUARE_SIZE, (c+1)*SQUARE_SIZE, (r+1)*SQUARE_SIZE, width=3, outline=color)

    def draw_pieces(self):
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                piece = self.gs.board[r][c]
                # Don't draw the piece if it's currently being dragged
                if self.selected_sq == (r, c) and self.dragging_piece:
                    continue
                if piece != EMPTY:
                    self.canvas.create_text(c*SQUARE_SIZE + SQUARE_SIZE/2, r*SQUARE_SIZE + SQUARE_SIZE/2, text=UNICODE_PIECES[piece], font=("Arial", self.font_size), fill="black")
        
        # Draw dragging piece on top
        if self.dragging_piece:
            self.canvas.create_text(self.drag_pos[0], self.drag_pos[1], text=UNICODE_PIECES[self.dragging_piece], font=("Arial", self.font_size), fill="black")

if __name__ == "__main__":
    ChessMain()
