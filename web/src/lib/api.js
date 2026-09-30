/**
 * SignalBrief Centralized API Client
 * Connects frontend views and components to the Cloudflare Worker REST API.
 */

export const API_BASE = (
  (typeof import.meta !== "undefined" && import.meta.env && import.meta.env.PUBLIC_API_URL) ||
  (typeof window !== "undefined" && window.location.origin) ||
  "http://localhost:8787"
).replace(/\/$/, "");

async function fetchJson(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  try {
    const res = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...(options.headers || {}),
      },
    });

    if (!res.ok) {
      const errBody = await res.json().catch(() => ({}));
      throw new Error(errBody.error || `Request failed with status ${res.status}`);
    }

    return await res.json();
  } catch (err) {
    console.warn(`[SignalBrief API] Error calling ${endpoint}:`, err.message);
    throw err;
  }
}

export async function getHealth() {
  return await fetchJson("/api/health");
}

export async function getDomains() {
  return await fetchJson("/api/domains");
}

export async function getReports(domain = "manufacturing", limit = 30, offset = 0) {
  return await fetchJson(`/api/reports?domain=${encodeURIComponent(domain)}&limit=${limit}&offset=${offset}`);
}

export async function getLatestReport(domain = "manufacturing") {
  return await fetchJson(`/api/reports/latest?domain=${encodeURIComponent(domain)}`);
}

export async function getReportById(id) {
  return await fetchJson(`/api/reports/${encodeURIComponent(id)}`);
}

export async function getReportsCalendar(domain = "manufacturing", limit = 30) {
  return await fetchJson(`/api/calendar?domain=${encodeURIComponent(domain)}&limit=${limit}`);
}

export async function getUserPreferences(userId, domainId = "manufacturing") {
  return await fetchJson(`/api/preferences?userId=${encodeURIComponent(userId)}&domainId=${encodeURIComponent(domainId)}`);
}

export async function updateUserPreferences(userId, domainId, keywords, emailEnabled) {
  return await fetchJson("/api/preferences", {
    method: "PUT",
    body: JSON.stringify({
      userId,
      domainId,
      custom_keywords: Array.isArray(keywords) ? keywords : String(keywords).split(",").map((k) => k.trim()),
      email_enabled: Boolean(emailEnabled),
    }),
  });
}

export async function inviteSubscriber(email, name = "", domainId = "manufacturing") {
  return await fetchJson("/api/subscribers/invite", {
    method: "POST",
    body: JSON.stringify({ email, name, domainId }),
  });
}

export async function getSubscribers(domainId = "manufacturing") {
  return await fetchJson(`/api/subscribers?domain=${encodeURIComponent(domainId)}`);
}

export async function getDeliveryLogs(limit = 20) {
  return await fetchJson(`/api/delivery-status?limit=${limit}`);
}

export async function getPipelineTelemetry() {
  return await fetchJson("/api/pipeline/telemetry");
}
