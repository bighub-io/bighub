# Releasing `bighub-openai`

Release process for the BIGHUB OpenAI adapter — decision intelligence for OpenAI tool calls.

## Versioning policy (SemVer)

The adapter follows `MAJOR.MINOR.PATCH`:

- **MAJOR**: breaking API changes
- **MINOR**: backward-compatible features
- **PATCH**: backward-compatible fixes

## Manual PyPI release (recommended)

### 1) Go to the adapter package directory

```bash
cd sdk/adapters/openai/python
```

### 2) Update version

Update both files to the same version:

- `src/bighub_openai/version.py`
- `pyproject.toml`

### 3) Run tests

```bash
pytest -q tests
```

### 4) Build artifacts

```bash
python -m pip install --upgrade build twine
python -m build
python -m twine check dist\*
```

### 5) Upload to PyPI

```bash
python -m twine upload dist/*
```

Use PyPI token auth:

- username: `__token__`
- password: `pypi-...`

## Optional: tag in git

```bash
git tag sdk-openai-vX.Y.Z
git push origin sdk-openai-vX.Y.Z
```

## Release checklist (current patch example)

- [ ] `src/bighub_openai/version.py` -> `"0.2.5"`
- [ ] `pyproject.toml` -> `version = "0.2.5"`
- [ ] `pyproject.toml` dependencies: `bighub>=0.2.6,<0.3.0`, `openai>=2.0.0,<3.0.0`
- [ ] All 27 tests pass (`pytest -q tests`)
- [ ] Build succeeds:
  - `python -m build`
  - `python -m twine check dist\*`
- [ ] README reflects Responses API v2 compatibility
- [ ] Upload: `python -m twine upload dist/*`
- [ ] Tag:
  - `git tag sdk-openai-v0.2.5`
  - `git push origin sdk-openai-v0.2.5`

### PowerShell note (Windows)

If you are running commands in PowerShell, avoid `&&` chaining in one line.
Run each command on its own line (or use `;`) for maximum compatibility.

## CI-based release (optional)

If you use a CI release workflow, keep the same steps (version bump, tests, build)
and let CI perform the final upload.

