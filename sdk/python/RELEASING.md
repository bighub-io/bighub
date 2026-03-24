# Releasing the BIGHUB Python SDK

Release process for the official BIGHUB Python SDK — decision learning for AI agent actions.

## Versioning policy (SemVer)

The SDK follows Semantic Versioning: `MAJOR.MINOR.PATCH`.

- **MAJOR**: Breaking API changes (method signatures, behavior contract, exception model).
- **MINOR**: Backward-compatible features (new endpoints, optional args, new resources).
- **PATCH**: Backward-compatible fixes (bugfixes, reliability, docs-only release metadata).

For any MAJOR release, include an explicit migration note in `CHANGELOG.md`.

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
6. **Cross-surface consistency gate**
  - Ensure `sdk/python/README.md`, `adapters/python/openai/README.md`, and `servers/mcp/README.md` use aligned method names and field names
  - Ensure outcome statuses in snippets are valid backend statuses
  - Ensure primary examples use `actions.submit` as Free BETA default and present `submit_payload` as advanced mode
7. **Backend contract gate**
  - Verify SDK resource paths still match `bighub-core` routes for actions/rules (publicly exposed as constraints)/outcomes/auth
  - Verify plan-gated endpoint notes are still accurate (`submit_payload`, observer stats, dry-run validation, etc.)

## Release template example

For any release `X.Y.Z`:

1. Set `sdk/python/src/bighub/version.py` to `X.Y.Z`
2. Set `sdk/python/pyproject.toml` version to `X.Y.Z`
3. Ensure `CHANGELOG.md` has:
   - `[Unreleased]` section at top
   - `[X.Y.Z] - YYYY-MM-DD` section finalized
4. Run:
   - `pytest -q sdk/python/tests`
   - `python -m build sdk/python`
   - `python -m twine check sdk/python/dist\*`
5. Create and push tag:
   - `sdk-python-vX.Y.Z`

## Git tag convention

- `sdk-python-v0.1.0`
- `sdk-python-v0.2.0`
- `sdk-python-v0.2.1`
- `sdk-python-v0.2.4`
- `sdk-python-v0.2.6`
- `sdk-python-v0.3.0`
- `sdk-python-v3.0.0`
- `sdk-python-v1.0.0`

## Branch policy

- Releases are cut from `main`.
- Hotfixes are allowed and must increment PATCH.
- No direct publishing from local machines; publication is CI-controlled.

## PowerShell note (Windows)

If you run release commands in PowerShell, execute commands line-by-line instead
of using `&&` chaining for best compatibility.

