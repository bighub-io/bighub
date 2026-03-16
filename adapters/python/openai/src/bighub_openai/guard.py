from __future__ import annotations

import asyncio
import json
import inspect
import logging
import random
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from dataclasses import dataclass
from typing import Any, AsyncIterator, Callable, Dict, Iterator, List, Optional, Union, get_args, get_origin
from uuid import uuid4

from bighub import AsyncBighubClient, BighubClient

from .version import __version__

logger = logging.getLogger("bighub_openai")

_RETRYABLE_OPENAI_ERRORS: tuple[type[Exception], ...] = ()
try:
    from openai import APIConnectionError as _ConnErr, APITimeoutError as _TimeoutErr, RateLimitError as _RateErr
    _RETRYABLE_OPENAI_ERRORS = (_ConnErr, _TimeoutErr, _RateErr)
except ImportError:
    pass


def _is_retryable_openai_error(exc: Exception) -> bool:
    return bool(_RETRYABLE_OPENAI_ERRORS) and isinstance(exc, _RETRYABLE_OPENAI_ERRORS)


class AdapterConfigurationError(ValueError):
    """Raised when adapter/tool configuration is invalid."""


class ProviderResponseError(RuntimeError):
    """Raised when provider response shape is unexpected."""


@dataclass
class _RegisteredTool:
    name: str
    fn: Callable[..., Any]
    description: str
    parameters_schema: Dict[str, Any]
    value_from_args: Optional[Callable[[Dict[str, Any]], float]] = None
    target_from_args: Optional[Callable[[Dict[str, Any]], str]] = None
    action_name: Optional[str] = None
    domain: Optional[str] = None
    actor: Optional[str] = None
    metadata_from_args: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None
    decision_mode: Optional[str] = None
    strict: bool = True


@dataclass
class ToolResult:
    status: str
    decision: Dict[str, Any]
    output: Optional[Any] = None
    error: Optional[str] = None


GuardedToolResult = ToolResult


@dataclass
class ToolExecutionEvent:
    tool: str
    call_id: str
    status: str
    decision: Dict[str, Any]
    arguments: Dict[str, Any]
    output: Optional[Any] = None
    error: Optional[str] = None
    event_id: Optional[str] = None
    trace_id: Optional[str] = None
    request_id: Optional[str] = None
    seq: Optional[int] = None
    schema_version: int = 1
    source_version: Optional[str] = None


class BighubOpenAI:
    """
    OpenAI tool-calling adapter that evaluates actions via BIGHUB before tool execution.
    Integrates the full decision learning loop: evaluate → execute → report outcome → learn.
    """

    def __init__(
        self,
        *,
        bighub_api_key: str,
        actor: str,
        domain: str,
        decision_mode: str = "submit",
        on_decision: Optional[Callable[[Dict[str, Any]], None]] = None,
        memory_enabled: bool = True,
        memory_source: str = "openai_adapter",
        memory_source_version: str = f"bighub-openai@{__version__}",
        memory_ingest_timeout_ms: int = 300,
        outcome_reporting: bool = True,
        openai_api_key: Optional[str] = None,
        openai_client: Optional[Any] = None,
        bighub_client: Optional[BighubClient] = None,
        fail_mode: str = "closed",
        max_tool_rounds: int = 8,
        provider_timeout_seconds: float = 30.0,
        provider_max_retries: int = 2,
        provider_retry_backoff_seconds: float = 0.25,
        provider_retry_max_backoff_seconds: float = 2.0,
        provider_retry_jitter_seconds: float = 0.1,
        provider_circuit_breaker_failures: int = 0,
        provider_circuit_breaker_reset_seconds: float = 30.0,
    ) -> None:
        self._init_shared_config(
            actor=actor,
            domain=domain,
            decision_mode=decision_mode,
            on_decision=on_decision,
            memory_enabled=memory_enabled,
            memory_source=memory_source,
            memory_source_version=memory_source_version,
            memory_ingest_timeout_ms=memory_ingest_timeout_ms,
            outcome_reporting=outcome_reporting,
            fail_mode=fail_mode,
            max_tool_rounds=max_tool_rounds,
            provider_timeout_seconds=provider_timeout_seconds,
            provider_max_retries=provider_max_retries,
            provider_retry_backoff_seconds=provider_retry_backoff_seconds,
            provider_retry_max_backoff_seconds=provider_retry_max_backoff_seconds,
            provider_retry_jitter_seconds=provider_retry_jitter_seconds,
            provider_circuit_breaker_failures=provider_circuit_breaker_failures,
            provider_circuit_breaker_reset_seconds=provider_circuit_breaker_reset_seconds,
        )

        self._bighub = bighub_client or BighubClient(api_key=bighub_api_key)
        self._openai = openai_client or self._build_openai_client(openai_api_key)

    def _init_shared_config(
        self,
        *,
        actor: str,
        domain: str,
        decision_mode: str,
        on_decision: Optional[Callable[[Dict[str, Any]], Any]],
        memory_enabled: bool,
        memory_source: str,
        memory_source_version: str,
        memory_ingest_timeout_ms: int,
        outcome_reporting: bool,
        fail_mode: str,
        max_tool_rounds: int,
        provider_timeout_seconds: float,
        provider_max_retries: int,
        provider_retry_backoff_seconds: float,
        provider_retry_max_backoff_seconds: float,
        provider_retry_jitter_seconds: float,
        provider_circuit_breaker_failures: int,
        provider_circuit_breaker_reset_seconds: float,
    ) -> None:
        if fail_mode not in {"closed", "open"}:
            raise AdapterConfigurationError("fail_mode must be 'closed' or 'open'")
        if decision_mode not in {"submit", "submit_v2"}:
            raise AdapterConfigurationError("decision_mode must be 'submit' or 'submit_v2'")
        if max_tool_rounds < 1:
            raise AdapterConfigurationError("max_tool_rounds must be >= 1")

        self.actor = actor
        self.domain = domain
        self.decision_mode = decision_mode
        self.on_decision = on_decision
        self.memory_enabled = memory_enabled
        self.memory_source = memory_source
        self.memory_source_version = memory_source_version
        self.memory_ingest_timeout_ms = max(100, int(memory_ingest_timeout_ms))
        self.outcome_reporting = outcome_reporting
        self.fail_mode = fail_mode
        self.max_tool_rounds = max_tool_rounds
        self.provider_timeout_seconds = max(1.0, float(provider_timeout_seconds))
        self.provider_max_retries = max(0, int(provider_max_retries))
        self.provider_retry_backoff_seconds = max(0.0, float(provider_retry_backoff_seconds))
        self.provider_retry_max_backoff_seconds = max(0.0, float(provider_retry_max_backoff_seconds))
        self.provider_retry_jitter_seconds = max(0.0, float(provider_retry_jitter_seconds))
        self.provider_circuit_breaker_failures = max(0, int(provider_circuit_breaker_failures))
        self.provider_circuit_breaker_reset_seconds = max(1.0, float(provider_circuit_breaker_reset_seconds))
        self._provider_consecutive_failures = 0
        self._provider_circuit_opened_at: Optional[float] = None
        self._tools: Dict[str, _RegisteredTool] = {}

    @staticmethod
    def _build_openai_client(openai_api_key: Optional[str]) -> Any:
        if openai_api_key is None:
            raise AdapterConfigurationError(
                "openai_api_key is required when openai_client is not provided"
            )
        try:
            from openai import OpenAI
        except ImportError as exc:  # pragma: no cover - import path check only
            raise AdapterConfigurationError(
                "openai package is required for BighubOpenAI"
            ) from exc
        return OpenAI(api_key=openai_api_key)

    def register_tool(
        self,
        name: str,
        fn: Callable[..., Any],
        description: Optional[str] = None,
        parameters_schema: Optional[Dict[str, Any]] = None,
        value_from_args: Optional[Callable[[Dict[str, Any]], float]] = None,
        target_from_args: Optional[Callable[[Dict[str, Any]], str]] = None,
        action_name: Optional[str] = None,
        domain: Optional[str] = None,
        actor: Optional[str] = None,
        metadata_from_args: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None,
        decision_mode: Optional[str] = None,
        strict: bool = True,
    ) -> None:
        effective_mode = decision_mode or self.decision_mode
        if effective_mode not in {"submit", "submit_v2"}:
            raise AdapterConfigurationError("decision_mode must be 'submit' or 'submit_v2'")
        self._tools[name] = _RegisteredTool(
            name=name,
            fn=fn,
            description=description or (fn.__doc__ or f"Execute {name}"),
            parameters_schema=parameters_schema or self._default_parameters_schema(fn),
            value_from_args=value_from_args,
            target_from_args=target_from_args,
            action_name=action_name,
            domain=domain,
            actor=actor,
            metadata_from_args=metadata_from_args,
            decision_mode=effective_mode,
            strict=strict,
        )

    def tool(self, name: str, fn: Callable[..., Any], **kwargs: Any) -> None:
        """
        Alias for register_tool to keep integration terse.
        """
        self.register_tool(name=name, fn=fn, **kwargs)

    def close(self) -> None:
        self._bighub.close()

    def __enter__(self) -> "BighubOpenAI":
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        self.close()

    def run(
        self,
        *,
        messages: List[Dict[str, Any]],
        model: str,
        instructions: Optional[str] = None,
        temperature: Optional[float] = None,
        extra_create_args: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        if not self._tools:
            raise AdapterConfigurationError("No tools registered")
        execution_events: List[ToolExecutionEvent] = []
        trace_id = str(uuid4())

        create_args: Dict[str, Any] = {
            "model": model,
            "input": messages,
            "tools": self._openai_tools(),
        }
        if instructions:
            create_args["instructions"] = instructions
        if temperature is not None:
            create_args["temperature"] = temperature
        if extra_create_args:
            create_args.update(extra_create_args)

        response = self._provider_create(create_args)

        for _ in range(self.max_tool_rounds):
            function_calls = self._extract_function_calls(response)
            if not function_calls:
                self._persist_decisions(events=execution_events, model=model, trace_id=trace_id)
                llm_response = self._serialize_response(response)
                payload: Dict[str, Any] = {
                    **llm_response,  # backwards compatibility
                    "llm_response": llm_response,
                    "execution": {
                        "events": [event.__dict__ for event in execution_events],
                        "last": execution_events[-1].__dict__ if execution_events else None,
                    },
                }
                return payload

            tool_outputs = []
            for idx, call in enumerate(function_calls):
                tool_output, event = self._handle_function_call(call)
                event = self._decorate_event(
                    event=event,
                    trace_id=trace_id,
                    seq=len(execution_events) + idx,
                )
                tool_outputs.append(tool_output)
                execution_events.append(event)
                if self.on_decision:
                    try:
                        self.on_decision(event.__dict__)
                    except Exception:
                        # Hooks must not break execution flow.
                        pass

            continuation: Dict[str, Any] = {
                "model": model,
                "input": tool_outputs,
                "tools": self._openai_tools(),
            }
            resp_id = self._get_attr(response, "id")
            if resp_id:
                continuation["previous_response_id"] = resp_id
            if instructions:
                continuation["instructions"] = instructions
            response = self._provider_create(continuation)

        raise ProviderResponseError("Max tool rounds reached without final response")

    def run_stream(
        self,
        *,
        messages: List[Dict[str, Any]],
        model: str,
        instructions: Optional[str] = None,
        temperature: Optional[float] = None,
        extra_create_args: Optional[Dict[str, Any]] = None,
    ) -> Iterator[Dict[str, Any]]:
        """
        Stream model output while evaluating tool calls via BIGHUB.

        Yields event envelopes:
        - {"type": "llm_delta", "delta": "...", "response_id": "..."}
        - {"type": "execution_event", "event": {...}}
        - {"type": "final_response", "response": {...}}
        """
        if not self._tools:
            raise AdapterConfigurationError("No tools registered")
        execution_events: List[ToolExecutionEvent] = []
        trace_id = str(uuid4())

        create_args: Dict[str, Any] = {
            "model": model,
            "input": messages,
            "tools": self._openai_tools(),
        }
        if instructions:
            create_args["instructions"] = instructions
        if temperature is not None:
            create_args["temperature"] = temperature
        if extra_create_args:
            create_args.update(extra_create_args)

        for _ in range(self.max_tool_rounds):
            stream_method = getattr(getattr(self._openai, "responses", None), "stream", None)
            if callable(stream_method):
                with self._provider_stream(stream_method, create_args) as stream:
                    for raw_event in stream:
                        parsed = self._parse_stream_event(raw_event)
                        if parsed:
                            yield parsed
                    response = stream.get_final_response()
            else:
                # Provider/client does not support streaming API; fallback to one-shot create.
                response = self._provider_create(create_args)

            function_calls = self._extract_function_calls(response)
            if not function_calls:
                self._persist_decisions(events=execution_events, model=model, trace_id=trace_id)
                llm_response = self._serialize_response(response)
                payload: Dict[str, Any] = {
                    **llm_response,  # backwards compatibility
                    "llm_response": llm_response,
                    "execution": {
                        "events": [event.__dict__ for event in execution_events],
                        "last": execution_events[-1].__dict__ if execution_events else None,
                    },
                }
                yield {"type": "final_response", "response": payload}
                return

            tool_outputs = []
            for idx, call in enumerate(function_calls):
                tool_output, event = self._handle_function_call(call)
                event = self._decorate_event(
                    event=event,
                    trace_id=trace_id,
                    seq=len(execution_events) + idx,
                )
                tool_outputs.append(tool_output)
                execution_events.append(event)
                yield {"type": "execution_event", "event": event.__dict__}
                if self.on_decision:
                    try:
                        self.on_decision(event.__dict__)
                    except Exception:
                        pass

            create_args = {
                "model": model,
                "input": tool_outputs,
                "tools": self._openai_tools(),
            }
            resp_id = self._get_attr(response, "id")
            if resp_id:
                create_args["previous_response_id"] = resp_id
            if instructions:
                create_args["instructions"] = instructions

        raise ProviderResponseError("Max tool rounds reached without final response")

    def resume_after_approval(
        self,
        *,
        tool_name: str,
        arguments: Dict[str, Any],
        request_id: str,
        resolution: str = "approved",
        comment: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Resolve an approval request and (if approved) execute the pending tool call.
        """
        approval = self._bighub.approvals.resolve(
            request_id=request_id,
            resolution=resolution,
            comment=comment,
        )
        approved = (
            str(approval.get("status", "")).lower() == "approved"
            and str(approval.get("resolution", resolution)).lower() == "approved"
        )
        if not approved:
            return {
                "request_id": request_id,
                "resolved": True,
                "resumed": False,
                "approval": approval,
            }
        if tool_name not in self._tools:
            raise AdapterConfigurationError(f"Tool '{tool_name}' is not registered")
        tool = self._tools[tool_name]
        maybe_result = tool.fn(**arguments)
        if inspect.isawaitable(maybe_result):
            raise AdapterConfigurationError(
                "Async tool callable detected in sync adapter. Use AsyncBighubOpenAI."
            )
        return {
            "request_id": request_id,
            "resolved": True,
            "resumed": True,
            "approval": approval,
            "tool_output": maybe_result,
        }

    def run_with_approval(
        self,
        *,
        messages: List[Dict[str, Any]],
        model: str,
        instructions: Optional[str] = None,
        temperature: Optional[float] = None,
        extra_create_args: Optional[Dict[str, Any]] = None,
        on_approval_required: Optional[Callable[[Dict[str, Any]], Optional[Dict[str, Any]]]] = None,
    ) -> Dict[str, Any]:
        """
        Run an evaluated interaction and optionally resume execution after human approval.
        """
        response = self.run(
            messages=messages,
            model=model,
            instructions=instructions,
            temperature=temperature,
            extra_create_args=extra_create_args,
        )
        events = ((response.get("execution") or {}).get("events")) or []
        approval_event = next((e for e in reversed(events) if e.get("status") == "approval_required"), None)
        if not approval_event:
            response["approval_loop"] = {"required": False, "resolved": False, "resumed": False}
            return response

        decision = approval_event.get("decision") or {}
        request_id = decision.get("request_id")
        if not request_id:
            response["approval_loop"] = {
                "required": True,
                "resolved": False,
                "resumed": False,
                "error": "missing_request_id",
            }
            return response

        resolution_payload = on_approval_required(
            {"request_id": request_id, "event": approval_event, "response": response}
        ) if on_approval_required else None
        if not resolution_payload:
            response["approval_loop"] = {
                "required": True,
                "resolved": False,
                "resumed": False,
                "request_id": request_id,
            }
            return response

        resolution = resolution_payload.get("resolution", "approved")
        comment = resolution_payload.get("comment")
        resume_result = self.resume_after_approval(
            tool_name=approval_event["tool"],
            arguments=approval_event.get("arguments") or {},
            request_id=request_id,
            resolution=resolution,
            comment=comment,
        )
        response["approval_loop"] = {"required": True, **resume_result}
        return response

    def check_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate action decision without executing the tool.
        """
        if tool_name not in self._tools:
            raise AdapterConfigurationError(f"Tool '{tool_name}' is not registered")
        tool = self._tools[tool_name]
        return self._evaluate_action(tool, arguments)

    def _persist_decisions(
        self,
        *,
        events: List[ToolExecutionEvent],
        model: str,
        trace_id: str,
    ) -> None:
        if not self.memory_enabled or not events:
            return
        try:
            payload_events: List[Dict[str, Any]] = []
            for idx, event in enumerate(events):
                event_id = event.event_id or str(uuid4())
                seq = idx
                event.event_id = event_id
                event.seq = seq
                event.schema_version = 1
                event.source_version = self.memory_source_version
                payload_events.append(
                    {
                        **event.__dict__,
                        "event_id": event_id,
                        "seq": seq,
                        "schema_version": 1,
                        "source_version": self.memory_source_version,
                    }
                )
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(
                    self._bighub.actions.ingest_memory,
                    events=payload_events,
                    source=self.memory_source,
                    source_version=self.memory_source_version,
                    actor=self.actor,
                    domain=self.domain,
                    model=model,
                    trace_id=trace_id,
                    redact=True,
                    redaction_policy="default",
                )
                future.result(timeout=self.memory_ingest_timeout_ms / 1000.0)
        except FutureTimeoutError:
            return
        except Exception:
            # Memory ingest is best-effort; evaluation path must never fail because of telemetry.
            return

    def _openai_tools(self) -> List[Dict[str, Any]]:
        tools: List[Dict[str, Any]] = []
        for tool in self._tools.values():
            tools.append(
                {
                    "type": "function",
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters_schema,
                    "strict": tool.strict,
                }
            )
        return tools

    @staticmethod
    def _default_parameters_schema(fn: Callable[..., Any]) -> Dict[str, Any]:
        sig = inspect.signature(fn)
        properties: Dict[str, Any] = {}
        required: List[str] = []
        for param in sig.parameters.values():
            if param.kind not in (
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                inspect.Parameter.KEYWORD_ONLY,
            ):
                continue
            if param.name in {"self", "cls"}:
                continue
            annotation = param.annotation if param.annotation is not inspect._empty else Any
            properties[param.name] = {"type": BighubOpenAI._json_schema_type(annotation)}
            if param.default is inspect._empty:
                required.append(param.name)
        return {
            "type": "object",
            "properties": properties,
            "required": required,
            "additionalProperties": False,
        }

    @staticmethod
    def _json_schema_type(annotation: Any) -> str:
        origin = get_origin(annotation)
        args = get_args(annotation)
        if origin is None:
            if annotation in {int}:
                return "integer"
            if annotation in {float}:
                return "number"
            if annotation in {bool}:
                return "boolean"
            if annotation in {dict, Dict}:
                return "object"
            if annotation in {list, List}:
                return "array"
            return "string"
        if origin in {list, List}:
            return "array"
        if origin in {dict, Dict}:
            return "object"
        if origin is Union and args:
            non_none = [arg for arg in args if arg is not type(None)]
            if non_none:
                return BighubOpenAI._json_schema_type(non_none[0])
        return "string"

    def _extract_function_calls(self, response: Any) -> List[Dict[str, Any]]:
        output = self._get_attr(response, "output") or []
        calls: List[Dict[str, Any]] = []
        for item in output:
            item_type = self._get_attr(item, "type")
            if item_type == "function_call":
                calls.append(
                    {
                        "id": self._get_attr(item, "id"),
                        "call_id": self._get_attr(item, "call_id"),
                        "name": self._get_attr(item, "name"),
                        "arguments": self._get_attr(item, "arguments") or "{}",
                    }
                )
        return calls

    def _handle_function_call(self, call: Dict[str, Any]) -> tuple[Dict[str, Any], ToolExecutionEvent]:
        name = call["name"]
        if name not in self._tools:
            event = ToolExecutionEvent(
                tool=name,
                call_id=call["call_id"],
                status="blocked",
                decision={},
                arguments={},
                error=f"Tool '{name}' is not registered",
            )
            return (
                self._function_output(
                    call_id=call["call_id"],
                    output={
                        "status": "blocked",
                        "error": f"Tool '{name}' is not registered",
                    },
                ),
                event,
            )

        tool = self._tools[name]
        args = self._parse_arguments(call["arguments"])
        decision = self._evaluate_action(tool, args)

        if decision.get("allowed"):
            try:
                output = tool.fn(**args)
                result = ToolResult(
                    status="executed",
                    decision=decision,
                    output=output,
                )
                self._report_outcome(
                    decision=decision, tool_name=name, status="SUCCESS",
                    description=f"Tool {name} executed successfully",
                )
            except Exception as exc:
                result = ToolResult(
                    status="tool_error",
                    decision=decision,
                    error=str(exc),
                )
                # Backend outcome taxonomy does not define TOOL_ERROR.
                # Map execution failures to FAILURE for /outcomes/report compatibility.
                self._report_outcome(
                    decision=decision, tool_name=name, status="FAILURE",
                    description=f"Tool {name} raised: {exc}",
                )
        elif decision.get("result") == "requires_approval":
            result = ToolResult(
                status="approval_required",
                decision=decision,
            )
        else:
            result = ToolResult(
                status="blocked",
                decision=decision,
            )

        event = ToolExecutionEvent(
            tool=name,
            call_id=call["call_id"],
            status=result.status,
            decision=result.decision,
            arguments=args,
            output=result.output,
            error=result.error,
        )
        return self._function_output(call_id=call["call_id"], output=result.__dict__), event

    def _evaluate_action(
        self, tool: _RegisteredTool, args: Dict[str, Any]
    ) -> Dict[str, Any]:
        action = tool.action_name or tool.name
        domain = tool.domain or self.domain
        actor = tool.actor or self.actor
        target = tool.target_from_args(args) if tool.target_from_args else str(args.get("target", ""))
        decision_mode = tool.decision_mode or self.decision_mode

        try:
            value = (
                float(tool.value_from_args(args))
                if tool.value_from_args
                else self._infer_value(args)
            )
            metadata = tool.metadata_from_args(args) if tool.metadata_from_args else None
            if decision_mode == "submit_v2":
                payload: Dict[str, Any] = {
                    "action": action,
                    "value": value,
                    "target": target,
                    "domain": domain,
                    "actor": actor,
                }
                if metadata:
                    payload["context"] = metadata
                return self._bighub.actions.submit_v2(payload=payload)
            return self._bighub.actions.submit(
                action=action,
                value=value,
                target=target,
                domain=domain,
                actor=actor,
                context=metadata,
            )
        except Exception as exc:
            if self.fail_mode == "open":
                return {
                    "allowed": True,
                    "result": "allowed",
                    "reason": f"Evaluation bypassed (fail_open): {exc}",
                }
            return {
                "allowed": False,
                "result": "blocked",
                "reason": f"Evaluation failed (fail_closed): {exc}",
            }

    def _validate_with_bighub(
        self, tool: _RegisteredTool, args: Dict[str, Any]
    ) -> Dict[str, Any]:
        return self._evaluate_action(tool, args)

    def _report_outcome(
        self,
        *,
        decision: Dict[str, Any],
        tool_name: str,
        status: str,
        description: str,
    ) -> None:
        if not self.outcome_reporting:
            return
        request_id = decision.get("request_id")
        if not request_id:
            return
        try:
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(
                    self._bighub.outcomes.report,
                    request_id=request_id,
                    status=status,
                    description=description,
                )
                future.result(timeout=self.memory_ingest_timeout_ms / 1000.0)
        except Exception:
            pass

    @staticmethod
    def _infer_value(args: Dict[str, Any]) -> float:
        for key in ("value", "amount", "price", "total"):
            val = args.get(key)
            if isinstance(val, (int, float)):
                return float(val)
        raise AdapterConfigurationError(
            "Cannot infer value from args. Provide value_from_args in register_tool."
        )

    @staticmethod
    def _parse_arguments(raw: str) -> Dict[str, Any]:
        if not raw:
            return {}
        if isinstance(raw, dict):
            return raw
        return json.loads(raw)

    @staticmethod
    def _decorate_event(
        *,
        event: ToolExecutionEvent,
        trace_id: str,
        seq: int,
    ) -> ToolExecutionEvent:
        if not event.event_id:
            event.event_id = str(uuid4())
        event.trace_id = trace_id
        event.seq = seq
        decision = event.decision or {}
        event.request_id = decision.get("request_id")
        return event

    @staticmethod
    def _function_output(call_id: str, output: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "type": "function_call_output",
            "call_id": call_id,
            "output": json.dumps(output),
        }

    @staticmethod
    def _serialize_response(response: Any) -> Dict[str, Any]:
        response_id = BighubOpenAI._get_attr(response, "id")
        output = BighubOpenAI._get_attr(response, "output") or []
        output_text = BighubOpenAI._normalize_output_text(response=response, output=output)
        return {
            "response_id": response_id,
            "output_text": output_text,
            "output": [BighubOpenAI._to_dict(item) for item in output],
        }

    @staticmethod
    def _normalize_output_text(*, response: Any, output: List[Any]) -> str:
        output_text = BighubOpenAI._get_attr(response, "output_text")
        if isinstance(output_text, str) and output_text:
            return output_text

        # Fallback parser for provider objects where output_text can be absent.
        chunks: List[str] = []
        for item in output:
            content = BighubOpenAI._get_attr(item, "content") or []
            for block in content:
                text_val = BighubOpenAI._get_attr(block, "text")
                if isinstance(text_val, str) and text_val:
                    chunks.append(text_val)

        return "".join(chunks)

    @staticmethod
    def _to_dict(item: Any) -> Dict[str, Any]:
        if isinstance(item, dict):
            return item
        if hasattr(item, "model_dump"):
            return item.model_dump()
        if hasattr(item, "__dict__"):
            return dict(item.__dict__)
        return {"value": str(item)}

    @staticmethod
    def _get_attr(obj: Any, key: str) -> Any:
        if obj is None:
            return None
        if isinstance(obj, dict):
            return obj.get(key)
        return getattr(obj, key, None)

    def _parse_stream_event(self, raw_event: Any) -> Optional[Dict[str, Any]]:
        event_type = self._get_attr(raw_event, "type")
        if event_type == "response.output_text.delta":
            return {
                "type": "llm_delta",
                "delta": self._get_attr(raw_event, "delta") or "",
                "response_id": self._get_attr(raw_event, "response_id"),
            }
        if event_type == "response.output_text.done":
            return {
                "type": "llm_text_done",
                "text": self._get_attr(raw_event, "text") or "",
                "response_id": self._get_attr(raw_event, "response_id"),
            }
        if event_type == "response.output_item.added":
            item = self._get_attr(raw_event, "item")
            return {
                "type": "output_item_added",
                "item_type": self._get_attr(item, "type") if item else None,
                "output_index": self._get_attr(raw_event, "output_index"),
                "response_id": self._get_attr(raw_event, "response_id"),
            }
        if event_type == "response.function_call_arguments.delta":
            return {
                "type": "function_call_args_delta",
                "delta": self._get_attr(raw_event, "delta") or "",
                "call_id": self._get_attr(raw_event, "call_id"),
                "output_index": self._get_attr(raw_event, "output_index"),
                "response_id": self._get_attr(raw_event, "response_id"),
            }
        if event_type == "response.function_call_arguments.done":
            return {
                "type": "function_call_args_done",
                "arguments": self._get_attr(raw_event, "arguments") or "",
                "call_id": self._get_attr(raw_event, "call_id"),
                "name": self._get_attr(raw_event, "name"),
                "output_index": self._get_attr(raw_event, "output_index"),
                "response_id": self._get_attr(raw_event, "response_id"),
            }
        if event_type == "response.refusal.delta":
            return {
                "type": "refusal_delta",
                "delta": self._get_attr(raw_event, "delta") or "",
                "response_id": self._get_attr(raw_event, "response_id"),
            }
        if event_type in ("response.completed", "response.done"):
            return {
                "type": "response_done",
                "response_id": self._get_attr(raw_event, "response_id"),
            }
        if event_type == "response.failed":
            error = self._get_attr(raw_event, "error")
            return {
                "type": "response_failed",
                "error": self._to_dict(error) if error else None,
                "response_id": self._get_attr(raw_event, "response_id"),
            }
        return None

    def _provider_create(self, payload: Dict[str, Any]) -> Any:
        payload_with_timeout = {**payload, "timeout": self.provider_timeout_seconds}
        payload_with_timeout.setdefault("store", False)
        return self._provider_retry_sync(lambda: self._openai.responses.create(**payload_with_timeout))

    def _provider_stream(self, stream_method: Callable[..., Any], payload: Dict[str, Any]) -> Any:
        payload_with_timeout = {**payload, "timeout": self.provider_timeout_seconds}
        payload_with_timeout.setdefault("store", False)
        return self._provider_retry_sync(lambda: stream_method(**payload_with_timeout))

    def _provider_retry_sync(self, operation: Callable[[], Any]) -> Any:
        if self._is_provider_circuit_open():
            raise ProviderResponseError("Provider circuit breaker is open")
        attempts = self.provider_max_retries + 1
        last_error: Optional[Exception] = None
        for attempt in range(1, attempts + 1):
            try:
                result = operation()
                self._on_provider_call_success()
                return result
            except Exception as exc:
                if _is_retryable_openai_error(exc):
                    last_error = exc
                    logger.warning("Provider transient error (attempt %d/%d): %s", attempt, attempts, exc)
                    if attempt >= attempts:
                        break
                    delay = min(
                        self.provider_retry_backoff_seconds * (2 ** (attempt - 1)),
                        self.provider_retry_max_backoff_seconds,
                    )
                    if self.provider_retry_jitter_seconds:
                        delay += random.uniform(0.0, self.provider_retry_jitter_seconds)
                    if delay > 0:
                        time.sleep(delay)
                    continue
                self._on_provider_call_failure()
                raise ProviderResponseError(f"Provider call failed (non-retryable): {exc}") from exc
        self._on_provider_call_failure()
        raise ProviderResponseError(f"Provider call failed after retries: {last_error}")

    def _is_provider_circuit_open(self) -> bool:
        if self.provider_circuit_breaker_failures <= 0:
            return False
        if self._provider_circuit_opened_at is None:
            return False
        if (time.monotonic() - self._provider_circuit_opened_at) >= self.provider_circuit_breaker_reset_seconds:
            self._provider_circuit_opened_at = None
            self._provider_consecutive_failures = 0
            return False
        return True

    def _on_provider_call_success(self) -> None:
        self._provider_consecutive_failures = 0
        self._provider_circuit_opened_at = None

    def _on_provider_call_failure(self) -> None:
        if self.provider_circuit_breaker_failures <= 0:
            return
        self._provider_consecutive_failures += 1
        if self._provider_consecutive_failures >= self.provider_circuit_breaker_failures:
            self._provider_circuit_opened_at = time.monotonic()


class AsyncBighubOpenAI(BighubOpenAI):
    """
    Async OpenAI tool-calling adapter that evaluates actions via BIGHUB before tool execution.
    """

    def __init__(
        self,
        *,
        bighub_api_key: str,
        actor: str,
        domain: str,
        decision_mode: str = "submit",
        on_decision: Optional[Callable[[Dict[str, Any]], Any]] = None,
        memory_enabled: bool = True,
        memory_source: str = "openai_adapter",
        memory_source_version: str = f"bighub-openai@{__version__}",
        memory_ingest_timeout_ms: int = 300,
        outcome_reporting: bool = True,
        openai_api_key: Optional[str] = None,
        openai_client: Optional[Any] = None,
        bighub_client: Optional[AsyncBighubClient] = None,
        fail_mode: str = "closed",
        max_tool_rounds: int = 8,
        provider_timeout_seconds: float = 30.0,
        provider_max_retries: int = 2,
        provider_retry_backoff_seconds: float = 0.25,
        provider_retry_max_backoff_seconds: float = 2.0,
        provider_retry_jitter_seconds: float = 0.1,
        provider_circuit_breaker_failures: int = 0,
        provider_circuit_breaker_reset_seconds: float = 30.0,
    ) -> None:
        self._init_shared_config(
            actor=actor,
            domain=domain,
            decision_mode=decision_mode,
            on_decision=on_decision,
            memory_enabled=memory_enabled,
            memory_source=memory_source,
            memory_source_version=memory_source_version,
            memory_ingest_timeout_ms=memory_ingest_timeout_ms,
            outcome_reporting=outcome_reporting,
            fail_mode=fail_mode,
            max_tool_rounds=max_tool_rounds,
            provider_timeout_seconds=provider_timeout_seconds,
            provider_max_retries=provider_max_retries,
            provider_retry_backoff_seconds=provider_retry_backoff_seconds,
            provider_retry_max_backoff_seconds=provider_retry_max_backoff_seconds,
            provider_retry_jitter_seconds=provider_retry_jitter_seconds,
            provider_circuit_breaker_failures=provider_circuit_breaker_failures,
            provider_circuit_breaker_reset_seconds=provider_circuit_breaker_reset_seconds,
        )

        self._bighub = bighub_client or AsyncBighubClient(api_key=bighub_api_key)
        self._openai = openai_client or self._build_openai_client(openai_api_key)

    @staticmethod
    def _build_openai_client(openai_api_key: Optional[str]) -> Any:
        if openai_api_key is None:
            raise AdapterConfigurationError(
                "openai_api_key is required when openai_client is not provided"
            )
        try:
            from openai import AsyncOpenAI
        except ImportError as exc:  # pragma: no cover - import path check only
            raise AdapterConfigurationError(
                "openai package is required for AsyncBighubOpenAI"
            ) from exc
        return AsyncOpenAI(api_key=openai_api_key)

    async def close(self) -> None:
        await self._bighub.close()

    async def __aenter__(self) -> "AsyncBighubOpenAI":
        return self

    async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        await self.close()

    async def run(
        self,
        *,
        messages: List[Dict[str, Any]],
        model: str,
        instructions: Optional[str] = None,
        temperature: Optional[float] = None,
        extra_create_args: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        if not self._tools:
            raise AdapterConfigurationError("No tools registered")
        execution_events: List[ToolExecutionEvent] = []
        trace_id = str(uuid4())

        create_args: Dict[str, Any] = {
            "model": model,
            "input": messages,
            "tools": self._openai_tools(),
        }
        if instructions:
            create_args["instructions"] = instructions
        if temperature is not None:
            create_args["temperature"] = temperature
        if extra_create_args:
            create_args.update(extra_create_args)

        response = await self._provider_create_async(create_args)

        for _ in range(self.max_tool_rounds):
            function_calls = self._extract_function_calls(response)
            if not function_calls:
                await self._persist_decisions(events=execution_events, model=model, trace_id=trace_id)
                llm_response = self._serialize_response(response)
                payload: Dict[str, Any] = {
                    **llm_response,  # backwards compatibility
                    "llm_response": llm_response,
                    "execution": {
                        "events": [event.__dict__ for event in execution_events],
                        "last": execution_events[-1].__dict__ if execution_events else None,
                    },
                }
                return payload

            tool_outputs = []
            for idx, call in enumerate(function_calls):
                tool_output, event = await self._handle_function_call(call)
                event = self._decorate_event(
                    event=event,
                    trace_id=trace_id,
                    seq=len(execution_events) + idx,
                )
                tool_outputs.append(tool_output)
                execution_events.append(event)
                if self.on_decision:
                    try:
                        maybe_awaitable = self.on_decision(event.__dict__)
                        if inspect.isawaitable(maybe_awaitable):
                            await maybe_awaitable
                    except Exception:
                        # Hooks must not break execution flow.
                        pass

            continuation: Dict[str, Any] = {
                "model": model,
                "input": tool_outputs,
                "tools": self._openai_tools(),
            }
            resp_id = self._get_attr(response, "id")
            if resp_id:
                continuation["previous_response_id"] = resp_id
            if instructions:
                continuation["instructions"] = instructions
            response = await self._provider_create_async(continuation)

        raise ProviderResponseError("Max tool rounds reached without final response")

    async def run_stream(
        self,
        *,
        messages: List[Dict[str, Any]],
        model: str,
        instructions: Optional[str] = None,
        temperature: Optional[float] = None,
        extra_create_args: Optional[Dict[str, Any]] = None,
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Stream model output while evaluating tool calls via BIGHUB.

        Yields event envelopes:
        - {"type": "llm_delta", "delta": "...", "response_id": "..."}
        - {"type": "execution_event", "event": {...}}
        - {"type": "final_response", "response": {...}}
        """
        if not self._tools:
            raise AdapterConfigurationError("No tools registered")
        execution_events: List[ToolExecutionEvent] = []
        trace_id = str(uuid4())

        create_args: Dict[str, Any] = {
            "model": model,
            "input": messages,
            "tools": self._openai_tools(),
        }
        if instructions:
            create_args["instructions"] = instructions
        if temperature is not None:
            create_args["temperature"] = temperature
        if extra_create_args:
            create_args.update(extra_create_args)

        for _ in range(self.max_tool_rounds):
            stream_method = getattr(getattr(self._openai, "responses", None), "stream", None)
            if callable(stream_method):
                async with await self._provider_stream_async(stream_method, create_args) as stream:
                    async for raw_event in stream:
                        parsed = self._parse_stream_event(raw_event)
                        if parsed:
                            yield parsed
                    final_response = stream.get_final_response()
                    response = await final_response if inspect.isawaitable(final_response) else final_response
            else:
                # Provider/client does not support streaming API; fallback to one-shot create.
                response = await self._provider_create_async(create_args)

            function_calls = self._extract_function_calls(response)
            if not function_calls:
                await self._persist_decisions(events=execution_events, model=model, trace_id=trace_id)
                llm_response = self._serialize_response(response)
                payload: Dict[str, Any] = {
                    **llm_response,  # backwards compatibility
                    "llm_response": llm_response,
                    "execution": {
                        "events": [event.__dict__ for event in execution_events],
                        "last": execution_events[-1].__dict__ if execution_events else None,
                    },
                }
                yield {"type": "final_response", "response": payload}
                return

            tool_outputs = []
            for idx, call in enumerate(function_calls):
                tool_output, event = await self._handle_function_call(call)
                event = self._decorate_event(
                    event=event,
                    trace_id=trace_id,
                    seq=len(execution_events) + idx,
                )
                tool_outputs.append(tool_output)
                execution_events.append(event)
                yield {"type": "execution_event", "event": event.__dict__}
                if self.on_decision:
                    try:
                        maybe_awaitable = self.on_decision(event.__dict__)
                        if inspect.isawaitable(maybe_awaitable):
                            await maybe_awaitable
                    except Exception:
                        pass

            create_args = {
                "model": model,
                "input": tool_outputs,
                "tools": self._openai_tools(),
            }
            resp_id = self._get_attr(response, "id")
            if resp_id:
                create_args["previous_response_id"] = resp_id
            if instructions:
                create_args["instructions"] = instructions

        raise ProviderResponseError("Max tool rounds reached without final response")

    async def _provider_create_async(self, payload: Dict[str, Any]) -> Any:
        payload_with_timeout = {**payload, "timeout": self.provider_timeout_seconds}
        payload_with_timeout.setdefault("store", False)
        return await self._provider_retry_async(lambda: self._openai.responses.create(**payload_with_timeout))

    async def _provider_stream_async(self, stream_method: Callable[..., Any], payload: Dict[str, Any]) -> Any:
        payload_with_timeout = {**payload, "timeout": self.provider_timeout_seconds}
        payload_with_timeout.setdefault("store", False)
        return await self._provider_retry_async(lambda: stream_method(**payload_with_timeout))

    async def _provider_retry_async(self, operation: Callable[[], Any]) -> Any:
        if self._is_provider_circuit_open():
            raise ProviderResponseError("Provider circuit breaker is open")
        attempts = self.provider_max_retries + 1
        last_error: Optional[Exception] = None
        for attempt in range(1, attempts + 1):
            try:
                result = operation()
                if inspect.isawaitable(result):
                    result = await result
                self._on_provider_call_success()
                return result
            except Exception as exc:
                if _is_retryable_openai_error(exc):
                    last_error = exc
                    logger.warning("Provider transient error (attempt %d/%d): %s", attempt, attempts, exc)
                    if attempt >= attempts:
                        break
                    delay = min(
                        self.provider_retry_backoff_seconds * (2 ** (attempt - 1)),
                        self.provider_retry_max_backoff_seconds,
                    )
                    if self.provider_retry_jitter_seconds:
                        delay += random.uniform(0.0, self.provider_retry_jitter_seconds)
                    if delay > 0:
                        await asyncio.sleep(delay)
                    continue
                self._on_provider_call_failure()
                raise ProviderResponseError(f"Provider call failed (non-retryable): {exc}") from exc
        self._on_provider_call_failure()
        raise ProviderResponseError(f"Provider call failed after retries: {last_error}")

    async def resume_after_approval(
        self,
        *,
        tool_name: str,
        arguments: Dict[str, Any],
        request_id: str,
        resolution: str = "approved",
        comment: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Resolve an approval request and (if approved) execute the pending tool call.
        """
        approval = await self._bighub.approvals.resolve(
            request_id=request_id,
            resolution=resolution,
            comment=comment,
        )
        approved = (
            str(approval.get("status", "")).lower() == "approved"
            and str(approval.get("resolution", resolution)).lower() == "approved"
        )
        if not approved:
            return {
                "request_id": request_id,
                "resolved": True,
                "resumed": False,
                "approval": approval,
            }
        if tool_name not in self._tools:
            raise AdapterConfigurationError(f"Tool '{tool_name}' is not registered")
        tool = self._tools[tool_name]
        maybe_result = tool.fn(**arguments)
        output = await maybe_result if inspect.isawaitable(maybe_result) else maybe_result
        return {
            "request_id": request_id,
            "resolved": True,
            "resumed": True,
            "approval": approval,
            "tool_output": output,
        }

    async def run_with_approval(
        self,
        *,
        messages: List[Dict[str, Any]],
        model: str,
        instructions: Optional[str] = None,
        temperature: Optional[float] = None,
        extra_create_args: Optional[Dict[str, Any]] = None,
        on_approval_required: Optional[Callable[[Dict[str, Any]], Any]] = None,
    ) -> Dict[str, Any]:
        """
        Run an evaluated interaction and optionally resume execution after human approval.
        """
        response = await self.run(
            messages=messages,
            model=model,
            instructions=instructions,
            temperature=temperature,
            extra_create_args=extra_create_args,
        )
        events = ((response.get("execution") or {}).get("events")) or []
        approval_event = next((e for e in reversed(events) if e.get("status") == "approval_required"), None)
        if not approval_event:
            response["approval_loop"] = {"required": False, "resolved": False, "resumed": False}
            return response

        decision = approval_event.get("decision") or {}
        request_id = decision.get("request_id")
        if not request_id:
            response["approval_loop"] = {
                "required": True,
                "resolved": False,
                "resumed": False,
                "error": "missing_request_id",
            }
            return response

        resolution_payload = None
        if on_approval_required:
            maybe_awaitable = on_approval_required(
                {"request_id": request_id, "event": approval_event, "response": response}
            )
            resolution_payload = await maybe_awaitable if inspect.isawaitable(maybe_awaitable) else maybe_awaitable
        if not resolution_payload:
            response["approval_loop"] = {
                "required": True,
                "resolved": False,
                "resumed": False,
                "request_id": request_id,
            }
            return response

        resolution = resolution_payload.get("resolution", "approved")
        comment = resolution_payload.get("comment")
        resume_result = await self.resume_after_approval(
            tool_name=approval_event["tool"],
            arguments=approval_event.get("arguments") or {},
            request_id=request_id,
            resolution=resolution,
            comment=comment,
        )
        response["approval_loop"] = {"required": True, **resume_result}
        return response

    async def check_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate action decision without executing the tool.
        """
        if tool_name not in self._tools:
            raise AdapterConfigurationError(f"Tool '{tool_name}' is not registered")
        tool = self._tools[tool_name]
        return await self._evaluate_action(tool, arguments)

    async def _persist_decisions(
        self,
        *,
        events: List[ToolExecutionEvent],
        model: str,
        trace_id: str,
    ) -> None:
        if not self.memory_enabled or not events:
            return
        try:
            payload_events: List[Dict[str, Any]] = []
            for idx, event in enumerate(events):
                event_id = event.event_id or str(uuid4())
                seq = idx
                event.event_id = event_id
                event.seq = seq
                event.schema_version = 1
                event.source_version = self.memory_source_version
                payload_events.append(
                    {
                        **event.__dict__,
                        "event_id": event_id,
                        "seq": seq,
                        "schema_version": 1,
                        "source_version": self.memory_source_version,
                    }
                )
            await asyncio.wait_for(
                self._bighub.actions.ingest_memory(
                    events=payload_events,
                    source=self.memory_source,
                    source_version=self.memory_source_version,
                    actor=self.actor,
                    domain=self.domain,
                    model=model,
                    trace_id=trace_id,
                    redact=True,
                    redaction_policy="default",
                ),
                timeout=self.memory_ingest_timeout_ms / 1000.0,
            )
        except Exception:
            # Memory ingest is best-effort; evaluation path must never fail because of telemetry.
            return

    async def _handle_function_call(self, call: Dict[str, Any]) -> tuple[Dict[str, Any], ToolExecutionEvent]:
        name = call["name"]
        if name not in self._tools:
            event = ToolExecutionEvent(
                tool=name,
                call_id=call["call_id"],
                status="blocked",
                decision={},
                arguments={},
                error=f"Tool '{name}' is not registered",
            )
            return (
                self._function_output(
                    call_id=call["call_id"],
                    output={
                        "status": "blocked",
                        "error": f"Tool '{name}' is not registered",
                    },
                ),
                event,
            )

        tool = self._tools[name]
        args = self._parse_arguments(call["arguments"])
        decision = await self._evaluate_action(tool, args)

        if decision.get("allowed"):
            try:
                maybe_result = tool.fn(**args)
                output = await maybe_result if inspect.isawaitable(maybe_result) else maybe_result
                result = ToolResult(
                    status="executed",
                    decision=decision,
                    output=output,
                )
                await self._report_outcome(
                    decision=decision, tool_name=name, status="SUCCESS",
                    description=f"Tool {name} executed successfully",
                )
            except Exception as exc:
                result = ToolResult(
                    status="tool_error",
                    decision=decision,
                    error=str(exc),
                )
                # Backend outcome taxonomy does not define TOOL_ERROR.
                # Map execution failures to FAILURE for /outcomes/report compatibility.
                await self._report_outcome(
                    decision=decision, tool_name=name, status="FAILURE",
                    description=f"Tool {name} raised: {exc}",
                )
        elif decision.get("result") == "requires_approval":
            result = ToolResult(
                status="approval_required",
                decision=decision,
            )
        else:
            result = ToolResult(
                status="blocked",
                decision=decision,
            )

        event = ToolExecutionEvent(
            tool=name,
            call_id=call["call_id"],
            status=result.status,
            decision=result.decision,
            arguments=args,
            output=result.output,
            error=result.error,
        )
        return self._function_output(call_id=call["call_id"], output=result.__dict__), event

    async def _evaluate_action(
        self, tool: _RegisteredTool, args: Dict[str, Any]
    ) -> Dict[str, Any]:
        action = tool.action_name or tool.name
        domain = tool.domain or self.domain
        actor = tool.actor or self.actor
        target = tool.target_from_args(args) if tool.target_from_args else str(args.get("target", ""))
        decision_mode = tool.decision_mode or self.decision_mode

        try:
            value = (
                float(tool.value_from_args(args))
                if tool.value_from_args
                else self._infer_value(args)
            )
            metadata = tool.metadata_from_args(args) if tool.metadata_from_args else None
            if decision_mode == "submit_v2":
                payload: Dict[str, Any] = {
                    "action": action,
                    "value": value,
                    "target": target,
                    "domain": domain,
                    "actor": actor,
                }
                if metadata:
                    payload["context"] = metadata
                return await self._bighub.actions.submit_v2(payload=payload)
            return await self._bighub.actions.submit(
                action=action,
                value=value,
                target=target,
                domain=domain,
                actor=actor,
                context=metadata,
            )
        except Exception as exc:
            if self.fail_mode == "open":
                return {
                    "allowed": True,
                    "result": "allowed",
                    "reason": f"Evaluation bypassed (fail_open): {exc}",
                }
            return {
                "allowed": False,
                "result": "blocked",
                "reason": f"Evaluation failed (fail_closed): {exc}",
            }

    async def _validate_with_bighub(
        self, tool: _RegisteredTool, args: Dict[str, Any]
    ) -> Dict[str, Any]:
        return await self._evaluate_action(tool, args)

    async def _report_outcome(
        self,
        *,
        decision: Dict[str, Any],
        tool_name: str,
        status: str,
        description: str,
    ) -> None:
        if not self.outcome_reporting:
            return
        request_id = decision.get("request_id")
        if not request_id:
            return
        try:
            await asyncio.wait_for(
                self._bighub.outcomes.report(
                    request_id=request_id,
                    status=status,
                    description=description,
                ),
                timeout=self.memory_ingest_timeout_ms / 1000.0,
            )
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Backward-compat aliases (deprecated, use BighubOpenAI / AsyncBighubOpenAI)
# ---------------------------------------------------------------------------
GuardedOpenAI = BighubOpenAI
AsyncGuardedOpenAI = AsyncBighubOpenAI

