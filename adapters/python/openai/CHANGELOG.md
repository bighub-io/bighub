# Changelog

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
- **Responses API v2 support**: Targets `openai>=2.0.0,<3.0.0` and `client.responses.create`.
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
