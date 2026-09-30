/**
 * SignalBrief REST API Worker
 * Full-featured edge API handling dashboard queries, preferences,
 * internal report ingestion, subscriber management, and R2 report retrieval.
 */

import { D1Client } from "../db.js";
import emailWorker from "../email/index.js";

function getCorsHeaders(request, env) {
  const origin = request.headers.get("Origin");
  const allowed = (env.ALLOWED_ORIGINS || "*").split(",").map((s) => s.trim());
  const allowOrigin = (allowed.includes("*") || (origin && allowed.includes(origin)))
    ? (origin || "*")
    : allowed[0] || "*";

  return {
    "Access-Control-Allow-Origin": allowOrigin,
    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
    "Access-Control-Max-Age": "86400",
  };
}

function jsonResponse(data, status = 200, corsHeaders = {}) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      "Content-Type": "application/json",
      ...corsHeaders,
    },
  });
}

export default {
  async fetch(request, env, ctx) {
    const cors = getCorsHeaders(request, env);

    if (request.method === "OPTIONS") {
      return new Response(null, { headers: cors });
    }

    const url = new URL(request.url);
    const path = url.pathname;
    const db = env.DB ? new D1Client(env.DB) : null;

    try {
      // 1. Health check
      if (path === "/api/health") {
        return jsonResponse(
          {
            status: "healthy",
            service: "signalbrief-api",
            environment: env.ENVIRONMENT || "development",
            timestamp: new Date().toISOString(),
            database_connected: Boolean(env.DB),
            storage_connected: Boolean(env.REPORTS_BUCKET),
            default_domain: env.DEFAULT_DOMAIN || "manufacturing",
            max_subscribers: parseInt(env.REPORT_RECIPIENT_LIMIT || "7", 10),
          },
          200,
          cors
        );
      }

      // 2. Domains catalog
      if (path === "/api/domains" && request.method === "GET") {
        return jsonResponse(
          {
            domains: [
              {
                id: "manufacturing",
                name: "Manufacturing",
                description: "Industrial AI, smart factories, robotics automation, and supply chain resilience.",
                active: true,
                max_subscribers: parseInt(env.REPORT_RECIPIENT_LIMIT || "7", 10),
              },
            ],
          },
          200,
          cors
        );
      }

      // 3. Reports List (Paginated)
      if (path === "/api/reports" && request.method === "GET") {
        const domain = url.searchParams.get("domain") || env.DEFAULT_DOMAIN || "manufacturing";
        const limit = Math.min(100, Math.max(1, parseInt(url.searchParams.get("limit") || "30", 10)));
        const offset = Math.max(0, parseInt(url.searchParams.get("offset") || "0", 10));

        if (db) {
          const reports = await db.getReports(domain, limit, offset);
          return jsonResponse({ domain, limit, offset, count: reports.length, reports }, 200, cors);
        }
        return jsonResponse({ domain, limit, offset, count: 0, reports: [] }, 200, cors);
      }

      // 4. Latest Report
      if (path === "/api/reports/latest" && request.method === "GET") {
        const domain = url.searchParams.get("domain") || env.DEFAULT_DOMAIN || "manufacturing";
        if (db) {
          const report = await db.getLatestReport(domain);
          if (report) return jsonResponse(report, 200, cors);
        }
        return jsonResponse(
          {
            id: `rep_${new Date().toISOString().split("T")[0].replace(/-/g, "")}_${domain}`,
            domain_id: domain,
            domain_name: "Manufacturing",
            report_date: new Date().toISOString().split("T")[0],
            headline: "SignalBrief Daily Manufacturing Intelligence Brief",
            executive_summary: "Awaiting first scheduled analytics pipeline execution for this environment.",
            developments: [],
            status: "pending",
          },
          200,
          cors
        );
      }

      // 5. Raw HTML Report from R2 Storage
      if (path.startsWith("/api/reports/") && path.endsWith("/html") && request.method === "GET") {
        const reportId = path.split("/")[3];
        if (env.REPORTS_BUCKET) {
          // Check standard and dated keys
          const candidateKeys = [
            `reports/${reportId}.html`,
          ];
          if (db) {
            const rep = await db.getReportById(reportId);
            if (rep && rep.r2_key) {
              candidateKeys.unshift(rep.r2_key);
            }
          }

          for (const key of candidateKeys) {
            const r2Object = await env.REPORTS_BUCKET.get(key);
            if (r2Object) {
              return new Response(r2Object.body, {
                headers: {
                  "Content-Type": "text/html; charset=utf-8",
                  ...cors,
                },
              });
            }
          }
        }
        return new Response("<!DOCTYPE html><html><body>Report HTML archive not found.</body></html>", {
          status: 404,
          headers: { "Content-Type": "text/html; charset=utf-8", ...cors },
        });
      }

      // 6. Report by ID
      if (path.startsWith("/api/reports/") && request.method === "GET") {
        const reportId = path.split("/")[3];
        if (!reportId) return jsonResponse({ error: "Missing report ID" }, 400, cors);

        if (db) {
          const report = await db.getReportById(reportId);
          if (report) return jsonResponse(report, 200, cors);
        }
        return jsonResponse({ error: "Report not found", id: reportId }, 404, cors);
      }

      // 7. Calendar View
      if (path === "/api/calendar" && request.method === "GET") {
        const domain = url.searchParams.get("domain") || env.DEFAULT_DOMAIN || "manufacturing";
        const limit = Math.min(100, Math.max(1, parseInt(url.searchParams.get("limit") || "30", 10)));
        if (db) {
          const calendar = await db.getReportsCalendar(domain, limit);
          return jsonResponse({ domain, count: calendar.length, reports: calendar }, 200, cors);
        }
        return jsonResponse({ domain, count: 0, reports: [] }, 200, cors);
      }

      // 8. User Preferences (GET /api/preferences)
      if (path === "/api/preferences" && request.method === "GET") {
        const userId = url.searchParams.get("userId");
        const domainId = url.searchParams.get("domainId") || env.DEFAULT_DOMAIN || "manufacturing";
        if (!userId) {
          return jsonResponse({ error: "Query parameter 'userId' is required" }, 400, cors);
        }
        if (db) {
          const prefs = await db.getUserPreferences(userId, domainId);
          if (prefs) return jsonResponse(prefs, 200, cors);
        }
        return jsonResponse({ error: "Subscriber not found" }, 404, cors);
      }

      // 9. Update Preferences (PUT /api/preferences or POST /api/subscribers/preferences)
      if (
        (path === "/api/preferences" && (request.method === "PUT" || request.method === "POST")) ||
        (path === "/api/subscribers/preferences" && request.method === "POST")
      ) {
        const body = await request.json().catch(() => ({}));
        const { userId, domainId, custom_keywords, keywords, email_enabled, emailEnabled } = body;
        const targetDomain = domainId || env.DEFAULT_DOMAIN || "manufacturing";
        const targetKeywords = custom_keywords || keywords || [];
        const isEmailEnabled = email_enabled !== undefined ? email_enabled : (emailEnabled !== false);

        if (!userId) {
          return jsonResponse({ error: "Field 'userId' is required" }, 400, cors);
        }
        if (db) {
          await db.updateUserPreferences(userId, targetDomain, targetKeywords, isEmailEnabled);
          return jsonResponse({ success: true, message: "Preferences updated successfully" }, 200, cors);
        }
        return jsonResponse({ success: true, simulated: true }, 200, cors);
      }

      // 10. Subscriber List (GET /api/subscribers)
      if (path === "/api/subscribers" && request.method === "GET") {
        const domain = url.searchParams.get("domain") || env.DEFAULT_DOMAIN || "manufacturing";
        const maxSubs = parseInt(env.REPORT_RECIPIENT_LIMIT || "7", 10);
        if (db) {
          const subs = await db.getActiveSubscribers(domain);
          return jsonResponse({ domain, count: subs.length, max_subscribers: maxSubs, subscribers: subs }, 200, cors);
        }
        return jsonResponse({ domain, count: 0, max_subscribers: maxSubs, subscribers: [] }, 200, cors);
      }

      // 11. Subscriber Invite (POST /api/subscribers/invite)
      if (path === "/api/subscribers/invite" && request.method === "POST") {
        const authHeader = request.headers.get("Authorization") || "";
        const expectedSecret = env.ADMIN_SECRET_KEY || env.SIGNALBRIEF_INTERNAL_KEY;
        const token = authHeader.replace(/^Bearer\s+/i, "").trim();

        if (!expectedSecret || !token || token !== expectedSecret) {
          return jsonResponse({ error: "Unauthorized: admin authorization required to invite subscribers" }, 401, cors);
        }

        const body = await request.json().catch(() => ({}));
        const { email, name, domainId } = body;
        if (!email || !email.includes("@")) {
          return jsonResponse({ error: "A valid 'email' address is required" }, 400, cors);
        }
        const targetDomain = domainId || env.DEFAULT_DOMAIN || "manufacturing";

        if (db) {
          try {
            const result = await db.inviteSubscriber(email, name, targetDomain);
            return jsonResponse({ success: true, message: "Subscriber invited successfully", ...result }, 201, cors);
          } catch (quotaErr) {
            return jsonResponse({ error: quotaErr.message }, 400, cors);
          }
        }
        return jsonResponse({ success: true, simulated: true, email }, 201, cors);
      }

      // 12. Delivery Status (GET /api/delivery-status)
      if (path === "/api/delivery-status" && request.method === "GET") {
        const limit = Math.min(100, Math.max(1, parseInt(url.searchParams.get("limit") || "50", 10)));
        if (db) {
          const logs = await db.getDeliveryLogs(limit);
          return jsonResponse({ count: logs.length, logs }, 200, cors);
        }
        return jsonResponse({ count: 0, logs: [] }, 200, cors);
      }

      // 13. Pipeline Telemetry — sourced from real D1 pipeline_jobs records
      if (path === "/api/pipeline/telemetry" && request.method === "GET") {
        const domain = url.searchParams.get("domain") || env.DEFAULT_DOMAIN || "manufacturing";
        if (db) {
          const job = await db.getLatestTelemetry(domain);
          if (job) {
            return jsonResponse({
              job_id: job.id,
              status: job.status,
              domain_id: job.domain_id,
              run_date: job.run_date,
              sources_total: job.sources_total || 0,
              articles_collected: job.articles_collected || 0,
              articles_processed: job.articles_processed || 0,
              relevant_articles: job.relevant_articles || 0,
              clusters_formed: job.clusters_formed || 0,
              report_id: job.report_id || null,
              queued_at: job.queued_at,
              started_at: job.started_at,
              completed_at: job.completed_at,
            }, 200, cors);
          }
        }
        // No real jobs yet — return honest zero state
        return jsonResponse({
          status: "no_runs",
          sources_total: 0,
          articles_collected: 0,
          articles_processed: 0,
          relevant_articles: 0,
          clusters_formed: 0,
          report_id: null,
        }, 200, cors);
      }

      // 13b. Create Pipeline Job (POST /api/jobs or POST /trigger)
      // Called by GenerateReportModal or external webhook when triggering a run
      if ((path === "/api/jobs" || path === "/trigger" || path === "/api/pipeline/trigger") && request.method === "POST") {
        const body = await request.json().catch(() => ({}));
        const domain = body.domain || url.searchParams.get("domain") || env.DEFAULT_DOMAIN || "manufacturing";
        const runDate = new Date().toISOString().split("T")[0];
        const randomId = (typeof crypto !== "undefined" && crypto.randomUUID) ? crypto.randomUUID().replace(/-/g, "") : Math.random().toString(36).substring(2, 10);
        const jobId = `job_${domain}_${runDate}_${randomId.substring(0, 8)}`;

        // Generate a cryptographically secure one-time callback token
        const entropy = (typeof crypto !== "undefined" && crypto.randomUUID) ? crypto.randomUUID().replace(/-/g, "") : Math.random().toString(36).substring(2, 18);
        const jobToken = `tok_${entropy}_${Date.now()}`;

        if (db) {
          await db.createJob(jobId, domain, runDate, "user", jobToken);
        }

        // Dispatch GitHub Actions workflow_dispatch if GH_PAT and GH_REPO are configured
        let dispatchResult = { dispatched: false };
        if (env.GH_PAT && env.GH_REPO) {
          try {
            const ghRes = await fetch(
              `https://api.github.com/repos/${env.GH_REPO}/actions/workflows/daily-pipeline.yml/dispatches`,
              {
                method: "POST",
                headers: {
                  "Authorization": `Bearer ${env.GH_PAT}`,
                  "Accept": "application/vnd.github+json",
                  "Content-Type": "application/json",
                  "User-Agent": "SignalBrief-Cloudflare-Worker/1.0",
                  "X-GitHub-Api-Version": "2022-11-28",
                },
                body: JSON.stringify({
                  ref: env.GH_REF || "master",
                  inputs: {
                    domain,
                    sync_to_cloud: "true",
                    dispatch_email: "false",
                    job_id: jobId,
                    job_token: jobToken,
                    worker_api_url: env.WORKER_PUBLIC_URL || "",
                  },
                }),
              }
            );
            const errText = ghRes.status !== 204 ? await ghRes.text() : "";
            dispatchResult = {
              dispatched: ghRes.status === 204,
              http_status: ghRes.status,
              ...(errText ? { detail: errText } : {}),
            };
          } catch (ghErr) {
            console.error(`[Job Dispatch] GitHub API error: ${ghErr.message}`);
            dispatchResult = { dispatched: false, error: ghErr.message };
          }
        } else {
          // GH_PAT not configured — job is queued but won't auto-execute
          console.warn("[Job Dispatch] GH_PAT or GH_REPO not configured; job queued but not dispatched.");
          dispatchResult = { dispatched: false, reason: "GH_PAT not configured" };
        }

        return jsonResponse({
          job_id: jobId,
          status: "queued",
          domain,
          run_date: runDate,
          dispatch: dispatchResult,
          message: dispatchResult.dispatched
            ? "Pipeline job queued and dispatched to GitHub Actions runner."
            : "Pipeline job queued. Configure GH_PAT secret to enable automatic dispatch.",
        }, 201, cors);
      }

      // 13c. Get Job Status (GET /api/jobs/:id)
      if (path.startsWith("/api/jobs/") && request.method === "GET" && path.split("/").length === 4) {
        const jobId = path.split("/")[3];
        if (!jobId) return jsonResponse({ error: "Missing job ID" }, 400, cors);
        if (db) {
          const job = await db.getJobById(jobId);
          if (job) {
            // Security hardening: Never leak the callback job_token to public GET requests
            const { job_token, ...safeJob } = job;
            return jsonResponse(safeJob, 200, cors);
          }
        }
        return jsonResponse({ error: "Job not found", job_id: jobId }, 404, cors);
      }

      // 13d. Job Callback (POST /api/jobs/:id/callback)
      // Called by GitHub Actions (Python pipeline) to report status updates and final metrics
      if (path.match(/^\/api\/jobs\/[^/]+\/callback$/) && request.method === "POST") {
        const pathParts = path.split("/");
        const jobId = pathParts[3];

        // Validate job_token from Authorization header
        const authHeader = request.headers.get("Authorization") || "";
        const providedToken = authHeader.replace(/^Bearer\s+/i, "").trim();

        if (db) {
          const job = await db.getJobById(jobId);
          if (!job) return jsonResponse({ error: "Job not found" }, 404, cors);

          // Verify token matches what was issued at job creation
          if (!job.job_token || !providedToken || providedToken !== job.job_token) {
            return jsonResponse({ error: "Unauthorized: invalid or missing job token" }, 401, cors);
          }

          const body = await request.json().catch(() => ({}));
          const {
            status,
            sources_total,
            articles_collected,
            articles_processed,
            relevant_articles,
            clusters_formed,
            report_id,
            error_message,
          } = body;

          const allowedStatuses = ["running", "completed", "failed", "partial"];
          if (!status || !allowedStatuses.includes(status)) {
            return jsonResponse({ error: `Invalid status. Must be one of: ${allowedStatuses.join(", ")}` }, 400, cors);
          }

          await db.updateJobStatus(jobId, status, {
            sources_total,
            articles_collected,
            articles_processed,
            relevant_articles,
            clusters_formed,
            report_id,
            error_message,
          });

          return jsonResponse({ success: true, job_id: jobId, status }, 200, cors);
        }
        return jsonResponse({ error: "Database not available" }, 503, cors);
      }

      // 14. Internal Ingestion Endpoint (POST /api/internal/report)
      // Secured by Bearer token matching SIGNALBRIEF_INTERNAL_KEY
      if (path === "/api/internal/report" && request.method === "POST") {
        const authHeader = request.headers.get("Authorization") || "";
        const expectedSecret = env.SIGNALBRIEF_INTERNAL_KEY;
        const token = authHeader.replace(/^Bearer\s+/i, "").trim();

        if (!expectedSecret || !token || token !== expectedSecret) {
          return jsonResponse({ error: "Unauthorized: invalid or missing bearer token" }, 401, cors);
        }

        const body = await request.json().catch(() => null);
        if (!body || !body.report) {
          return jsonResponse({ error: "Invalid payload: 'report' object is required" }, 400, cors);
        }

        const report = body.report;
        const html = body.html || "";
        const dispatchEmail = Boolean(body.dispatch_email || env.AUTO_DISPATCH_EMAIL === "true");

        // Validate report contract
        if (!report.id || !report.report_date || !report.domain_id) {
          return jsonResponse({ error: "Report payload missing required fields (id, report_date, domain_id)" }, 400, cors);
        }
        if (!report.developments || !Array.isArray(report.developments) || report.developments.length === 0) {
          return jsonResponse({ error: "Report must contain at least one development" }, 400, cors);
        }
        for (const dev of report.developments) {
          if (!dev.sources || !Array.isArray(dev.sources) || dev.sources.length === 0) {
            return jsonResponse({ error: `Development '${dev.headline || dev.id}' has 0 citations; 100% citation coverage required` }, 400, cors);
          }
        }

        // Generate stable R2 object key: reports/YYYY/MM/DD/report-id.html
        const dateParts = report.report_date.split("-");
        const r2Key = (dateParts.length === 3)
          ? `reports/${dateParts[0]}/${dateParts[1]}/${dateParts[2]}/${report.id}.html`
          : `reports/${report.id}.html`;

        // Store HTML to R2
        if (env.REPORTS_BUCKET && html) {
          await env.REPORTS_BUCKET.put(r2Key, html, {
            httpMetadata: {
              contentType: "text/html; charset=utf-8",
            },
            customMetadata: {
              reportId: report.id,
              domainId: report.domain_id,
              reportDate: report.report_date,
              articleCount: String(report.article_count || 0),
            },
          });
        }

        // Store metadata & developments in D1
        if (db) {
          await db.insertReportWithDevelopments(report, r2Key);
          // Record pipeline run
          await db.recordPipelineRun({
            id: `run_${report.id}`,
            domain_id: report.domain_id,
            run_date: report.report_date,
            status: "completed",
            articles_collected: body.articles_collected || report.article_count || 0,
            articles_processed: body.articles_processed || report.article_count || 0,
            reports_generated: 1,
            emails_sent: 0,
            duration_seconds: body.duration_seconds || 0.0,
          });
          // Update job record if a job_id was provided
          if (body.job_id) {
            await db.updateJobStatus(body.job_id, "completed", {
              articles_collected: body.articles_collected || report.article_count || 0,
              articles_processed: body.articles_processed || report.article_count || 0,
              relevant_articles: body.relevant_articles || 0,
              clusters_formed: body.clusters_formed || 0,
              report_id: report.id,
            });
          }
        }

        // Optional email dispatch
        let emailResults = null;
        if (dispatchEmail && env.RESEND_API_KEY) {
          try {
            report.html_content = html;
            emailResults = await emailWorker.dispatchDailyBatch(report, env);
          } catch (emailErr) {
            console.error(`[Ingestion Email Dispatch Error]: ${emailErr.message}`);
          }
        }

        return jsonResponse(
          {
            success: true,
            report_id: report.id,
            r2_key: r2Key,
            storage_stored: Boolean(env.REPORTS_BUCKET && html),
            database_stored: Boolean(db),
            email_dispatched: Boolean(emailResults),
            message: "Report successfully ingested and archived",
          },
          201,
          cors
        );
      }

      // Default: Not Found
      return jsonResponse({ error: "Endpoint not found", path }, 404, cors);
    } catch (err) {
      console.error(`[API Error] ${err.message}`, err.stack);
      return jsonResponse({ error: "Internal server error", details: err.message }, 500, cors);
    }
  },
};
