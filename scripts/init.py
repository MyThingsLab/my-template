"""Rename the freshly-copied template into a real my-<x> tool in one command.

Run from the copy's root: `python scripts/init.py my-foo`. Replaces the manual
`grep -rl template` sweep: renames the package dir, rewrites `mytemplate` /
`my-template` across the tree, seeds the dev-ledger scaffold entry, and
removes itself. The four CLAUDE.md prose seams stay open on purpose — filling
them is a judgment call, and the seam-check test fails CI until a human does.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

# Never rewritten: HARNESS.md is the vendored canonical copy (the drift test
# pins it byte-for-byte to core), and the seam test's pristine-template branch
# must keep comparing against the literal string "mytemplate".
SKIP_FILES = {"HARNESS.md", "test_claude_md_seams.py"}
SKIP_DIRS = {".git", ".venv", "__pycache__", ".pytest_cache", ".ruff_cache", "dev-ledger"}

NAME_RE = re.compile(r"^my-[a-z0-9]+(-[a-z0-9]+)*$")


def rewrite_tree(root: Path, name: str, package: str) -> list[Path]:
    changed: list[Path] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.name in SKIP_FILES:
            continue
        if any(part in SKIP_DIRS for part in path.relative_to(root).parts):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:  # stray binary (a .coverage db, an image) — nothing to rename
            continue
        replaced = (
            text.replace("mytemplate", package).replace("my-template", name).replace("my-<x>", name)
        )
        if replaced != text:
            path.write_text(replaced, encoding="utf-8")
            changed.append(path)
    return changed


def init(root: Path, name: str) -> list[Path]:
    if not NAME_RE.match(name):
        raise SystemExit(f"tool name must look like my-foo, got {name!r}")
    package = name.replace("-", "")
    src = root / "src" / "mytemplate"
    if not src.is_dir():
        raise SystemExit(f"{src} not found — run from a fresh copy of my-template")

    changed = rewrite_tree(root, name, package)
    src.rename(root / "src" / package)

    # The copy records its own provenance from scratch.
    for stale in (root / "dev-ledger").glob("*.jsonl"):
        stale.unlink()
    seed = subprocess.run(
        [
            sys.executable,
            "-m",
            "mythings._devledger",
            "add",
            "scaffold",
            "--detail",
            "initialized from my-template via scripts/init.py",
        ],
        cwd=root,
        capture_output=True,
        text=True,
    )
    if seed.returncode != 0:
        print(
            "note: could not seed dev-ledger (is my-things-core installed?) — run\n"
            '  python -m mythings._devledger add scaffold --detail "initialized from my-template"'
        )
    return changed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python scripts/init.py",
        description="Rename this fresh copy of my-template into a real my-<x> tool.",
    )
    parser.add_argument("name", help="the new tool's repo name, e.g. my-foo")
    args = parser.parse_args(argv)

    root = Path(__file__).resolve().parents[1]
    changed = init(root, args.name)
    print(f"renamed {len(changed)} files; package is src/{args.name.replace('-', '')}/")

    # Job done — a renamed tool has no template left to initialize. The test
    # that guards this script only makes sense in my-template itself, so it
    # leaves with the script rather than shipping as a permanent red test.
    Path(__file__).resolve().unlink()
    if not any((root / "scripts").iterdir()):
        shutil.rmtree(root / "scripts")
    test_init_script = root / "tests" / "test_init_script.py"
    if test_init_script.exists():
        test_init_script.unlink()

    print(
        "next: fill the four CLAUDE.md seams, override the tool.py seam methods,\n"
        'rewrite README.md, then `pip install -e ../my-things-core -e ".[dev]"` and pytest'
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
