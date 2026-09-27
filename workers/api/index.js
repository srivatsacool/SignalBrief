/**
 * SignalBrief REST API Worker (Phase 3 Backend)
 * Handles client endpoints for dashboard, calendar, and preferences.
 */

import { D1Client } from "../db.js";

const CORS_HEADERS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, PUT, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Authorization",
};

function jsonResponse(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      "Content-Type": "application/json",
      ...CORS_HEADERS,
    },
  });
}

export default {
  async fetch(request, env, ctx) {
    if (request.method === "OPTIONS") {
      return new Response(null, { headers: CORS_HEADERS });
    }

    const url = new URL(request.url);
    const path = url.pathname;
    const db = env.DB ? new D1Client(env.DB) : null;

    try {
      // 1. Health check
      if (path === "/api/health") {
        return jsonResponse({
          status: "healthy",
          service: "signalbrief-api",
          environment: env.ENVIRONMENT || "production",
          timestamp: new Date().toISOString(),
          database_connected: Boolean(env.DB),
          storage_connected: Boolean(env.REPORTS_BUCKET),
        });
      }

      // 2. Domains catalog
      if (path === "/api/domains") {
        return jsonResponse({
          domains: [
            {
              id: "manufacturing",
              name: "Manufacturing",
              description: "Industrial AI, smart factories, robotics automation, and supply chain resilience.",
              active: true,
              subscriber_count: 10,
              max_subscribers: 10,
            },
          ],
        });
      }

      // 3. Latest Report
      if (path === "/api/reports/latest") {
        const domain = url.searchParams.get("domain") || "manufacturing";
        if (db) {
          const report = await db.getLatestReport(domain);
          if (report) return jsonResponse(report);
        }
        // Fallback mock representation if DB uninitialized
        return jsonResponse({
          id: `rep_${new Date().toISOString().split("T")[0].replace(/-/g, "")}_${domain}`,
          domain_id: domain,
          domain_name: "Manufacturing",
          report_date: new Date().toISOString().split("T")[0],
          headline: "SignalBrief Daily Manufacturing Intelligence Brief",
          executive_summary: "Automated analysis of industrial AI deployment, robotics expansion, and federal standards across verified public sources.",
          developments: [],
          status: "preview",
        });
      }

      // 4. Report by ID
      if (path.startsWith("/api/reports/") && !path.endsWith("/html")) {
        const reportId = path.split("/")[3];
        if (db) {
          const report = await db.getReportById(reportId);
          if (report) return jsonResponse(report);
        }
        return jsonResponse({ error: "Report not found" }, 404);
      }

      // 5. Raw HTML Report from R2 Storage
      if (path.startsWith("/api/reports/") && path.endsWith("/html")) {
        const reportId = path.split("/")[3];
        if (env.REPORTS_BUCKET) {
          const r2Object = await env.REPORTS_BUCKET.get(`reports/${reportId}.html`);
          if (r2Object) {
            return new Response(r2Object.body, {
              headers: {
                "Content-Type": "text/html; charset=utf-8",
                ...CORS_HEADERS,
              },
            });
          }
        }
        return new Response("<html><body>Report archive not found</body></html>", {
          status: 404,
          headers: { "Content-Type": "text/html" },
        });
      }

      // 6. Calendar View
      if (path === "/api/calendar") {
        const domain = url.searchParams.get("domain") || "manufacturing";
        if (db) {
          const calendar = await db.getReportsCalendar(domain, 30);
          return jsonResponse({ domain, reports: calendar });
        }
        return jsonResponse({ domain, reports: [] });
      }

      // 7. Subscriber Management (User preferences for the 10 invited subscribers)
      if (path === "/api/subscribers" && request.method === "GET") {
        const domain = url.searchParams.get("domain") || "manufacturing";
        if (db) {
          const subs = await db.getActiveSubscribers(domain);
          return jsonResponse({ domain, count: subs.length, subscribers: subs });
        }
        return jsonResponse({ domain, count: 0, subscribers: [] });
      }

      if (path === "/api/subscribers/preferences" && request.method === "POST") {
        const body = await request.json();
        const { userId, domainId, keywords, emailEnabled } = body;
        if (!userId || !domainId) {
          return jsonResponse({ error: "Missing userId or domainId" }, 400);
        }
        if (db) {
          await db.updateUserPreferences(userId, domainId, keywords || [], emailEnabled !== false);
          return jsonResponse({ success: true, message: "Preferences updated" });
        }
        return jsonResponse({ success: true, simulated: true });
      }

      return jsonResponse({ error: "Endpoint not found" }, 404);
    } catch (err) {
      console.error(`[API Error] ${err.message}`, err.stack);
      return jsonResponse({ error: err.message }, 500);
    }
  },
};
