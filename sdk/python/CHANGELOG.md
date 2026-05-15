# Changelog

All notable changes to the official BIGHUB Python SDK are documented in this file.

The format is based on Keep a Changelog and this project uses Semantic Versioning.

## [Unreleased]

No unreleased entries at this time.

## [0.1.0b2] - 2026-05-15

### Changed

- Refined the PyPI README to position `bighub` as the Better Decision SDK for risky IT agent actions and CI/CD workflows.
- Shortened package landing-page content, removed stale beta plan details, and aligned examples with the current decision contract.

## [0.1.0b1] - 2026-05-15

### Added

- Added the modern Better Decision SDK surface: `Bighub`, `BighubClient`, `AsyncBighubClient`, `Decision`, `AsyncDecision`, `DecisionPacket`, `DecisionBrainResult`, and `ModelSelection`.
- Added `DecisionBrief` plus `decision.brief()` / `decision.to_brief_dict()` for a stable, polished decision surface that hides backend legacy/raw response history.
- Added first-class Systems SDK support for GitHub, Sentry, Datadog, AWS CloudTrail, Terraform, Kubernetes, Argo CD, GitLab, Jenkins, Azure, Prometheus, Grafana, and OpenShift.
- Added sync and async helpers for integration connections, config tests, saves/deletes, manual polls, schedules, history, scheduler status, polling metrics, and operational world state.
- Added public system integration TypedDicts for provider, connection, schedule, history, status, and metrics responses.
- Added resources for actions, approvals, outcomes, constraints/rules, webhooks, API keys, events, cases, precedents, calibration, retrieval, simulations, insights, features, and learning controls.

### Changed

- Reset package metadata and runtime version to `0.1.0b1` for the new public SDK beta release line.
- Documented `DecisionBrief` as the recommended interface for agents and product code that do not need the full normalized `Decision` object.
- Documented the systems evidence flow so callers can route poll-derived operational state into Better Decision workflows.

