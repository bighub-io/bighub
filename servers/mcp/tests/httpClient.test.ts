import { afterEach, describe, expect, it, vi } from "vitest";

import { BighubHttpClient, BighubHttpError } from "../src/httpClient.js";

describe("BighubHttpClient", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("sends auth/idempotency headers and query params", async () => {
    const fetchMock = vi.fn(async () => new Response(JSON.stringify({ ok: true }), { status: 200, headers: { "content-type": "application/json" } }));
    vi.stubGlobal("fetch", fetchMock);

    const client = new BighubHttpClient({
      baseUrl: "https://api.bighub.io",
      apiKey: "bhk_test",
      timeoutMs: 1000,
      maxRetries: 0,
      userAgent: "bighub-mcp/test",
    });

    const result = await client.request<{ ok: boolean }>({
      method: "GET",
      path: "/rules",
      query: { status: "active", limit: 10 },
      idempotencyKey: "idem-1",
    });

    expect(result.ok).toBe(true);
    expect(fetchMock).toHaveBeenCalledTimes(1);
    const [url, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(url).toContain("/rules");
    expect(url).toContain("status=active");
    expect(url).toContain("limit=10");
    expect((init.headers as Record<string, string>)["X-API-Key"]).toBe("bhk_test");
    expect((init.headers as Record<string, string>)["Idempotency-Key"]).toBe("idem-1");
    expect((init.headers as Record<string, string>)["User-Agent"]).toBe("bighub-mcp/test");
  });

  it("raises structured error metadata from API responses", async () => {
    const fetchMock = vi.fn(async () =>
      new Response(
        JSON.stringify({
          detail: { code: "rule_invalid", message: "invalid rule" },
          request_id: "req_123",
        }),
        { status: 400, statusText: "Bad Request", headers: { "content-type": "application/json" } },
      ),
    );
    vi.stubGlobal("fetch", fetchMock);

    const client = new BighubHttpClient({
      baseUrl: "https://api.bighub.io",
      apiKey: "bhk_test",
      timeoutMs: 1000,
      maxRetries: 0,
      userAgent: "bighub-mcp/test",
    });

    await expect(
      client.request({
        method: "POST",
        path: "/rules",
        body: { name: "bad" },
      }),
    ).rejects.toMatchObject<BighubHttpError>({
      statusCode: 400,
      requestId: "req_123",
      code: "rule_invalid",
    });
  });
});
