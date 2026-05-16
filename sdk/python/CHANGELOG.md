# Changelog

All notable changes to the official BIGHUB Python SDK are documented in this file.

The format is based on Keep a Changelog and this project uses Semantic Versioning.

## [Unreleased]

No unreleased entries at this time.

## [0.1.0b6] - 2026-05-16

### Added

- Added the Federated Noosphere SDK surface: `client.noosphere.contribute()`, `snapshot()`, `invariant_patterns()`, `disagreement_patterns()`, `breach_patterns()`, `invariant_applicability()`, `disagreement_applicability()`, and `applicability_report()`.
- Added typed responses for cross-organization civilizational learning: `FederatedInvariantPatternDict`, `FederatedDisagreementPatternDict`, `FederatedBreachPatternDict`, `FederatedNoosphereSummaryDict`, `FederatedNoosphereSnapshotResponse`, `FederatedContributionResponse`, `FederatedApplicabilityVerdictDict`, `FederatedApplicabilityReportDict`, and their wrapping responses.
- Exposed signal-manipulation audit on `Decision`, `DecisionBrief`, and typed evaluate responses via `SignalManipulationAuditDict`.
- Added multi-domain causality cascades, deontic registry, and decision freedom metrics on the learning impact report typed responses.

### Notes

- Federated patterns are advisory and never carry org_id, transition_id, or payload data. They are published only after k-anonymity filtering.
- Decision freedom metrics expose stagnation risk and conservative-pressure scoring so SDK consumers can observe whether BIGHUB is over-blocking legitimate novelty.

## [0.1.0b5] - 2026-05-16

### Added

- Exposed expanded decision intelligence surfaces on `Decision`, `DecisionBrief`, and typed evaluate responses: performative contracts, catastrophic ceilings, regret vectors, signal epistemology, and safe novelty lanes.
- Added learning impact report typing for promise metrics and regret vector summaries.

### Changed

- Switched public package licensing metadata and license text from MIT to Apache-2.0.

## [0.1.0b4] - 2026-05-16

### Added

- Exposed semantic decision views on `Decision` and typed evaluate responses: `operational_intent`, `agent_operational_body`, and `action_interpretation_layer`.
- Added compact `DecisionBrief` accessors for `action_family`, `interpreted_action`, and `intent_mismatch`.

### Changed

- Documented semantic decision views as explanatory, additive signals separate from runtime gating.

## [0.1.0b3] - 2026-05-16

### Added

- Exposed `responsible_action_space` and `salient_factors` on `Decision`, `DecisionBrief`, and typed evaluate responses.
- Added `client.learning.impact()` and `client.learning.disagreement_metrics()` for post-outcome learning impact metrics, including `avg_regret_reduction`.

### Changed

- Updated README examples to separate pre-execution decision signals from post-outcome learning impact metrics.

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

