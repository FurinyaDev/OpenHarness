"""Compare two reviewed Git commits under a project's all-path size budget."""

import argparse
import re
import subprocess
import sys


def nonnegative(value):
    number = int(value)
    if number < 0:
        raise argparse.ArgumentTypeError("budget must be nonnegative")
    return number


def commit_sha(value):
    if re.fullmatch(r"[0-9a-f]{40}", value) is None:
        raise argparse.ArgumentTypeError("expected a full 40-character commit SHA")
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("base", type=commit_sha)
    parser.add_argument("head", type=commit_sha)
    parser.add_argument("--max-lines", type=nonnegative, required=True)
    parser.add_argument("--max-files", type=nonnegative, required=True)
    args = parser.parse_args()

    try:
        stats = subprocess.check_output([
            "git", "diff", "--numstat", "-z", "--no-renames", "--no-ext-diff",
            "--no-textconv", "--no-relative", "--ignore-submodules=none",
            f"{args.base}^{{commit}}", f"{args.head}^{{commit}}", "--",
        ])
    except (OSError, subprocess.CalledProcessError) as error:
        print(f"Size check incomplete: {error}", file=sys.stderr)
        return 2

    lines = files = 0
    binary_paths = []
    for row in stats.split(b"\0")[:-1]:
        added, deleted, path = row.split(b"\t", 2)
        files += 1
        if added == deleted == b"-":
            binary_paths.append(path)
        else:
            lines += int(added) + int(deleted)

    print(f"All paths: {lines} text lines (+/-) in {files} files")
    for path in binary_paths:
        print(f"Binary change: {path!r}", file=sys.stderr)
    if lines > args.max_lines or files > args.max_files:
        print(f"Size budget exceeded ({args.max_lines} lines, {args.max_files} files)",
              file=sys.stderr)
        return 1
    return int(bool(binary_paths))


if __name__ == "__main__":
    sys.exit(main())
