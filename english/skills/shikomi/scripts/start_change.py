#!/usr/bin/env python3
"""Allocate a local change branch and its specification directory."""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

CHANGE_SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
NUMBERED_NAME = re.compile(r"([0-9]+)-.+")
NUMBERED_BRANCH = re.compile(
    r"refs/(?:heads|remotes/.+)/feature/([0-9]+)-[^/]+"
)


def git(*args, cwd=None):
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=True,
        stdout=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="surrogateescape",
    ).stdout.rstrip("\n")


def next_number(root, specs):
    refs = git("for-each-ref", "--format=%(refname)", "refs/heads", "refs/remotes", cwd=root)
    numbers = [
        int(match[1])
        for ref in refs.splitlines()
        if (match := NUMBERED_BRANCH.fullmatch(ref))
    ]
    if specs.is_dir():
        numbers.extend(
            int(match[1])
            for item in specs.iterdir()
            if item.is_dir() and (match := NUMBERED_NAME.fullmatch(item.name))
        )
    return max(numbers, default=0) + 1


def create_change(slug):
    root = Path(git("rev-parse", "--show-toplevel"))
    common_dir = root / git("rev-parse", "--git-common-dir", cwd=root)
    lock = common_dir / "nikomi-allocation.lock"
    try:
        lock.mkdir()
    except FileExistsError:
        raise RuntimeError(
            f"Change allocation is locked at {lock}. "
            "Retry after the other allocation finishes. "
            "If interrupted, inspect the current branch and change directories "
            "before removing a stale lock."
        ) from None

    try:
        specs = root / "specs"
        if specs.is_symlink():
            raise RuntimeError(f"Use a regular directory for {specs}")
        parent_existed = specs.exists()
        name = f"{next_number(root, specs):03d}-{slug}"
        branch = f"feature/{name}"
        directory = specs / name
        specs.mkdir(exist_ok=True)
        made_directory = False
        try:
            directory.mkdir()
            made_directory = True
            git("switch", "-c", branch, cwd=root)
        except (OSError, subprocess.CalledProcessError):
            if made_directory:
                directory.rmdir()
            if not parent_existed and not any(specs.iterdir()):
                specs.rmdir()
            raise
        return {"branch": branch, "directory": f"specs/{name}"}
    finally:
        lock.rmdir()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("slug", help="Short change name, for example export-csv")
    args = parser.parse_args()
    if not CHANGE_SLUG.fullmatch(args.slug):
        parser.error("Use lowercase letters, digits, and single hyphens for the change name.")
    try:
        print(json.dumps(create_change(args.slug)))
    except (OSError, RuntimeError, subprocess.CalledProcessError) as error:
        print(f"Unable to start the change: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
