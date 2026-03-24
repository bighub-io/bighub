# Changelog

## [3.1.1] - 2026-03-24

### Changed
- Restructured PyPI README: added TL;DR, "When to use bighub-openai", table of contents, and clearer section hierarchy.
- Bumped core SDK dependency floor to `bighub>=3.1.1,<4.0.0`.

## [3.1.0] - 2026-03-24

### Breaking product shift — advisory-first model

- **Moved from `allowed`/`blocked` verdicts to structured recommendations.** The adapter now surfaces `recommendation`, `recommendation_confidence`, `risk_score`, and `decision_intelligence` (including `rationale`, `evidence_status`, `trajectory_health`) as the primary response shape. The agent/runtime decides how to act based on the recommendation and the configured mode (`advisory`, `review`, `enforced`). Legacy fields (`allowed`, `result`) remain for backward compatibility.
- **Trajectory-aware evaluation.** Tool calls are no longer evaluated as isolated actions. BIGHUB considers prior decisions and their outcomes in the current sequence, producing trajectory-aware recommendations for multi-step agent workflows.
- **Fail-safe enforcement.** In `enforced` mode, unknown or missing verdicts now default to blocked (fail-safe) instead of silently executing.
- **Renamed `guard` to `runtime` in all examples** to reflect the advisory-first positioning: BIGHUB is a decision runtime, not a guardrail.

### Added

- Exhaustive PyPI-facing README with full API reference, configuration details, and advanced usage patterns.
- Automatic outcome reporting with `recommendation_followed` inference.

### Changed

- Bumped core SDK compatibility floor to `bighub>=3.1.0,<4.0.0`.
- Synced package metadata and runtime version to `3.1.0`.

## [3.0.1] - 2026-03-16

### Changed
- Added missing project links in PyPI metadata:
  - GitHub repository: `https://github.com/bighub-io/bighub`
  - MCP package: `https://www.npmjs.com/package/@bighub/bighub-mcp`
- Bumped core SDK dependency floor to `bighub>=3.0.1,<4.0.0`.

## [3.0.0] - 2026-03-12

### Changed
- Bumped adapter version to `3.0.0` to align with the SDK major release line.
- Updated SDK compatibility constraint to `bighub>=3.0.0,<4.0.0`.
- Consolidated release readiness guidance for 3.0 alignment (version sync + compatibility checks).
- Fixed outcome reporting alignment with backend taxonomy by mapping tool execution failures to `FAILURE` (instead of non-existent `TOOL_ERROR`).

## [0.3.0] - 2026-03-15

### Changed
- Pivoted adapter positioning and documentation to the full decision learning loop:
  - evaluate tool call
  - execute when allowed
  - report real outcome
  - learn for future similar actions.
- Promoted `BighubOpenAI` and `AsyncBighubOpenAI` as canonical public classes.
- Rewrote README around decision cases, outcome linkage, calibration, learned guidance, and safety floor behavior.

### Added

- Automatic outcome reporting hooks after tool execution outcomes (success/error) so adapter flows can feed BIGHUB outcome learning.
- Outcome-aware integration path to support `evaluate -> execute -> report outcome -> learn` end-to-end from OpenAI tool calls.
- Expanded tests for canonical class naming, alias compatibility, and outcome reporting behavior.

### Compatibility

- Kept `GuardedOpenAI` / `AsyncGuardedOpenAI` as backward-compatible aliases to avoid breaking existing integrations.
- Aligned dependencies to the SDK decision learning line: `bighub>=0.3.0,<0.4.0`.
- Synced package metadata and runtime version to `0.3.0`.

## [0.2.5] - 2026-03-09

### Changed
- Aligned all documentation with decision intelligence positioning (simulate, score, enforce, learn).
- Updated PyPI description and keywords to reflect self-improving rules branding.
- Synced package version and runtime version constant to `0.2.5`.
- Refactored shared guarded-client initialization to reduce sync/async duplication and keep config validation consistent.
- Made retryable provider error handling explicit and safer by removing the broad fallback that could retry non-retryable exceptions.
- Aligned core SDK dependency to `bighub>=0.2.6,<0.3.0`.

## [0.2.3] - 2026-03-05

### Fixed
- Default Future Memory `source_version` now follows the package version dynamically instead of reporting stale `bighub-openai@0.1.x`.

### Changed
- Dependency floor now targets `bighub>=0.2.4,<0.3.0` to align with the current core SDK release.
- Refreshed release instructions so the documented checklist matches the current patch release workflow.

## [0.2.2] - 2026-03-02

- Security hardening: much safer.

## [0.2.1] - 2026-03-01

### Changed
- **Documentation updates**: Switched adapter examples to `domain="customer_transactions"` to align with current execution domains.
- **Future Memory disclaimer**: Marked Future Memory as experimental and potentially bug-prone in README guidance.

## [0.2.0] - 2026-02-27

### Added
- **Responses API support**: Targets `openai>=2.0.0,<3.0.0` and `client.responses.create`.
- **`store=false` by default**: All provider calls set `store=false` to avoid persisting tool-call data on OpenAI servers. Override via `extra_create_args={"store": True}`.
- **Expanded stream events**: `run_stream` now emits `llm_text_done`, `output_item_added`, `function_call_args_delta`, `function_call_args_done`, `refusal_delta`, `response_done`, and `response_failed` in addition to existing `llm_delta`, `execution_event`, `final_response`.
- **Typed retry on transient errors**: Retries only trigger on `APIConnectionError`, `APITimeoutError`, `RateLimitError`. Non-retryable errors (e.g. `BadRequestError`) fail immediately.
- **Reasoning item resilience**: `_extract_function_calls` safely ignores reasoning, message, and other non-function-call items in response output.
- **Multi-turn instructions forwarding**: Continuation calls now forward `instructions` parameter on subsequent turns.
- **`AsyncGuardedOpenAI`**: Full async counterpart with streaming, approval loop, and circuit breaker support.
- **Approval loop helpers**: `run_with_approval` and `resume_after_approval` (sync + async).
- **Provider resilience**: Configurable retries, exponential backoff with jitter, circuit breaker.
- **Observability contract**: All events carry `trace_id`, `request_id`, `event_id`.
- **Future Memory ingest**: Best-effort telemetry with `schema_version` and `source_version`.

### Changed
- **openai dependency**: `openai>=2.0.0,<3.0.0` (was `>=1.0.0,<2.0.0`).
- **bighub dependency**: `bighub>=0.2.0,<0.3.0` (was `>=0.1.0`).
- **Tool schema format**: Flat `{type, name, parameters, strict}` for Responses API (not nested Chat Completions wrapper).
- **Output text extraction**: Uses `response.output_text` with fallback to `response.output[].content[].text`.

## [0.1.0] - 2026-02-15

Initial release with decision intelligence for tools via `GuardedOpenAI.run()`.
