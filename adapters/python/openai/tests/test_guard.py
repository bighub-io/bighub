from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from bighub_openai import AsyncBighubOpenAI, AsyncGuardedOpenAI, BighubOpenAI, GuardedOpenAI, ToolResult

try:
    from openai import APIConnectionError as _RetryableError
except ImportError:
    _RetryableError = None  # type: ignore[assignment, misc]


class FakeResponses:
    def __init__(self) -> None:
        self.calls = 0
        self.last_kwargs: dict = {}

    def create(self, **kwargs):
        self.calls += 1
        self.last_kwargs = kwargs
        if self.calls == 1:
            return SimpleNamespace(
                id="resp_1",
                output=[
                    SimpleNamespace(
                        type="function_call",
                        id="fc_1",
                        call_id="call_1",
                        name="refund_payment",
                        arguments=json.dumps({"order_id": "ord_1", "amount": 120.0}),
                        status="completed",
                    )
                ],
                output_text="",
            )
        return SimpleNamespace(
            id="resp_2",
            output=[
                SimpleNamespace(
                    type="message",
                    id="msg_1",
                    role="assistant",
                    status="completed",
                    content=[SimpleNamespace(type="output_text", text="Done")],
                )
            ],
            output_text="Done",
        )

    def stream(self, **kwargs):
        return FakeStream(self, kwargs)


class FakeOpenAIClient:
    def __init__(self) -> None:
        self.responses = FakeResponses()


class FakeStream:
    def __init__(self, responses: FakeResponses, kwargs) -> None:
        self._responses = responses
        self._kwargs = kwargs
        self._final = None

    def __enter__(self):
        self._final = self._responses.create(**self._kwargs)
        events = []
        has_function_call = any(
            getattr(item, "type", None) == "function_call"
            for item in (getattr(self._final, "output", None) or [])
        )
        if not has_function_call:
            text = getattr(self._final, "output_text", "") or "Done"
            events.append(SimpleNamespace(type="response.output_text.delta", delta=text, response_id=self._final.id))
        self._events = iter(events)
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def __iter__(self):
        return self

    def __next__(self):
        return next(self._events)

    def get_final_response(self):
        return self._final


class FakeOutcomes:
    def __init__(self) -> None:
        self.reported = []

    def report(self, **kwargs):
        self.reported.append(kwargs)
        return {"ok": True}


class FakeActions:
    def __init__(self) -> None:
        self.memory_payloads = []

    def submit(self, **kwargs):
        return {"allowed": True, "result": "allowed", "reason": "ok", "request_id": "req_sync_1", "echo": kwargs}

    def submit_payload(self, **kwargs):
        return {"allowed": True, "result": "allowed", "reason": "ok-payload", "request_id": "req_sync_payload", "echo": kwargs}

    def ingest_memory(self, **kwargs):
        self.memory_payloads.append(kwargs)
        return {"accepted": len(kwargs.get("events", []))}


class FakeBighubClient:
    def __init__(self) -> None:
        self.actions = FakeActions()
        self.outcomes = FakeOutcomes()
        self.approvals = SimpleNamespace(
            resolve=lambda request_id, resolution, comment=None: {
                "request_id": request_id,
                "status": "approved",
                "resolution": resolution,
            }
        )

    def close(self):
        return None


class FakeAsyncResponses:
    def __init__(self) -> None:
        self.calls = 0
        self.last_kwargs: dict = {}

    async def create(self, **kwargs):
        self.calls += 1
        self.last_kwargs = kwargs
        if self.calls == 1:
            return SimpleNamespace(
                id="resp_1",
                output=[
                    SimpleNamespace(
                        type="function_call",
                        id="fc_1",
                        call_id="call_1",
                        name="refund_payment",
                        arguments=json.dumps({"order_id": "ord_1", "amount": 120.0}),
                        status="completed",
                    )
                ],
                output_text="",
            )
        return SimpleNamespace(
            id="resp_2",
            output=[
                SimpleNamespace(
                    type="message",
                    id="msg_1",
                    role="assistant",
                    status="completed",
                    content=[SimpleNamespace(type="output_text", text="Done")],
                )
            ],
            output_text="Done",
        )

    def stream(self, **kwargs):
        return FakeAsyncStream(self, kwargs)


class FakeAsyncOpenAIClient:
    def __init__(self) -> None:
        self.responses = FakeAsyncResponses()


class FakeAsyncStream:
    def __init__(self, responses: FakeAsyncResponses, kwargs) -> None:
        self._responses = responses
        self._kwargs = kwargs
        self._final = None
        self._events: list = []
        self._idx = 0

    async def __aenter__(self):
        self._final = await self._responses.create(**self._kwargs)
        has_function_call = any(
            getattr(item, "type", None) == "function_call"
            for item in (getattr(self._final, "output", None) or [])
        )
        if not has_function_call:
            text = getattr(self._final, "output_text", "") or "Done"
            self._events = [SimpleNamespace(type="response.output_text.delta", delta=text, response_id=self._final.id)]
        else:
            self._events = []
        self._idx = 0
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self._idx >= len(self._events):
            raise StopAsyncIteration
        event = self._events[self._idx]
        self._idx += 1
        return event

    async def get_final_response(self):
        return self._final


class FakeAsyncOutcomes:
    def __init__(self) -> None:
        self.reported = []

    async def report(self, **kwargs):
        self.reported.append(kwargs)
        return {"ok": True}


class FakeAsyncActions:
    def __init__(self) -> None:
        self.memory_payloads = []

    async def submit(self, **kwargs):
        return {"allowed": True, "result": "allowed", "reason": "ok", "request_id": "req_async_1", "echo": kwargs}

    async def submit_payload(self, **kwargs):
        return {"allowed": True, "result": "allowed", "reason": "ok-payload", "request_id": "req_async_payload", "echo": kwargs}

    async def ingest_memory(self, **kwargs):
        self.memory_payloads.append(kwargs)
        return {"accepted": len(kwargs.get("events", []))}


class FakeAsyncBighubClient:
    def __init__(self) -> None:
        self.actions = FakeAsyncActions()
        self.outcomes = FakeAsyncOutcomes()
        self.approvals = SimpleNamespace(resolve=self._resolve)

    async def _resolve(self, request_id, resolution, comment=None):
        return {
            "request_id": request_id,
            "status": "approved",
            "resolution": resolution,
        }

    async def close(self):
        return None


def _make_transient_error() -> Exception:
    if _RetryableError is not None:
        return _RetryableError(request=SimpleNamespace(method="POST", url="https://api.openai.com/v1/responses"))
    return RuntimeError("transient provider failure")


class FlakyResponses:
    def __init__(self, fail_times: int) -> None:
        self.calls = 0
        self.fail_times = fail_times

    def create(self, **kwargs):
        self.calls += 1
        if self.calls <= self.fail_times:
            raise _make_transient_error()
        return SimpleNamespace(id="resp_ok", output=[], output_text="Done")


class FlakyOpenAIClient:
    def __init__(self, fail_times: int) -> None:
        self.responses = FlakyResponses(fail_times=fail_times)


class AsyncFlakyResponses:
    def __init__(self, fail_times: int) -> None:
        self.calls = 0
        self.fail_times = fail_times

    async def create(self, **kwargs):
        self.calls += 1
        if self.calls <= self.fail_times:
            raise _make_transient_error()
        return SimpleNamespace(id="resp_ok", output=[], output_text="Done")


class AsyncFlakyOpenAIClient:
    def __init__(self, fail_times: int) -> None:
        self.responses = AsyncFlakyResponses(fail_times=fail_times)


class ApprovalRequiredActions:
    def submit(self, **kwargs):
        return {
            "allowed": False,
            "result": "requires_approval",
            "reason": "approval required",
            "request_id": "req_1",
        }

    def ingest_memory(self, **kwargs):
        return {"accepted": len(kwargs.get("events", []))}


class ApprovalRequiredBighubClient:
    def __init__(self) -> None:
        self.actions = ApprovalRequiredActions()
        self.outcomes = FakeOutcomes()
        self.approvals = SimpleNamespace(
            resolve=lambda request_id, resolution, comment=None: {
                "request_id": request_id,
                "status": "approved",
                "resolution": resolution,
            }
        )

    def close(self):
        return None


class AsyncApprovalRequiredActions:
    async def submit(self, **kwargs):
        return {
            "allowed": False,
            "result": "requires_approval",
            "reason": "approval required",
            "request_id": "req_1",
        }

    async def ingest_memory(self, **kwargs):
        return {"accepted": len(kwargs.get("events", []))}


class AsyncApprovalRequiredBighubClient:
    def __init__(self) -> None:
        self.actions = AsyncApprovalRequiredActions()
        self.outcomes = FakeAsyncOutcomes()
        self.approvals = SimpleNamespace(resolve=self._resolve)

    async def _resolve(self, request_id, resolution, comment=None):
        return {
            "request_id": request_id,
            "status": "approved",
            "resolution": resolution,
        }

    async def close(self):
        return None


def test_guarded_openai_executes_tool_when_allowed() -> None:
    executed = {"called": False}

    def refund_payment(order_id: str, amount: float):
        executed["called"] = True
        return {"order_id": order_id, "amount": amount, "ok": True}

    guard = BighubOpenAI(
        bighub_api_key="bhk_test",
        actor="AI_AGENT_001",
        domain="payments",
        openai_client=FakeOpenAIClient(),
        bighub_client=FakeBighubClient(),
    )
    guard.register_tool(
        name="refund_payment",
        fn=refund_payment,
        description="Refund payment",
        parameters_schema={
            "type": "object",
            "properties": {
                "order_id": {"type": "string"},
                "amount": {"type": "number"},
            },
            "required": ["order_id", "amount"],
            "additionalProperties": False,
        },
        value_from_args=lambda a: float(a["amount"]),
        target_from_args=lambda a: a["order_id"],
    )

    result = guard.run(
        messages=[{"role": "user", "content": "refund order ord_1 for 120"}],
        model="gpt-4.1",
    )

    assert executed["called"] is True
    assert result["output_text"] == "Done"
    assert result["execution"]["last"]["status"] == "executed"
    assert result["execution"]["last"]["tool"] == "refund_payment"


def test_guarded_openai_blocks_when_policy_denies() -> None:
    class BlockingActions:
        def submit(self, **kwargs):
            return {"allowed": False, "result": "blocked", "reason": "Too risky"}

    class BlockingBighubClient:
        def __init__(self) -> None:
            self.actions = BlockingActions()
            self.outcomes = FakeOutcomes()

        def close(self):
            return None

    executed = {"called": False}

    def refund_payment(order_id: str, amount: float):
        executed["called"] = True
        return {"ok": True}

    guard = BighubOpenAI(
        bighub_api_key="bhk_test",
        actor="AI_AGENT_001",
        domain="payments",
        openai_client=FakeOpenAIClient(),
        bighub_client=BlockingBighubClient(),
    )
    guard.tool(
        "refund_payment",
        refund_payment,
        description="Refund payment",
        parameters_schema={
            "type": "object",
            "properties": {
                "order_id": {"type": "string"},
                "amount": {"type": "number"},
            },
            "required": ["order_id", "amount"],
            "additionalProperties": False,
        },
        value_from_args=lambda a: float(a["amount"]),
    )
    guard.run(messages=[{"role": "user", "content": "refund"}], model="gpt-4.1")
    assert executed["called"] is False


def test_guarded_openai_supports_submit_payload_mode() -> None:
    executed = {"called": False}

    def refund_payment(order_id: str, amount: float):
        executed["called"] = True
        return {"ok": True}

    guard = BighubOpenAI(
        bighub_api_key="bhk_test",
        actor="AI_AGENT_001",
        domain="payments",
        decision_mode="submit_payload",
        openai_client=FakeOpenAIClient(),
        bighub_client=FakeBighubClient(),
    )
    guard.tool(
        "refund_payment",
        refund_payment,
        value_from_args=lambda a: float(a["amount"]),
    )
    result = guard.run(messages=[{"role": "user", "content": "refund"}], model="gpt-4.1")
    assert executed["called"] is True
    assert result["output_text"] == "Done"


def test_guarded_openai_inferrs_parameters_schema() -> None:
    def refund_payment(order_id: str, amount: float):
        return {"ok": True}

    guard = BighubOpenAI(
        bighub_api_key="bhk_test",
        actor="AI_AGENT_001",
        domain="payments",
        openai_client=FakeOpenAIClient(),
        bighub_client=FakeBighubClient(),
    )
    guard.tool("refund_payment", refund_payment, value_from_args=lambda a: float(a["amount"]))
    tools = guard._openai_tools()
    assert tools[0]["parameters"]["type"] == "object"
    assert "order_id" in tools[0]["parameters"]["properties"]


def test_check_tool_silent_mode_returns_decision_only() -> None:
    guard = BighubOpenAI(
        bighub_api_key="bhk_test",
        actor="AI_AGENT_001",
        domain="payments",
        openai_client=FakeOpenAIClient(),
        bighub_client=FakeBighubClient(),
    )
    guard.tool(
        "refund_payment",
        lambda order_id, amount: {"ok": True},
        value_from_args=lambda a: float(a["amount"]),
    )
    decision = guard.check_tool("refund_payment", {"order_id": "ord_1", "amount": 120.0})
    assert decision["allowed"] is True


def test_on_decision_hook_is_called() -> None:
    events = []

    guard = BighubOpenAI(
        bighub_api_key="bhk_test",
        actor="AI_AGENT_001",
        domain="payments",
        openai_client=FakeOpenAIClient(),
        bighub_client=FakeBighubClient(),
        on_decision=lambda d: events.append(d),
    )
    guard.tool(
        "refund_payment",
        lambda order_id, amount: {"ok": True},
        value_from_args=lambda a: float(a["amount"]),
    )
    guard.run(messages=[{"role": "user", "content": "refund"}], model="gpt-4.1")
    assert len(events) == 1
    assert events[0]["tool"] == "refund_payment"
    assert isinstance(events[0].get("event_id"), str)
    assert isinstance(events[0].get("trace_id"), str)
    assert "request_id" in events[0]


def test_guarded_openai_alias_points_to_bighub() -> None:
    assert GuardedOpenAI is BighubOpenAI


def test_guarded_openai_persists_decision_memory_events() -> None:
    fake_bighub = FakeBighubClient()
    guard = BighubOpenAI(
        bighub_api_key="bhk_test",
        actor="AI_AGENT_001",
        domain="payments",
        openai_client=FakeOpenAIClient(),
        bighub_client=fake_bighub,
        memory_enabled=True,
    )
    guard.tool(
        "refund_payment",
        lambda order_id, amount: {"ok": True},
        value_from_args=lambda a: float(a["amount"]),
    )
    guard.run(messages=[{"role": "user", "content": "refund"}], model="gpt-4.1")
    assert len(fake_bighub.actions.memory_payloads) == 1
    assert fake_bighub.actions.memory_payloads[0]["source"] == "openai_adapter"


def test_outcome_reporting_after_tool_execution() -> None:
    fake_bighub = FakeBighubClient()
    guard = BighubOpenAI(
        bighub_api_key="bhk_test",
        actor="AI_AGENT_001",
        domain="payments",
        openai_client=FakeOpenAIClient(),
        bighub_client=fake_bighub,
        outcome_reporting=True,
    )
    guard.tool(
        "refund_payment",
        lambda order_id, amount: {"ok": True},
        value_from_args=lambda a: float(a["amount"]),
    )
    guard.run(messages=[{"role": "user", "content": "refund"}], model="gpt-4.1")
    assert len(fake_bighub.outcomes.reported) == 1
    assert fake_bighub.outcomes.reported[0]["status"] == "SUCCESS"
    assert fake_bighub.outcomes.reported[0]["request_id"] == "req_sync_1"


def test_outcome_reporting_maps_tool_error_to_failure() -> None:
    fake_bighub = FakeBighubClient()

    def refund_payment(order_id: str, amount: float):
        raise RuntimeError("tool exploded")

    guard = BighubOpenAI(
        bighub_api_key="bhk_test",
        actor="AI_AGENT_001",
        domain="payments",
        openai_client=FakeOpenAIClient(),
        bighub_client=fake_bighub,
        outcome_reporting=True,
    )
    guard.tool(
        "refund_payment",
        refund_payment,
        value_from_args=lambda a: float(a["amount"]),
    )
    result = guard.run(messages=[{"role": "user", "content": "refund"}], model="gpt-4.1")
    assert result["execution"]["last"]["status"] == "tool_error"
    assert len(fake_bighub.outcomes.reported) == 1
    assert fake_bighub.outcomes.reported[0]["status"] == "FAILURE"
    assert fake_bighub.outcomes.reported[0]["request_id"] == "req_sync_1"


def test_outcome_reporting_disabled() -> None:
    fake_bighub = FakeBighubClient()
    guard = BighubOpenAI(
        bighub_api_key="bhk_test",
        actor="AI_AGENT_001",
        domain="payments",
        openai_client=FakeOpenAIClient(),
        bighub_client=fake_bighub,
        outcome_reporting=False,
    )
    guard.tool(
        "refund_payment",
        lambda order_id, amount: {"ok": True},
        value_from_args=lambda a: float(a["amount"]),
    )
    guard.run(messages=[{"role": "user", "content": "refund"}], model="gpt-4.1")
    assert len(fake_bighub.outcomes.reported) == 0


def test_async_outcome_reporting() -> None:
    async def _run() -> None:
        fake_bighub = FakeAsyncBighubClient()
        guard = AsyncBighubOpenAI(
            bighub_api_key="bhk_test",
            actor="AI_AGENT_001",
            domain="payments",
            openai_client=FakeAsyncOpenAIClient(),
            bighub_client=fake_bighub,
            outcome_reporting=True,
        )
        guard.tool(
            "refund_payment",
            lambda order_id, amount: {"ok": True},
            value_from_args=lambda a: float(a["amount"]),
        )
        await guard.run(
            messages=[{"role": "user", "content": "refund"}],
            model="gpt-4.1",
        )
        assert len(fake_bighub.outcomes.reported) == 1
        assert fake_bighub.outcomes.reported[0]["status"] == "SUCCESS"
        await guard.close()

    asyncio.run(_run())


def test_async_outcome_reporting_maps_tool_error_to_failure() -> None:
    async def _run() -> None:
        fake_bighub = FakeAsyncBighubClient()

        async def refund_payment(order_id: str, amount: float):
            raise RuntimeError("tool exploded")

        guard = AsyncBighubOpenAI(
            bighub_api_key="bhk_test",
            actor="AI_AGENT_001",
            domain="payments",
            openai_client=FakeAsyncOpenAIClient(),
            bighub_client=fake_bighub,
            outcome_reporting=True,
        )
        guard.tool(
            "refund_payment",
            refund_payment,
            value_from_args=lambda a: float(a["amount"]),
        )
        result = await guard.run(
            messages=[{"role": "user", "content": "refund"}],
            model="gpt-4.1",
        )
        assert result["execution"]["last"]["status"] == "tool_error"
        assert len(fake_bighub.outcomes.reported) == 1
        assert fake_bighub.outcomes.reported[0]["status"] == "FAILURE"
        await guard.close()

    asyncio.run(_run())


def test_async_guarded_openai_executes_tool_when_allowed() -> None:
    async def _run() -> None:
        executed = {"called": False}

        async def refund_payment(order_id: str, amount: float):
            executed["called"] = True
            return {"order_id": order_id, "amount": amount, "ok": True}

        guard = AsyncBighubOpenAI(
            bighub_api_key="bhk_test",
            actor="AI_AGENT_001",
            domain="payments",
            openai_client=FakeAsyncOpenAIClient(),
            bighub_client=FakeAsyncBighubClient(),
        )
        guard.tool(
            "refund_payment",
            refund_payment,
            value_from_args=lambda a: float(a["amount"]),
        )

        result = await guard.run(
            messages=[{"role": "user", "content": "refund order ord_1 for 120"}],
            model="gpt-4.1",
        )
        assert executed["called"] is True
        assert result["output_text"] == "Done"
        assert result["execution"]["last"]["status"] == "executed"
        await guard.close()

    asyncio.run(_run())


def test_async_check_tool_silent_mode_returns_decision_only() -> None:
    async def _run() -> None:
        guard = AsyncBighubOpenAI(
            bighub_api_key="bhk_test",
            actor="AI_AGENT_001",
            domain="payments",
            openai_client=FakeAsyncOpenAIClient(),
            bighub_client=FakeAsyncBighubClient(),
        )
        guard.tool(
            "refund_payment",
            lambda order_id, amount: {"ok": True},
            value_from_args=lambda a: float(a["amount"]),
        )
        decision = await guard.check_tool("refund_payment", {"order_id": "ord_1", "amount": 120.0})
        assert decision["allowed"] is True
        await guard.close()

    asyncio.run(_run())


def test_async_guarded_openai_alias_points_to_async_bighub() -> None:
    assert AsyncGuardedOpenAI is AsyncBighubOpenAI


def test_guarded_openai_run_stream_emits_events() -> None:
    guard = BighubOpenAI(
        bighub_api_key="bhk_test",
        actor="AI_AGENT_001",
        domain="payments",
        openai_client=FakeOpenAIClient(),
        bighub_client=FakeBighubClient(),
    )
    guard.tool(
        "refund_payment",
        lambda order_id, amount: {"ok": True},
        value_from_args=lambda a: float(a["amount"]),
    )
    events = list(guard.run_stream(messages=[{"role": "user", "content": "refund"}], model="gpt-4.1"))
    event_types = [e["type"] for e in events]
    assert "execution_event" in event_types
    assert "llm_delta" in event_types
    assert event_types[-1] == "final_response"
    execution_event = next(e for e in events if e["type"] == "execution_event")["event"]
    assert isinstance(execution_event.get("event_id"), str)
    assert isinstance(execution_event.get("trace_id"), str)
    assert "request_id" in execution_event


def test_async_guarded_openai_run_stream_emits_events() -> None:
    async def _run() -> None:
        guard = AsyncBighubOpenAI(
            bighub_api_key="bhk_test",
            actor="AI_AGENT_001",
            domain="payments",
            openai_client=FakeAsyncOpenAIClient(),
            bighub_client=FakeAsyncBighubClient(),
        )
        guard.tool(
            "refund_payment",
            lambda order_id, amount: {"ok": True},
            value_from_args=lambda a: float(a["amount"]),
        )
        events = []
        async for event in guard.run_stream(messages=[{"role": "user", "content": "refund"}], model="gpt-4.1"):
            events.append(event)
        event_types = [e["type"] for e in events]
        assert "execution_event" in event_types
        assert "llm_delta" in event_types
        assert event_types[-1] == "final_response"
        execution_event = next(e for e in events if e["type"] == "execution_event")["event"]
        assert isinstance(execution_event.get("event_id"), str)
        assert isinstance(execution_event.get("trace_id"), str)
        assert "request_id" in execution_event
        await guard.close()

    asyncio.run(_run())


def test_run_with_approval_resumes_tool_after_resolution() -> None:
    executed = {"called": False}

    def refund_payment(order_id: str, amount: float):
        executed["called"] = True
        return {"ok": True, "order_id": order_id, "amount": amount}

    guard = BighubOpenAI(
        bighub_api_key="bhk_test",
        actor="AI_AGENT_001",
        domain="payments",
        openai_client=FakeOpenAIClient(),
        bighub_client=ApprovalRequiredBighubClient(),
    )
    guard.tool("refund_payment", refund_payment, value_from_args=lambda a: float(a["amount"]))

    result = guard.run_with_approval(
        messages=[{"role": "user", "content": "refund"}],
        model="gpt-4.1",
        on_approval_required=lambda ctx: {"resolution": "approved", "comment": "approved by operator"},
    )

    assert result["approval_loop"]["required"] is True
    assert result["approval_loop"]["resolved"] is True
    assert result["approval_loop"]["resumed"] is True
    assert executed["called"] is True


def test_async_run_with_approval_resumes_tool_after_resolution() -> None:
    async def _run() -> None:
        executed = {"called": False}

        async def refund_payment(order_id: str, amount: float):
            executed["called"] = True
            return {"ok": True, "order_id": order_id, "amount": amount}

        guard = AsyncBighubOpenAI(
            bighub_api_key="bhk_test",
            actor="AI_AGENT_001",
            domain="payments",
            openai_client=FakeAsyncOpenAIClient(),
            bighub_client=AsyncApprovalRequiredBighubClient(),
        )
        guard.tool("refund_payment", refund_payment, value_from_args=lambda a: float(a["amount"]))

        result = await guard.run_with_approval(
            messages=[{"role": "user", "content": "refund"}],
            model="gpt-4.1",
            on_approval_required=lambda ctx: {"resolution": "approved", "comment": "approved by operator"},
        )

        assert result["approval_loop"]["required"] is True
        assert result["approval_loop"]["resolved"] is True
        assert result["approval_loop"]["resumed"] is True
        assert executed["called"] is True
        await guard.close()

    asyncio.run(_run())


def test_provider_retry_recovers_transient_failure_sync() -> None:
    guard = BighubOpenAI(
        bighub_api_key="bhk_test",
        actor="AI_AGENT_001",
        domain="payments",
        openai_client=FlakyOpenAIClient(fail_times=1),
        bighub_client=FakeBighubClient(),
        provider_max_retries=2,
        provider_retry_backoff_seconds=0.0,
        provider_retry_jitter_seconds=0.0,
    )
    guard.tool("refund_payment", lambda order_id, amount: {"ok": True}, value_from_args=lambda a: float(a["amount"]))
    result = guard.run(messages=[{"role": "user", "content": "refund"}], model="gpt-4.1")
    assert result["output_text"] == "Done"


def test_provider_circuit_breaker_opens_sync() -> None:
    openai_client = FlakyOpenAIClient(fail_times=10)
    guard = BighubOpenAI(
        bighub_api_key="bhk_test",
        actor="AI_AGENT_001",
        domain="payments",
        openai_client=openai_client,
        bighub_client=FakeBighubClient(),
        provider_max_retries=0,
        provider_retry_backoff_seconds=0.0,
        provider_retry_jitter_seconds=0.0,
        provider_circuit_breaker_failures=1,
        provider_circuit_breaker_reset_seconds=60.0,
    )
    guard.tool("refund_payment", lambda order_id, amount: {"ok": True}, value_from_args=lambda a: float(a["amount"]))
    try:
        guard.run(messages=[{"role": "user", "content": "refund"}], model="gpt-4.1")
    except Exception:
        pass
    first_calls = openai_client.responses.calls
    try:
        guard.run(messages=[{"role": "user", "content": "refund"}], model="gpt-4.1")
    except Exception:
        pass
    assert openai_client.responses.calls == first_calls


def test_provider_retry_recovers_transient_failure_async() -> None:
    async def _run() -> None:
        guard = AsyncBighubOpenAI(
            bighub_api_key="bhk_test",
            actor="AI_AGENT_001",
            domain="payments",
            openai_client=AsyncFlakyOpenAIClient(fail_times=1),
            bighub_client=FakeAsyncBighubClient(),
            provider_max_retries=2,
            provider_retry_backoff_seconds=0.0,
            provider_retry_jitter_seconds=0.0,
        )
        guard.tool("refund_payment", lambda order_id, amount: {"ok": True}, value_from_args=lambda a: float(a["amount"]))
        result = await guard.run(messages=[{"role": "user", "content": "refund"}], model="gpt-4.1")
        assert result["output_text"] == "Done"
        await guard.close()

    asyncio.run(_run())


def test_serialize_response_falls_back_to_content_text_when_output_text_missing() -> None:
    response = SimpleNamespace(
        id="resp_fallback",
        output_text=None,
        output=[
            SimpleNamespace(
                type="message",
                content=[
                    {"type": "output_text", "text": "Hello"},
                    {"type": "output_text", "text": " world"},
                ],
            )
        ],
    )
    serialized = BighubOpenAI._serialize_response(response)
    assert serialized["output_text"] == "Hello world"


def test_store_false_is_sent_to_provider() -> None:
    """Verify that store=False is automatically injected into provider create calls."""
    fake_openai = FakeOpenAIClient()
    guard = BighubOpenAI(
        bighub_api_key="bhk_test",
        actor="AI_AGENT_001",
        domain="payments",
        openai_client=fake_openai,
        bighub_client=FakeBighubClient(),
    )
    guard.tool(
        "refund_payment",
        lambda order_id, amount: {"ok": True},
        value_from_args=lambda a: float(a["amount"]),
    )
    guard.run(messages=[{"role": "user", "content": "refund"}], model="gpt-4.1")
    assert fake_openai.responses.last_kwargs.get("store") is False


def test_store_can_be_overridden_via_extra_create_args() -> None:
    """User can explicitly set store=True via extra_create_args."""

    class SingleShotResponses:
        def __init__(self) -> None:
            self.last_kwargs: dict = {}

        def create(self, **kwargs):
            self.last_kwargs = kwargs
            return SimpleNamespace(
                id="resp_1",
                output=[
                    SimpleNamespace(
                        type="message", id="msg_1", role="assistant",
                        status="completed",
                        content=[SimpleNamespace(type="output_text", text="Hi")],
                    )
                ],
                output_text="Hi",
            )

    class SingleShotOpenAI:
        def __init__(self) -> None:
            self.responses = SingleShotResponses()

    fake_openai = SingleShotOpenAI()
    guard = BighubOpenAI(
        bighub_api_key="bhk_test",
        actor="AI_AGENT_001",
        domain="payments",
        openai_client=fake_openai,
        bighub_client=FakeBighubClient(),
    )
    guard.tool(
        "refund_payment",
        lambda order_id, amount: {"ok": True},
        value_from_args=lambda a: float(a["amount"]),
    )
    guard.run(
        messages=[{"role": "user", "content": "just say hi"}],
        model="gpt-4.1",
        extra_create_args={"store": True},
    )
    assert fake_openai.responses.last_kwargs.get("store") is True


def test_extract_function_calls_ignores_reasoning_and_message_items() -> None:
    """Reasoning items and message items in output must not break function call extraction."""
    guard = BighubOpenAI(
        bighub_api_key="bhk_test",
        actor="AI_AGENT_001",
        domain="test",
        openai_client=FakeOpenAIClient(),
        bighub_client=FakeBighubClient(),
    )
    response = SimpleNamespace(
        id="resp_mixed",
        output=[
            SimpleNamespace(type="reasoning", id="r_1", summary=[{"type": "summary_text", "text": "thinking..."}]),
            SimpleNamespace(
                type="function_call",
                id="fc_1",
                call_id="call_1",
                name="refund_payment",
                arguments='{"order_id":"ord_1","amount":50}',
                status="completed",
            ),
            SimpleNamespace(
                type="message",
                id="msg_1",
                role="assistant",
                status="completed",
                content=[SimpleNamespace(type="output_text", text="Here you go")],
            ),
        ],
        output_text="Here you go",
    )
    calls = guard._extract_function_calls(response)
    assert len(calls) == 1
    assert calls[0]["name"] == "refund_payment"
    assert calls[0]["call_id"] == "call_1"


def test_parse_stream_event_handles_all_event_types() -> None:
    """Verify _parse_stream_event correctly maps all Responses API stream event types."""
    guard = BighubOpenAI(
        bighub_api_key="bhk_test",
        actor="AI_AGENT_001",
        domain="payments",
        openai_client=FakeOpenAIClient(),
        bighub_client=FakeBighubClient(),
    )
    guard.tool("x", lambda: None, value_from_args=lambda a: 0.0)

    delta_evt = guard._parse_stream_event(
        SimpleNamespace(type="response.output_text.delta", delta="hello", response_id="r1")
    )
    assert delta_evt["type"] == "llm_delta"
    assert delta_evt["delta"] == "hello"

    done_text_evt = guard._parse_stream_event(
        SimpleNamespace(type="response.output_text.done", text="full text", response_id="r1")
    )
    assert done_text_evt["type"] == "llm_text_done"
    assert done_text_evt["text"] == "full text"

    item_added_evt = guard._parse_stream_event(
        SimpleNamespace(
            type="response.output_item.added",
            item=SimpleNamespace(type="function_call"),
            output_index=0,
            response_id="r1",
        )
    )
    assert item_added_evt["type"] == "output_item_added"
    assert item_added_evt["item_type"] == "function_call"

    args_delta_evt = guard._parse_stream_event(
        SimpleNamespace(
            type="response.function_call_arguments.delta",
            delta='{"ord',
            call_id="c1",
            output_index=0,
            response_id="r1",
        )
    )
    assert args_delta_evt["type"] == "function_call_args_delta"
    assert args_delta_evt["delta"] == '{"ord'

    args_done_evt = guard._parse_stream_event(
        SimpleNamespace(
            type="response.function_call_arguments.done",
            arguments='{"order_id":"o1"}',
            call_id="c1",
            name="refund",
            output_index=0,
            response_id="r1",
        )
    )
    assert args_done_evt["type"] == "function_call_args_done"
    assert args_done_evt["arguments"] == '{"order_id":"o1"}'

    refusal_evt = guard._parse_stream_event(
        SimpleNamespace(type="response.refusal.delta", delta="I cannot", response_id="r1")
    )
    assert refusal_evt["type"] == "refusal_delta"

    done_evt = guard._parse_stream_event(SimpleNamespace(type="response.completed", response_id="r1"))
    assert done_evt["type"] == "response_done"

    failed_evt = guard._parse_stream_event(
        SimpleNamespace(type="response.failed", error={"code": "rate_limit"}, response_id="r1")
    )
    assert failed_evt["type"] == "response_failed"

    unknown = guard._parse_stream_event(SimpleNamespace(type="response.unknown_event", response_id="r1"))
    assert unknown is None


def test_continuation_passes_previous_response_id_and_instructions() -> None:
    """Multi-turn loop should forward previous_response_id and instructions."""
    call_log: list[dict] = []

    class TrackingResponses:
        def __init__(self) -> None:
            self.calls = 0

        def create(self, **kwargs):
            self.calls += 1
            call_log.append(kwargs)
            if self.calls == 1:
                return SimpleNamespace(
                    id="resp_1",
                    output=[
                        SimpleNamespace(
                            type="function_call",
                            id="fc_1",
                            call_id="call_1",
                            name="do_thing",
                            arguments='{"value": 1}',
                            status="completed",
                        )
                    ],
                    output_text="",
                )
            return SimpleNamespace(
                id="resp_2",
                output=[
                    SimpleNamespace(
                        type="message",
                        id="msg_1",
                        role="assistant",
                        status="completed",
                        content=[SimpleNamespace(type="output_text", text="OK")],
                    )
                ],
                output_text="OK",
            )

    class TrackingOpenAI:
        def __init__(self) -> None:
            self.responses = TrackingResponses()

    guard = BighubOpenAI(
        bighub_api_key="bhk_test",
        actor="AI_AGENT_001",
        domain="test",
        openai_client=TrackingOpenAI(),
        bighub_client=FakeBighubClient(),
    )
    guard.tool("do_thing", lambda value: {"ok": True}, value_from_args=lambda a: float(a["value"]))

    guard.run(
        messages=[{"role": "user", "content": "do it"}],
        model="gpt-4.1",
        instructions="Be careful",
    )

    assert len(call_log) == 2
    second_call = call_log[1]
    assert second_call.get("previous_response_id") == "resp_1"
    assert second_call.get("instructions") == "Be careful"
    assert second_call.get("store") is False


def test_non_retryable_error_fails_immediately() -> None:
    """Non-retryable errors should raise immediately without retries."""

    class NonRetryableResponses:
        def __init__(self) -> None:
            self.calls = 0

        def create(self, **kwargs):
            self.calls += 1
            raise ValueError("bad request - not retryable")

    class NonRetryableOpenAI:
        def __init__(self) -> None:
            self.responses = NonRetryableResponses()

    openai_client = NonRetryableOpenAI()
    guard = BighubOpenAI(
        bighub_api_key="bhk_test",
        actor="AI_AGENT_001",
        domain="test",
        openai_client=openai_client,
        bighub_client=FakeBighubClient(),
        provider_max_retries=3,
        provider_retry_backoff_seconds=0.0,
    )
    guard.tool("do_thing", lambda value: {"ok": True}, value_from_args=lambda a: float(a["value"]))

    try:
        guard.run(messages=[{"role": "user", "content": "do it"}], model="gpt-4.1")
        assert False, "Should have raised"
    except Exception:
        pass

    if _RetryableError is not None:
        assert openai_client.responses.calls == 1, "Non-retryable error should not trigger retries"


def test_openai_tools_matches_responses_api_schema() -> None:
    """Tools produced by _openai_tools must match the Responses API schema (no function wrapper)."""
    guard = BighubOpenAI(
        bighub_api_key="bhk_test",
        actor="AI_AGENT_001",
        domain="test",
        openai_client=FakeOpenAIClient(),
        bighub_client=FakeBighubClient(),
    )
    guard.tool(
        "get_weather",
        lambda location, units="celsius": {"temp": 25},
        description="Get current weather",
        parameters_schema={
            "type": "object",
            "properties": {
                "location": {"type": "string"},
                "units": {"type": "string", "enum": ["celsius", "fahrenheit"]},
            },
            "required": ["location", "units"],
            "additionalProperties": False,
        },
        value_from_args=lambda a: 0.0,
        strict=True,
    )
    tools = guard._openai_tools()
    assert len(tools) == 1
    t = tools[0]
    assert t["type"] == "function"
    assert t["name"] == "get_weather"
    assert t["description"] == "Get current weather"
    assert t["strict"] is True
    assert t["parameters"]["type"] == "object"
    assert "function" not in t, "Responses API uses flat tool schema, not nested function wrapper"


def test_function_call_output_format_matches_responses_api() -> None:
    """function_call_output dict must have type, call_id, and JSON-string output."""
    result = BighubOpenAI._function_output(
        call_id="call_abc",
        output={"status": "executed", "data": 42},
    )
    assert result["type"] == "function_call_output"
    assert result["call_id"] == "call_abc"
    parsed = json.loads(result["output"])
    assert parsed["status"] == "executed"
    assert parsed["data"] == 42


# ---------------------------------------------------------------------------
# Structured recommendation / trajectory tests
# ---------------------------------------------------------------------------


class StructuredRecommendationActions:
    """Simulates a backend returning the new structured recommendation format."""

    def __init__(self, recommendation: str = "proceed", enforcement_mode: str = "advisory") -> None:
        self._recommendation = recommendation
        self._enforcement_mode = enforcement_mode
        self.memory_payloads: list = []
        self.last_submit_kwargs: dict = {}

    def submit(self, **kwargs):
        self.last_submit_kwargs = kwargs
        base = {
            "allowed": self._recommendation in ("proceed", "proceed_with_caution"),
            "result": "allowed" if self._recommendation in ("proceed", "proceed_with_caution") else "blocked",
            "recommendation": self._recommendation,
            "recommendation_confidence": "high",
            "risk_score": 0.15 if self._recommendation == "proceed" else 0.85,
            "enforcement_mode": self._enforcement_mode,
            "request_id": "req_v2_1",
            "intelligence": {
                "trajectory_health": "healthy",
                "trajectory_id": "traj_abc123",
                "projected_regret": 0.05,
            },
            "decision_intelligence": {
                "rationale": "Low risk action within normal parameters",
                "alternatives": [],
            },
        }
        if self._recommendation == "do_not_proceed":
            base["allowed"] = False
            base["result"] = "blocked"
        elif self._recommendation == "review_recommended":
            base["allowed"] = False
            base["result"] = "requires_approval"
            base["requires_approval"] = True
        return base

    def submit_payload(self, **kwargs):
        return self.submit(**kwargs)

    def ingest_memory(self, **kwargs):
        self.memory_payloads.append(kwargs)
        return {"accepted": len(kwargs.get("events", []))}


class StructuredBighubClient:
    def __init__(self, recommendation: str = "proceed", enforcement_mode: str = "advisory") -> None:
        self.actions = StructuredRecommendationActions(recommendation, enforcement_mode)
        self.outcomes = FakeOutcomes()
        self.approvals = SimpleNamespace(
            resolve=lambda request_id, resolution, comment=None: {
                "request_id": request_id, "status": "approved", "resolution": resolution,
            }
        )

    def close(self):
        return None


def test_resolve_decision_proceed() -> None:
    assert BighubOpenAI._resolve_decision({"recommendation": "proceed"}) == "execute"
    assert BighubOpenAI._resolve_decision({"recommendation": "proceed_with_caution"}) == "execute"


def test_resolve_decision_do_not_proceed() -> None:
    assert BighubOpenAI._resolve_decision({"recommendation": "do_not_proceed"}) == "blocked"


def test_resolve_decision_review_recommended_with_approval() -> None:
    assert BighubOpenAI._resolve_decision({
        "recommendation": "review_recommended",
        "requires_approval": True,
    }) == "approval_required"


def test_resolve_decision_review_recommended_without_approval() -> None:
    assert BighubOpenAI._resolve_decision({
        "recommendation": "review_recommended",
    }) == "execute"


def test_resolve_decision_enforced_blocked() -> None:
    assert BighubOpenAI._resolve_decision({
        "enforcement_mode": "enforced",
        "enforced_verdict": "blocked",
        "recommendation": "proceed",
    }) == "blocked"


def test_resolve_decision_enforced_allowed() -> None:
    assert BighubOpenAI._resolve_decision({
        "enforcement_mode": "enforced",
        "enforced_verdict": "allowed",
    }) == "execute"


def test_resolve_decision_enforced_requires_approval() -> None:
    assert BighubOpenAI._resolve_decision({
        "enforcement_mode": "enforced",
        "enforced_verdict": "requires_approval",
    }) == "approval_required"


def test_resolve_decision_legacy_fallback() -> None:
    assert BighubOpenAI._resolve_decision({"allowed": True}) == "execute"
    assert BighubOpenAI._resolve_decision({"allowed": False, "result": "blocked"}) == "blocked"
    assert BighubOpenAI._resolve_decision({"allowed": False, "result": "requires_approval"}) == "approval_required"


def test_structured_recommendation_fields_on_tool_result() -> None:
    executed = {"called": False}

    def refund_payment(order_id: str, amount: float):
        executed["called"] = True
        return {"ok": True}

    guard = BighubOpenAI(
        bighub_api_key="bhk_test",
        actor="AI_AGENT_001",
        domain="payments",
        openai_client=FakeOpenAIClient(),
        bighub_client=StructuredBighubClient("proceed"),
    )
    guard.tool("refund_payment", refund_payment, value_from_args=lambda a: float(a["amount"]))
    result = guard.run(messages=[{"role": "user", "content": "refund"}], model="gpt-4.1")

    assert executed["called"] is True
    last = result["execution"]["last"]
    assert last["status"] == "executed"
    assert last["recommendation"] == "proceed"
    assert last["risk_score"] == 0.15
    assert last["enforcement_mode"] == "advisory"


def test_structured_recommendation_blocks_do_not_proceed() -> None:
    executed = {"called": False}

    def refund_payment(order_id: str, amount: float):
        executed["called"] = True
        return {"ok": True}

    guard = BighubOpenAI(
        bighub_api_key="bhk_test",
        actor="AI_AGENT_001",
        domain="payments",
        openai_client=FakeOpenAIClient(),
        bighub_client=StructuredBighubClient("do_not_proceed"),
    )
    guard.tool("refund_payment", refund_payment, value_from_args=lambda a: float(a["amount"]))
    result = guard.run(messages=[{"role": "user", "content": "refund"}], model="gpt-4.1")

    assert executed["called"] is False
    last = result["execution"]["last"]
    assert last["status"] == "blocked"
    assert last["recommendation"] == "do_not_proceed"


def test_session_id_injected_into_context() -> None:
    bighub = StructuredBighubClient("proceed")
    guard = BighubOpenAI(
        bighub_api_key="bhk_test",
        actor="AI_AGENT_001",
        domain="payments",
        session_id="sess_custom_42",
        openai_client=FakeOpenAIClient(),
        bighub_client=bighub,
    )
    guard.tool("refund_payment", lambda order_id, amount: {"ok": True}, value_from_args=lambda a: float(a["amount"]))
    guard.run(messages=[{"role": "user", "content": "refund"}], model="gpt-4.1")

    ctx = bighub.actions.last_submit_kwargs.get("context") or {}
    assert ctx.get("session_id") == "sess_custom_42"


def test_session_id_auto_generated_when_not_provided() -> None:
    guard = BighubOpenAI(
        bighub_api_key="bhk_test",
        actor="AI_AGENT_001",
        domain="payments",
        openai_client=FakeOpenAIClient(),
        bighub_client=StructuredBighubClient("proceed"),
    )
    assert guard.session_id is not None
    assert len(guard.session_id) > 0


def test_trajectory_id_propagated_across_calls() -> None:
    bighub = StructuredBighubClient("proceed")
    guard = BighubOpenAI(
        bighub_api_key="bhk_test",
        actor="AI_AGENT_001",
        domain="payments",
        openai_client=FakeOpenAIClient(),
        bighub_client=bighub,
    )
    guard.tool("refund_payment", lambda order_id, amount: {"ok": True}, value_from_args=lambda a: float(a["amount"]))
    guard.run(messages=[{"role": "user", "content": "refund"}], model="gpt-4.1")
    assert guard._trajectory_id == "traj_abc123"


def test_check_tool_returns_resolved_action() -> None:
    guard = BighubOpenAI(
        bighub_api_key="bhk_test",
        actor="AI_AGENT_001",
        domain="payments",
        openai_client=FakeOpenAIClient(),
        bighub_client=StructuredBighubClient("proceed"),
    )
    guard.tool("refund_payment", lambda order_id, amount: {"ok": True}, value_from_args=lambda a: float(a["amount"]))
    decision = guard.check_tool("refund_payment", {"order_id": "ord_1", "amount": 120.0})
    assert decision["_resolved_action"] == "execute"
    assert decision["recommendation"] == "proceed"
    assert decision["risk_score"] == 0.15


def test_enrich_result_extracts_trajectory_health() -> None:
    result = ToolResult(status="executed", decision={})
    BighubOpenAI._enrich_result(result, {
        "recommendation": "proceed_with_caution",
        "risk_score": 0.42,
        "enforcement_mode": "advisory",
        "intelligence": {"trajectory_health": "degrading"},
    })
    assert result.recommendation == "proceed_with_caution"
    assert result.risk_score == 0.42
    assert result.enforcement_mode == "advisory"
    assert result.trajectory_health == "degrading"


def test_fail_open_includes_recommendation_fields() -> None:
    class FailingActions:
        def submit(self, **kwargs):
            raise ConnectionError("backend down")

        def ingest_memory(self, **kwargs):
            return {"accepted": 0}

    class FailingBighubClient:
        def __init__(self) -> None:
            self.actions = FailingActions()
            self.outcomes = FakeOutcomes()

        def close(self):
            return None

    guard = BighubOpenAI(
        bighub_api_key="bhk_test",
        actor="AI_AGENT_001",
        domain="payments",
        openai_client=FakeOpenAIClient(),
        bighub_client=FailingBighubClient(),
        fail_mode="open",
    )
    guard.tool("refund_payment", lambda order_id, amount: {"ok": True}, value_from_args=lambda a: float(a["amount"]))
    result = guard.run(messages=[{"role": "user", "content": "refund"}], model="gpt-4.1")
    last = result["execution"]["last"]
    assert last["status"] == "executed"
    assert last["recommendation"] == "proceed"
    assert last["enforcement_mode"] == "advisory"


def test_fail_closed_includes_recommendation_fields() -> None:
    class FailingActions:
        def submit(self, **kwargs):
            raise ConnectionError("backend down")

        def ingest_memory(self, **kwargs):
            return {"accepted": 0}

    class FailingBighubClient:
        def __init__(self) -> None:
            self.actions = FailingActions()
            self.outcomes = FakeOutcomes()

        def close(self):
            return None

    guard = BighubOpenAI(
        bighub_api_key="bhk_test",
        actor="AI_AGENT_001",
        domain="payments",
        openai_client=FakeOpenAIClient(),
        bighub_client=FailingBighubClient(),
        fail_mode="closed",
    )
    guard.tool("refund_payment", lambda order_id, amount: {"ok": True}, value_from_args=lambda a: float(a["amount"]))
    result = guard.run(messages=[{"role": "user", "content": "refund"}], model="gpt-4.1")
    last = result["execution"]["last"]
    assert last["status"] == "blocked"
    assert last["recommendation"] == "do_not_proceed"
    assert last["enforcement_mode"] == "advisory"


# ---------------------------------------------------------------------------
# _resolve_decision — enforced mode edge cases
# ---------------------------------------------------------------------------


def test_resolve_decision_enforced_missing_verdict_blocks() -> None:
    """Enforced mode with no enforced_verdict must fail-safe to blocked."""
    assert BighubOpenAI._resolve_decision({
        "enforcement_mode": "enforced",
        "recommendation": "proceed",
    }) == "blocked"


def test_resolve_decision_enforced_unknown_verdict_blocks() -> None:
    """Enforced mode with an unknown verdict string must fail-safe to blocked."""
    assert BighubOpenAI._resolve_decision({
        "enforcement_mode": "enforced",
        "enforced_verdict": "some_future_verdict",
    }) == "blocked"


def test_resolve_decision_enforced_proceed_allows() -> None:
    assert BighubOpenAI._resolve_decision({
        "enforcement_mode": "enforced",
        "enforced_verdict": "proceed",
    }) == "execute"


# ---------------------------------------------------------------------------
# _resolve_decision — review mode
# ---------------------------------------------------------------------------


def test_resolve_decision_review_mode_proceed() -> None:
    assert BighubOpenAI._resolve_decision({
        "enforcement_mode": "review",
        "recommendation": "proceed",
    }) == "execute"


def test_resolve_decision_review_mode_proceed_with_caution() -> None:
    assert BighubOpenAI._resolve_decision({
        "enforcement_mode": "review",
        "recommendation": "proceed_with_caution",
    }) == "approval_required"


def test_resolve_decision_review_mode_review_recommended() -> None:
    assert BighubOpenAI._resolve_decision({
        "enforcement_mode": "review",
        "recommendation": "review_recommended",
    }) == "approval_required"


def test_resolve_decision_review_mode_do_not_proceed() -> None:
    assert BighubOpenAI._resolve_decision({
        "enforcement_mode": "review",
        "recommendation": "do_not_proceed",
    }) == "blocked"


def test_resolve_decision_review_mode_unknown_recommendation() -> None:
    """Review mode with unknown/missing recommendation defaults to approval."""
    assert BighubOpenAI._resolve_decision({
        "enforcement_mode": "review",
    }) == "approval_required"


# ---------------------------------------------------------------------------
# _enrich_result — trajectory_health priority
# ---------------------------------------------------------------------------


def test_enrich_result_prefers_decision_intelligence_trajectory_health() -> None:
    """When both decision_intelligence and intelligence have trajectory_health,
    the value from decision_intelligence wins."""
    result = ToolResult(status="executed", decision={})
    BighubOpenAI._enrich_result(result, {
        "decision_intelligence": {"trajectory_health": "healthy"},
        "intelligence": {"trajectory_health": "degrading"},
    })
    assert result.trajectory_health == "healthy"


def test_enrich_result_falls_back_to_intelligence_trajectory_health() -> None:
    """When decision_intelligence has no trajectory_health, fall back to intelligence."""
    result = ToolResult(status="executed", decision={})
    BighubOpenAI._enrich_result(result, {
        "decision_intelligence": {"rationale": "ok"},
        "intelligence": {"trajectory_health": "degrading"},
    })
    assert result.trajectory_health == "degrading"


def test_enrich_result_handles_bad_risk_score() -> None:
    """Non-numeric risk_score should not crash — just set None."""
    result = ToolResult(status="executed", decision={})
    BighubOpenAI._enrich_result(result, {
        "risk_score": "not_a_number",
    })
    assert result.risk_score is None


# ---------------------------------------------------------------------------
# list_tools
# ---------------------------------------------------------------------------


def test_list_tools_returns_registered_tools() -> None:
    guard = BighubOpenAI(
        bighub_api_key="bhk_test",
        actor="agent",
        domain="test",
        bighub_client=type("C", (), {
            "actions": type("A", (), {"submit": lambda **kw: {}, "ingest_memory": lambda **kw: {}})(),
            "outcomes": type("O", (), {"report": lambda **kw: {}})(),
            "close": lambda self: None,
        })(),
        openai_client=type("OAI", (), {"responses": type("R", (), {"create": lambda **kw: None})()})(),
    )
    guard.register_tool("my_tool", lambda x: x, description="A tool", parameters_schema={
        "type": "object", "properties": {"x": {"type": "string"}}, "required": ["x"], "additionalProperties": False,
    })
    tools = guard.list_tools()
    assert len(tools) == 1
    assert tools[0]["type"] == "function"
    assert tools[0]["function"]["name"] == "my_tool"
    assert tools[0]["function"]["description"] == "A tool"
    assert tools[0]["function"]["strict"] is True

