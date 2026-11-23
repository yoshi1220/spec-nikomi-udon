#!/usr/bin/env python3
"""Run a project's unit-test command and check the expected phase."""

import argparse
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("red", "green"))
    parser.add_argument(
        "--expect-output", required=True,
        help="Literal assertion failure (red) or positive test result from the runner (green)",
    )
    parser.add_argument(
        "--failure-exit", type=int,
        help="Runner exit code for assertion failures in red (default: 1)",
    )
    # Keep runner options separate from harness options and pass argv without a shell.
    argv = sys.argv[1:]
    boundary = argv.index("--") if "--" in argv else len(argv)
    args = parser.parse_args(argv[:boundary])
    command = argv[boundary + 1:]
    if not command or not args.expect_output.strip():
        parser.error("Provide nonempty expected output and a test command after --")
    if args.failure_exit is not None and (args.phase != "red" or args.failure_exit <= 0):
        parser.error("--failure-exit requires red and a positive runner exit code")
    try:
        run = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    except OSError as error:
        parser.exit(1, f"Unit test command could not start: {error}\n")

    output = run.stdout.decode("utf-8", errors="replace")
    print(output, end="" if output.endswith("\n") else "\n", flush=True)
    if args.phase == "red":
        expected_exit = run.returncode == (args.failure_exit or 1)
    else:
        expected_exit = run.returncode == 0
    if not expected_exit or args.expect_output not in output:
        parser.exit(1, f"{args.phase}: expected test outcome not observed (runner exit {run.returncode})\n")
    print(f"{args.phase}: expected test outcome observed (runner exit {run.returncode})")


if __name__ == "__main__":
    main()
