export type JsonValue =
  | string
  | number
  | boolean
  | null
  | JsonValue[]
  | { [key: string]: JsonValue };

export interface BighubClientConfig {
  baseUrl: string;
  apiKey?: string;
  bearerToken?: string;
  timeoutMs: number;
  maxRetries: number;
  userAgent: string;
}

export interface RequestOptions {
  method: "GET" | "POST" | "PATCH" | "DELETE";
  path: string;
  query?: Record<string, unknown>;
  body?: Record<string, unknown> | unknown[];
  headers?: Record<string, string>;
  idempotencyKey?: string;
}

export class BighubHttpError extends Error {
  public readonly statusCode?: number;
  public readonly requestId?: string;
  public readonly code?: string;
  public readonly responseBody?: unknown;

  constructor(message: string, options?: { statusCode?: number; requestId?: string; code?: string; responseBody?: unknown }) {
    super(message);
    this.name = "BighubHttpError";
    this.statusCode = options?.statusCode;
    this.requestId = options?.requestId;
    this.code = options?.code;
    this.responseBody = options?.responseBody;
  }
}

const RETRYABLE_STATUS_CODES = new Set([408, 409, 425, 429, 500, 502, 503, 504]);

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function shouldRetry(statusCode?: number, err?: unknown): boolean {
  if (err !== undefined) {
    return true;
  }
  return statusCode !== undefined && RETRYABLE_STATUS_CODES.has(statusCode);
}

function buildRetryDelayMs(attempt: number): number {
  const base = 250;
  const cap = 2500;
  const delay = Math.min(cap, base * 2 ** Math.max(0, attempt - 1));
  const jitter = Math.random() * Math.min(250, delay / 2);
  return delay + jitter;
}

function ensureSecureBaseUrl(baseUrl: string): void {
  const url = new URL(baseUrl);
  const scheme = url.protocol.replace(":", "").toLowerCase();
  const host = (url.hostname || "").toLowerCase();
  const allowInsecure = new Set(["1", "true", "yes", "on"]).has(
    (process.env.BIGHUB_ALLOW_INSECURE_HTTP || "").trim().toLowerCase(),
  );

  const localhost = host === "localhost" || host === "127.0.0.1";
  const privateHost = host.endsWith(".local");
  if (scheme !== "https" && !(localhost || (allowInsecure && privateHost))) {
    throw new Error(
      "Insecure base_url is not allowed. Use https:// or set BIGHUB_ALLOW_INSECURE_HTTP=true only for localhost/private hosts.",
    );
  }
}

function buildUrl(baseUrl: string, path: string, query?: Record<string, unknown>): string {
  const url = new URL(`${baseUrl.replace(/\/+$/, "")}/${path.replace(/^\/+/, "")}`);
  if (query) {
    for (const [key, value] of Object.entries(query)) {
      if (value === undefined || value === null) {
        continue;
      }
      if (Array.isArray(value)) {
        for (const item of value) {
          if (item !== undefined && item !== null) {
            url.searchParams.append(key, String(item));
          }
        }
      } else {
        url.searchParams.set(key, String(value));
      }
    }
  }
  return url.toString();
}

function extractErrorMetadata(body: unknown): { requestId?: string; code?: string; detail?: unknown } {
  if (!body || typeof body !== "object") {
    return {};
  }
  const value = body as Record<string, unknown>;
  const detail = value.detail;
  const requestId =
    (typeof value.request_id === "string" ? value.request_id : undefined) ||
    (typeof value.validation_id === "string" ? value.validation_id : undefined) ||
    (value.error && typeof value.error === "object" && typeof (value.error as Record<string, unknown>).request_id === "string"
      ? ((value.error as Record<string, unknown>).request_id as string)
      : undefined);
  const code = detail && typeof detail === "object" && typeof (detail as Record<string, unknown>).code === "string"
    ? ((detail as Record<string, unknown>).code as string)
    : undefined;
  return { requestId, code, detail };
}

async function parseResponseBody(response: Response): Promise<unknown> {
  const contentType = response.headers.get("content-type") || "";
  if (contentType.includes("application/json")) {
    try {
      return await response.json();
    } catch {
      return {};
    }
  }
  const text = await response.text();
  return text ? { text } : {};
}

export class BighubHttpClient {
  private readonly config: BighubClientConfig;

  constructor(config: BighubClientConfig) {
    ensureSecureBaseUrl(config.baseUrl);
    this.config = config;
  }

  async request<T = unknown>(options: RequestOptions): Promise<T> {
    const url = buildUrl(this.config.baseUrl, options.path, options.query);
    const headers: Record<string, string> = {
      Accept: "application/json",
      "User-Agent": this.config.userAgent,
      ...(options.headers || {}),
    };

    if (this.config.apiKey) {
      headers["X-API-Key"] = this.config.apiKey;
    } else if (this.config.bearerToken) {
      headers.Authorization = `Bearer ${this.config.bearerToken}`;
    }
    if (options.idempotencyKey) {
      headers["Idempotency-Key"] = options.idempotencyKey;
    }
    if (options.body !== undefined) {
      headers["Content-Type"] = "application/json";
    }

    let lastError: unknown;
    for (let attempt = 1; attempt <= this.config.maxRetries + 1; attempt += 1) {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), this.config.timeoutMs);
      try {
        const response = await fetch(url, {
          method: options.method,
          headers,
          body: options.body !== undefined ? JSON.stringify(options.body) : undefined,
          signal: controller.signal,
        });
        clearTimeout(timeoutId);

        if (shouldRetry(response.status) && attempt <= this.config.maxRetries) {
          await sleep(buildRetryDelayMs(attempt));
          continue;
        }

        const body = await parseResponseBody(response);
        if (response.ok) {
          return body as T;
        }

        const { requestId, code, detail } = extractErrorMetadata(body);
        const message = typeof detail === "string" ? detail : response.statusText || "API error";
        throw new BighubHttpError(message, {
          statusCode: response.status,
          requestId,
          code,
          responseBody: body,
        });
      } catch (error) {
        clearTimeout(timeoutId);
        lastError = error;
        const isAbort = error instanceof DOMException && error.name === "AbortError";
        const retryable = shouldRetry(undefined, error);
        if (isAbort) {
          if (attempt <= this.config.maxRetries) {
            await sleep(buildRetryDelayMs(attempt));
            continue;
          }
          throw new BighubHttpError(`Request timed out: ${options.method} ${options.path}`);
        }
        if (retryable && attempt <= this.config.maxRetries) {
          await sleep(buildRetryDelayMs(attempt));
          continue;
        }
        if (error instanceof BighubHttpError) {
          throw error;
        }
        throw new BighubHttpError(`Network error: ${options.method} ${options.path}`);
      }
    }

    if (lastError instanceof BighubHttpError) {
      throw lastError;
    }
    throw new BighubHttpError(`Request failed after retries: ${options.method} ${options.path}`);
  }
}
