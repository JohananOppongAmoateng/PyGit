"""Git object model implementation.

This module implements Git's internal object model, including:
- Blobs (file content storage)
- Trees (directory structure)
- Commits (snapshots with metadata)
"""

import os
import sys
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path

from pygit.utils.hash import hash_object


class GitObject(ABC):
    """Base class for all Git objects."""

    @abstractmethod
    def __init__(self, repo_path: Path, id=None):
        """Initialize the Git object."""
        self.repo_path = Path(repo_path)
        self.git_dir = repo_path / ".pygit"
        self.id = id

    def get_object(self, hash_id: str):
        """Retrieve the blob data from storage using its id."""
        obj_path = self.git_dir / "objects" / hash_id[:2] / hash_id[2:]
        if not obj_path.exists():
            raise FileNotFoundError(f"Object {hash_id} not found in repository.")
        with open(obj_path, "rb") as f:
            obj = f.read()

        type_, _, data = obj.partition(b"\x00")
        type_ = type_.decode()

        if type_ != "blob" and type_ != "tree" and type_ != "commit":
            raise ValueError(f"Object {hash_id} is not a valid Git object.")
        return data


class Blob(GitObject):
    """Represents a Git blob object (file content)."""

    def __init__(self, data, repo_path, id=None):
        """Initialize the blob with data and optional id."""
        super().__init__(repo_path=repo_path, id=id)
        self.data = data
        self.type_ = "blob"

    def cat_file(self, hash_id: str):
        """Read a blob object from storage using its hash and print it.

        Similar to `git cat-file -p <hash>`
        """
        data = self.get_object(hash_id)
        sys.stdout.flush()
        sys.stdout.buffer.write(data)
        return self


class Tree(GitObject):
    """Represents a Git tree object (directory structure)."""

    def __init__(self, repo_path, id=None):
        """Initialize the tree."""
        super().__init__(repo_path=repo_path, id=id)
        self.type_ = "tree"
        self.entries: list[
            tuple[str, str, str]
        ] = []  # List of ( type, hash, name) tuples

    def add_entry(self, type_: str, hash_id: str, name: str):
        """Add an entry to the tree."""
        self.entries.append((type_, hash_id, name))

    def write_tree(self, directory: Path):
        """Recursively write the directory and its contents as a tree object."""
        with os.scandir(directory) as it:
            for entry in it:
                full_path = os.path.join(directory, entry.name)
                if entry.is_file(follow_symlinks=False):
                    if is_ignored(full_path):
                        continue
                    # Write the file to object storage as a blob
                    with open(full_path, "rb") as f:
                        hash_id = hash_object(self.git_dir, f.read(), "blob")
                        self.add_entry("blob", hash_id, entry.name)
                elif entry.is_dir(follow_symlinks=False):
                    # Recursively write the directory as a tree
                    subtree = Tree(repo_path=self.repo_path)
                    subtree.write_tree(full_path)
                    hash_id = subtree.store()
                    self.add_entry("tree", hash_id, entry.name)

    def store(self) -> str:
        """Store the tree in the Git object database."""
        # Create the object data
        tree = "".join(
            f"{type_} {hash_id} {name}" for type_, hash_id, name in self.entries
        )
        return hash_object(self.git_dir, tree, self.type_)

    def get_tree(self, hash_id, base_path=""):
        """Get a dictionary of all files in the tree and its subtrees."""
        result = {}
        for type_, hash_id, name in self._iter_tree(hash_id):
            assert "/" not in name
            assert name not in ("..", ".")
            path = base_path + name
            if type_ == "blob":
                result[path] = hash_id
            elif type_ == "tree":
                result.update(self.get_tree(hash_id, f"{path}/"))
            else:
                raise ValueError(f"Unknown object type {type_} in tree.")

        return result

    def _iter_tree(self, hash_id):
        """Iterate over the entries in a tree object."""
        if not hash_id:
            return
        tree = self.get_object(hash_id)
        for entry in tree.decode().splitlines():
            type_, hash_id, name = entry.split(" ", 2)
            yield type_, hash_id, name

    def read_tree(self, hash_id):
        """Read a tree object from storage using its hash."""
        self._empty_directory()
        for path, hash_id in self.get_tree(hash_id).items():
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "wb") as f:
                f.write(self.get_object(hash_id))

    def _empty_directory(self):
        """Remove all files and directories in the repository. Skip ignored ones."""
        for root, directories, files in os.walk(self.repo_path, topdown=False):
            for file in files:
                path = os.path.realpath(f"{root}/{file}")
                if is_ignored(path) or not os.path.isfile(path):
                    continue
                os.remove(path)
            for directory in directories:
                dir_path = os.path.realpath(f"{root}/{directory}")
                if is_ignored(dir_path) or not os.path.isdir(dir_path):
                    continue
                try:
                    os.rmdir(dir_path)
                except (FileNotFoundError, OSError):
                    # Deletion might fail if the directory is not empty
                    pass


class Commit(GitObject):
    """Represents a Git commit object (snapshot with metadata)."""

    def __init__(self, message="", tree_hash_id=None, repo_path=None, id=None):
        """Initialize the commit object."""
        super().__init__(repo_path=repo_path, id=id)
        self.type = "commit"
        self.message = message
        self.tree_hash_id = tree_hash_id

    def commit(self):
        """Create a commit object and store it in the Git object database."""
        commit_data = f"""
        author: PyGit <{os.getenv("GIT_AUTHOR_EMAIL", "unknown@example.com")}>
        timestamp: {int(datetime.now().timestamp())}
        timezone: {datetime.now().astimezone().strftime('%z')}
        message: {self.message}
        tree: {self.tree_hash_id}
        """
        HEAD = self.get_HEAD()
        if HEAD:
            commit_data += f"parent: {HEAD}\n"
        oid = hash_object(self.git_dir, commit_data, self.type)
        self.set_HEAD(oid)
        return oid

    def set_HEAD(self, oid):
        """Set HEAD to point to the new commit."""
        with open(self.git_dir / "HEAD", "w") as f:
            f.write(oid)

    def get_HEAD(self):
        """Get the current HEAD commit hash."""
        head_path = self.git_dir / "HEAD"
        if os.path.isfile(head_path):
            with open(head_path, "r") as f:
                return f.read().strip()


def is_ignored(path: str) -> bool:
    """Check if a file or directory should be ignored (e.g., .pygit)."""
    if os.path.basename(path) == ".pygit":
        return True
    gitignore_path = os.path.join(os.path.dirname(path), ".gitignore")
    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r") as f:
            patterns = [
                line.strip() for line in f if line.strip() and not line.startswith("#")
            ]
        for pattern in patterns:
            if pattern and Path(path).match(pattern):
                return True
    return False
