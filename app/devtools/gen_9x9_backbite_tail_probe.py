"""Dev tool: probe 9x9 backbite_v1 generation and report tail heuristic metrics.

Run with project venv Python. Prints per-seed clue counts, density, and tail length of given suffix.
"""
import os
import sys

# Ensure project root is on sys.path when running as a script
THIS_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(THIS_DIR, "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from generate.generator import Generator

def head_len_from_givens(givens: list[tuple[int, int, int]]) -> int:
    values = {v for _, _, v in givens}
    v = 1
    hl = 0
    while v in values:
        hl += 1
        v += 1
    return hl

SEEDS = [42, 99, 123, 2025, 314159, 8675309]


def tail_len_from_givens(givens: list[tuple[int, int, int]], max_v: int) -> int:
    values = {v for _, _, v in givens}
    v = max_v
    tl = 0
    while v >= 1 and v in values:
        tl += 1
        v -= 1
    return tl


def main():
    for sd in SEEDS:
        try:
            gp = Generator.generate_puzzle(
                size=9,
                difficulty="hard",
                path_mode="backbite_v1",
                seed=sd,
                allow_diagonal=True,
                structural_repair_enabled=False,
            )
        except Exception as e:
            print(f"Seed={sd} ERROR: {e}")
            continue
        if gp is None:
            print(f"Seed={sd} generation failed")
            continue
        max_v = len(gp.solution)
        tl = tail_len_from_givens(gp.givens, max_v)
        hl = head_len_from_givens(gp.givens)
        density = gp.clue_count / max_v if max_v else 1.0
        print(
            f"Seed={sd} clues={gp.clue_count} density={density:.3f} head_len={hl} tail_len={tl} path={gp.path_mode} anchors={len(gp.solver_metrics.get('anchor_positions', []))}"
        )


if __name__ == "__main__":
    main()
