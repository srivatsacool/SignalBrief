/**
 * Cloudflare D1 Database Helper Module
 * Provides typed query helpers for Users, Domains, Reports, Developments, and Sources.
 */

export class D1Client {
  constructor(db) {
    this.db = db;
  }

  // --- Users & Preferences ---
  async getActiveSubscribers(domainId = "manufacturing") {
    const query = `
      SELECT u.id, u.email, u.name, u.timezone, up.custom_keywords, up.delivery_time_utc
      FROM users u
      JOIN user_preferences up ON u.id = up.user_id
      WHERE u.status = 'active'
        AND up.email_enabled = 1
        AND up.domain_id = ?
      LIMIT 7;
    `;
    const result = await this.db.prepare(query).bind(domainId).all();
    return result.results || [];
  }

  async updateUserPreferences(userId, domainId, keywords, emailEnabled) {
    // 1. Ensure domain exists to satisfy foreign key constraint
    const domainName = domainId ? domainId.charAt(0).toUpperCase() + domainId.slice(1) : "Manufacturing";
    await this.db.prepare(`
      INSERT OR IGNORE INTO domains (id, name, description)
      VALUES (?, ?, 'Monitored intelligence domain');
    `).bind(domainId, domainName).run();

    // 2. Ensure user exists to satisfy foreign key constraint
    const userEmail = userId.includes('@') ? userId : `${userId}@pilot.signalbrief.internal`;
    await this.db.prepare(`
      INSERT OR IGNORE INTO users (id, email, name, status)
      VALUES (?, ?, 'Pilot Subscriber', 'active');
    `).bind(userId, userEmail).run();

    // 3. Upsert preferences
    const query = `
      INSERT INTO user_preferences (id, user_id, domain_id, custom_keywords, email_enabled, updated_at)
      VALUES (?, ?, ?, ?, ?, datetime('now'))
      ON CONFLICT(user_id, domain_id) DO UPDATE SET
        custom_keywords = excluded.custom_keywords,
        email_enabled = excluded.email_enabled,
        updated_at = datetime('now');
    `;
    const id = `pref_${userId}_${domainId}`;
    return await this.db.prepare(query).bind(id, userId, domainId, JSON.stringify(keywords), emailEnabled ? 1 : 0).run();
  }

  // --- Reports & Developments ---
  async getLatestReport(domainId = "manufacturing") {
    const reportQuery = `
      SELECT * FROM reports
      WHERE domain_id = ?
      ORDER BY report_date DESC, created_at DESC
      LIMIT 1;
    `;
    const report = await this.db.prepare(reportQuery).bind(domainId).first();
    if (!report) return null;

    const devsQuery = `
      SELECT rd.*, 
             json_group_array(
               json_object('article_id', rs.article_id, 'source_name', rs.source_name, 'title', rs.title, 'url', rs.url)
             ) as sources_json
      FROM report_developments rd
      LEFT JOIN report_sources rs ON rd.id = rs.development_id
      WHERE rd.report_id = ?
      GROUP BY rd.id
      ORDER BY rd.relevance_score DESC;
    `;
    const devsResult = await this.db.prepare(devsQuery).bind(report.id).all();
    const developments = (devsResult.results || []).map((d) => ({
      ...d,
      sources: d.sources_json ? JSON.parse(d.sources_json).filter((s) => s.article_id || s.url) : [],
    }));

    return {
      ...report,
      developments,
    };
  }

  async getReportsCalendar(domainId = "manufacturing", limit = 30) {
    const query = `
      SELECT id, report_date, headline, article_count, r2_key, created_at
      FROM reports
      WHERE domain_id = ?
      ORDER BY report_date DESC
      LIMIT ?;
    `;
    const result = await this.db.prepare(query).bind(domainId, limit).all();
    return result.results || [];
  }

  async getReportById(reportId) {
    const report = await this.db.prepare(`SELECT * FROM reports WHERE id = ?`).bind(reportId).first();
    if (!report) return null;

    const devsResult = await this.db.prepare(`
      SELECT rd.*, 
             json_group_array(
               json_object('article_id', rs.article_id, 'source_name', rs.source_name, 'title', rs.title, 'url', rs.url)
             ) as sources_json
      FROM report_developments rd
      LEFT JOIN report_sources rs ON rd.id = rs.development_id
      WHERE rd.report_id = ?
      GROUP BY rd.id
      ORDER BY rd.relevance_score DESC;
    `).bind(reportId).all();

    const developments = (devsResult.results || []).map((d) => ({
      ...d,
      sources: d.sources_json ? JSON.parse(d.sources_json).filter((s) => s.article_id || s.url) : [],
    }));

    return {
      ...report,
      developments,
    };
  }

  // --- Delivery Logging ---
  async logDelivery(userId, reportId, email, status, providerMessageId = null, error = null) {
    const id = `del_${Date.now()}_${Math.random().toString(36).substring(2, 7)}`;
    const query = `
      INSERT INTO delivery_logs (id, user_id, report_id, recipient_email, delivery_status, provider_message_id, error_message, delivered_at)
      VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'));
    `;
    return await this.db.prepare(query).bind(id, userId, reportId, email, status, providerMessageId, error).run();
  }

  async getDeliveryLogs(limit = 50) {
    const query = `
      SELECT id, user_id, report_id, recipient_email, delivery_status, provider_message_id, error_message, delivered_at, created_at
      FROM delivery_logs
      ORDER BY delivered_at DESC, created_at DESC
      LIMIT ?;
    `;
    const result = await this.db.prepare(query).bind(limit).all();
    return result.results || [];
  }

  async hasDelivered(userId, reportId) {
    const query = `
      SELECT id FROM delivery_logs
      WHERE user_id = ? AND report_id = ? AND delivery_status = 'delivered'
      LIMIT 1;
    `;
    const res = await this.db.prepare(query).bind(userId, reportId).first();
    return Boolean(res);
  }

  // --- Report Ingestion & Sync ---
  async insertReportWithDevelopments(report, r2Key) {
    const statements = [];

    // 0. Ensure domain exists to satisfy foreign key constraint
    const domainName = report.domain_name || (report.domain_id ? report.domain_id.charAt(0).toUpperCase() + report.domain_id.slice(1) : "Manufacturing");
    statements.push(
      this.db.prepare(`
        INSERT OR IGNORE INTO domains (id, name, description)
        VALUES (?, ?, 'Monitored intelligence domain');
      `).bind(report.domain_id, domainName)
    );

    // 1. Upsert Report
    const reportQuery = `
      INSERT INTO reports (id, domain_id, report_date, headline, status, r2_key, article_count, executive_summary, created_at)
      VALUES (?, ?, ?, ?, 'archived', ?, ?, ?, datetime('now'))
      ON CONFLICT(id) DO UPDATE SET
        headline = excluded.headline,
        status = 'archived',
        r2_key = excluded.r2_key,
        article_count = excluded.article_count,
        executive_summary = excluded.executive_summary;
    `;
    const headline = report.headline || (report.developments && report.developments[0] ? report.developments[0].headline : "Daily Intelligence Brief");
    statements.push(
      this.db.prepare(reportQuery).bind(
        report.id,
        report.domain_id,
        report.report_date,
        headline,
        r2Key,
        report.article_count || 0,
        report.executive_summary
      )
    );

    // 2. Clear old developments for this report (foreign key cascade deletes sources)
    statements.push(
      this.db.prepare("DELETE FROM report_developments WHERE report_id = ?;").bind(report.id)
    );

    // 3. Insert developments and sources
    if (report.developments && Array.isArray(report.developments)) {
      for (const dev of report.developments) {
        const devId = dev.id || `dev_${Date.now()}_${Math.random().toString(36).substring(2, 6)}`;
        const devQuery = `
          INSERT INTO report_developments (id, report_id, headline, what_changed, why_it_matters, what_to_watch, topic_label, relevance_score)
          VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        `;
        statements.push(
          this.db.prepare(devQuery).bind(
            devId,
            report.id,
            dev.headline || "Industrial Development",
            dev.what_changed || "",
            dev.why_it_matters || "",
            dev.what_to_watch || "",
            dev.topic_label || "General",
            dev.relevance_score || 0.0
          )
        );

        if (dev.sources && Array.isArray(dev.sources)) {
          for (const s of dev.sources) {
            const srcId = `src_${Date.now()}_${Math.random().toString(36).substring(2, 6)}`;
            const srcQuery = `
              INSERT INTO report_sources (id, development_id, article_id, source_name, title, url)
              VALUES (?, ?, ?, ?, ?, ?);
            `;
            statements.push(
              this.db.prepare(srcQuery).bind(
                srcId,
                devId,
                s.article_id || null,
                s.source_name || "Verified Source",
                s.title || dev.headline,
                s.url || ""
              )
            );
          }
        }
      }
    }

    if (this.db.batch) {
      return await this.db.batch(statements);
    } else {
      for (const stmt of statements) {
        await stmt.run();
      }
      return { success: true };
    }
  }

  async getReports(domainId = "manufacturing", limit = 30, offset = 0) {
    const query = `
      SELECT id, domain_id, report_date, headline, status, r2_key, article_count, executive_summary, created_at
      FROM reports
      WHERE domain_id = ?
      ORDER BY report_date DESC
      LIMIT ? OFFSET ?;
    `;
    const result = await this.db.prepare(query).bind(domainId, limit, offset).all();
    return result.results || [];
  }

  // --- Subscriber Management & 10-User Quota ---
  async getUserPreferences(userId, domainId = "manufacturing") {
    const query = `
      SELECT u.id, u.email, u.name, u.timezone, u.status, up.custom_keywords, up.delivery_time_utc, up.email_enabled
      FROM users u
      LEFT JOIN user_preferences up ON u.id = up.user_id AND up.domain_id = ?
      WHERE u.id = ?;
    `;
    return await this.db.prepare(query).bind(domainId, userId).first();
  }

  async inviteSubscriber(email, name = null, domainId = "manufacturing") {
    // Enforce strict server-side limit of 7 invited/active subscribers
    const countQuery = `SELECT count(*) as count FROM users WHERE status IN ('active', 'invited');`;
    const countResult = await this.db.prepare(countQuery).first();
    const currentCount = countResult ? countResult.count : 0;

    if (currentCount >= 7) {
      throw new Error(`Pilot subscriber quota exceeded: maximum 7 active/invited subscribers allowed (current: ${currentCount}).`);
    }

    const userId = `usr_${Date.now()}_${Math.random().toString(36).substring(2, 7)}`;
    const userInsert = `
      INSERT INTO users (id, email, name, status)
      VALUES (?, ?, ?, 'invited')
      ON CONFLICT(email) DO UPDATE SET
        name = coalesce(excluded.name, users.name),
        status = 'invited',
        updated_at = datetime('now');
    `;
    const prefInsert = `
      INSERT INTO user_preferences (id, user_id, domain_id, email_enabled)
      VALUES (?, ?, ?, 1)
      ON CONFLICT(user_id, domain_id) DO NOTHING;
    `;
    const prefId = `pref_${userId}_${domainId}`;

    if (this.db.batch) {
      await this.db.batch([
        this.db.prepare(userInsert).bind(userId, email, name),
        this.db.prepare(prefInsert).bind(prefId, userId, domainId),
      ]);
    } else {
      await this.db.prepare(userInsert).bind(userId, email, name).run();
      await this.db.prepare(prefInsert).bind(prefId, userId, domainId).run();
    }
    return { userId, email, status: "invited", totalSubscribers: currentCount + 1 };
  }

  // --- Pipeline Run Tracking ---
  async recordPipelineRun(runData) {
    const query = `
      INSERT INTO pipeline_runs (
        id, domain_id, run_date, status, articles_collected, articles_processed, reports_generated, emails_sent, error_log, duration_seconds, started_at, completed_at
      )
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
      ON CONFLICT(id) DO UPDATE SET
        status = excluded.status,
        articles_collected = excluded.articles_collected,
        articles_processed = excluded.articles_processed,
        reports_generated = excluded.reports_generated,
        emails_sent = excluded.emails_sent,
        error_log = excluded.error_log,
        duration_seconds = excluded.duration_seconds,
        completed_at = datetime('now');
    `;
    return await this.db.prepare(query).bind(
      runData.id,
      runData.domain_id,
      runData.run_date,
      runData.status,
      runData.articles_collected || 0,
      runData.articles_processed || 0,
      runData.reports_generated || 0,
      runData.emails_sent || 0,
      runData.error_log || null,
      runData.duration_seconds || 0.0
    ).run();
  }
}
