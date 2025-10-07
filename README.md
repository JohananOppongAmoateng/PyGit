# PyGit

Rebuilding Git in Python — because the best way to understand version control is to create your own

## Overview

PyGit is an educational project that implements basic Git functionality in Python. The goal is to understand how Git works under the hood by recreating its core features from scratch.

## Features (Planned)

- Repository initialization (`pygit init`)
- Basic file tracking and staging (`pygit add`)
- Committing changes (`pygit commit`)
- Object storage (blobs, trees, commits)
- Basic branching
- Basic remote operations

## Project Structure

```
pygit/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── repository.py    # Repository management
│   ├── objects.py       # Git objects (blob, tree, commit)
│   └── index.py         # Staging area management
├── commands/
│   ├── __init__.py
│   ├── init.py
│   ├── add.py
│   └── commit.py
└── utils/
    ├── __init__.py
    └── hash.py          # Hash utilities
```

## Development Status

🚧 Under active development
