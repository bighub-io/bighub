# Releasing the Official BIGHUB Python SDK

This document defines the release process for the official BIGHUB Python SDK.

## Versioning policy (SemVer)

The SDK follows Semantic Versioning: `MAJOR.MINOR.PATCH`.

- **MAJOR**: Breaking API changes (method signatures, behavior contract, exception model).
- **MINOR**: Backward-compatible features (new endpoints, optional args, new resources).
- **PATCH**: Backward-compatible fixes (bugfixes, reliability, docs-only release metadata).

Until `1.0.0`, breaking changes may still occur, but must be explicitly documented in changelog.

## Changelog policy

- `CHANGELOG.md` must be updated for every release.
- Keep an `[Unreleased]` section at top for upcoming changes.
- Move items from `[Unreleased]` into the released version section on release day.

## Release checklist

1. **Finalize version**
  - Update `sdk/python/src/bighub/version.py`
  - Update `sdk/python/pyproject.toml` version
2. **Update changelog**
  - Move release notes from `[Unreleased]` to `[X.Y.Z] - YYYY-MM-DD`
3. **Run local validation**
  - `pytest -q sdk/python/tests`
  - `python -m build sdk/python`
  - `python -m twine check sdk/python/dist\*`
4. **Tag**
  - Create git tag: `sdk-python-vX.Y.Z`
5. **Publish**
  - Push the version tag; the CI release workflow publishes the package to PyPI.

## Current release example

For the current patch release:

1. Set `sdk/python/src/bighub/version.py` to `0.2.6`
2. Set `sdk/python/pyproject.toml` version to `0.2.6`
3. Ensure `CHANGELOG.md` has:
   - `[Unreleased]` section at top
   - `[0.2.6] - 2026-03-08` section finalized
4. Run:
   - `pytest -q sdk/python/tests`
   - `python -m build sdk/python`
   - `python -m twine check sdk/python/dist\*`
5. Create and push tag:
   - `sdk-python-v0.2.6`

## Git tag convention

- `sdk-python-v0.1.0`
- `sdk-python-v0.2.0`
- `sdk-python-v0.2.1`
- `sdk-python-v0.2.4`
- `sdk-python-v0.2.6`
- `sdk-python-v1.0.0`

## Branch policy

- Releases are cut from `main`.
- Hotfixes are allowed and must increment PATCH.
- No direct publishing from local machines; publication is CI-controlled.

## PowerShell note (Windows)

If you run release commands in PowerShell, execute commands line-by-line instead
of using `&&` chaining for best compatibility.

