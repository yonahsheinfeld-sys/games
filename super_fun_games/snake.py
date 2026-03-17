#!/usr/bin/env python3
"""A simple Snake clone you can play entirely from the terminal."""

import argparse
import os
import random
import sys
import time
from collections import deque

try:
    import msvcrt
except ImportError:  # pragma: no cover - platform specific
    msvcrt = None

if os.name != "nt":
    import select
    import termios
    import tty
else:  # pragma: no cover - platform specific
    select = termios = tty = None

CLEAR_CMD = "cls" if os.name == "nt" else "clear"

KEY_NORMALIZATION = {
    "w": "up",
    "k": "up",
    "i": "up",
    "s": "down",
    "j": "left",
    "a": "left",
    "h": "left",
    "l": "right",
    "d": "right",
    "q": "quit",
    "\x1b": "quit",
    "escape": "quit",
    "up": "up",
    "down": "down",
    "left": "left",
    "right": "right",
}

WINDOWS_ARROW_KEYS = {
    "H": "up",
    "P": "down",
    "K": "left",
    "M": "right",
}

UNICODE_ARROW_SEQS = {
    "\x1b[A": "up",
    "\x1b[B": "down",
    "\x1b[D": "left",
    "\x1b[C": "right",
}

DIRECTION_VECTORS = {
    "up": (0, -1),
    "down": (0, 1),
    "left": (-1, 0),
    "right": (1, 0),
}


def clear_screen():
    os.system(CLEAR_CMD)


def normalize_key(raw):
    if raw is None:
        return None
    return KEY_NORMALIZATION.get(raw.lower(), raw.lower())


class KeyPoller:
    """Non-blocking key reader for Windows and Unix terminals."""

    def __init__(self):
        self.is_windows = os.name == "nt"
        self.fd = None
        self.old_settings = None
        if not self.is_windows:
            self.fd = sys.stdin.fileno()
            self.old_settings = termios.tcgetattr(self.fd)

    def __enter__(self):
        if not self.is_windows and self.fd is not None:
            tty.setcbreak(self.fd)
        return self

    def __exit__(self, exc_type, exc, exc_tb):
        self.close()

    def close(self):
        if not self.is_windows and self.fd is not None and self.old_settings is not None:
            termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old_settings)

    def poll(self):
        if self.is_windows:
            return self._poll_windows()
        return self._poll_unix()

    def _poll_windows(self):
        if not msvcrt or not msvcrt.kbhit():
            return None
        key = msvcrt.getwch()
        if key in ("\x00", "\xe0"):
            arrow = msvcrt.getwch()
            return WINDOWS_ARROW_KEYS.get(arrow)
        return normalize_key(key)

    def _poll_unix(self):
        dr, _, _ = select.select([sys.stdin], [], [], 0)
        if not dr:
            return None
        key = sys.stdin.read(1)
        if key == "\x1b":
            seq = sys.stdin.read(2)
            return UNICODE_ARROW_SEQS.get(key + seq, "escape")
        return normalize_key(key)


def random_food_position(width, height, occupied):
    empty = [
        (x, y)
        for y in range(height)
        for x in range(width)
        if (x, y) not in occupied
    ]
    if not empty:
        return None
    return random.choice(empty)


def render_board(width, height, snake, food, score, high_score, status, delay):
    clear_screen()
    header = f"Score: {score}  High Score: {high_score}  Speed: {max(1, round(1 / delay, 1))}"
    controls = "Use arrows, WASD, or IJKL to steer. Q/Esc quits the game."
    top_border = "+" + "-" * width + "+"
    print(header)
    print(controls)
    print(top_border)
    snake_body = set(snake)
    for y in range(height):
        row = ["|"]
        for x in range(width):
            pos = (x, y)
            if pos == snake[0]:
                row.append("O")
            elif pos in snake_body:
                row.append("o")
            elif food is not None and pos == food:
                row.append("*")
            else:
                row.append(" ")
        row.append("|")
        print("".join(row))
    print(top_border)
    if status:
        print(status)


def run_game(width, height, base_delay):
    width = max(10, width)
    height = max(10, height)
    base_delay = max(0.02, base_delay)

    start_x = width // 2
    start_y = height // 2
    snake = deque([
        (start_x, start_y),
        (start_x - 1, start_y),
        (start_x - 2, start_y),
    ])
    direction = (1, 0)
    snake_set = set(snake)
    food = random_food_position(width, height, snake_set)
    score = 0
    high_score = 0
    status = "Ready! Use any direction to get started."

    with KeyPoller() as poller:
        render_board(width, height, snake, food, score, high_score, status, base_delay)
        while True:
            frame_start = time.time()
            action = poller.poll()
            if action == "quit":
                status = "Quit command received."
                break
            if action in DIRECTION_VECTORS:
                new_direction = DIRECTION_VECTORS[action]
                if not is_opposite(direction, new_direction):
                    direction = new_direction
            new_head = (snake[0][0] + direction[0], snake[0][1] + direction[1])
            if not (0 <= new_head[0] < width and 0 <= new_head[1] < height):
                status = "Bumped into the wall!"
                break
            will_eat = food is not None and new_head == food
            if not will_eat:
                tail = snake.pop()
                snake_set.remove(tail)
            if new_head in snake_set:
                status = "You ran into your own body!"
                break
            snake.appendleft(new_head)
            snake_set.add(new_head)
            if will_eat:
                score += 1
                high_score = max(high_score, score)
                food = random_food_position(width, height, snake_set)
                if food is None:
                    status = "Victory! You filled the board."
                    break
                status = "Food eaten! Keep going."
            delay = compute_delay(base_delay, score)
            render_board(width, height, snake, food, score, high_score, status, delay)
            elapsed = time.time() - frame_start
            if elapsed < delay:
                time.sleep(delay - elapsed)

    final_delay = compute_delay(base_delay, score)
    render_board(width, height, snake, food, score, high_score, status, final_delay)
    print("Game over. Thanks for playing!")


def is_opposite(current, new):
    return current[0] == -new[0] and current[1] == -new[1]


def compute_delay(base_delay, score):
    ramp = min(score, 30)
    return max(0.02, base_delay - ramp * 0.003)


def main():
    parser = argparse.ArgumentParser(description="Play Snake inside your terminal.")
    parser.add_argument("--width", "-w", type=int, default=40, help="Board width (min 10).")
    parser.add_argument("--height", "-H", type=int, default=20, help="Board height (min 10).")
    parser.add_argument(
        "--speed",
        "-s",
        type=float,
        default=0.14,
        help="Starting delay between frames in seconds (lower = faster).",
    )
    args = parser.parse_args()
    run_game(args.width, args.height, args.speed)


if __name__ == "__main__":
    main()
