from __future__ import annotations

import importlib.util
import shutil
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def load_init():
    spec = importlib.util.spec_from_file_location("init_script", ROOT / "scripts" / "init.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture()
def copy(tmp_path: Path) -> Path:
    dest = tmp_path / "my-foo"
    shutil.copytree(
        ROOT,
        dest,
        ignore=shutil.ignore_patterns(
            ".git", ".venv", "__pycache__", "*.jsonl", ".coverage", ".*_cache"
        ),
    )
    return dest


def test_init_renames_package_and_rewrites_references(copy: Path) -> None:
    load_init().init(copy, "my-foo")
    assert (copy / "src" / "myfoo" / "tool.py").exists()
    assert not (copy / "src" / "mytemplate").exists()
    pyproject = (copy / "pyproject.toml").read_text()
    assert 'name = "my-foo"' in pyproject
    assert 'myfoo = "myfoo.cli:main"' in pyproject
    assert "mytemplate" not in pyproject
    ci = (copy / ".github" / "workflows" / "ci.yml").read_text()
    assert "--cov=myfoo" in ci
    tool = (copy / "src" / "myfoo" / "tool.py").read_text()
    assert 'BACKLOG_LABEL = "my-foo"' in tool
    assert 'TOOL = "myfoo"' in tool


def test_init_leaves_the_judgment_seams_open(copy: Path) -> None:
    load_init().init(copy, "my-foo")
    claude = (copy / "CLAUDE.md").read_text()
    assert "my-<x>" not in claude  # the mechanical seam is filled...
    assert "<one line — what this tool does>" in claude  # ...the judgment ones are not
    # The seam test's pristine-template branch must survive the rewrite intact.
    assert (
        'if _package_name() == "mytemplate":'
        in (copy / "tests" / "test_claude_md_seams.py").read_text()
    )


def test_init_never_touches_the_vendored_harness(copy: Path) -> None:
    before = (copy / "HARNESS.md").read_bytes()
    load_init().init(copy, "my-foo")
    assert (copy / "HARNESS.md").read_bytes() == before


def test_init_seeds_a_fresh_dev_ledger(copy: Path) -> None:
    load_init().init(copy, "my-foo")
    entries = list((copy / "dev-ledger").glob("*.jsonl"))
    assert entries, "expected the scaffold provenance entry"
    text = "".join(e.read_text() for e in entries)
    assert "scaffold" in text


def test_init_rejects_a_bad_name(copy: Path) -> None:
    with pytest.raises(SystemExit):
        load_init().init(copy, "MyFoo")
