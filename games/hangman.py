"""
Simple Hangman game that adds body parts for each wrong guess.

The chosen word is randomized every round, and the six wrong guesses
correspond to the head, torso, left arm, left leg, right arm, and
right leg in that order.
"""

import random
import string

BODY_PARTS = [
    "head",
    "torso",
    "left arm",
    "left leg",
    "right arm",
    "right leg",
]

WORD_BANK = [
    "python",
    "hangman",
    "nebula",
    "bicycle",
    "jazz",
    "oxygen",
    "planet",
    "galaxy",
    "puzzle",
    "mystery",
    "cipher",
    "journey",
    "zodiac",
    "adventure",
    "horizon",
    "treasure",
    "dragon",
    "alchemy",
    "ember",
    "vacation",
    "forest",
    "island",
    "pirate",
    "quantum",
    "radiant",
    "seascape",
    "tundra",
    "voyage",
    "whisper",
    "zephyr",
    "canvas",
    "dynamo",
    "echo",
    "flutter",
    "glimmer",
    "harbor",
    "ignite",
    "jukebox",
    "kaleidoscope",
    "luminous",
    "miracle",
    "nimbus",
    "oasis",
    "paradox",
    "quartz",
    "rhythm",
    "saffron",
    "tornado",
    "unicorn",
    "vortex",
    "wizard",
    "yonder",
    "zenith",
]


def get_random_word() -> str:
    """Choose and return a random word from the bank."""
    return random.choice(WORD_BANK).upper()


def render_hangman(wrong_parts: list[str]) -> str:
    """Return a simple ASCII hangman based on the wrong body parts."""
    head = "O" if "head" in wrong_parts else " "
    torso = "|" if "torso" in wrong_parts else " "
    left_arm = "/" if "left arm" in wrong_parts else " "
    right_arm = "\\" if "right arm" in wrong_parts else " "
    left_leg = "/" if "left leg" in wrong_parts else " "
    right_leg = "\\" if "right leg" in wrong_parts else " "

    lines = [
        "  ____",
        " |    |",
        f" |    {head}",
        f" |   {left_arm}{torso}{right_arm}",
        f" |   {left_leg} {right_leg}",
        " |",
        "_|_",
    ]

    return "\n".join(lines)


def display_board(
    word: str,
    guessed_letters: set[str],
    wrong_parts: list[str],
    wrong_letters: set[str],
) -> None:
    """Show the current board, guessed letters, and the hangman."""
    puzzle = " ".join(letter if letter in guessed_letters else "_" for letter in word)
    wrong_list = ", ".join(sorted(wrong_letters)) if wrong_letters else "None yet"
    remaining = BODY_PARTS[len(wrong_parts) :]
    remaining_display = ", ".join(remaining) if remaining else "none"

    print()
    print(render_hangman(wrong_parts))
    print()
    print("Word:  ", puzzle)
    print("Wrong letters:", wrong_list)
    print(f"Body parts added ({len(wrong_parts)}/{len(BODY_PARTS)}):", end=" ")
    print(", ".join(wrong_parts) if wrong_parts else "none yet")
    print("Parts remaining:", remaining_display)
    print()


def prompt_for_guess(
    guessed_letters: set[str], wrong_letters: set[str]
) -> str:
    """Ask the player for a new letter and validate the input."""
    while True:
        guess = input("Guess a letter: ").strip().lower()
        if len(guess) != 1 or guess not in string.ascii_lowercase:
            print("Please enter exactly one letter (a–z).")
            continue
        if guess.upper() in guessed_letters or guess.upper() in wrong_letters:
            print("You already guessed that letter. Try a new one.")
            continue
        return guess.upper()


def play_round() -> None:
    """Play one round of Hangman."""
    word = get_random_word()
    guessed_letters: set[str] = set()
    wrong_letters: set[str] = set()
    wrong_parts: list[str] = []

    print("\nStarting a new word. You can make six wrong guesses:")
    print("Head, torso, left arm, left leg, right arm, right leg.")

    while True:
        display_board(word, guessed_letters, wrong_parts, wrong_letters)
        guess = prompt_for_guess(guessed_letters, wrong_letters)
        if guess in word:
            guessed_letters.add(guess)
        else:
            wrong_letters.add(guess)
            part_to_add = BODY_PARTS[len(wrong_parts)]
            wrong_parts.append(part_to_add)
            print(f"Wrong guess. Added the {part_to_add}.")

        if set(word) <= guessed_letters:
            display_board(word, guessed_letters, wrong_parts, wrong_letters)
            print(f"Congrats! You guessed {word}.")
            break

        if len(wrong_parts) >= len(BODY_PARTS):
            display_board(word, guessed_letters, wrong_parts, wrong_letters)
            print(f"Out of chances. The word was {word}.")
            break


def main() -> None:
    """Continuous play loop until the player opts out."""
    print("Hangman — guess the word before the body is complete.")
    while True:
        play_round()
        again = input("Play again? (y/n): ").strip().lower()
        if not again or again[0] != "y":
            print("Thanks for playing Hangman!")
            break


if __name__ == "__main__":
    main()
