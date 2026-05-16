# Changelog

All notable changes to the BIGHUB OpenAI adapter are documented in this file.

The format is based on Keep a Changelog and this project uses Semantic Versioning.

## [Unreleased]

No unreleased entries at this time.

## [0.1.0b3] - 2026-05-16

### Added

- Propagated BIGHUB `responsible_action_space` and `salient_factors` into OpenAI tool results and execution events.

### Changed

- Aligned the core SDK dependency to `bighub>=0.1.0b3,<0.2.0`.
- Documented that responsible action space and salient factors are explanatory signals and do not override runtime gating.

## [0.1.0b2] - 2026-05-15

### Changed

- Refined the PyPI README to position `bighub-openai` as the Better Decision layer for risky OpenAI tool calls in IT workflows.
- Shortened the package landing page, removed legacy refund/payment framing, and aligned examples with the current decision surface.

## [0.1.0b1] - 2026-05-15

### Added

- Added the `BighubOpenAI` and `AsyncBighubOpenAI` adapters for OpenAI tool-call flows protected by BIGHUB Better Decision.
- Added backward-compatible `GuardedOpenAI` and `AsyncGuardedOpenAI` aliases.
- Added OpenAI Responses API support with safe tool execution, approval loop helpers, streaming events, transient retry handling, and outcome reporting hooks.
- Added Future Memory ingest metadata with dynamic `bighub-openai@0.1.0b1` source versioning.

### Changed

- Reset package metadata and runtime version to `0.1.0b1` for the new public adapter beta release line.
- Aligned the core SDK dependency to `bighub>=0.1.0b1,<0.2.0`.
