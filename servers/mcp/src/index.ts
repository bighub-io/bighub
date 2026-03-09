#!/usr/bin/env node
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";

import { BighubHttpClient } from "./httpClient.js";
import { registerBighubTools } from "./registerTools.js";

function parseNumberEnv(name: string, fallback: number): number {
  const raw = process.env[name];
  if (!raw) {
    return fallback;
  }
  const parsed = Number(raw);
  return Number.isFinite(parsed) && parsed > 0 ? parsed : fallback;
}

async function main(): Promise<void> {
  const baseUrl = process.env.BIGHUB_BASE_URL || "https://api.bighub.io";
  const apiKey = process.env.BIGHUB_API_KEY;
  const bearerToken = process.env.BIGHUB_BEARER_TOKEN;

  if (!apiKey && !bearerToken) {
    console.error(
      "BIGHUB_API_KEY or BIGHUB_BEARER_TOKEN must be set. " +
        "Most tools require authentication against api.bighub.io.",
    );
  }

  const client = new BighubHttpClient({
    baseUrl,
    apiKey,
    bearerToken,
    timeoutMs: parseNumberEnv("BIGHUB_TIMEOUT_MS", 15000),
    maxRetries: parseNumberEnv("BIGHUB_MAX_RETRIES", 2),
    userAgent: "bighub-mcp/0.1.0",
  });

  const server = new McpServer({
    name: "bighub-mcp",
    version: "0.1.0",
  });

  registerBighubTools(server, client);

  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("bighub-mcp server running on stdio");

  const shutdown = async () => {
    await server.close();
    process.exit(0);
  };
  process.on("SIGINT", shutdown);
  process.on("SIGTERM", shutdown);
}

main().catch((error) => {
  console.error("bighub-mcp startup error:", error);
  process.exit(1);
});
