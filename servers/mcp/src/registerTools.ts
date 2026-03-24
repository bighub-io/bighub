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
    "bighub_actions_evaluate",
    {
      description: "Evaluate an action via /actions/evaluate — returns decision intelligence (recommendation, risk, trajectory health, alternatives).",
      outputSchema: AnyOutputSchema,
      inputSchema: {
        action: z.string(),
        actor: z.string().default("AI_AGENT"),
        value: z.number().optional(),
        target: z.string().optional(),
        domain: z.string().optional(),
        context: JsonObjectSchema.optional(),
        metadata: JsonObjectSchema.optional(),
        idempotency_key: z.string().optional(),
      },
    },
    async ({ action, actor, value, target, domain, context, metadata, idempotency_key }) => {
      const mergedContext = { ...(metadata || {}), ...(context || {}) };
      const body = cleanObject({ action, actor, value, target, domain, context: Object.keys(mergedContext).length ? mergedContext : undefined });
      return toResult(
        await client.request({
          method: "POST",
          path: "/actions/evaluate",
          body,
          idempotencyKey: idempotency_key,
        }),
      );
    },
  );

  server.registerTool(
    "bighub_actions_evaluate_payload",
    {
      description: "Evaluate an action with full decision intelligence payload via /actions/evaluate.",
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
          path: "/actions/evaluate",
          body: payload,
          idempotencyKey: idempotency_key,
        }),
      ),
  );

  server.registerTool(
    "bighub_actions_dry_run",
    {
      description: "Dry-run action evaluation (non-persistent) via /actions/evaluate with dry_run=true.",
      inputSchema: {
        payload: JsonObjectSchema,
        idempotency_key: z.string().optional(),
      },
    },
    async ({ payload, idempotency_key }) =>
      toResult(
        await client.request({
          method: "POST",
          path: "/actions/evaluate",
          body: { ...payload, dry_run: true },
          idempotencyKey: idempotency_key,
        }),
      ),
  );

  server.registerTool(
    "bighub_actions_live_connect",
    {
      description: "Open a concurrent live agent connection slot. Returns connection_id to reuse for heartbeats and submits.",
      outputSchema: AnyOutputSchema,
      inputSchema: {
        actor: z.string().default("AI_AGENT"),
        context: JsonObjectSchema.optional(),
      },
    },
    async ({ actor, context }) =>
      toResult(
        await client.request({
          method: "POST",
          path: "/actions/live/connect",
          body: { actor, context: context || {} },
        }),
      ),
  );

  server.registerTool(
    "bighub_actions_live_heartbeat",
    {
      description: "Heartbeat an existing live agent connection to keep it alive (recommended every 40s, TTL 120s).",
      outputSchema: AnyOutputSchema,
      inputSchema: {
        connection_id: z.string(),
        context: JsonObjectSchema.optional(),
      },
    },
    async ({ connection_id, context }) =>
      toResult(
        await client.request({
          method: "POST",
          path: "/actions/live/heartbeat",
          body: { connection_id, context: context || {} },
        }),
      ),
  );

  server.registerTool(
    "bighub_actions_live_disconnect",
    {
      description: "Disconnect a live agent connection, freeing the slot immediately.",
      outputSchema: AnyOutputSchema,
      inputSchema: {
        connection_id: z.string(),
        context: JsonObjectSchema.optional(),
      },
    },
    async ({ connection_id, context }) =>
      toResult(
        await client.request({
          method: "POST",
          path: "/actions/live/disconnect",
          body: { connection_id, context: context || {} },
        }),
      ),
  );

  server.registerTool(
    "bighub_actions_verify_validation",
    {
      description: "Verify a previous evaluation by validation_id.",
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
      description: "Ingest scored execution events into decision memory.",
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
      description: "Read decision memory context window and rates.",
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
      description: "Refresh decision memory aggregates.",
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
      description: "Compute decision memory recommendations.",
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
    "bighub_constraints_create",
    {
      description: "Create a boundary rule.",
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
    "bighub_constraints_list",
    {
      description: "List boundary rules.",
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
    "bighub_constraints_get",
    {
      description: "Fetch a single rule by rule_id.",
      outputSchema: AnyOutputSchema,
      inputSchema: { rule_id: z.string() },
    },
    async ({ rule_id }) => toResult(await client.request({ method: "GET", path: `/rules/${rule_id}` })),
  );

  server.registerTool(
    "bighub_constraints_update",
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
    "bighub_constraints_delete",
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
    "bighub_constraints_pause",
    {
      description: "Pause a rule by rule_id.",
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
    "bighub_constraints_resume",
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
    "bighub_constraints_dry_run",
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
    "bighub_constraints_validate",
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
    "bighub_constraints_validate_dry_run",
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
    "bighub_constraints_domains",
    {
      description: "List available rule domains.",
      inputSchema: {},
    },
    async () => toResult(await client.request({ method: "GET", path: "/rules/domains" })),
  );

  server.registerTool(
    "bighub_constraints_versions",
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
    "bighub_constraints_purge_idempotency",
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
    "bighub_constraints_apply_patch",
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
        resolution: z.enum(["approved", "denied", "rejected"]),
        comment: z.string().optional(),
      },
    },
    async ({ request_id, resolution, comment }) =>
      toResult(
        await client.request({
          method: "POST",
          path: `/approvals/${request_id}/resolve`,
          body: cleanObject({
            resolution: resolution === "rejected" ? "denied" : resolution,
            comment,
          }),
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
      description: "Activate global/domain kill switch. Requires a reason.",
      inputSchema: {
        reason: z.string().min(1).describe("Why the kill switch is being activated"),
        scope: z.string().default("global").describe("Scope: global or domain"),
        domain: z.string().optional().describe("Domain to target (when scope=domain)"),
        rule_id: z.string().optional().describe("Specific rule to kill"),
      },
    },
    async ({ reason, scope, domain, rule_id }) =>
      toResult(await client.request({ method: "POST", path: "/kill-switch/activate", body: cleanObject({ reason, scope, domain, rule_id }) })),
  );

  server.registerTool(
    "bighub_kill_switch_deactivate",
    {
      description: "Deactivate kill switch by switch_id. Requires a reason.",
      inputSchema: {
        switch_id: z.string(),
        reason: z.string().min(1).describe("Why the kill switch is being deactivated"),
        scope: z.string().default("global").optional(),
        domain: z.string().optional(),
        rule_id: z.string().optional(),
      },
    },
    async ({ switch_id, reason, scope, domain, rule_id }) =>
      toResult(
        await client.request({
          method: "POST",
          path: `/kill-switch/deactivate/${switch_id}`,
          body: cleanObject({ reason, scope, domain, rule_id }),
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
      inputSchema: { refresh_token: z.string().optional() },
    },
    async ({ refresh_token }) =>
      toResult(await client.request({ method: "POST", path: "/auth/refresh", body: { refresh_token } })),
  );

  server.registerTool(
    "bighub_auth_logout",
    {
      description: "Invalidate a refresh token.",
      inputSchema: { refresh_token: z.string().optional() },
    },
    async ({ refresh_token }) =>
      toResult(await client.request({ method: "POST", path: "/auth/logout", body: { refresh_token } })),
  );

  // ---------------------------------------------------------------------------
  // Cases — Decision case lifecycle
  // ---------------------------------------------------------------------------

  server.registerTool(
    "bighub_cases_create",
    {
      description: "Create a decision case. Requires action and verdict.",
      outputSchema: AnyOutputSchema,
      inputSchema: {
        domain: z.string(),
        action: JsonObjectSchema.describe("Action payload: {tool, action, arguments, value, target, domain}"),
        verdict: JsonObjectSchema.describe("Required verdict: {verdict: ALLOWED|BLOCKED|APPROVAL_REQUIRED|LIMITED|DRY_RUN, mode, reasons, risk_score, confidence}"),
        context: JsonObjectSchema.optional(),
        simulation: JsonObjectSchema.optional(),
        goal_summary: z.string().optional(),
        trigger_source: z.string().optional(),
        actor_type: z.string().default("AI_AGENT"),
        actor_id: z.string().optional(),
        agent_model: z.string().optional(),
        refs: JsonObjectSchema.optional(),
        tags: z.array(z.string()).optional(),
      },
    },
    async ({ domain, action, context, simulation, verdict, goal_summary, trigger_source, actor_type, actor_id, agent_model, refs, tags }) =>
      toResult(
        await client.request({
          method: "POST",
          path: "/cases",
          body: cleanObject({ domain, action, context, simulation, verdict, goal_summary, trigger_source, actor_type, actor_id, agent_model, refs, tags }),
        }),
      ),
  );

  server.registerTool(
    "bighub_cases_get",
    {
      description: "Get a decision case by ID.",
      outputSchema: AnyOutputSchema,
      inputSchema: { case_id: z.string() },
    },
    async ({ case_id }) => toResult(await client.request({ method: "GET", path: `/cases/${case_id}` })),
  );

  server.registerTool(
    "bighub_cases_list",
    {
      description: "List decision cases with filters.",
      outputSchema: AnyOutputSchema,
      inputSchema: {
        domain: z.string().optional(),
        tool: z.string().optional(),
        action: z.string().optional(),
        verdict: z.string().optional(),
        outcome_status: z.string().optional(),
        has_outcome: z.boolean().optional(),
        min_risk_score: z.number().optional(),
        max_risk_score: z.number().optional(),
        limit: z.number().int().default(50),
        offset: z.number().int().default(0),
      },
    },
    async ({ domain, tool, action, verdict, outcome_status, has_outcome, min_risk_score, max_risk_score, limit, offset }) =>
      toResult(
        await client.request({
          method: "GET",
          path: "/cases",
          query: cleanObject({ domain, tool, action, verdict, outcome_status, has_outcome, min_risk_score, max_risk_score, limit, offset }),
        }),
      ),
  );

  server.registerTool(
    "bighub_cases_report_outcome",
    {
      description: "Report a real-world outcome for a decision case.",
      outputSchema: AnyOutputSchema,
      inputSchema: {
        case_id: z.string(),
        status: z.string(),
        description: z.string().optional(),
        details: JsonObjectSchema.optional(),
        actual_impact: JsonObjectSchema.optional(),
        correction_needed: z.boolean().default(false),
        rollback_performed: z.boolean().default(false),
        revenue_impact: z.number().optional(),
      },
    },
    async ({ case_id, status, description, details, actual_impact, correction_needed, rollback_performed, revenue_impact }) =>
      toResult(
        await client.request({
          method: "POST",
          path: `/cases/${case_id}/outcome`,
          body: cleanObject({ status, description, details, actual_impact, correction_needed, rollback_performed, revenue_impact }),
        }),
      ),
  );

  server.registerTool(
    "bighub_cases_precedents",
    {
      description: "Get precedent intelligence for a proposed action. action must be a nested ActionInput object.",
      outputSchema: AnyOutputSchema,
      inputSchema: {
        domain: z.string().optional().describe("Domain to scope precedent search"),
        action: JsonObjectSchema.describe("ActionInput: {action, tool, action_type, arguments, value, target}"),
        context: JsonObjectSchema.optional().describe("ContextInput: {axes, axes_risk_score, intent, irreversibility}"),
        min_similarity: z.number().min(0).max(1).default(0.5).optional(),
        limit: z.number().int().min(1).max(100).default(20).optional(),
      },
    },
    async ({ domain, action, context, min_similarity, limit }) =>
      toResult(
        await client.request({
          method: "POST",
          path: "/cases/precedents",
          body: cleanObject({ domain, action, context, min_similarity, limit }),
        }),
      ),
  );

  server.registerTool(
    "bighub_cases_calibration",
    {
      description: "Get calibration metrics (prediction vs reality) for cases.",
      outputSchema: AnyOutputSchema,
      inputSchema: {
        domain: z.string().optional(),
      },
    },
    async ({ domain }) =>
      toResult(
        await client.request({
          method: "GET",
          path: "/cases/calibration",
          query: cleanObject({ domain }),
        }),
      ),
  );

  // ---------------------------------------------------------------------------
  // Outcomes — Report and analyze what actually happened after execution
  // ---------------------------------------------------------------------------

  server.registerTool(
    "bighub_outcomes_report",
    {
      description: "Report a real-world outcome linked to a decision.",
      outputSchema: AnyOutputSchema,
      inputSchema: {
        status: z.string(),
        request_id: z.string().optional(),
        case_id: z.string().optional(),
        validation_id: z.string().optional(),
        description: z.string().optional(),
        details: JsonObjectSchema.optional(),
        actual_impact: JsonObjectSchema.optional(),
        correction_needed: z.boolean().default(false),
        correction_description: z.string().optional(),
        correction_cost: z.number().optional(),
        time_to_detect_s: z.number().optional(),
        time_to_resolve_s: z.number().optional(),
        rollback_performed: z.boolean().default(false),
        revenue_impact: z.number().optional(),
        customer_impact_count: z.number().int().default(0),
        support_tickets_created: z.number().int().default(0),
        observed_at: z.string().optional(),
        reported_by: z.string().optional(),
        tags: z.array(z.string()).optional(),
      },
    },
    async ({ status, request_id, case_id, validation_id, description, details, actual_impact, correction_needed, correction_description, correction_cost, time_to_detect_s, time_to_resolve_s, rollback_performed, revenue_impact, customer_impact_count, support_tickets_created, observed_at, reported_by, tags }) =>
      toResult(
        await client.request({
          method: "POST",
          path: "/outcomes/report",
          body: cleanObject({ status, request_id, case_id, validation_id, description, details, actual_impact, correction_needed, correction_description, correction_cost, time_to_detect_s, time_to_resolve_s, rollback_performed, revenue_impact, customer_impact_count, support_tickets_created, observed_at, reported_by, tags }),
        }),
      ),
  );

  server.registerTool(
    "bighub_outcomes_report_batch",
    {
      description: "Batch report outcomes (max 100).",
      outputSchema: AnyOutputSchema,
      inputSchema: {
        outcomes: z.array(JsonObjectSchema),
      },
    },
    async ({ outcomes }) =>
      toResult(
        await client.request({
          method: "POST",
          path: "/outcomes/report/batch",
          body: { outcomes },
        }),
      ),
  );

  server.registerTool(
    "bighub_outcomes_get",
    {
      description: "Get outcome by request_id.",
      outputSchema: AnyOutputSchema,
      inputSchema: { request_id: z.string() },
    },
    async ({ request_id }) =>
      toResult(await client.request({ method: "GET", path: `/outcomes/${request_id}` })),
  );

  server.registerTool(
    "bighub_outcomes_get_by_validation",
    {
      description: "Get outcome by validation_id.",
      outputSchema: AnyOutputSchema,
      inputSchema: { validation_id: z.string() },
    },
    async ({ validation_id }) =>
      toResult(await client.request({ method: "GET", path: `/outcomes/by-validation/${validation_id}` })),
  );

  server.registerTool(
    "bighub_outcomes_get_by_case",
    {
      description: "Get outcome by case_id.",
      outputSchema: AnyOutputSchema,
      inputSchema: { case_id: z.string() },
    },
    async ({ case_id }) =>
      toResult(await client.request({ method: "GET", path: `/outcomes/by-case/${case_id}` })),
  );

  server.registerTool(
    "bighub_outcomes_timeline",
    {
      description: "Get full outcome timeline for a request.",
      outputSchema: AnyOutputSchema,
      inputSchema: { request_id: z.string() },
    },
    async ({ request_id }) =>
      toResult(await client.request({ method: "GET", path: `/outcomes/${request_id}/timeline` })),
  );

  server.registerTool(
    "bighub_outcomes_pending",
    {
      description: "List decisions still awaiting outcome reports.",
      outputSchema: AnyOutputSchema,
      inputSchema: {
        min_age_hours: z.number().int().optional(),
        limit: z.number().int().default(50),
      },
    },
    async ({ min_age_hours, limit }) =>
      toResult(
        await client.request({
          method: "GET",
          path: "/outcomes/pending/list",
          query: cleanObject({ min_age_hours, limit }),
        }),
      ),
  );

  server.registerTool(
    "bighub_outcomes_analytics",
    {
      description: "Outcome analytics summary.",
      outputSchema: AnyOutputSchema,
      inputSchema: {
        domain: z.string().optional(),
        since: z.string().optional(),
        until: z.string().optional(),
      },
    },
    async ({ domain, since, until }) =>
      toResult(
        await client.request({
          method: "GET",
          path: "/outcomes/analytics/summary",
          query: cleanObject({ domain, since, until }),
        }),
      ),
  );

  server.registerTool(
    "bighub_outcomes_taxonomy",
    {
      description: "Supported outcome status taxonomy.",
      inputSchema: {},
    },
    async () => toResult(await client.request({ method: "GET", path: "/outcomes/taxonomy" })),
  );

  server.registerTool(
    "bighub_outcomes_recommendation_quality",
    {
      description:
        "Recommendation quality analytics: follow rate, quadrants (followed+positive, followed+negative, ignored+positive, ignored+negative), breakdowns by domain/actor, and notable examples of BIGHUB helped / missed.",
      inputSchema: {
        domain: z.string().optional().describe("Filter by domain"),
        since: z.string().optional().describe("Start date (ISO 8601)"),
        until: z.string().optional().describe("End date (ISO 8601)"),
      },
    },
    async ({ domain, since, until }) => {
      return toResult(
        await client.request({
          method: "GET",
          path: `/outcomes/analytics/recommendation-quality`,
          query: cleanObject({ domain, since, until }),
        }),
      );
    },
  );

  server.registerTool(
    "bighub_outcomes_partner_view",
    {
      description:
        "Self-contained partner/domain view: decisions evaluated, follow rate, positive after following, trend, by-action breakdown, sparse evidence pockets, and helped/missed examples.",
      inputSchema: {
        domain: z.string().describe("The domain to generate the partner view for"),
      },
    },
    async ({ domain }) =>
      toResult(
        await client.request({
          method: "GET",
          path: `/outcomes/analytics/partner-view/${encodeURIComponent(domain)}`,
        }),
      ),
  );

  // ---------------------------------------------------------------------------
  // Precedents — Case-based reasoning from past decisions
  // ---------------------------------------------------------------------------

  server.registerTool(
    "bighub_precedents_query",
    {
      description: "Query similar past decision cases.",
      outputSchema: AnyOutputSchema,
      inputSchema: {
        domain: z.string(),
        action: z.string(),
        tool: z.string().optional(),
        actor_type: z.string().default("AI_AGENT"),
        axes: JsonObjectSchema.optional(),
        risk_score: z.number().optional(),
        intent: z.string().optional(),
        min_similarity: z.number().optional(),
        max_results: z.number().int().optional(),
        require_outcome: z.boolean().optional(),
      },
    },
    async ({ domain, action, tool, actor_type, axes, risk_score, intent, min_similarity, max_results, require_outcome }) =>
      toResult(
        await client.request({
          method: "POST",
          path: "/precedents/query",
          body: cleanObject({ domain, action, tool, actor_type, axes, risk_score, intent, min_similarity, max_results, require_outcome }),
        }),
      ),
  );

  server.registerTool(
    "bighub_precedents_signals",
    {
      description: "Get aggregated precedent signals for an action.",
      outputSchema: AnyOutputSchema,
      inputSchema: {
        domain: z.string(),
        action: z.string(),
        tool: z.string().optional(),
        actor_type: z.string().default("AI_AGENT"),
        axes: JsonObjectSchema.optional(),
        risk_score: z.number().optional(),
      },
    },
    async ({ domain, action, tool, actor_type, axes, risk_score }) =>
      toResult(
        await client.request({
          method: "POST",
          path: "/precedents/signals",
          body: cleanObject({ domain, action, tool, actor_type, axes, risk_score }),
        }),
      ),
  );

  server.registerTool(
    "bighub_precedents_stats",
    {
      description: "Get precedent engine statistics.",
      inputSchema: {},
    },
    async () => toResult(await client.request({ method: "GET", path: "/precedents/stats" })),
  );

  // ---------------------------------------------------------------------------
  // Calibration — Prediction vs reality
  // ---------------------------------------------------------------------------

  server.registerTool(
    "bighub_calibration_report",
    {
      description: "Calibration report: how well do predicted risk scores match real outcomes.",
      outputSchema: AnyOutputSchema,
      inputSchema: {
        domain: z.string().optional(),
        tool: z.string().optional(),
        risk_band: z.string().optional(),
      },
    },
    async ({ domain, tool, risk_band }) =>
      toResult(
        await client.request({
          method: "GET",
          path: "/calibration/report",
          query: cleanObject({ domain, tool, risk_band }),
        }),
      ),
  );

  server.registerTool(
    "bighub_calibration_reliability",
    {
      description: "Calibration reliability diagram data.",
      outputSchema: AnyOutputSchema,
      inputSchema: {
        domain: z.string().optional(),
        tool: z.string().optional(),
      },
    },
    async ({ domain, tool }) =>
      toResult(
        await client.request({
          method: "GET",
          path: "/calibration/reliability",
          query: cleanObject({ domain, tool }),
        }),
      ),
  );

  server.registerTool(
    "bighub_calibration_drift",
    {
      description: "Detect calibration drift over time.",
      outputSchema: AnyOutputSchema,
      inputSchema: {
        window_days: z.number().int().optional(),
        domain: z.string().optional(),
      },
    },
    async ({ window_days, domain }) =>
      toResult(
        await client.request({
          method: "GET",
          path: "/calibration/drift",
          query: cleanObject({ window_days, domain }),
        }),
      ),
  );

  server.registerTool(
    "bighub_calibration_breakdown",
    {
      description: "Calibration breakdown by dimension.",
      outputSchema: AnyOutputSchema,
      inputSchema: {
        by: z.string().default("domain"),
      },
    },
    async ({ by }) =>
      toResult(
        await client.request({
          method: "GET",
          path: "/calibration/breakdown",
          query: { by },
        }),
      ),
  );

  server.registerTool(
    "bighub_calibration_feedback",
    {
      description: "Calibration feedback and improvement suggestions.",
      outputSchema: AnyOutputSchema,
      inputSchema: {
        domain: z.string().optional(),
      },
    },
    async ({ domain }) =>
      toResult(
        await client.request({
          method: "GET",
          path: "/calibration/feedback",
          query: cleanObject({ domain }),
        }),
      ),
  );

  server.registerTool(
    "bighub_calibration_observe",
    {
      description: "Submit a calibration observation (predicted risk vs real outcome).",
      outputSchema: AnyOutputSchema,
      inputSchema: {
        case_id: z.string(),
        predicted_risk: z.number(),
        outcome_status: z.string(),
        domain: z.string().optional(),
        tool: z.string().optional(),
        action: z.string().optional(),
        actor_type: z.string().optional(),
        verdict: z.string().optional(),
      },
    },
    async ({ case_id, predicted_risk, outcome_status, domain, tool, action, actor_type, verdict }) =>
      toResult(
        await client.request({
          method: "POST",
          path: "/calibration/observe",
          body: cleanObject({ case_id, predicted_risk, outcome_status, domain, tool, action, actor_type, verdict }),
        }),
      ),
  );

  server.registerTool(
    "bighub_calibration_quality_history",
    {
      description: "Daily quality score over time — powers the Learning chart. Returns quality_score (1 − Brier), positive_rate per day.",
      outputSchema: AnyOutputSchema,
      inputSchema: {
        days: z.number().int().min(1).max(180).default(30).describe("Number of days to include"),
        domain: z.string().optional(),
      },
    },
    async ({ days, domain }) =>
      toResult(
        await client.request({
          method: "GET",
          path: "/calibration/quality-history",
          query: cleanObject({ days, domain }),
        }),
      ),
  );

  // ---------------------------------------------------------------------------
  // Retrieval — Multi-signal decision retrieval engine
  // ---------------------------------------------------------------------------

  server.registerTool(
    "bighub_retrieval_query",
    {
      description: "Multi-signal decision retrieval: find relevant past cases for an upcoming action.",
      outputSchema: AnyOutputSchema,
      inputSchema: {
        domain: z.string(),
        action: z.string(),
        tool: z.string().optional(),
        actor_type: z.string().default("AI_AGENT"),
        axes: JsonObjectSchema.optional(),
        risk_score: z.number().optional(),
        strategy: z.string().default("balanced"),
        strategy_name: z.string().optional(),
      },
    },
    async ({ domain, action, tool, actor_type, axes, risk_score, strategy, strategy_name }) =>
      toResult(
        await client.request({
          method: "POST",
          path: "/retrieval/query",
          body: cleanObject({
            domain,
            action,
            tool,
            actor_type,
            axes,
            risk_score,
            strategy: strategy_name ?? strategy,
            strategy_name: strategy_name ?? strategy,
          }),
        }),
      ),
  );

  server.registerTool(
    "bighub_retrieval_query_explained",
    {
      description: "Retrieval query with full scoring explanation.",
      outputSchema: AnyOutputSchema,
      inputSchema: {
        domain: z.string(),
        action: z.string(),
        tool: z.string().optional(),
        actor_type: z.string().default("AI_AGENT"),
        axes: JsonObjectSchema.optional(),
        risk_score: z.number().optional(),
        strategy: z.string().default("balanced"),
        strategy_name: z.string().optional(),
      },
    },
    async ({ domain, action, tool, actor_type, axes, risk_score, strategy, strategy_name }) =>
      toResult(
        await client.request({
          method: "POST",
          path: "/retrieval/query/explained",
          body: cleanObject({
            domain,
            action,
            tool,
            actor_type,
            axes,
            risk_score,
            strategy: strategy_name ?? strategy,
            strategy_name: strategy_name ?? strategy,
          }),
        }),
      ),
  );

  server.registerTool(
    "bighub_retrieval_strategies",
    {
      description: "List available retrieval strategies.",
      inputSchema: {},
    },
    async () => toResult(await client.request({ method: "GET", path: "/retrieval/strategies" })),
  );

  server.registerTool(
    "bighub_retrieval_strategy",
    {
      description: "Get details of a retrieval strategy by name.",
      outputSchema: AnyOutputSchema,
      inputSchema: { name: z.string() },
    },
    async ({ name }) =>
      toResult(await client.request({ method: "GET", path: `/retrieval/strategy/${name}` })),
  );

  server.registerTool(
    "bighub_retrieval_index_case",
    {
      description: "Index a decision case into the retrieval engine.",
      outputSchema: AnyOutputSchema,
      inputSchema: {
        case_id: z.string(),
        org_id: z.string(),
        tool: z.string(),
        action: z.string(),
        domain: z.string(),
        actor_type: z.string().default("AI_AGENT"),
        risk_score: z.number().default(0.0),
        verdict: z.string().default("ALLOWED"),
        axes: JsonObjectSchema.optional(),
      },
    },
    async ({ case_id, org_id, tool, action, domain, actor_type, risk_score, verdict, axes }) =>
      toResult(
        await client.request({
          method: "POST",
          path: "/retrieval/index",
          body: cleanObject({ case_id, org_id, tool, action, domain, actor_type, risk_score, verdict, axes }),
        }),
      ),
  );

  server.registerTool(
    "bighub_retrieval_stats",
    {
      description: "Get retrieval engine statistics.",
      inputSchema: {},
    },
    async () => toResult(await client.request({ method: "GET", path: "/retrieval/stats" })),
  );

  server.registerTool(
    "bighub_retrieval_compare",
    {
      description: "Compare two retrieval strategies on the same query. Returns scored results, risk level, confidence, and stability for each strategy.",
      outputSchema: AnyOutputSchema,
      inputSchema: {
        domain: z.string().default(""),
        tool: z.string().default(""),
        action: z.string().default(""),
        actor_type: z.string().default(""),
        axes: JsonObjectSchema.optional().describe("Risk axes as {axis_name: score}"),
        risk_score: z.number().default(0.0),
        intent: z.string().default(""),
        strategy_a: z.string().default("balanced").describe("First strategy to compare"),
        strategy_b: z.string().default("consequence-focused").describe("Second strategy to compare"),
      },
    },
    async ({ domain, tool, action, actor_type, axes, risk_score, intent, strategy_a, strategy_b }) =>
      toResult(
        await client.request({
          method: "POST",
          path: "/retrieval/compare",
          body: cleanObject({ domain, tool, action, actor_type, axes, risk_score, intent, strategy_a, strategy_b }),
        }),
      ),
  );

  // ---------------------------------------------------------------------------
  // Features — Decision feature layer
  // ---------------------------------------------------------------------------

  server.registerTool(
    "bighub_features_compute",
    {
      description: "Compute decision features for a case.",
      outputSchema: AnyOutputSchema,
      inputSchema: {
        case_id: z.string(),
        org_id: z.string(),
        case_data: JsonObjectSchema,
        precedent_data: JsonObjectSchema.optional(),
        advisory_data: JsonObjectSchema.optional(),
      },
    },
    async ({ case_id, org_id, case_data, precedent_data, advisory_data }) =>
      toResult(
        await client.request({
          method: "POST",
          path: "/features/compute",
          body: cleanObject({ case_id, org_id, case_data, precedent_data, advisory_data }),
        }),
      ),
  );

  server.registerTool(
    "bighub_features_snapshot",
    {
      description: "Create a versioned feature snapshot for a case.",
      outputSchema: AnyOutputSchema,
      inputSchema: {
        case_id: z.string(),
        tag: z.string().optional(),
      },
    },
    async ({ case_id, tag }) =>
      toResult(
        await client.request({
          method: "POST",
          path: "/features/snapshot",
          body: cleanObject({ case_id, tag }),
        }),
      ),
  );

  server.registerTool(
    "bighub_features_get_snapshot",
    {
      description: "Get a feature snapshot by ID.",
      outputSchema: AnyOutputSchema,
      inputSchema: { snapshot_id: z.string() },
    },
    async ({ snapshot_id }) =>
      toResult(await client.request({ method: "GET", path: `/features/snapshot/${snapshot_id}` })),
  );

  server.registerTool(
    "bighub_features_list_snapshots",
    {
      description: "List feature snapshots.",
      outputSchema: AnyOutputSchema,
      inputSchema: {
        tag: z.string().optional(),
        case_id: z.string().optional(),
      },
    },
    async ({ tag, case_id }) =>
      toResult(
        await client.request({
          method: "GET",
          path: "/features/snapshots",
          query: cleanObject({ tag, case_id }),
        }),
      ),
  );

  server.registerTool(
    "bighub_features_explain",
    {
      description: "Explain computed features for a case.",
      outputSchema: AnyOutputSchema,
      inputSchema: {
        case_id: z.string(),
        feature_key: z.string().optional(),
      },
    },
    async ({ case_id, feature_key }) =>
      toResult(
        await client.request({
          method: "GET",
          path: feature_key ? `/features/explain/${case_id}/${feature_key}` : `/features/explain/${case_id}`,
        }),
      ),
  );

  server.registerTool(
    "bighub_features_export",
    {
      description: "Export all features for a case.",
      outputSchema: AnyOutputSchema,
      inputSchema: { case_id: z.string() },
    },
    async ({ case_id }) =>
      toResult(await client.request({ method: "GET", path: `/features/export/${case_id}` })),
  );

  server.registerTool(
    "bighub_features_schema",
    {
      description: "Get the feature schema (all defined features and types).",
      inputSchema: {},
    },
    async () => toResult(await client.request({ method: "GET", path: "/features/schema" })),
  );

  server.registerTool(
    "bighub_features_stats",
    {
      description: "Get feature layer statistics.",
      inputSchema: {},
    },
    async () => toResult(await client.request({ method: "GET", path: "/features/stats" })),
  );

  server.registerTool(
    "bighub_features_compute_batch",
    {
      description: "Compute feature vectors for multiple cases in a single request (max 500).",
      outputSchema: AnyOutputSchema,
      inputSchema: {
        cases: z.array(
          z.object({
            case_id: z.string(),
            org_id: z.string().default(""),
            case_data: JsonObjectSchema.optional(),
            outcome_data: JsonObjectSchema.optional(),
            precedent_data: JsonObjectSchema.optional(),
            calibration_data: JsonObjectSchema.optional(),
            advisory_data: JsonObjectSchema.optional(),
            domain_stats: JsonObjectSchema.optional(),
          }),
        ).min(1).max(500),
      },
    },
    async ({ cases }) =>
      toResult(
        await client.request({
          method: "POST",
          path: "/features/compute/batch",
          body: { cases },
        }),
      ),
  );

  server.registerTool(
    "bighub_features_compare",
    {
      description: "Compare two feature snapshots or cached vectors. Returns changed features with diffs.",
      outputSchema: AnyOutputSchema,
      inputSchema: {
        snapshot_id_a: z.string().optional(),
        snapshot_id_b: z.string().optional(),
        case_id_a: z.string().optional(),
        case_id_b: z.string().optional(),
        changed_only: z.boolean().default(true).describe("Only return features that differ"),
      },
    },
    async ({ snapshot_id_a, snapshot_id_b, case_id_a, case_id_b, changed_only }) =>
      toResult(
        await client.request({
          method: "POST",
          path: "/features/compare",
          body: cleanObject({ snapshot_id_a, snapshot_id_b, case_id_a, case_id_b, changed_only }),
        }),
      ),
  );

  server.registerTool(
    "bighub_features_export_batch",
    {
      description: "Export flat feature dicts for multiple cases (max 500).",
      outputSchema: AnyOutputSchema,
      inputSchema: {
        case_ids: z.array(z.string()).min(1).max(500),
      },
    },
    async ({ case_ids }) =>
      toResult(
        await client.request({
          method: "POST",
          path: "/features/export/batch",
          body: { case_ids },
        }),
      ),
  );

  // ---------------------------------------------------------------------------
  // Insights — Patterns, advisories, and action profiles
  // ---------------------------------------------------------------------------

  server.registerTool(
    "bighub_insights_advise",
    {
      description: "Get decision advisory for a proposed action based on learned patterns.",
      outputSchema: AnyOutputSchema,
      inputSchema: {
        tool: z.string(),
        action: z.string(),
        domain: z.string(),
        actor_type: z.string().default("AI_AGENT"),
        risk_band: z.string().optional(),
      },
    },
    async ({ tool, action, domain, actor_type, risk_band }) =>
      toResult(
        await client.request({
          method: "POST",
          path: "/insights/advise",
          body: cleanObject({ tool, action, domain, actor_type, risk_band }),
        }),
      ),
  );

  server.registerTool(
    "bighub_insights_patterns",
    {
      description: "List detected decision patterns.",
      outputSchema: AnyOutputSchema,
      inputSchema: {
        pattern_type: z.string().optional(),
        domain: z.string().optional(),
        tool: z.string().optional(),
        min_severity: z.string().optional(),
      },
    },
    async ({ pattern_type, domain, tool, min_severity }) =>
      toResult(
        await client.request({
          method: "GET",
          path: "/insights/patterns",
          query: cleanObject({ pattern_type, domain, tool, min_severity }),
        }),
      ),
  );

  server.registerTool(
    "bighub_insights_learn",
    {
      description: "Trigger pattern learning from accumulated cases.",
      inputSchema: {},
    },
    async () => toResult(await client.request({ method: "GET", path: "/insights/patterns/learn" })),
  );

  server.registerTool(
    "bighub_insights_profile",
    {
      description: "Get action quality profile for a tool/action/domain.",
      outputSchema: AnyOutputSchema,
      inputSchema: {
        tool: z.string().optional(),
        action: z.string().optional(),
        domain: z.string().optional(),
      },
    },
    async ({ tool, action, domain }) =>
      toResult(
        await client.request({
          method: "GET",
          path: "/insights/profile",
          query: cleanObject({ tool, action, domain }),
        }),
      ),
  );

  // ---------------------------------------------------------------------------
  // Simulations — Chronos simulation vault
  // ---------------------------------------------------------------------------

  server.registerTool(
    "bighub_simulations_list",
    {
      description: "List persisted simulation snapshots.",
      outputSchema: AnyOutputSchema,
      inputSchema: {
        domain: z.string().optional(),
        tool: z.string().optional(),
        with_outcome: z.boolean().optional(),
        limit: z.number().int().default(50),
      },
    },
    async ({ domain, tool, with_outcome, limit }) =>
      toResult(
        await client.request({
          method: "GET",
          path: "/simulations",
          query: cleanObject({ domain, tool, with_outcome, limit }),
        }),
      ),
  );

  server.registerTool(
    "bighub_simulations_get",
    {
      description: "Get a simulation snapshot by ID.",
      outputSchema: AnyOutputSchema,
      inputSchema: { snapshot_id: z.string() },
    },
    async ({ snapshot_id }) =>
      toResult(await client.request({ method: "GET", path: `/simulations/${snapshot_id}` })),
  );

  server.registerTool(
    "bighub_simulations_by_request",
    {
      description: "Get simulation snapshot for a given request_id.",
      outputSchema: AnyOutputSchema,
      inputSchema: { request_id: z.string() },
    },
    async ({ request_id }) =>
      toResult(await client.request({ method: "GET", path: `/simulations/by-request/${request_id}` })),
  );

  server.registerTool(
    "bighub_simulations_compare",
    {
      description: "Compare simulation prediction vs real outcome for a request.",
      outputSchema: AnyOutputSchema,
      inputSchema: { request_id: z.string() },
    },
    async ({ request_id }) =>
      toResult(await client.request({ method: "GET", path: `/simulations/by-request/${request_id}/compare` })),
  );

  server.registerTool(
    "bighub_simulations_accuracy",
    {
      description: "Simulation accuracy metrics.",
      outputSchema: AnyOutputSchema,
      inputSchema: {
        domain: z.string().optional(),
        tool: z.string().optional(),
      },
    },
    async ({ domain, tool }) =>
      toResult(
        await client.request({
          method: "GET",
          path: "/simulations/accuracy",
          query: cleanObject({ domain, tool }),
        }),
      ),
  );

  server.registerTool(
    "bighub_simulations_stats",
    {
      description: "Get simulation vault statistics.",
      inputSchema: {},
    },
    async () => toResult(await client.request({ method: "GET", path: "/simulations/stats" })),
  );

  // ---------------------------------------------------------------------------
  // Learning — Outcome-to-learning pipeline management
  // ---------------------------------------------------------------------------

  server.registerTool(
    "bighub_learning_strategy",
    {
      description: "Get current learning strategy version and configuration.",
      inputSchema: {},
    },
    async () => toResult(await client.request({ method: "GET", path: "/ops/learning/strategy" })),
  );

  server.registerTool(
    "bighub_learning_runs",
    {
      description: "List recent learning pipeline runs.",
      outputSchema: AnyOutputSchema,
      inputSchema: {
        limit: z.number().int().default(50),
      },
    },
    async ({ limit }) =>
      toResult(
        await client.request({
          method: "GET",
          path: "/ops/learning/runs",
          query: { limit },
        }),
      ),
  );

  server.registerTool(
    "bighub_learning_recompute",
    {
      description: "Trigger recomputation of learning artifacts for a scope.",
      outputSchema: AnyOutputSchema,
      inputSchema: {
        domain: z.string().default(""),
        action_family: z.string().default(""),
        force: z.boolean().default(false),
        limit: z.number().int().default(5000),
        async_mode: z.boolean().default(true),
      },
    },
    async ({ domain, action_family, force, limit, async_mode }) =>
      toResult(
        await client.request({
          method: "POST",
          path: "/ops/learning/recompute",
          body: { domain, action_family, force, limit, async_mode },
        }),
      ),
  );

  server.registerTool(
    "bighub_learning_backfill",
    {
      description: "Backfill learning artifacts from historical outcomes.",
      outputSchema: AnyOutputSchema,
      inputSchema: {
        domain: z.string().default(""),
        action_family: z.string().default(""),
        force: z.boolean().default(false),
        limit: z.number().int().default(5000),
        async_mode: z.boolean().default(true),
      },
    },
    async ({ domain, action_family, force, limit, async_mode }) =>
      toResult(
        await client.request({
          method: "POST",
          path: "/ops/learning/backfill",
          body: { domain, action_family, force, limit, async_mode },
        }),
      ),
  );

  // ═══════════════════════════════════════════════════════════════════════════
  // Batch action evaluation
  // ═══════════════════════════════════════════════════════════════════════════

  server.registerTool(
    "bighub_actions_evaluate_batch",
    {
      description:
        "Evaluate multiple actions in a single request via /actions/evaluate/batch. " +
        "Each element follows the same schema as bighub_actions_evaluate. Max 100 actions. Rate limited: 10/min.",
      outputSchema: AnyOutputSchema,
      inputSchema: {
        actions: z.array(
          z.object({
            action: z.string(),
            actor: z.string().default("AI_AGENT"),
            value: z.number().optional(),
            target: z.string().optional(),
            domain: z.string().optional(),
            context: JsonObjectSchema.optional(),
            dry_run: z.boolean().default(false),
            check_contracts: z.boolean().default(false),
          }),
        ).max(100),
        idempotency_key: z.string().optional(),
      },
    },
    async ({ actions, idempotency_key }) =>
      toResult(
        await client.request({
          method: "POST",
          path: "/actions/evaluate/batch",
          body: { actions },
          idempotencyKey: idempotency_key,
        }),
      ),
  );

  // ═══════════════════════════════════════════════════════════════════════════
  // Ingest — real-world event lifecycle
  // ═══════════════════════════════════════════════════════════════════════════

  server.registerTool(
    "bighub_ingest_event",
    {
      description:
        "Ingest a single real-world event into BIGHUB. Events flow through: " +
        "normalize → enrich → correlate → sync. BIGHUB links the event to the " +
        "correct decision lifecycle using any provided correlation key.",
      outputSchema: AnyOutputSchema,
      inputSchema: {
        event_type: z.string().default("OUTCOME_OBSERVED").describe(
          "Event type: ACTION_PROPOSED, ACTION_EXECUTED, ACTION_BLOCKED, " +
          "HUMAN_OVERRIDE, HUMAN_APPROVAL, HUMAN_REJECTION, " +
          "OUTCOME_OBSERVED, OUTCOME_UPDATED, ROLLBACK_PERFORMED, " +
          "CORRECTION_APPLIED, ESCALATION_TRIGGERED, FRAUD_DETECTED, " +
          "CHURN_SIGNAL, TICKET_REOPENED, REFUND_COMPLETED, PRICING_CORRECTION",
        ),
        timestamp: z.string().optional().describe("ISO 8601 timestamp (defaults to now)"),
        request_id: z.string().default("").describe("Link to BIGHUB decision (from /actions/evaluate response)"),
        case_id: z.string().default("").describe("Link to DecisionCase"),
        validation_id: z.string().default("").describe("Link to rule validation"),
        external_ref: z.string().default("").describe("Your system's reference (e.g. order_id)"),
        tenant_ref: z.string().default("").describe("Tenant-level reference"),
        entity_id: z.string().default("").describe("Entity being acted on"),
        session_id: z.string().default("").describe("Session / conversation ID"),
        action: JsonObjectSchema.optional().describe("Action payload: {tool, action, arguments, value, target, domain}"),
        context: JsonObjectSchema.optional().describe("Context: {risk_score, axes, environment, ...}"),
        execution: JsonObjectSchema.optional().describe("Execution result: {executed, status_code, error, ...}"),
        outcome: JsonObjectSchema.optional().describe("Outcome: {status, description, revenue_impact, ...}"),
        human_feedback: JsonObjectSchema.optional().describe("Human: {feedback_type, decision, reason, ...}"),
        intent: JsonObjectSchema.optional().describe("Intent: {goal_summary, trigger_source, actor_type, ...}"),
        adapter: z.string().default("generic_webhook"),
        domain: z.string().default(""),
        tags: z.array(z.string()).optional(),
      },
    },
    async (args) =>
      toResult(
        await client.request({
          method: "POST",
          path: "/ingest",
          body: cleanObject(args as Record<string, unknown>),
        }),
      ),
  );

  server.registerTool(
    "bighub_ingest_batch",
    {
      description:
        "Ingest multiple real-world events in a single request (max 500). " +
        "Events are processed through the same normalize → enrich → correlate → sync pipeline.",
      outputSchema: AnyOutputSchema,
      inputSchema: {
        events: z.array(JsonObjectSchema).max(500).describe("Raw event payloads"),
        adapter: z.string().default("generic_webhook"),
        domain: z.string().default(""),
      },
    },
    async ({ events, adapter, domain }) =>
      toResult(
        await client.request({
          method: "POST",
          path: "/ingest/batch",
          body: { events, adapter, domain },
        }),
      ),
  );

  server.registerTool(
    "bighub_ingest_reconcile",
    {
      description:
        "Reconcile a late-arriving outcome with a previous decision. " +
        "Use when the outcome arrives after the initial event was already ingested.",
      outputSchema: AnyOutputSchema,
      inputSchema: {
        key_name: z.string().describe("Correlation key: request_id, case_id, external_ref, tenant_ref, or entity_id"),
        key_value: z.string().describe("Value of the correlation key"),
        outcome: JsonObjectSchema.describe("Outcome event payload to attach"),
      },
    },
    async ({ key_name, key_value, outcome }) =>
      toResult(
        await client.request({
          method: "POST",
          path: "/ingest/reconcile",
          body: { key_name, key_value, outcome },
        }),
      ),
  );

  server.registerTool(
    "bighub_ingest_lifecycles",
    {
      description: "List decision lifecycles with optional status filter.",
      outputSchema: AnyOutputSchema,
      inputSchema: {
        status_filter: z.string().optional().describe("Filter by lifecycle status"),
        limit: z.number().int().default(50),
      },
    },
    async ({ status_filter, limit }) =>
      toResult(
        await client.request({
          method: "GET",
          path: "/ingest/lifecycles",
          query: cleanObject({ status_filter, limit }),
        }),
      ),
  );

  server.registerTool(
    "bighub_ingest_lifecycle",
    {
      description: "Get a specific decision lifecycle by correlation key.",
      outputSchema: AnyOutputSchema,
      inputSchema: {
        request_id: z.string().optional(),
        case_id: z.string().optional(),
        external_ref: z.string().optional(),
        tenant_ref: z.string().optional(),
        entity_id: z.string().optional(),
      },
    },
    async ({ request_id, case_id, external_ref, tenant_ref, entity_id }) =>
      toResult(
        await client.request({
          method: "GET",
          path: "/ingest/lifecycle",
          query: cleanObject({ request_id, case_id, external_ref, tenant_ref, entity_id }),
        }),
      ),
  );

  server.registerTool(
    "bighub_ingest_pending",
    {
      description: "List lifecycles awaiting outcome reconciliation.",
      outputSchema: AnyOutputSchema,
      inputSchema: {
        limit: z.number().int().default(50),
      },
    },
    async ({ limit }) =>
      toResult(
        await client.request({
          method: "GET",
          path: "/ingest/pending",
          query: { limit },
        }),
      ),
  );

  server.registerTool(
    "bighub_ingest_stale",
    {
      description: "List stale lifecycles that have not received an outcome within the expected timeframe.",
      outputSchema: AnyOutputSchema,
      inputSchema: {
        stale_after_days: z.number().int().default(7),
        limit: z.number().int().default(50),
      },
    },
    async ({ stale_after_days, limit }) =>
      toResult(
        await client.request({
          method: "GET",
          path: "/ingest/stale",
          query: { stale_after_days, limit },
        }),
      ),
  );

  server.registerTool(
    "bighub_ingest_stats",
    {
      description: "Get organization-wide ingestion statistics (event counts, adapter breakdown, lifecycle status distribution).",
      outputSchema: AnyOutputSchema,
      inputSchema: {},
    },
    async () =>
      toResult(
        await client.request({
          method: "GET",
          path: "/ingest/stats",
        }),
      ),
  );

  server.registerTool(
    "bighub_ingest_adapters",
    {
      description: "List available ingestion adapters and domain normalizers.",
      outputSchema: AnyOutputSchema,
      inputSchema: {},
    },
    async () =>
      toResult(
        await client.request({
          method: "GET",
          path: "/ingest/adapters",
        }),
      ),
  );
}
