# BIGHUB Python examples

Sample code using the BIGHUB Python SDK and adapters.

- Use `bighub` to evaluate agent actions, report outcomes, and learn from past decisions.
- Use `bighub-openai` to add decision learning to OpenAI tool calls.

## Quick smoke example (SDK)

```python
from bighub import BighubClient

client = BighubClient(api_key="your_api_key")

decision = client.actions.submit(
    action="refund_full",
    value=199.99,
    domain="customer_transactions",
    actor="refund_agent",
)

if decision["allowed"]:
    # execute your runtime action here
    client.outcomes.report(
        request_id=decision["request_id"],
        status="SUCCESS",
        description="Refund processed successfully",
    )

client.close()
```

## Notes

- Free BETA limits: 3 agents, 2,500 actions/month, 30 days history, 1 environment.
- `actions.submit(...)` is the default endpoint in Free BETA.
- `actions.submit_payload(...)` is available as an advanced action submission endpoint.
- Use valid outcome statuses such as `SUCCESS`, `FAILURE`, `ROLLBACK`, `INCIDENT`, `CHURN`, or `NO_EFFECT`.

See [sdk/python/](../../sdk/python/) and [adapters/python/openai/](../../adapters/python/openai/).
