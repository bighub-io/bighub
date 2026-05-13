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
    const tool = fakeServer.tools.get("bighub_constraints_purge_idempotency");

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
      "bighub_actions_evaluate",
      "bighub_constraints_create",
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

    const submitTool = fakeServer.tools.get("bighub_actions_evaluate");
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
        path: "/actions/evaluate",
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

  it("registers modern better-decision MCP primitives", async () => {
    const fakeServer = new FakeServer();
    const request = vi.fn(async () => ({
      request_id: "req_1",
      proposed_action: "Grant Okta admin access",
      better_action: "Grant scoped Okta admin access for 4h",
      execution_mode: "review",
      risk: 0.68,
      can_run: false,
      needs_review: true,
      decision_packet: { system: "okta", packet_sha256: "abc" },
      decision_brain: { recommendation: "review_recommended" },
      model_selection: { selected_model: null },
      allowed: false,
      result: "requires_approval",
      recommendation: "review_recommended",
    }));
    const fakeClient = { request } as unknown as BighubHttpClient;

    registerBighubTools(fakeServer as never, fakeClient);

    for (const toolName of [
      "bighub_decide",
      "bighub_build_packet",
      "bighub_run_brain",
      "bighub_list_reviews",
      "bighub_resolve_review",
      "bighub_get_system_context",
      "bighub_get_world_state",
      "bighub_report_outcome",
    ]) {
      expect(fakeServer.tools.get(toolName), `${toolName} should be registered`).toBeDefined();
    }

    const result = await fakeServer.tools.get("bighub_decide")?.handler({
      action: "Grant Okta admin access",
      context: { system: "okta" },
      objective: "better_decision",
      model_selection: "auto",
      actor: "AI_AGENT",
    });

    expect(request).toHaveBeenCalledWith(
      expect.objectContaining({
        method: "POST",
        path: "/actions/evaluate",
        body: expect.objectContaining({
          action: "Grant Okta admin access",
          context: { system: "okta", objective: "better_decision", model_selection: "auto" },
        }),
      }),
    );
    const text = (result as { content: Array<{ text: string }> }).content[0].text;
    const payload = JSON.parse(text);
    expect(payload.better_action).toBe("Grant scoped Okta admin access for 4h");
    expect(payload.needs_review).toBe(true);
    expect(payload.allowed).toBe(false);
  });
});
