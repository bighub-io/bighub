# Releasing `bighub-openai`

Release process for the BIGHUB OpenAI adapter — decision learning for OpenAI tool calls.

## Versioning policy (SemVer)

The adapter follows `MAJOR.MINOR.PATCH`:

- **MAJOR**: breaking API changes
- **MINOR**: backward-compatible features
- **PATCH**: backward-compatible fixes

## Manual PyPI release (recommended)

### 1) Go to the adapter package directory

```bash
cd adapters/python/openai
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

## Release checklist (template)

- [ ] `src/bighub_openai/version.py` -> `"X.Y.Z"`
- [ ] `pyproject.toml` -> `version = "X.Y.Z"`
- [ ] `pyproject.toml` dependencies aligned:
  - `bighub>=X.0.0,<(X+1).0.0` (where `X` matches the SDK major line)
  - `openai>=2.0.0,<3.0.0`
- [ ] All tests pass (`pytest -q tests`)
- [ ] Build succeeds:
  - `python -m build`
  - `python -m twine check dist\*`
- [ ] README snippets align with current SDK/public API names and statuses
- [ ] README reflects Responses API v2 compatibility
- [ ] Upload: `python -m twine upload dist/*`
- [ ] Tag:
  - `git tag sdk-openai-vX.Y.Z`
  - `git push origin sdk-openai-vX.Y.Z`

### PowerShell note (Windows)

If you are running commands in PowerShell, avoid `&&` chaining in one line.
Run each command on its own line (or use `;`) for maximum compatibility.

## CI-based release (optional)

If you use a CI release workflow, keep the same steps (version bump, tests, build)
and let CI perform the final upload.

