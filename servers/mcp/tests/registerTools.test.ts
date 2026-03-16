import { describe, expect, it, vi } from "vitest";

import type { BighubHttpClient } from "../src/httpClient.js";
import { registerBighubTools } from "../src/registerTools.js";

type RegisteredTool = {
  config: Record<string, unknown>;
  handler: (args: Record<string, unknown>) => Promise<unknown>;
};

class FakeServer {
  public readonly tools = new Map<string, RegisteredTool>();

  registerTool(name: string, config: Record<string, unknown>, handler: (args: Record<string, unknown>) => Promise<unknown>) {
    this.tools.set(name, { config, handler });
    return {
      disable: () => undefined,
      enable: () => undefined,
      update: () => undefined,
      remove: () => undefined,
    };
  }
}

describe("registerBighubTools", () => {
  it("registers purge idempotency tool and calls expected endpoint", async () => {
    const fakeServer = new FakeServer();
    const request = vi.fn(async () => ({ purged: 42 }));
    const fakeClient = { request } as unknown as BighubHttpClient;

    registerBighubTools(fakeServer as never, fakeClient);
    const tool = fakeServer.tools.get("bighub_rules_purge_idempotency");

    expect(tool).toBeDefined();
    expect(tool?.config.outputSchema).toBeDefined();

    await tool?.handler({
      only_expired: true,
      older_than_hours: 24,
      limit: 100,
    });

    expect(request).toHaveBeenCalledWith({
      method: "POST",
      path: "/rules/admin/idempotency/purge",
      query: {
        only_expired: true,
        older_than_hours: 24,
        limit: 100,
      },
    });
  });

  it("adds output schema on key tools for better MCP compatibility", () => {
    const fakeServer = new FakeServer();
    const request = vi.fn(async () => ({}));
    const fakeClient = { request } as unknown as BighubHttpClient;

    registerBighubTools(fakeServer as never, fakeClient);

    for (const toolName of [
      "bighub_actions_submit",
      "bighub_rules_create",
      "bighub_approvals_list",
      "bighub_webhooks_list",
      "bighub_auth_login",
    ]) {
      const entry = fakeServer.tools.get(toolName);
      expect(entry, `${toolName} should be registered`).toBeDefined();
      expect(entry?.config.outputSchema, `${toolName} should define outputSchema`).toBeDefined();
    }
  });

  it("maps legacy metadata and strategy_name to backend contract fields", async () => {
    const fakeServer = new FakeServer();
    const request = vi.fn(async () => ({}));
    const fakeClient = { request } as unknown as BighubHttpClient;

    registerBighubTools(fakeServer as never, fakeClient);

    const submitTool = fakeServer.tools.get("bighub_actions_submit");
    const retrievalTool = fakeServer.tools.get("bighub_retrieval_query");

    await submitTool?.handler({
      action: "refund_full",
      actor: "AI_AGENT",
      metadata: { order_id: "ord_1" },
    });
    await retrievalTool?.handler({
      domain: "customer_transactions",
      action: "refund_full",
      strategy_name: "balanced",
    });

    expect(request).toHaveBeenNthCalledWith(
      1,
      expect.objectContaining({
        path: "/actions/submit",
        body: expect.objectContaining({
          context: { order_id: "ord_1" },
        }),
      }),
    );
    expect(request).toHaveBeenNthCalledWith(
      2,
      expect.objectContaining({
        path: "/retrieval/query",
        body: expect.objectContaining({
          strategy: "balanced",
          strategy_name: "balanced",
        }),
      }),
    );
  });
});
