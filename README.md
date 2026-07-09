# my-template

[![CI](https://github.com/MyThingsLab/my-template/actions/workflows/ci.yml/badge.svg)](https://github.com/MyThingsLab/my-template/actions/workflows/ci.yml) [![codecov](https://codecov.io/gh/MyThingsLab/my-template/branch/main/graph/badge.svg)](https://codecov.io/gh/MyThingsLab/my-template) ![Python](https://img.shields.io/badge/python-3.11%2B-blue) [![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

The canonical scaffold for a [MyThingsLab](../my-things-core) `My[X]` tool. It is
a **working, CI-green skeleton** — the shared seams (pyproject, `ci.yml`,
`.gitignore`, LICENSE, `.pre-commit-config.yaml`, vendored `HARNESS.md`, the
harness drift-check test, `dev-ledger/`) are already wired up and verified, so a
new tool starts from a passing build instead of an empty directory.

The package is a working harness loop, not an empty dir: `src/mytemplate/`
ships the plumbing (read one labeled issue → deterministic pre-work → one
Engine call → apply inside an isolated `Workspace` → draft PR, Policy-gated
and ledgered) with the judgment left as three seam methods
(`prework`/`request`/`apply`) and the constants at the top of `tool.py`.
Out of the box `apply` changes nothing, so

```bash
mytemplate run --engine noop   # or: python -m mytemplate run
```

is a safe end-to-end dry run: zero tokens, no branch, no PR, one honest
ledger entry.

This is not itself a `My[X]` tool: it ships no judgment of its own. It
exists only to be copied.

## Starting a new tool from it

1. Copy this repo to `../my-<x>` (drop `.git`, `.venv`, the caches, and
   `dev-ledger/*.jsonl` — the new tool records its own provenance).
2. Run the rename in one command (it renames the package dir, rewrites every
   `mytemplate`/`my-template` reference, seeds the dev-ledger scaffold entry,
   and deletes itself):
   ```bash
   python scripts/init.py my-<x>
   ```
3. Fill the four per-tool seams in [`CLAUDE.md`](CLAUDE.md) — purpose, the single
   Engine call, invariants, backlog label — and rewrite this README for the tool.
   The seam-check test fails CI while any seam is left unfilled after the rename.
   In code, override the seam methods in `tool.py` (`prework`/`request`/`apply`)
   and its `TOOL`/`LEDGER_KIND`/`BACKLOG_LABEL`/`SYSTEM` constants.
4. `pip install -e ../my-things-core -e ".[dev]" && pre-commit install`.
5. Record the scaffold in provenance:
   `python -m mythings._devledger add scaffold --detail "copied my-template"`.
6. Red → green → refactor locally; open a PR; let CI gate it.

Everything above the seams is fixed by the build harness — see
[`HARNESS.md`](HARNESS.md) and `my-things-core/docs/CONVENTIONS.md`. Do not edit
the vendored `HARNESS.md`; the drift-check test fails CI if it diverges from the
canonical copy in `my-things-core`.

## Install (development)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ../my-things-core -e ".[dev]"
pytest
```

## License

MIT — see [`LICENSE`](LICENSE).
