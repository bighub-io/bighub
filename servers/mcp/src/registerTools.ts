import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

import { BighubHttpClient } from "./httpClient.js";

const JsonObjectSchema = z.record(z.string(), z.unknown());
const JsonPatchSchema = z.union([
  z.array(JsonObjectSchema),
  z.object({
    ops: z.array(JsonObjectSchema),
    format: z.string().optional(),
  }),
]);
const AnyOutputSchema = z.object({}).passthrough();

function toResult(data: unknown) {
  return {
    content: [{ type: "text" as const, text: JSON.stringify(data, null, 2) }],
  };
}

function cleanObject(input: Record<string, unknown>): Record<string, unknown> {
  return Object.fromEntries(Object.entries(input).filter(([, value]) => value !== undefined));
}

export function registerBighubTools(server: McpServer, client: BighubHttpClient): void {
  server.registerTool(
    "bighub_http_request",
    {
      description: "Low-level passthrough for any BIGHUB API endpoint.",
      outputSchema: AnyOutputSchema,
      inputSchema: {
        method: z.enum(["GET", "POST", "PATCH", "DELETE"]),
        path: z.string().regex(/^\/.*/, "Path must start with '/'"),
        query: JsonObjectSchema.optional(),
        body: z.union([JsonObjectSchema, z.array(JsonObjectSchema)]).optional(),
        headers: z.record(z.string(), z.string()).optional(),
        idempotency_key: z.string().optional(),
      },
    },
    async ({ method, path, query, body, headers, idempotency_key }) =>
      toResult(
        await client.request({
          method,
          path,
          query,
          body,
          headers,
          idempotencyKey: idempotency_key,
        }),
      ),
  );

  server.registerTool(
    "bighub_actions_submit",
    {
      description: "Validate an action via /actions/submit.",
      outputSchema: AnyOutputSchema,
      inputSchema: {
        action: z.string(),
        actor: z.string().default("AI_AGENT"),
        value: z.number().optional(),
        target: z.string().optional(),
        domain: z.string().optional(),
        metadata: JsonObjectSchema.optional(),
        idempotency_key: z.string().optional(),
      },
    },
    async ({ action, actor, value, target, domain, metadata, idempotency_key }) =>
      toResult(
        await client.request({
          method: "POST",
          path: "/actions/submit",
          body: cleanObject({ action, actor, value, target, domain, metadata }),
          idempotencyKey: idempotency_key,
        }),
      ),
  );

  server.registerTool(
    "bighub_actions_submit_v2",
    {
      description: "Validate an action with pro decision intelligence via /actions/submit/v2.",
      outputSchema: AnyOutputSchema,
      inputSchema: {
        payload: JsonObjectSchema,
        idempotency_key: z.string().optional(),
      },
    },
    async ({ payload, idempotency_key }) =>
      toResult(
        await client.request({
          method: "POST",
          path: "/actions/submit/v2",
          body: payload,
          idempotencyKey: idempotency_key,
        }),
      ),
  );

  server.registerTool(
    "bighub_actions_dry_run",
    {
      description: "Run a non-persistent action validation via /actions/submit/dry-run.",
      inputSchema: {
        payload: JsonObjectSchema,
        idempotency_key: z.string().optional(),
      },
    },
    async ({ payload, idempotency_key }) =>
      toResult(
        await client.request({
          method: "POST",
          path: "/actions/submit/dry-run",
          body: payload,
          idempotencyKey: idempotency_key,
        }),
      ),
  );

  server.registerTool(
    "bighub_actions_verify_validation",
    {
      description: "Verify a previous validation by validation_id.",
      inputSchema: { validation_id: z.string() },
    },
    async ({ validation_id }) =>
      toResult(
        await client.request({
          method: "GET",
          path: `/actions/validations/${validation_id}/verify`,
        }),
      ),
  );

  server.registerTool(
    "bighub_actions_observer_stats",
    {
      description: "Get action observer stats.",
      inputSchema: {},
    },
    async () => toResult(await client.request({ method: "GET", path: "/actions/observer/stats" })),
  );

  server.registerTool(
    "bighub_actions_dashboard_summary",
    {
      description: "Get action dashboard summary.",
      inputSchema: {},
    },
    async () => toResult(await client.request({ method: "GET", path: "/actions/dashboard/summary" })),
  );

  server.registerTool(
    "bighub_actions_status",
    {
      description: "Get action system status.",
      inputSchema: {},
    },
    async () => toResult(await client.request({ method: "GET", path: "/actions/status" })),
  );

  server.registerTool(
    "bighub_actions_memory_ingest",
    {
      description: "Ingest governed execution events into Future Memory.",
      inputSchema: {
        events: z.array(JsonObjectSchema),
        source: z.string().default("adapter"),
        source_version: z.string().optional(),
        actor: z.string().optional(),
        domain: z.string().optional(),
        model: z.string().optional(),
        trace_id: z.string().optional(),
        redact: z.boolean().default(true),
        redaction_policy: z.string().default("default"),
      },
    },
    async ({ events, source, source_version, actor, domain, model, trace_id, redact, redaction_policy }) =>
      toResult(
        await client.request({
          method: "POST",
          path: "/actions/memory/ingest",
          body: cleanObject({
            source,
            events,
            source_version,
            actor,
            domain,
            model,
            trace_id,
            redact,
            redaction_policy,
          }),
        }),
      ),
  );

  server.registerTool(
    "bighub_actions_memory_context",
    {
      description: "Read Future Memory context window and rates.",
      inputSchema: {
        window_hours: z.number().int().default(24),
        tool: z.string().optional(),
        domain: z.string().optional(),
        actor: z.string().optional(),
        source: z.string().optional(),
        limit_recent: z.number().int().default(25),
      },
    },
    async ({ window_hours, tool, domain, actor, source, limit_recent }) =>
      toResult(
        await client.request({
          method: "GET",
          path: "/actions/memory/context",
          query: cleanObject({ window_hours, tool, domain, actor, source, limit_recent }),
        }),
      ),
  );

  server.registerTool(
    "bighub_actions_memory_refresh_aggregates",
    {
      description: "Refresh Future Memory aggregates.",
      inputSchema: {
        concurrent: z.boolean().default(false),
        window_hours: z.number().int().default(24),
      },
    },
    async ({ concurrent, window_hours }) =>
      toResult(
        await client.request({
          method: "POST",
          path: "/actions/memory/refresh-aggregates",
          query: { concurrent, window_hours },
        }),
      ),
  );

  server.registerTool(
    "bighub_actions_memory_recommendations",
    {
      description: "Compute Future Memory policy recommendations.",
      outputSchema: AnyOutputSchema,
      inputSchema: {
        window_hours: z.number().int().default(24),
        scope: JsonObjectSchema.optional(),
        tool: z.string().optional(),
        domain: z.string().optional(),
        actor: z.string().optional(),
        source: z.string().optional(),
        min_events: z.number().int().default(20),
        min_blocked_rate: z.number().default(0.15),
        min_approval_rate: z.number().default(0.1),
        min_tool_error_rate: z.number().default(0.05),
        limit_recommendations: z.number().int().default(10),
        include_examples: z.boolean().default(true),
        auto_apply: z.boolean().default(false),
      },
    },
    async (args) =>
      toResult(
        await client.request({
          method: "POST",
          path: "/actions/memory/recommendations",
          body: cleanObject(args),
        }),
      ),
  );

  server.registerTool(
    "bighub_rules_create",
    {
      description: "Create a governance rule.",
      outputSchema: AnyOutputSchema,
      inputSchema: {
        payload: JsonObjectSchema,
        idempotency_key: z.string().optional(),
      },
    },
    async ({ payload, idempotency_key }) =>
      toResult(
        await client.request({
          method: "POST",
          path: "/rules",
          body: payload,
          idempotencyKey: idempotency_key,
        }),
      ),
  );

  server.registerTool(
    "bighub_rules_list",
    {
      description: "List governance rules.",
      outputSchema: AnyOutputSchema,
      inputSchema: {
        status: z.string().optional(),
        domain: z.string().optional(),
        limit: z.number().int().optional(),
        offset: z.number().int().optional(),
      },
    },
    async ({ status, domain, limit, offset }) =>
      toResult(
        await client.request({
          method: "GET",
          path: "/rules",
          query: cleanObject({ status, domain, limit, offset }),
        }),
      ),
  );

  server.registerTool(
    "bighub_rules_get",
    {
      description: "Fetch a single rule by rule_id.",
      outputSchema: AnyOutputSchema,
      inputSchema: { rule_id: z.string() },
    },
    async ({ rule_id }) => toResult(await client.request({ method: "GET", path: `/rules/${rule_id}` })),
  );

  server.registerTool(
    "bighub_rules_update",
    {
      description: "Update a rule by rule_id.",
      outputSchema: AnyOutputSchema,
      inputSchema: {
        rule_id: z.string(),
        payload: JsonObjectSchema,
        idempotency_key: z.string().optional(),
      },
    },
    async ({ rule_id, payload, idempotency_key }) =>
      toResult(
        await client.request({
          method: "PATCH",
          path: `/rules/${rule_id}`,
          body: payload,
          idempotencyKey: idempotency_key,
        }),
      ),
  );

  server.registerTool(
    "bighub_rules_delete",
    {
      description: "Delete a rule.",
      inputSchema: {
        rule_id: z.string(),
        idempotency_key: z.string().optional(),
      },
    },
    async ({ rule_id, idempotency_key }) =>
      toResult(
        await client.request({
          method: "DELETE",
          path: `/rules/${rule_id}`,
          idempotencyKey: idempotency_key,
        }),
      ),
  );

  server.registerTool(
    "bighub_rules_pause",
    {
      description: "Pause rule enforcement for a rule_id.",
      inputSchema: {
        rule_id: z.string(),
        idempotency_key: z.string().optional(),
      },
    },
    async ({ rule_id, idempotency_key }) =>
      toResult(
        await client.request({
          method: "POST",
          path: `/rules/${rule_id}/pause`,
          idempotencyKey: idempotency_key,
        }),
      ),
  );

  server.registerTool(
    "bighub_rules_resume",
    {
      description: "Resume a paused rule.",
      inputSchema: {
        rule_id: z.string(),
        idempotency_key: z.string().optional(),
      },
    },
    async ({ rule_id, idempotency_key }) =>
      toResult(
        await client.request({
          method: "POST",
          path: `/rules/${rule_id}/resume`,
          idempotencyKey: idempotency_key,
        }),
      ),
  );

  server.registerTool(
    "bighub_rules_dry_run",
    {
      description: "Dry run a rule payload without persisting.",
      inputSchema: {
        payload: JsonObjectSchema,
      },
    },
    async ({ payload }) =>
      toResult(
        await client.request({
          method: "POST",
          path: "/rules/dry-run",
          body: payload,
        }),
      ),
  );

  server.registerTool(
    "bighub_rules_validate",
    {
      description: "Validate a rule payload.",
      inputSchema: {
        payload: JsonObjectSchema,
      },
    },
    async ({ payload }) =>
      toResult(
        await client.request({
          method: "POST",
          path: "/rules/validate",
          body: payload,
        }),
      ),
  );

  server.registerTool(
    "bighub_rules_validate_dry_run",
    {
      description: "Dry-run validate a rule payload.",
      inputSchema: {
        payload: JsonObjectSchema,
      },
    },
    async ({ payload }) =>
      toResult(
        await client.request({
          method: "POST",
          path: "/rules/validate/dry-run",
          body: payload,
        }),
      ),
  );

  server.registerTool(
    "bighub_rules_domains",
    {
      description: "List available rule domains.",
      inputSchema: {},
    },
    async () => toResult(await client.request({ method: "GET", path: "/rules/domains" })),
  );

  server.registerTool(
    "bighub_rules_versions",
    {
      description: "List historical versions for a rule.",
      outputSchema: AnyOutputSchema,
      inputSchema: {
        rule_id: z.string(),
        limit: z.number().int().optional(),
      },
    },
    async ({ rule_id, limit }) =>
      toResult(
        await client.request({
          method: "GET",
          path: `/rules/${rule_id}/versions`,
          query: cleanObject({ limit }),
        }),
      ),
  );

  server.registerTool(
    "bighub_rules_purge_idempotency",
    {
      description: "Purge rule idempotency records from the backend store.",
      outputSchema: AnyOutputSchema,
      inputSchema: {
        only_expired: z.boolean().default(true),
        older_than_hours: z.number().int().optional(),
        limit: z.number().int().optional(),
      },
    },
    async ({ only_expired, older_than_hours, limit }) =>
      toResult(
        await client.request({
          method: "POST",
          path: "/rules/admin/idempotency/purge",
          query: cleanObject({ only_expired, older_than_hours, limit }),
        }),
      ),
  );

  server.registerTool(
    "bighub_rules_apply_patch",
    {
      description: "Apply JSON Patch operations to a rule with preview/optimistic locking support.",
      outputSchema: AnyOutputSchema,
      inputSchema: {
        rule_id: z.string(),
        patch: JsonPatchSchema,
        preview: z.boolean().default(true),
        reason: z.string().optional(),
        if_match_version: z.number().int().optional(),
        idempotency_key: z.string().optional(),
        if_match: z.string().optional(),
      },
    },
    async ({ rule_id, patch, preview, reason, if_match_version, idempotency_key, if_match }) => {
      const patchOps = Array.isArray(patch) ? patch : patch.ops;
      return toResult(
        await client.request({
          method: "POST",
          path: `/rules/${rule_id}/apply_patch`,
          body: cleanObject({ patch: patchOps, preview, reason, if_match_version }),
          idempotencyKey: idempotency_key,
          headers: cleanObject({ "If-Match": if_match }) as Record<string, string>,
        }),
      );
    },
  );

  server.registerTool(
    "bighub_approvals_list",
    {
      description: "List approval queue items.",
      outputSchema: AnyOutputSchema,
      inputSchema: {
        status_filter: z.string().default("pending"),
        limit: z.number().int().optional(),
      },
    },
    async ({ status_filter, limit }) =>
      toResult(
        await client.request({
          method: "GET",
          path: "/approvals",
          query: cleanObject({ status: status_filter, limit }),
        }),
      ),
  );

  server.registerTool(
    "bighub_approvals_resolve",
    {
      description: "Resolve an approval request.",
      outputSchema: AnyOutputSchema,
      inputSchema: {
        request_id: z.string(),
        resolution: z.enum(["approved", "rejected"]),
        comment: z.string().optional(),
      },
    },
    async ({ request_id, resolution, comment }) =>
      toResult(
        await client.request({
          method: "POST",
          path: `/approvals/${request_id}/resolve`,
          body: cleanObject({ resolution, comment }),
        }),
      ),
  );

  server.registerTool(
    "bighub_kill_switch_status",
    {
      description: "Read kill switch status.",
      outputSchema: AnyOutputSchema,
      inputSchema: {},
    },
    async () => toResult(await client.request({ method: "GET", path: "/kill-switch/status" })),
  );

  server.registerTool(
    "bighub_kill_switch_activate",
    {
      description: "Activate global/domain kill switch.",
      inputSchema: {
        payload: JsonObjectSchema.optional(),
      },
    },
    async ({ payload }) =>
      toResult(await client.request({ method: "POST", path: "/kill-switch/activate", body: payload || {} })),
  );

  server.registerTool(
    "bighub_kill_switch_deactivate",
    {
      description: "Deactivate kill switch by switch_id.",
      inputSchema: {
        switch_id: z.string(),
        payload: JsonObjectSchema.optional(),
      },
    },
    async ({ switch_id, payload }) =>
      toResult(
        await client.request({
          method: "POST",
          path: `/kill-switch/deactivate/${switch_id}`,
          body: payload || {},
        }),
      ),
  );

  server.registerTool(
    "bighub_events_list",
    {
      description: "List event stream entries.",
      outputSchema: AnyOutputSchema,
      inputSchema: {
        event_type: z.string().optional(),
        severity: z.string().optional(),
        rule_id: z.string().optional(),
        limit: z.number().int().optional(),
        offset: z.number().int().optional(),
      },
    },
    async ({ event_type, severity, rule_id, limit, offset }) =>
      toResult(
        await client.request({
          method: "GET",
          path: "/events",
          query: cleanObject({ event_type, severity, rule_id, limit, offset }),
        }),
      ),
  );

  server.registerTool(
    "bighub_events_stats",
    {
      description: "Get aggregate event stats.",
      inputSchema: {},
    },
    async () => toResult(await client.request({ method: "GET", path: "/events/stats" })),
  );

  server.registerTool(
    "bighub_api_keys_create",
    {
      description: "Create an API key.",
      inputSchema: {
        payload: JsonObjectSchema,
      },
    },
    async ({ payload }) => toResult(await client.request({ method: "POST", path: "/api-keys", body: payload })),
  );

  server.registerTool(
    "bighub_api_keys_list",
    {
      description: "List API keys.",
      outputSchema: AnyOutputSchema,
      inputSchema: {
        include_revoked: z.boolean().default(false),
      },
    },
    async ({ include_revoked }) =>
      toResult(await client.request({ method: "GET", path: "/api-keys", query: { include_revoked } })),
  );

  server.registerTool(
    "bighub_api_keys_delete",
    {
      description: "Delete or revoke an API key.",
      inputSchema: {
        key_id: z.string(),
        reason: z.string().optional(),
      },
    },
    async ({ key_id, reason }) =>
      toResult(
        await client.request({
          method: "DELETE",
          path: `/api-keys/${key_id}`,
          body: reason ? { reason } : undefined,
        }),
      ),
  );

  server.registerTool(
    "bighub_api_keys_rotate",
    {
      description: "Rotate an API key.",
      inputSchema: {
        key_id: z.string(),
      },
    },
    async ({ key_id }) => toResult(await client.request({ method: "POST", path: `/api-keys/${key_id}/rotate` })),
  );

  server.registerTool(
    "bighub_api_keys_validate",
    {
      description: "Validate an API key (query + X-API-Key header).",
      inputSchema: {
        api_key: z.string(),
      },
    },
    async ({ api_key }) =>
      toResult(
        await client.request({
          method: "GET",
          path: "/api-keys/validate",
          query: { api_key },
          headers: { "X-API-Key": api_key },
        }),
      ),
  );

  server.registerTool(
    "bighub_api_keys_scopes",
    {
      description: "List available API key scopes.",
      inputSchema: {},
    },
    async () => toResult(await client.request({ method: "GET", path: "/api-keys/scopes" })),
  );

  server.registerTool(
    "bighub_webhooks_create",
    {
      description: "Create a webhook endpoint.",
      inputSchema: {
        payload: JsonObjectSchema,
      },
    },
    async ({ payload }) => toResult(await client.request({ method: "POST", path: "/webhooks", body: payload })),
  );

  server.registerTool(
    "bighub_webhooks_list",
    {
      description: "List webhooks.",
      outputSchema: AnyOutputSchema,
      inputSchema: {
        include_inactive: z.boolean().default(false),
      },
    },
    async ({ include_inactive }) =>
      toResult(await client.request({ method: "GET", path: "/webhooks", query: { include_inactive } })),
  );

  server.registerTool(
    "bighub_webhooks_get",
    {
      description: "Get a webhook by webhook_id.",
      outputSchema: AnyOutputSchema,
      inputSchema: {
        webhook_id: z.string(),
      },
    },
    async ({ webhook_id }) => toResult(await client.request({ method: "GET", path: `/webhooks/${webhook_id}` })),
  );

  server.registerTool(
    "bighub_webhooks_update",
    {
      description: "Update webhook by webhook_id.",
      inputSchema: {
        webhook_id: z.string(),
        payload: JsonObjectSchema,
      },
    },
    async ({ webhook_id, payload }) =>
      toResult(await client.request({ method: "PATCH", path: `/webhooks/${webhook_id}`, body: payload })),
  );

  server.registerTool(
    "bighub_webhooks_delete",
    {
      description: "Delete a webhook.",
      inputSchema: {
        webhook_id: z.string(),
      },
    },
    async ({ webhook_id }) => toResult(await client.request({ method: "DELETE", path: `/webhooks/${webhook_id}` })),
  );

  server.registerTool(
    "bighub_webhooks_deliveries",
    {
      description: "List webhook delivery logs.",
      inputSchema: {
        webhook_id: z.string(),
        limit: z.number().int().optional(),
      },
    },
    async ({ webhook_id, limit }) =>
      toResult(
        await client.request({
          method: "GET",
          path: `/webhooks/${webhook_id}/deliveries`,
          query: cleanObject({ limit }),
        }),
      ),
  );

  server.registerTool(
    "bighub_webhooks_test",
    {
      description: "Send a test webhook delivery.",
      inputSchema: {
        webhook_id: z.string(),
        event_type: z.string().default("signal.new"),
      },
    },
    async ({ webhook_id, event_type }) =>
      toResult(
        await client.request({
          method: "POST",
          path: `/webhooks/${webhook_id}/test`,
          body: { event_type },
        }),
      ),
  );

  server.registerTool(
    "bighub_webhooks_list_events",
    {
      description: "List supported webhook event types.",
      inputSchema: {},
    },
    async () => toResult(await client.request({ method: "GET", path: "/webhooks/events/list" })),
  );

  server.registerTool(
    "bighub_webhooks_verify_signature",
    {
      description: "Verify webhook signature payload.",
      inputSchema: {
        payload: z.string(),
        signature: z.string(),
        secret: z.string(),
        timestamp: z.number().int(),
      },
    },
    async ({ payload, signature, secret, timestamp }) =>
      toResult(
        await client.request({
          method: "POST",
          path: "/webhooks/verify-signature",
          body: { payload, signature, secret, timestamp },
        }),
      ),
  );

  server.registerTool(
    "bighub_webhooks_replay_failed_delivery",
    {
      description: "Replay a failed webhook delivery.",
      inputSchema: {
        webhook_id: z.string(),
        delivery_id: z.number().int(),
      },
    },
    async ({ webhook_id, delivery_id }) =>
      toResult(
        await client.request({
          method: "POST",
          path: `/webhooks/${webhook_id}/deliveries/${delivery_id}/replay`,
        }),
      ),
  );

  server.registerTool(
    "bighub_auth_signup",
    {
      description: "Sign up and return access/refresh tokens.",
      inputSchema: { payload: JsonObjectSchema },
    },
    async ({ payload }) => toResult(await client.request({ method: "POST", path: "/auth/signup", body: payload })),
  );

  server.registerTool(
    "bighub_auth_login",
    {
      description: "Authenticate and return access/refresh tokens.",
      outputSchema: AnyOutputSchema,
      inputSchema: { payload: JsonObjectSchema },
    },
    async ({ payload }) => toResult(await client.request({ method: "POST", path: "/auth/login", body: payload })),
  );

  server.registerTool(
    "bighub_auth_refresh",
    {
      description: "Rotate auth tokens with refresh token.",
      inputSchema: { refresh_token: z.string() },
    },
    async ({ refresh_token }) =>
      toResult(await client.request({ method: "POST", path: "/auth/refresh", body: { refresh_token } })),
  );

  server.registerTool(
    "bighub_auth_logout",
    {
      description: "Invalidate a refresh token.",
      inputSchema: { refresh_token: z.string() },
    },
    async ({ refresh_token }) =>
      toResult(await client.request({ method: "POST", path: "/auth/logout", body: { refresh_token } })),
  );
}
