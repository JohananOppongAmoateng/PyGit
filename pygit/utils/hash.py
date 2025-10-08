"""Hash utilities module.

Provides functions for SHA-1 hashing of Git objects and
other hash-related utilities used in Git's object storage
system.
"""
from hashlib import sha1


def get_hash(data) -> str:
    """Compute the SHA-1 hash of the blob."""
    return sha1(data).hexdigest()


def hash_object(git_dir, data, type_):
    """Compute the SHA-1 hash of the object."""
    obj = type_.encode() + b"\x00" + data
    hash_id = get_hash(obj)
    obj_dir = git_dir / "objects" / hash_id[:2]
    obj_path = obj_dir / hash_id[2:]
    obj_dir.mkdir(parents=True, exist_ok=True)
    # Write the object data to the file
    if not obj_path.exists():
        with open(obj_path, "wb") as f:
            f.write(obj)
    return hash_id
