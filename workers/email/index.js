/**
 * SignalBrief Email Delivery Worker
 * Handles sending daily intelligence reports to the 10 invited subscribers
 * via Resend API (or MailChannels) with duplicate prevention and D1 logging.
 */

import { D1Client } from "../db.js";

export default {
  /**
   * Send a daily brief email to a single recipient.
   */
  async sendReportEmail(recipient, report, env) {
    const db = env.DB ? new D1Client(env.DB) : null;
    const recipientEmail = recipient.email;
    const dashboardBase = env.DASHBOARD_URL || "https://signalbrief.local";
    const reportUrl = `${dashboardBase}/report/${report.id}`;
    const unsubscribeUrl = `${dashboardBase}/settings?userId=${recipient.id}&domainId=${report.domain_id || "manufacturing"}`;
    const domainLabel = report.domain_name || "Manufacturing";
    const subject = `SignalBrief [${domainLabel}]: Daily Intelligence Brief (${report.report_date})`;

    // 1. Duplicate-Send Prevention
    if (db) {
      const alreadyDelivered = await db.hasDelivered(recipient.id, report.id);
      if (alreadyDelivered) {
        console.log(`[Email Dispatch] Report ${report.id} already delivered to ${recipientEmail}; skipping duplicate.`);
        return { success: true, recipient: recipientEmail, skipped: true, reason: "Already delivered" };
      }
    }

    console.log(`[Email Dispatch] Delivering report ${report.id} to ${recipientEmail}`);

    const htmlContent = report.html_content || `
      <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #0284c7;">SignalBrief ${domainLabel} Intelligence Brief</h2>
        <p style="font-size: 14px; color: #475569;">${report.report_date}</p>
        <p style="font-size: 16px; color: #1e293b; line-height: 1.5;">${report.executive_summary || "Daily intelligence summary."}</p>
        <div style="margin: 24px 0;">
          <a href="${reportUrl}" style="background-color: #0284c7; color: white; padding: 10px 20px; text-decoration: none; border-radius: 6px; font-weight: bold; font-size: 14px;">Open Complete Brief →</a>
        </div>
        <hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 30px 0;" />
        <p style="font-size: 11px; color: #94a3b8;">
          You received this email as an invited SignalBrief subscriber.
          <a href="${unsubscribeUrl}" style="color: #64748b;">Manage preferences or unsubscribe</a>.
        </p>
      </div>
    `;

    const plainTextContent = `
SIGNALBRIEF ${domainLabel.toUpperCase()} INTELLIGENCE BRIEF
Date: ${report.report_date}

${report.executive_summary || ""}

Read the full report online:
${reportUrl}

Manage preferences:
${unsubscribeUrl}
    `.trim();

    try {
      let providerMessageId = `msg_sim_${Date.now()}`;

      // A. Outbound via Resend API
      if (env.RESEND_API_KEY) {
        const resendPayload = {
          from: env.SENDER_EMAIL || "SignalBrief <onboarding@resend.dev>",
          to: [recipientEmail],
          subject,
          html: htmlContent,
          text: plainTextContent,
        };

        const resendResponse = await fetch("https://api.resend.com/emails", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${env.RESEND_API_KEY.trim()}`,
          },
          body: JSON.stringify(resendPayload),
        });

        if (!resendResponse.ok) {
          const errText = await resendResponse.text();
          throw new Error(`Resend API error (${resendResponse.status}): ${errText}`);
        }

        const resendData = await resendResponse.json();
        providerMessageId = resendData.id || providerMessageId;
      }
      // B. Outbound via MailChannels (Cloudflare Workers free relay)
      else if (env.SEND_EMAILS === "true") {
        const mailChannelsPayload = {
          personalizations: [{ to: [{ email: recipientEmail, name: recipient.name || recipientEmail }] }],
          from: { email: env.SENDER_EMAIL || "briefs@signalbrief.local", name: "SignalBrief Intelligence" },
          subject,
          content: [
            { type: "text/plain", value: plainTextContent },
            { type: "text/html", value: htmlContent },
          ],
        };

        const mcResponse = await fetch("https://api.mailchannels.net/tx/v1/send", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(mailChannelsPayload),
        });

        if (!mcResponse.ok) {
          throw new Error(`MailChannels error (${mcResponse.status}): ${await mcResponse.text()}`);
        }
        providerMessageId = `mc_${Date.now()}`;
      } else {
        console.log(`[Email Dispatch Simulation] No RESEND_API_KEY; simulated delivery to ${recipientEmail}`);
      }

      // Log success to D1
      if (db) {
        await db.logDelivery(recipient.id, report.id, recipientEmail, "delivered", providerMessageId);
      }

      return { success: true, recipient: recipientEmail, provider_id: providerMessageId };
    } catch (err) {
      console.error(`[Email Delivery Failure] ${recipientEmail}: ${err.message}`);
      if (db) {
        await db.logDelivery(recipient.id, report.id, recipientEmail, "failed", null, err.message);
      }
      return { success: false, recipient: recipientEmail, error: err.message };
    }
  },

  /**
   * Batch dispatch to all active subscribers (enforcing max 10 subscriber pilot quota).
   */
  async dispatchDailyBatch(report, env) {
    const db = env.DB ? new D1Client(env.DB) : null;
    let subscribers = [];
    if (db) {
      subscribers = await db.getActiveSubscribers(report.domain_id);
    }

    // Limit to max 7 invited pilot subscribers
    const limit = parseInt(env.REPORT_RECIPIENT_LIMIT || "7", 10);
    const targetSubscribers = subscribers.slice(0, limit);
    console.log(`[Batch Dispatch] Processing email delivery for ${targetSubscribers.length} subscribers (quota: ${limit}).`);

    const results = [];
    for (const sub of targetSubscribers) {
      const res = await this.sendReportEmail(sub, report, env);
      results.push(res);
    }
    return results;
  },
};
