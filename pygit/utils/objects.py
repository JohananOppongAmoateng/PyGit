"""Utility functions for Git objects."""
import itertools
import operator
import os

from pygit.core.objects import Commit


def get_commit(commit_hash: str) -> dict:
    """Retrieve commit data by its hash."""
    parent = None
    tree = ""
    commit_data = Commit.get_object(commit_hash).decode()
    lines = iter(commit_data.strip().splitlines())
    for line in itertools.takewhile(operator.truth, lines):
        key, value = line.split(":", 1)
        if key == "message":
            message = value.strip()
        elif key == "tree":
            tree = value.strip()
        elif key == "parent":
            parent = value.strip()

    message = "\n".join(lines)
    return {
        "message": message,
        "tree": tree,
        "parent": parent,
    }


def set_HEAD(head_path, oid):
    """Set HEAD to point to the new commit."""
    with open(head_path, "w", encoding="utf-8") as f:
        f.write(oid)


def get_HEAD(head_path):
    """Get the current HEAD commit hash."""
    if os.path.isfile(head_path):
        with open(head_path, "r", encoding="utf-8") as f:
            return f.read().strip()
