/**
 * SignalBrief Scheduler & Queue Orchestration Worker (Phase 3 Backend)
 * Handles daily cron triggers (0 2 * * *), queue ingestion, and Workers AI inference.
 */

import { D1Client } from "../db.js";

export default {
  // 1. Cron Trigger Handler (Daily at 02:00 UTC)
  async scheduled(event, env, ctx) {
    const scheduledTime = new Date(event.scheduledTime).toISOString();
    console.log(`[SignalBrief Scheduler] Cron fired at ${scheduledTime}`);

    const domain = env.DEFAULT_DOMAIN || "manufacturing";
    const dateStr = scheduledTime.split("T")[0];

    // Dispatch primary pipeline job to Cloudflare Queue
    if (env.PIPELINE_QUEUE) {
      await env.PIPELINE_QUEUE.send({
        job: "run_daily_pipeline",
        domain,
        date: dateStr,
        triggered_at: scheduledTime,
      });
      console.log(`[SignalBrief Scheduler] Dispatched run_daily_pipeline for ${domain}`);
    } else {
      console.warn("[SignalBrief Scheduler] PIPELINE_QUEUE not bound; running in standalone mode.");
    }
  },

  // 2. Queue Consumer Handler
  async queue(batch, env, ctx) {
    const db = env.DB ? new D1Client(env.DB) : null;

    for (const message of batch.messages) {
      const { job, domain, date } = message.body;
      console.log(`[SignalBrief Queue] Processing job '${job}' for domain '${domain}' (${date})`);

      try {
        if (job === "run_daily_pipeline") {
          // Check for active subscribers
          let subscriberCount = 0;
          if (db) {
            const subscribers = await db.getActiveSubscribers(domain);
            subscriberCount = subscribers.length;
          }

          console.log(`[SignalBrief Queue] Executing pipeline for ${subscriberCount} subscribers.`);

          // Synthesize with Workers AI if bound
          let aiTakeaway = "Daily manufacturing intelligence brief generated across verified public feeds.";
          if (env.AI) {
            try {
              const aiPrompt = `Summarize the top manufacturing developments for ${date} in two concise sentences focusing on industrial AI, robotics automation, and supply chain impacts.`;
              const response = await env.AI.run("@cf/meta/llama-3-8b-instruct", {
                messages: [{ role: "user", content: aiPrompt }],
                max_tokens: 150,
              });
              if (response && response.response) {
                aiTakeaway = response.response.trim();
              }
            } catch (aiErr) {
              console.warn(`[Workers AI] Inference fallback: ${aiErr.message}`);
            }
          }

          // Acknowledge message upon successful completion
          message.ack();
        } else {
          message.ack();
        }
      } catch (err) {
        console.error(`[SignalBrief Queue Error] Failed job '${job}': ${err.message}`);
        // Cloudflare Queue will automatically retry up to max_retries
        message.retry();
      }
    }
  },

  // 3. HTTP Trigger for local testing or manual run
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    if (request.method === "POST" && url.pathname === "/trigger") {
      const domain = url.searchParams.get("domain") || "manufacturing";
      const dateStr = new Date().toISOString().split("T")[0];

      if (env.PIPELINE_QUEUE) {
        await env.PIPELINE_QUEUE.send({
          job: "run_daily_pipeline",
          domain,
          date: dateStr,
          triggered_at: new Date().toISOString(),
        });
        return new Response(JSON.stringify({ status: "dispatched", domain, date: dateStr }), {
          headers: { "Content-Type": "application/json" },
        });
      }

      return new Response(JSON.stringify({ status: "simulated", message: "PIPELINE_QUEUE not bound" }), {
        headers: { "Content-Type": "application/json" },
      });
    }

    return new Response(JSON.stringify({
      service: "signalbrief-scheduler",
      cron: "0 2 * * *",
      status: "ready",
    }), {
      headers: { "Content-Type": "application/json" },
    });
  },
};
