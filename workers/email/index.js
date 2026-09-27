/**
 * SignalBrief Email Delivery Worker (Phase 4 Backend)
 * Handles sending daily intelligence reports to the 10 invited subscribers
 * and logging delivery status to Cloudflare D1.
 */

import { D1Client } from "../db.js";

export default {
  /**
   * Send a daily brief email to a single recipient.
   */
  async sendReportEmail(recipient, report, env) {
    const db = env.DB ? new D1Client(env.DB) : null;
    const recipientEmail = recipient.email;
    const reportUrl = `${env.DASHBOARD_URL || "https://signalbrief.local"}/report/${report.id}`;
    const subject = `SignalBrief [${report.domain_name || "Manufacturing"}]: Daily Intelligence Brief (${report.report_date})`;

    console.log(`[Email Dispatch] Delivering report ${report.id} to ${recipientEmail}`);

    try {
      // Free-tier outbound email via Cloudflare Email Routing or MailChannels API
      const emailPayload = {
        personalizations: [
          {
            to: [{ email: recipientEmail, name: recipient.name || recipientEmail }],
          },
        ],
        from: {
          email: env.SENDER_EMAIL || "briefs@signalbrief.local",
          name: "SignalBrief Intelligence",
        },
        subject,
        content: [
          {
            type: "text/html",
            value: report.html_content || `<p>View today's report at <a href="${reportUrl}">${reportUrl}</a></p>`,
          },
        ],
      };

      // If MailChannels / outbound endpoint configured:
      let providerMessageId = `msg_${Date.now()}`;
      if (env.SEND_EMAILS === "true") {
        const response = await fetch("https://api.mailchannels.net/tx/v1/send", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(emailPayload),
        });
        if (!response.ok) {
          throw new Error(`Email provider error: ${response.status} ${await response.text()}`);
        }
      }

      // Log success to D1
      if (db) {
        await db.logDelivery(recipient.id, report.id, recipientEmail, "delivered", providerMessageId);
      }

      return { success: true, recipient: recipientEmail };
    } catch (err) {
      console.error(`[Email Delivery Failure] ${recipientEmail}: ${err.message}`);
      if (db) {
        await db.logDelivery(recipient.id, report.id, recipientEmail, "failed", null, err.message);
      }
      return { success: false, recipient: recipientEmail, error: err.message };
    }
  },

  /**
   * Batch dispatch to all active subscribers (enforcing max 10 subscriber constraint).
   */
  async dispatchDailyBatch(report, env) {
    const db = env.DB ? new D1Client(env.DB) : null;
    let subscribers = [];
    if (db) {
      subscribers = await db.getActiveSubscribers(report.domain_id);
    }

    // Limit to max 10 invited subscribers
    const targetSubscribers = subscribers.slice(0, 10);
    console.log(`[Batch Dispatch] Sending report to ${targetSubscribers.length} subscribers.`);

    const results = [];
    for (const sub of targetSubscribers) {
      const res = await this.sendReportEmail(sub, report, env);
      results.push(res);
    }
    return results;
  },
};
