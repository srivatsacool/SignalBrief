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
      LIMIT 10;
    `;
    const result = await this.db.prepare(query).bind(domainId).all();
    return result.results || [];
  }

  async updateUserPreferences(userId, domainId, keywords, emailEnabled) {
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
      sources: d.sources_json ? JSON.parse(d.sources_json) : [],
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
      sources: d.sources_json ? JSON.parse(d.sources_json) : [],
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
}
