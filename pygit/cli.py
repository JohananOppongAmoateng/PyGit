"""Command-line interface for PyGit."""

import argparse
from pathlib import Path

from .core.repository import Repository


def init_cmd(args):
    """Initialize a new Git repository."""
    try:
        path = Path(args.directory).resolve()
        repo = Repository(path)
        repo.init()
        print(f"Initialized empty Git repository in {path / '.pygit'}")
        return 0
    except Exception as e:
        print(f"Error initializing repository: {str(e)}")
        return 1


def main():
    """Main entry point for PyGit command-line interface."""
    parser = argparse.ArgumentParser(description="A Python implementation of Git")
    subparsers = parser.add_subparsers(title="Commands", dest="command")

    # Init command
    init_parser = subparsers.add_parser("init", help="Create an empty Git repository")
    init_parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Directory to create the repository in",
    )
    init_parser.set_defaults(func=init_cmd)

    args = parser.parse_args()
    if args.command:
        return args.func(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    exit(main())
