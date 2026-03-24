# BIGHUB Python examples

Sample code using the BIGHUB Python SDK and adapters.

- Use `bighub` to evaluate agent actions, receive recommendations, report outcomes, and learn from past decisions.
- Use `bighub-openai` to add decision learning to OpenAI tool calls.

## Quick smoke example (SDK)

```python
from bighub import BighubClient

client = BighubClient(api_key="your_api_key")

result = client.actions.submit(
    action="refund_full",
    value=199.99,
    domain="customer_transactions",
    actor="refund_agent",
)

print(result["recommendation"])             # proceed, proceed_with_caution, review_recommended, do_not_proceed
print(result["recommendation_confidence"])   # high, medium, low
print(result["risk_score"])                  # 0.0 – 1.0

if result["recommendation"] in ("proceed", "proceed_with_caution"):
    # execute your runtime action here
    client.outcomes.report(
        request_id=result["request_id"],
        status="SUCCESS",
        description="Refund processed successfully",
    )

client.close()
```

## Quick smoke example (bighub-openai)

```python
import os
from bighub_openai import BighubOpenAI

def refund_payment(order_id: str, amount: float) -> dict:
    return {"ok": True, "order_id": order_id, "amount": amount}

runtime = BighubOpenAI(
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    bighub_api_key=os.getenv("BIGHUB_API_KEY"),
    actor="AI_AGENT_001",
    domain="customer_transactions",
)

runtime.tool("refund_payment", refund_payment, value_from_args=lambda a: a["amount"])

response = runtime.run(
    messages=[{"role": "user", "content": "Refund order ord_123 for 199.99"}],
    model="gpt-4.1",
)

print(response["execution"]["last"]["decision"]["recommendation"])
```

## Notes

- Free BETA limits: 3 agents, 2,500 actions/month, 30 days history, 1 environment.
- `actions.submit(...)` is the default endpoint in Free BETA.
- `actions.submit_payload(...)` is available as an advanced action submission endpoint.
- Use valid outcome statuses such as `SUCCESS`, `FAILURE`, `ROLLBACK`, `INCIDENT`, `CHURN`, or `NO_EFFECT`.

See [sdk/python/](../../sdk/python/) and [adapters/python/openai/](../../adapters/python/openai/).
