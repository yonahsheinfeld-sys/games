"""
Simple console Tic-Tac-Toe for two players.

Players alternate placing X and O on a 3×3 grid. The game ends when one wins
(three in a row vertically, horizontally, or diagonally) or the grid fills.
"""

from typing import Iterable


WINNING_LINES = (
    (0, 1, 2),
    (3, 4, 5),
    (6, 7, 8),
    (0, 3, 6),
    (1, 4, 7),
    (2, 5, 8),
    (0, 4, 8),
    (2, 4, 6),
)


def display_board(board: Iterable[str]) -> None:
    """Print the numbered board with current marks."""
    cells = [cell if cell != " " else str(idx + 1) for idx, cell in enumerate(board)]
    print()
    for row in range(3):
        start = row * 3
        print(f" {cells[start]} | {cells[start+1]} | {cells[start+2]}")
        if row < 2:
            print("---+---+---")
    print()


def check_winner(board: Iterable[str]) -> str | None:
    """Return the winner symbol or None."""
    for a, b, c in WINNING_LINES:
        if board[a] != " " and board[a] == board[b] == board[c]:
            return board[a]
    return None


def is_draw(board: Iterable[str]) -> bool:
    """Check whether the board is full without a winner."""
    return all(cell != " " for cell in board)


def prompt_move(player: str, board: list[str]) -> int:
    """Ask the player for a valid move (1-9)."""
    while True:
        try:
            choice = int(input(f"Player {player}, choose a square (1-9): ").strip())
        except ValueError:
            print("Invalid number. Enter 1 through 9.")
            continue
        if not 1 <= choice <= 9:
            print("Pick a position between 1 and 9.")
            continue
        if board[choice - 1] != " ":
            print("That square is already taken.")
            continue
        return choice - 1


def play_round() -> None:
    """Run one game until win or draw."""
    board = [" "] * 9
    current_player = "X"
    print("Let's play Tic-Tac-Toe!")

    while True:
        display_board(board)
        chosen_index = prompt_move(current_player, board)
        board[chosen_index] = current_player
        winner = check_winner(board)
        if winner:
            display_board(board)
            print(f"Player {winner} wins!")
            break
        if is_draw(board):
            display_board(board)
            print("It's a draw!")
            break
        current_player = "O" if current_player == "X" else "X"


def main() -> None:
    """Loop rounds until the user quits."""
    while True:
        play_round()
        again = input("Play again? (y/n): ").strip().lower()
        if not again or again[0] != "y":
            print("Goodbye!")
            break


if __name__ == "__main__":
    main()
