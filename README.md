# my-template

[![CI](https://github.com/MyThingsLab/my-template/actions/workflows/ci.yml/badge.svg)](https://github.com/MyThingsLab/my-template/actions/workflows/ci.yml) [![codecov](https://codecov.io/gh/MyThingsLab/my-template/branch/main/graph/badge.svg)](https://codecov.io/gh/MyThingsLab/my-template) ![Python](https://img.shields.io/badge/python-3.11%2B-blue) [![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

The canonical scaffold for a [MyThingsLab](../my-things-core) `My[X]` tool. It is
a **working, CI-green skeleton** — the shared seams (pyproject, `ci.yml`,
`.gitignore`, LICENSE, `.pre-commit-config.yaml`, vendored `HARNESS.md`, the
harness drift-check test, `dev-ledger/`) are already wired up and verified, so a
new tool starts from a passing build instead of an empty directory.

This is not itself a `My[X]` tool: it ships no Engine call and no rules. It
exists only to be copied.

## Starting a new tool from it

1. Copy this repo to `../my-<x>` (drop `.git`, `.venv`, the caches, and
   `dev-ledger/*.jsonl` — the new tool records its own provenance).
2. Rename the placeholder `template` everywhere:
   - the package dir `src/mytemplate/` → `src/my<x>/`
   - `pyproject.toml` (`name`, `description`, `packages`)
   - any `mytemplate` import in `src/` and `tests/`
   ```bash
   grep -rl template . --exclude-dir=.git
   ```
3. Fill the four per-tool seams in [`CLAUDE.md`](CLAUDE.md) — purpose, the single
   Engine call, invariants, backlog label — and rewrite this README for the tool.
   The seam-check test fails CI while any seam is left unfilled after the rename.
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
