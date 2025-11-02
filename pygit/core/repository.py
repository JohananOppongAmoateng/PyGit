"""Repository management module.

This module handles Git repository operations including initialization,
config management, and workspace interaction. It provides the main
interface for working with Git repositories.
"""

import os
import textwrap
from pathlib import Path

from pygit.core.objects import Tree
from pygit.utils.objects import get_commit, get_HEAD, set_HEAD


class NotARepositoryError(Exception):
    """Raised when a directory is not a valid Git repository."""

    pass


class Repository:
    """Manages the Git repository."""

    def __init__(self, path):
        """Initialize repository at the given path.

        Args:
            path: Path to the repository root

        Raises:
            NotARepositoryError: If the path is not a valid Git repository
        """
        self.path = Path(path)
        self.git_dir = self.path / ".pygit"

        if not self.git_dir.exists():
            raise NotARepositoryError(
                f"""fatal: not a git repository (or any of the parent
                directories): {self.git_dir}"""
            )

    @classmethod
    def create(cls, path):
        """Create a new repository structure.

        Args:
            path: Path where the repository should be created

        Returns:
            Repository: A new Repository instance

        Raises:
            FileExistsError: If a repository already exists at the given path
        """
        path = Path(path)
        git_dir = path / ".pygit"

        # Create root directory if it doesn't exist
        path.mkdir(parents=True, exist_ok=True)

        if git_dir.exists():
            raise FileExistsError(f"Repository already exists at {git_dir}")

        # Create repository structure
        os.makedirs(git_dir)
        os.makedirs(git_dir / "hooks")
        os.makedirs(git_dir / "info")
        os.makedirs(git_dir / "objects")
        os.makedirs(git_dir / "logs")
        os.makedirs(git_dir / "refs" / "heads")
        os.makedirs(git_dir / "refs" / "tags")
        os.makedirs(git_dir / "refs" / "remotes")

        # Return new repository instance
        return cls(path)

    def add_file(self, file_path):
        """Add a file to the staging area."""
        # TODO: Implement file staging

    def commit(self, message):
        """Commit staged changes with a message."""
        # TODO: Implement commit creation

    def status(self):
        """Show the current status of the repository."""
        # TODO: Implement status reporting

    @staticmethod
    def log(path, start_oid=None):
        """Show the commit history.

        Args:
            path: Path to the repository root
            start_oid: Optional commit hash to start from. If None, starts from HEAD

        Raises:
            NotARepositoryError: If the path is not a valid Git repository
            ValueError: If the start_oid is not a valid commit
        """
        git_dir = Path(path) / ".pygit"
        if not git_dir.exists():
            raise NotARepositoryError(
                f"""fatal: not a git repository\
                     (or any of the parent directories): {git_dir}"""
            )

        # Get starting commit OID
        if start_oid is None:
            oid = get_HEAD(git_dir / "HEAD")
            if not oid:
                print("fatal: your current branch does not have any commits yet")
                return
        else:
            # Validate the provided commit ID
            try:
                # Try to read the commit to validate it exists
                get_commit(start_oid)
                oid = start_oid
            except FileNotFoundError:
                print(f"fatal: not a valid commit name {start_oid}")
                return

        while oid:
            try:
                commit = get_commit(oid)

                # Header with commit hash
                print(f"\033[33mcommit {oid}\033[0m")  # Yellow color for hash

                # Author and date (to be added when we have this info)
                if "author" in commit:
                    print(f"Author: {commit['author']}")
                if "timestamp" in commit and "timezone" in commit:
                    print(f"Date:   {commit['timestamp']} {commit['timezone']}")

                # Commit message
                print()
                if "message" in commit:
                    print(textwrap.indent(commit["message"].strip(), "    "))
                print()

                oid = commit.get("parent")
            except FileNotFoundError:
                print(f"fatal: commit {oid} not found")
                return

    def checkout(self, commit_oid):
        """Checkout a specific commit by its hash."""
        commit = get_commit(commit_oid)
        Tree(self.path, commit_oid).read_tree(commit["tree"])
        set_HEAD(self.git_dir / "HEAD", commit_oid)
