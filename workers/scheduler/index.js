/**
 * SignalBrief Scheduler Worker (Phase 3 Backend)
 * Handles daily cron triggers (0 2 * * *) and queues collection/report generation.
 */

export default {
  async scheduled(event, env, ctx) {
    console.log(`[SignalBrief] Daily scheduled run triggered at ${new Date(event.scheduledTime).toISOString()}`);
    // Phase 3 implementation: Dispatch jobs to env.PIPELINE_QUEUE
  },

  async fetch(request, env, ctx) {
    return new Response(JSON.stringify({ status: "ok", service: "scheduler" }), {
      headers: { "Content-Type": "application/json" },
    });
  },
};
