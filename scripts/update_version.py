#!/usr/bin/env python3
"""
Update version strings in pyproject.toml and src/samcov/__init__.py
for semantic-release.
"""
import sys
from pathlib import Path


def update_file(path: Path, old: str, new: str) -> None:
    text = path.read_text()
    if old not in text:
        print(f"Warning: {old!r} not found in {path}", file=sys.stderr)
        return
    path.write_text(text.replace(old, new, 1))
    print(f"Updated {path}")


def main():
    if len(sys.argv) != 2:
        print("Usage: update_version.py <version>", file=sys.stderr)
        sys.exit(1)

    new_version = sys.argv[1]
    repo = Path(__file__).parent.parent

    # pyproject.toml
    pp = repo / "pyproject.toml"
    if pp.exists():
        text = pp.read_text()
        lines = text.splitlines()
        for i, line in enumerate(lines):
            if line.startswith("version ="):
                lines[i] = f'version = "{new_version}"'
                break
        pp.write_text("\n".join(lines) + "\n")
        print(f"Updated {pp}")

    # __init__.py
    init = repo / "src" / "samcov" / "__init__.py"
    if init.exists():
        init.write_text(f'__version__ = "{new_version}"\n')
        print(f"Updated {init}")


if __name__ == "__main__":
    main()
