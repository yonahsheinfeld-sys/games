#!/usr/bin/env python3
"""
Pop the Lock–style CLI minigame.

Goal: time your button press so the moving cursor lands inside the highlighted zone.
"""

from __future__ import annotations

import random
import time

try:
    import msvcrt
except ImportError:  # pragma: no cover
    msvcrt = None  # type: ignore[assignment]

TRACK_LENGTH = 30
HITS_TO_OPEN = 10
BASE_SPEED = 0.05


def render_track(pointer: int, zone_start: int, zone_end: int) -> str:
    """Render a single line that highlights the success zone and cursor."""
    track_chars = []
    for pos in range(TRACK_LENGTH):
        if zone_start <= pos <= zone_end:
            char = "="
        else:
            char = "-"
        if pos == pointer:
            char = "●"
        track_chars.append(char)
    return "".join(track_chars)


def spin_stage(stage: int) -> bool:
    """Animate the cursor until the player presses space/enter and return success."""
    zone_size = max(5, 8 - (stage // 2))
    zone_start = random.randint(1, TRACK_LENGTH - zone_size - 2)
    zone_end = zone_start + zone_size - 1
    pointer = 0
    direction = 1
    speed = max(0.03, BASE_SPEED - stage * 0.002)

    print("\nPress Space or Enter when the cursor lands inside the highlighted zone.")
    if not msvcrt:
        print("(Realtime input unavailable; a random position will be used.)")
        pointer = random.randrange(TRACK_LENGTH)
        print(render_stage(pointer, zone_start, zone_end, stage), flush=True)
        input("Press Enter to lock in that position.")
        print()
        return zone_start <= pointer <= zone_end

    while True:
        pointer += direction
        if pointer >= TRACK_LENGTH - 1:
            pointer = TRACK_LENGTH - 1
            direction = -1
        elif pointer <= 0:
            pointer = 0
            direction = 1

        print(render_stage(pointer, zone_start, zone_end, stage), end="\r", flush=True)

        if msvcrt and msvcrt.kbhit():
            key = msvcrt.getch()
            if key in (b" ", b"\r", b"\n"):
                print()
                return zone_start <= pointer <= zone_end
            if key == b"\x03":  # Ctrl+C
                raise KeyboardInterrupt

        time.sleep(speed)


def render_stage(pointer: int, zone_start: int, zone_end: int, stage: int) -> str:
    """Build the console string that shows progress and the moving cursor."""
    track = render_track(pointer, zone_start, zone_end)
    return f"Stage {stage}/{HITS_TO_OPEN} | {track}"


def main() -> None:
    print("=" * 48)
    print("Pop the Lock (CLI Edition)")
    print("Land the cursor in the highlighted zone before the timer runs out.")
    print("Press Space or Enter while the cursor is in the zone to lock it.")
    print("You need five successful hits to unlock the lock.")
    print("Ctrl+C exits anytime.")
    print("=" * 48)

    stage = 1
    tries = 0

    try:
        while stage <= HITS_TO_OPEN:
            success = spin_stage(stage)
            tries += 1
            if success:
                print(f"You nailed it! {stage}/{HITS_TO_OPEN} locks completed.")
                stage += 1
            else:
                print("Missed! The lock breaks immediately, so the run ends here.")
                print(f"You reached {stage - 1}/{HITS_TO_OPEN} completed locks.")
                return

        print("=" * 48)
        print(f"Lock opened in {tries} tries. Nicely done!")
    except KeyboardInterrupt:
        print("\nGame interrupted. Thanks for playing!")


if __name__ == "__main__":
    main()
