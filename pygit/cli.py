"""Command-line interface for PyGit."""

import argparse
from pathlib import Path

from .core.repository import NotARepositoryError, Repository


def init_cmd(args):
    """Initialize a new Git repository."""
    try:
        path = Path(args.directory).resolve()
        Repository.create(path)
        print(f"Initialized empty Git repository in {path / '.pygit'}")
        return 0
    except FileExistsError as e:
        print(f"Error: Repository already exists: {str(e)}")
        return 1
    except PermissionError as e:
        print(f"Error: Permission denied: {str(e)}")
        return 1
    except OSError as e:
        print(f"Error: Failed to create repository: {str(e)}")
        return 1


def log_cmd(args):
    """Show commit logs."""
    try:
        path = Path(args.directory).resolve()
        Repository.log(path, args.commit)  # Pass optional commit ID
        return 0
    except NotARepositoryError as e:
        print(str(e))
        return 1
    except PermissionError as e:
        print(f"Error: Permission denied: {str(e)}")
        return 1
    except OSError as e:
        print(f"Error: Failed to access repository: {str(e)}")
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

    # Log command
    log_parser = subparsers.add_parser("log", help="Show commit logs")
    log_parser.add_argument(
        "commit",
        nargs="?",
        default=None,
        help="Commit to start showing log from",
    )

    args = parser.parse_args()
    if args.command:
        return args.func(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    exit(main())
