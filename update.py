#!/usr/bin/python
"""
This script tracks explicitly installed packages on an Arch Linux system.

Packages are categorized into three groups: base, extra, and aur, with records stored locally and remotely in a GitHub repository.

The script updates the local records to reflect the currently installed packages and prompts the user to commit and push the changes.
"""

import subprocess
import sys
from collections import namedtuple
from pathlib import Path

from typing_extensions import Iterable

ROOT = Path(__file__).parent


def diff(current: Iterable[str], new: Iterable[str]) -> tuple[str]:
    Diff = namedtuple("Diff", ["added", "removed"])
    added = [pkg for pkg in new if pkg not in current]
    removed = [pkg for pkg in current if pkg not in new]
    return Diff(added=added, removed=removed)


def main():
    with open(str(ROOT / "base"), "r") as f:
        base = [line.rstrip("\n") for line in f]
    with open(str(ROOT / "extra"), "r") as f:
        current_extra = [line.rstrip("\n") for line in f]
    with open(str(ROOT / "aur"), "r") as f:
        current_aur = [line.rstrip("\n") for line in f]

    new_aur = subprocess.check_output(["pacman", "-Qqem"], text=True).splitlines()
    new_extra = [
        pkg for pkg in subprocess.check_output(["pacman", "-Qqe"], text=True).splitlines() if pkg not in base + new_aur
    ]

    diff_extra = diff(current_extra, new_extra)
    diff_aur = diff(current_aur, new_aur)

    if not any([diff_extra.added, diff_extra.removed, diff_aur.added, diff_extra.removed]):
        print("no new changes")
        sys.exit(0)

    print(f"extra added   : {', '.join(diff_extra.added) or 'none'}")
    print(f"extra removed : {', '.join(diff_extra.removed) or 'none'}")
    print(f"aur added     : {', '.join(diff_aur.added) or 'none'}")
    print(f"aur removed   : {', '.join(diff_aur.removed) or 'none'}")

    with open(str(ROOT / "aur"), "w") as f:
        f.write("\n".join(new_aur) + "\n")
    with open(str(ROOT / "extra"), "w") as f:
        f.write("\n".join(new_extra) + "\n")

    commit = input("changes saved locally. commit and push? (Y/n) ").strip().lower()
    if not commit:
        commit = "y"
    if commit not in {"y", "n"}:
        print("error: invalid response")
        sys.exit(1)
    if commit == "n":
        sys.exit(0)

    added = diff_extra.added + diff_aur.added
    removed = diff_extra.removed + diff_aur.removed

    if added and not removed:
        commit_msg = f"[pkg update] added: {', '.join(added)}"
    elif removed and not added:
        commit_msg = f"[pkg update] removed: {', '.join(removed)}"
    else:
        commit_msg = f"[pkg update] added: {', '.join(added)}; removed: {', '.join(removed)}"

    subprocess.run(["git", "add", str(ROOT / "aur"), str(ROOT / "extra")], check=True)
    subprocess.run(["git", "commit", "-m", commit_msg], check=True)
    subprocess.run(["git", "push"], check=True)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("interrupted!")
    except Exception as e:
        print(f"unexpected error: {str(e)}")
