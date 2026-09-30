/**
 * SignalBrief Unified Cloudflare Worker Entrypoint
 * Routes incoming HTTP fetch requests to REST API Worker,
 * Cron Triggers to Scheduler Worker, and Queue events to Queue Worker.
 */

import apiWorker from "./api/index.js";
import schedulerWorker from "./scheduler/index.js";

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    // Route POST /trigger to API worker for real job lifecycle & dispatch
    if (url.pathname === "/trigger" && request.method === "POST") {
      return await apiWorker.fetch(request, env, ctx);
    }

    // Support manual GET trigger / status endpoint from scheduler
    if (url.pathname === "/trigger") {
      return await schedulerWorker.fetch(request, env, ctx);
    }

    // Route all standard requests to API worker
    return await apiWorker.fetch(request, env, ctx);
  },

  async scheduled(event, env, ctx) {
    return await schedulerWorker.scheduled(event, env, ctx);
  },

  async queue(batch, env, ctx) {
    return await schedulerWorker.queue(batch, env, ctx);
  },
};
