/**
 * SignalBrief REST API Worker (Phase 3 Backend)
 * Handles client endpoints for dashboard, calendar, and preferences.
 */

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    if (url.pathname === "/api/health") {
      return new Response(JSON.stringify({ status: "healthy", timestamp: new Date().toISOString() }), {
        headers: { "Content-Type": "application/json" },
      });
    }
    return new Response(JSON.stringify({ message: "SignalBrief API service operational" }), {
      headers: { "Content-Type": "application/json" },
    });
  },
};
