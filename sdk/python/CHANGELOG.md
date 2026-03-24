# Changelog

All notable changes to the official BIGHUB Python SDK are documented in this file.

The format is based on Keep a Changelog and this project uses Semantic Versioning.

## [Unreleased]

- No unreleased entries at this time.

## [3.0.1] - 2026-03-16

### Changed

- Added missing project links in PyPI metadata:
  - GitHub repository: `https://github.com/bighub-io/bighub`
  - MCP package: `https://www.npmjs.com/package/@bighub/bighub-mcp`

## [3.0.0] - 2026-03-12

### Changed

- Bumped the Python SDK to major version `3.0.0` for the new decision learning release line.
- Aligned SDK examples with current backend contracts:
  - cross-plan evaluation defaults to `actions.submit(...)`
  - outcome examples use valid statuses supported by `/outcomes/report`
  - examples now use current domain values (`customer_transactions`).
- Hardened release readiness docs with explicit cross-surface and backend-contract verification gates.

### Packaging

- Added a package-local `LICENSE` file so `python -m build` and `twine check` pass reliably from `sdk/python`.

## [0.3.0] - 2026-03-15

### Changed

- Repositioned the SDK around the BIGHUB decision learning loop:
  - evaluate actions before execution
  - execute in runtime
  - report real outcomes
  - learn from similar past cases.
- Rewrote SDK documentation around DecisionCase, outcome-linked learning, and learned signals.
- Updated SDK wording to consistently prefer:
  - "evaluate/evaluation" for action decisions
  - decision learning terminology over legacy policy-centric language.
- Updated links and package references to match the current repository entry points.

### Added

- Complete decision learning coverage in a single SDK surface (sync + async):
  - `cases`: create/list/get, report outcome, case-level precedents and calibration
  - `outcomes`: report, batch report, timeline, pending, analytics, taxonomy
  - `precedents`: query and aggregate signals from similar past decisions
  - `calibration`: report/reliability/drift/breakdown/feedback/observe
  - `retrieval`: multi-signal retrieval strategies and explained retrieval
  - `features`: feature compute/snapshot/explain/export/schema/stats
  - `insights`: advisories, patterns, and action profiles
  - `simulations`: simulation vault queries and prediction-vs-reality comparison
  - `learning`: strategy/runs/recompute/backfill controls.

### Compatibility

- Synced package metadata and runtime version to `0.3.0` so publish metadata, import-time version, and docs remain consistent.

## [0.2.6] - 2026-03-09

### Changed

- Aligned all documentation with decision intelligence positioning (simulate, score, enforce, learn).
- Updated PyPI description and keywords to reflect self-improving rules branding.
- Synced package version and runtime version constant to `0.2.6` so user-agent and metadata always match.
- Removed duplicated `JSONDict` alias from models and kept a single source of truth in `types.py`.
- Added explicit sync/async transport protocols and replaced `transport: Any` in resource APIs for stronger typing.
- Improved SDK typing consistency across resource modules without changing public runtime behavior.

## [0.2.4] - 2026-03-05

### Changed

- Fixed `api_keys.validate()` (sync + async) to send the `api_key` query parameter expected by the public validation endpoint and SDK tests.
- Updated README Future Memory examples to reference the current OpenAI adapter release (`bighub-openai@0.2.3`) instead of stale `0.2.0` strings.
- Refreshed release-process guidance so package metadata, changelog updates, validation, and tagging instructions stay aligned with current patch releases.

## [0.2.3] - 2026-03-02

- Security hardening: much safer.

## [0.2.2] - 2026-02-28

### Changed

- Execution Domains naming is now fully aligned across SDK docs/examples:
  - `pricing` -> `financial_actions`
  - `payments` -> `customer_transactions`
  - `inventory` -> `operational_systems`
  - `supply_chain` -> `operational_systems`
  - `hr` -> `operational_systems`
  - `marketing` -> `data_modifications`
  - `generic` -> `custom`
- Updated README examples and snippets to consistently use current domain values and production vocabulary.
- Documentation polish for release readiness (event/domain wording), aligned with decision intelligence positioning.

## [0.2.1] - 2026-02-28

### Changed

- Updated `README.md` to improve first-run developer experience:
  - moved Sync/Async quickstarts near the top (right after install)
  - added direct PyPI links for `bighub` and `bighub-openai`
  - consolidated Provider Adapter guidance to a single clear runtime integration reference.
- Updated documentation examples to align with the current adapter release:
  - replaced stale `bighub-openai@0.1.0` references with `bighub-openai@0.2.0`
  - kept recommendation preview/apply examples aligned with optimistic locking usage.

## [0.2.0] - 2026-02-27

### Added

- Future Memory client coverage for production feedback loops:
  - `actions.ingest_memory(...)`
  - `actions.memory_context(...)`
  - `actions.refresh_memory_aggregates(...)`
  - `actions.memory_recommendations(...)`
- Policy recommendation compatibility fields documented and supported end-to-end:
  - `recommendation_id`, `scope`, `time_window_hours`
  - `target_rule_id` or `rule_selector`
  - `suggested_policy_patch` (JSON Patch envelope)
  - `apply_endpoint` for one-click UX.
- Optimistic concurrency workflow support for rules patching:
  - `RuleResponse.version` typing
  - preview/apply flow with version token usage.
- Expanded webhook/event interoperability in docs and typed surfaces:
  - `rule.patch_previewed`
  - `rule.patch_applied`
  - `decision_event.created`
  - approval lifecycle events.
- Documentation refresh aligned with decision intelligence positioning:
  - Architecture section
  - Policy Intelligence section
  - Provider Adapters section
  - preview-first safe apply examples.

### Changed

- Migration note: `rules.version` is required server-side for atomic optimistic locking
  (introduced via backend rules-version migration).
  If your backend is older, `apply_patch` optimistic locking may return `409`
  conflicts unexpectedly or be unavailable.
- `rules.apply_patch(...)` (sync + async) now accepts either:
  - raw JSON Patch ops list, or
  - wrapped payload `{ "format": "json_patch", "ops": [...] }`.
- `rules.apply_patch(...)` now supports optimistic locking inputs:
  - `if_match_version`
  - `if_match` (If-Match header passthrough).
- Recommended patch flow updated to explicit two-step safety:
  - `preview=True`
  - then `preview=False` with returned version token.

### Removed

- `if_match_updated_at` support in `rules.apply_patch(...)` has been removed in favor of version/ETag-based concurrency.

## [0.1.0] - 2026-02-26

### Added

- First institutional-grade SDK baseline (sync + async clients).
- Public clients: `BighubClient`, `AsyncBighubClient`.
- Resources:
  - `actions`: submit, submit_payload, dry_run, verify_validation, observer_stats, dashboard_summary, status
  - `auth`: signup, login, refresh, logout
  - `rules`: create, list, get, update, delete, pause, resume, dry_run, validate, validate_dry_run, domains, versions, purge_idempotency
  - `kill_switch`: status, activate, deactivate
  - `events`: list, stats
  - `approvals`: list, resolve
  - `api_keys`: create, list, delete/revoke, rotate, validate, scopes
  - `webhooks`: create, list, get, update, delete, deliveries, test, list_events, verify_signature, replay_failed_delivery
- Retry/backoff transport, auth headers, typed exceptions.
- Webhook signature verification helper.
- Reliability: timeout configuration, transient retry (429/5xx/network), Idempotency-Key forwarding.
- DX baseline for 0.1.0: stronger `TypedDict` coverage, ergonomic dataclass payload models, and overloaded method signatures (dict or model), including partial update models for rules/webhooks.
- Basic test suite for sync/async paths.

