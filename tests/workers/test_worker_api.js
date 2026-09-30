/**
 * Comprehensive integration tests for SignalBrief Cloudflare Worker API.
 * Uses Node.js native test runner (node:test) and mocks D1 and R2 environments.
 */

import test from "node:test";
import assert from "node:assert/strict";
import worker from "../../workers/index.js";

// Mock R2 Storage Bucket
class MockR2Bucket {
  constructor() {
    this.storage = new Map();
  }
  async get(key) {
    if (!this.storage.has(key)) return null;
    const item = this.storage.get(key);
    return {
      body: item.value,
      customMetadata: item.metadata || {},
    };
  }
  async put(key, value, options = {}) {
    this.storage.set(key, { value, metadata: options.customMetadata });
    return { key };
  }
}

// Mock D1 Database Client
class MockD1Database {
  constructor() {
    this.subscribers = [
      { id: "u1", email: "sub1@example.com", name: "User 1", timezone: "UTC", custom_keywords: "[]", delivery_time_utc: "06:00" },
      { id: "u2", email: "sub2@example.com", name: "User 2", timezone: "UTC", custom_keywords: "[]", delivery_time_utc: "06:00" },
    ];
    this.reports = new Map();
    this.deliveryLogs = [];
    this.pipelineRuns = [];
  }

  prepare(sql) {
    const db = this;
    let boundArgs = [];

    const stmt = {
      bind(...args) {
        boundArgs = args;
        return stmt;
      },
      async first() {
        if (sql.includes("SELECT count(*) as count FROM users")) {
          return { count: db.subscribers.length };
        }
        if (sql.includes("SELECT * FROM reports WHERE domain_id = ?")) {
          const list = Array.from(db.reports.values());
          return list[list.length - 1] || null;
        }
        if (sql.includes("SELECT * FROM reports WHERE id = ?")) {
          return db.reports.get(boundArgs[0]) || null;
        }
        if (sql.includes("SELECT u.id, u.email")) {
          const u = db.subscribers.find((s) => s.id === boundArgs[1]);
          return u || null;
        }
        return null;
      },
      async all() {
        if (sql.includes("SELECT u.id, u.email")) {
          return { results: db.subscribers.slice(0, 10) };
        }
        if (sql.includes("SELECT id, report_date, headline")) {
          return { results: Array.from(db.reports.values()) };
        }
        if (sql.includes("SELECT id, domain_id, report_date")) {
          return { results: Array.from(db.reports.values()) };
        }
        if (sql.includes("SELECT rd.*")) {
          const repId = boundArgs[0];
          const rep = db.reports.get(repId);
          if (!rep || !rep.developments) return { results: [] };
          return {
            results: rep.developments.map((d) => ({
              ...d,
              sources_json: JSON.stringify(d.sources || []),
            })),
          };
        }
        if (sql.includes("SELECT id, user_id, report_id")) {
          return { results: db.deliveryLogs };
        }
        return { results: [] };
      },
      async run() {
        if (sql.includes("INSERT INTO delivery_logs")) {
          db.deliveryLogs.push({ id: boundArgs[0], email: boundArgs[3], status: boundArgs[4] });
        }
        if (sql.includes("INSERT INTO pipeline_runs")) {
          db.pipelineRuns.push({ id: boundArgs[0], status: boundArgs[3] });
        }
        return { success: true };
      },
    };
    return stmt;
  }

  async batch(statements) {
    for (const stmt of statements) {
      await stmt.run();
    }
    return { success: true };
  }
}

function createEnv(overrides = {}) {
  return {
    ENVIRONMENT: "test",
    DEFAULT_DOMAIN: "manufacturing",
    REPORT_RECIPIENT_LIMIT: 7,
    SIGNALBRIEF_INTERNAL_KEY: "test-secret-key",
    ALLOWED_ORIGINS: "http://localhost:4321,https://signalbrief.pages.dev",
    DB: new MockD1Database(),
    REPORTS_BUCKET: new MockR2Bucket(),
    ...overrides,
  };
}

test("Worker API: GET /api/health", async () => {
  const env = createEnv();
  const req = new Request("http://localhost/api/health", { method: "GET" });
  const res = await worker.fetch(req, env);
  assert.strictEqual(res.status, 200);
  const data = await res.json();
  assert.strictEqual(data.status, "healthy");
  assert.strictEqual(data.service, "signalbrief-api");
  assert.strictEqual(data.database_connected, true);
  assert.strictEqual(data.storage_connected, true);
});

test("Worker API: CORS headers and OPTIONS preflight", async () => {
  const env = createEnv();
  const req = new Request("http://localhost/api/health", {
    method: "OPTIONS",
    headers: { Origin: "http://localhost:4321" },
  });
  const res = await worker.fetch(req, env);
  assert.strictEqual(res.status, 200);
  assert.strictEqual(res.headers.get("Access-Control-Allow-Origin"), "http://localhost:4321");
});

test("Worker API: GET /api/domains", async () => {
  const env = createEnv();
  const req = new Request("http://localhost/api/domains");
  const res = await worker.fetch(req, env);
  assert.strictEqual(res.status, 200);
  const data = await res.json();
  assert.strictEqual(data.domains.length, 1);
  assert.strictEqual(data.domains[0].id, "manufacturing");
});

test("Worker API: GET /api/subscribers adheres to pilot quota", async () => {
  const env = createEnv();
  const req = new Request("http://localhost/api/subscribers");
  const res = await worker.fetch(req, env);
  assert.strictEqual(res.status, 200);
  const data = await res.json();
  assert.strictEqual(data.max_subscribers, 7);
  assert.strictEqual(data.subscribers.length, 2);
});

test("Worker API: POST /api/subscribers/invite quota enforcement", async () => {
  const env = createEnv();
  // Fill subscribers to 7
  for (let i = 3; i <= 7; i++) {
    env.DB.subscribers.push({ id: `u${i}`, email: `sub${i}@example.com`, name: `U${i}` });
  }
  assert.strictEqual(env.DB.subscribers.length, 7);

  // 8th invite must fail
  const req = new Request("http://localhost/api/subscribers/invite", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: "Bearer test-secret-key",
    },
    body: JSON.stringify({ email: "overflow@example.com", name: "Overflow" }),
  });
  const res = await worker.fetch(req, env);
  assert.strictEqual(res.status, 400);
  const data = await res.json();
  assert.match(data.error, /quota exceeded/i);
});

test("Worker API: POST /api/subscribers/invite requires authorization", async () => {
  const env = createEnv();
  const req = new Request("http://localhost/api/subscribers/invite", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email: "test@example.com", name: "Test" }),
  });
  const res = await worker.fetch(req, env);
  assert.strictEqual(res.status, 401);
});

test("Worker API: POST /api/internal/report requires valid bearer token", async () => {
  const env = createEnv();
  const payload = {
    report: {
      id: "rep_auth_test",
      domain_id: "manufacturing",
      report_date: "2026-09-29",
      developments: [
        { headline: "Test", sources: [{ title: "T", url: "https://example.com" }] },
      ],
    },
    html: "<html>Test</html>",
  };

  // Missing token
  const req1 = new Request("http://localhost/api/internal/report", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const res1 = await worker.fetch(req1, env);
  assert.strictEqual(res1.status, 401);

  // Bad token
  const req2 = new Request("http://localhost/api/internal/report", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: "Bearer wrong-secret",
    },
    body: JSON.stringify(payload),
  });
  const res2 = await worker.fetch(req2, env);
  assert.strictEqual(res2.status, 401);
});

test("Worker API: POST /api/internal/report validates citation completeness", async () => {
  const env = createEnv();
  const invalidPayload = {
    report: {
      id: "rep_invalid_citations",
      domain_id: "manufacturing",
      report_date: "2026-09-29",
      developments: [
        { headline: "Uncited Rumor", sources: [] }, // 0 citations violates rule
      ],
    },
    html: "<html>Test</html>",
  };

  const req = new Request("http://localhost/api/internal/report", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: "Bearer test-secret-key",
    },
    body: JSON.stringify(invalidPayload),
  });
  const res = await worker.fetch(req, env);
  assert.strictEqual(res.status, 400);
  const data = await res.json();
  assert.match(data.error, /100% citation coverage required/i);
});

test("Worker API: POST /api/internal/report succeeds and writes to R2 and D1", async () => {
  const env = createEnv();
  const validPayload = {
    report: {
      id: "rep_20260929_manufacturing",
      domain_id: "manufacturing",
      domain_name: "Manufacturing",
      report_date: "2026-09-29",
      executive_summary: "Comprehensive manufacturing briefing.",
      article_count: 75,
      developments: [
        {
          id: "dev_01",
          headline: "Industrial Robotics Expansion",
          what_changed: "Robotics deployed.",
          why_it_matters: "Speeds production.",
          what_to_watch: "Q4 orders.",
          topic_label: "Robotics",
          relevance_score: 0.95,
          sources: [
            { article_id: "a1", source_name: "NIST", title: "Study", url: "https://example.com/robotics" },
          ],
        },
      ],
    },
    html: "<!DOCTYPE html><html><body><h1>Manufacturing Brief</h1></body></html>",
  };

  const req = new Request("http://localhost/api/internal/report", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: "Bearer test-secret-key",
    },
    body: JSON.stringify(validPayload),
  });
  const res = await worker.fetch(req, env);
  assert.strictEqual(res.status, 201);
  const data = await res.json();
  assert.strictEqual(data.success, true);
  assert.strictEqual(data.report_id, "rep_20260929_manufacturing");
  assert.strictEqual(data.r2_key, "reports/2026/09/29/rep_20260929_manufacturing.html");
  assert.strictEqual(data.storage_stored, true);

  // Verify stored in Mock R2
  const r2Obj = await env.REPORTS_BUCKET.get("reports/2026/09/29/rep_20260929_manufacturing.html");
  assert.ok(r2Obj);
  assert.strictEqual(r2Obj.body, validPayload.html);
});

test("Worker API: GET /api/reports/:id/html retrieves from R2", async () => {
  const env = createEnv();
  await env.REPORTS_BUCKET.put(
    "reports/rep_html_test.html",
    "<!DOCTYPE html><html><body>Report Content</body></html>"
  );

  const req = new Request("http://localhost/api/reports/rep_html_test/html");
  const res = await worker.fetch(req, env);
  assert.strictEqual(res.status, 200);
  assert.strictEqual(res.headers.get("Content-Type"), "text/html; charset=utf-8");
  const body = await res.text();
  assert.strictEqual(body, "<!DOCTYPE html><html><body>Report Content</body></html>");
});

test("Worker Email: duplicate send prevention", async () => {
  const env = createEnv();
  const emailWorker = (await import("../../workers/email/index.js")).default;
  const recipient = { id: "u_dup", email: "dup@example.com" };
  const report = {
    id: "rep_dup_test",
    domain_id: "manufacturing",
    domain_name: "Manufacturing",
    report_date: "2026-09-29",
    executive_summary: "Exec summary",
  };

  // Mock hasDelivered logic in MockD1Database
  let deliveredOnce = false;
  env.DB.prepare = (sql) => {
    return {
      bind(...args) {
        return {
          async first() {
            if (sql.includes("delivery_logs") && sql.includes("delivery_status = 'delivered'")) {
              return deliveredOnce ? { id: "del_exists" } : null;
            }
            return null;
          },
          async run() {
            if (sql.includes("INSERT INTO delivery_logs")) {
              deliveredOnce = true;
            }
            return { success: true };
          },
        };
      },
    };
  };

  // Run 1: Should deliver
  const res1 = await emailWorker.sendReportEmail(recipient, report, env);
  assert.strictEqual(res1.success, true);
  assert.strictEqual(res1.skipped, undefined);

  // Run 2: Should be skipped as duplicate
  const res2 = await emailWorker.sendReportEmail(recipient, report, env);
  assert.strictEqual(res2.success, true);
  assert.strictEqual(res2.skipped, true);
  assert.strictEqual(res2.reason, "Already delivered");
});

test("Worker API: PUT /api/preferences updates keywords and email state", async () => {
  const env = createEnv();
  const req = new Request("http://localhost/api/preferences", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      userId: "u1",
      domainId: "manufacturing",
      custom_keywords: ["robotics", "automation"],
      email_enabled: true,
    }),
  });
  const res = await worker.fetch(req, env);
  assert.strictEqual(res.status, 200);
  const data = await res.json();
  assert.strictEqual(data.success, true);
});

test("Worker API: GET /api/delivery-status returns recent logs", async () => {
  const env = createEnv();
  env.DB.deliveryLogs = [
    { id: "del_1", user_id: "u1", recipient_email: "test@example.com", delivery_status: "delivered" },
  ];
  const req = new Request("http://localhost/api/delivery-status");
  const res = await worker.fetch(req, env);
  assert.strictEqual(res.status, 200);
  const data = await res.json();
  assert.strictEqual(data.count, 1);
  assert.strictEqual(data.logs[0].recipient_email, "test@example.com");
});

