"""
Super Tic-Tac-Toe (Ultimate Tic-Tac-Toe) with a computer AI.

Rules:
- 3x3 grid of 3x3 small boards.
- A move in a cell (e.g., top-left) of a small board forces the opponent
  to play in the corresponding small board (e.g., top-left board).
- Winning a small board marks it for that player.
- Getting 3 small boards in a row on the large grid wins the game.
- If sent to a board that is already won or full, you can move anywhere.
"""

import copy
import random
import sys

# Winning lines for a 3x3 board
WINNING_LINES = (
    (0, 1, 2), (3, 4, 5), (6, 7, 8),  # Rows
    (0, 3, 6), (1, 4, 7), (2, 5, 8),  # Cols
    (0, 4, 8), (2, 4, 6)              # Diagonals
)

class SuperTicTacToe:
    def __init__(self):
        # 9 small boards, each with 9 cells
        self.boards = [[" " for _ in range(9)] for _ in range(9)]
        # Winner of each small board (' ', 'X', 'O', or 'T' for Tie)
        self.macro_board = [" " for _ in range(9)]
        # Index of the board for the next move (-1 for free choice)
        self.next_board = -1
        # Current player ('X' or 'O')
        self.current_player = "X"

    def check_winner(self, board):
        """Returns the winner ('X' or 'O') of a 3x3 board or None."""
        for a, b, c in WINNING_LINES:
            if board[a] != " " and board[a] == board[b] == board[c]:
                return board[a]
        return None

    def is_full(self, board):
        """Returns True if the board has no empty cells."""
        return all(cell != " " for cell in board)

    def get_valid_moves(self):
        """Returns a list of (board_idx, cell_idx) for valid moves."""
        moves = []
        if self.next_board != -1:
            # Must play in the specified board
            for cell_idx, cell in enumerate(self.boards[self.next_board]):
                if cell == " ":
                    moves.append((self.next_board, cell_idx))
        
        # If no valid moves in specified board, or free choice
        if not moves:
            for b_idx, board in enumerate(self.boards):
                if self.macro_board[b_idx] == " ":
                    for c_idx, cell in enumerate(board):
                        if cell == " ":
                            moves.append((b_idx, c_idx))
        return moves

    def make_move(self, board_idx, cell_idx):
        """Applies a move and updates the state."""
        self.boards[board_idx][cell_idx] = self.current_player
        
        # Check if this move wins the small board
        winner = self.check_winner(self.boards[board_idx])
        if winner:
            self.macro_board[board_idx] = winner
        elif self.is_full(self.boards[board_idx]):
            self.macro_board[board_idx] = "T" # Tie

        # Determine next board
        if self.macro_board[cell_idx] == " ":
            self.next_board = cell_idx
        else:
            self.next_board = -1 # Free choice

        self.current_player = "O" if self.current_player == "X" else "X"

    def display(self):
        """Prints the current state of the game."""
        print("\n" + "=" * 33)
        print("      SUPER TIC-TAC-TOE")
        print("=" * 33)
        
        # Print macro board status
        print(f"Next Board: {'ANY' if self.next_board == -1 else self.next_board + 1}")
        print(f"Current Player: {self.current_player}")
        print("-" * 33)

        for row_group in range(3):
            for cell_row in range(3):
                row_str = " "
                for col_group in range(3):
                    b_idx = row_group * 3 + col_group
                    winner = self.macro_board[b_idx]
                    
                    for cell_col in range(3):
                        c_idx = cell_row * 3 + cell_col
                        val = self.boards[b_idx][c_idx]
                        
                        if winner == "X":
                            display_val = "X"
                        elif winner == "O":
                            display_val = "O"
                        elif winner == "T":
                            display_val = "#"
                        else:
                            display_val = val if val != " " else "."
                        
                        row_str += display_val
                        if cell_col < 2: row_str += " "
                    
                    if col_group < 2:
                        row_str += " | "
                print(row_str)
            if row_group < 2:
                print(" " + "-------+-------+-------")
        
        # Print only the Reference Board Layout
        print("\nBoard Layout Reference:")
        for r in range(3):
            l_line = "  "
            for c in range(3):
                l_line += str(r*3 + c + 1) + " "
            print(l_line)
        print("-" * 33)

def evaluate(game):
    """Heuristic evaluation of the game state for AI."""
    winner = game.check_winner(game.macro_board)
    if winner == "O": return 1000
    if winner == "X": return -1000
    if game.is_full(game.macro_board): return 0
    
    score = 0
    # Score small board wins
    for i in range(9):
        if game.macro_board[i] == "O": score += 100
        elif game.macro_board[i] == "X": score -= 100
        
    # Score 2-in-a-row in macro board
    for a, b, c in WINNING_LINES:
        line = [game.macro_board[a], game.macro_board[b], game.macro_board[c]]
        if line.count("O") == 2 and line.count(" ") == 1: score += 50
        if line.count("X") == 2 and line.count(" ") == 1: score -= 50

    # Score small board threats
    for b_idx in range(9):
        if game.macro_board[b_idx] == " ":
            board = game.boards[b_idx]
            for a, b, c in WINNING_LINES:
                line = [board[a], board[b], board[c]]
                if line.count("O") == 2 and line.count(" ") == 1: score += 10
                if line.count("X") == 2 and line.count(" ") == 1: score -= 10
                
    return score

def minimax(game, depth, alpha, beta, is_maximizing):
    winner = game.check_winner(game.macro_board)
    if winner or game.is_full(game.macro_board) or depth == 0:
        return evaluate(game)
    
    valid_moves = game.get_valid_moves()
    if not valid_moves: return evaluate(game)

    if is_maximizing:
        max_eval = -float('inf')
        for move in valid_moves:
            new_game = copy.deepcopy(game)
            new_game.make_move(*move)
            eval = minimax(new_game, depth - 1, alpha, beta, False)
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha: break
        return max_eval
    else:
        min_eval = float('inf')
        for move in valid_moves:
            new_game = copy.deepcopy(game)
            new_game.make_move(*move)
            eval = minimax(new_game, depth - 1, alpha, beta, True)
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha: break
        return min_eval

def get_ai_move(game):
    """Calculates the best move for the AI."""
    valid_moves = game.get_valid_moves()
    best_move = None
    best_val = -float('inf')
    
    # Simple depth limit for speed
    depth = 3 if len(valid_moves) > 20 else 4
    
    # Shuffle moves to add variety
    random.shuffle(valid_moves)
    
    for move in valid_moves:
        new_game = copy.deepcopy(game)
        new_game.make_move(*move)
        move_val = minimax(new_game, depth - 1, -float('inf'), float('inf'), False)
        if move_val > best_val:
            best_val = move_val
            best_move = move
            
    return best_move

def main():
    game = SuperTicTacToe()
    print("Welcome to Super Tic-Tac-Toe!")
    print("Coordinates are 1-9 for board and 1-9 for cell.")
    
    while True:
        game.display()
        
        winner = game.check_winner(game.macro_board)
        if winner:
            print(f"\nGAME OVER! Player {winner} wins the Super Tic-Tac-Toe!")
            break
        if game.is_full(game.macro_board):
            print("\nGAME OVER! It's a draw!")
            break
            
        if game.current_player == "X":
            # Player move
            while True:
                try:
                    prompt = ""
                    if game.next_board == -1:
                        prompt = "Your move. Enter board (1-9) and cell (1-9) separated by space: "
                    else:
                        prompt = f"Board {game.next_board + 1} is active. Enter cell (1-9): "
                    
                    inp = input(prompt).split()
                    if game.next_board == -1:
                        if len(inp) != 2: raise ValueError
                        b_idx, c_idx = int(inp[0]) - 1, int(inp[1]) - 1
                    else:
                        if len(inp) != 1: raise ValueError
                        b_idx, c_idx = game.next_board, int(inp[0]) - 1
                    
                    if (b_idx, c_idx) in game.get_valid_moves():
                        game.make_move(b_idx, c_idx)
                        break
                    else:
                        print("Invalid move. Try again.")
                except (ValueError, IndexError):
                    print("Please enter valid numbers between 1 and 9.")
        else:
            # AI move
            print("AI is thinking...")
            b_idx, c_idx = get_ai_move(game)
            print(f"AI chose Board {b_idx + 1}, Cell {c_idx + 1}")
            game.make_move(b_idx, c_idx)

if __name__ == "__main__":
    main()
