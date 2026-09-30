"""Unit tests for D1 SQLite database schema and Worker query compatibility."""

import json
from pathlib import Path
import sqlite3
import pytest

SCHEMA_PATH = Path(__file__).resolve().parent.parent.parent / "migrations" / "0001_initial_schema.sql"


@pytest.fixture
def db_conn():
    """Create an in-memory SQLite connection with the initial schema applied."""
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys = ON;")
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    conn.executescript(schema_sql)
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()


def test_schema_tables_and_views_exist(db_conn):
    """Verify all required tables and views are created."""
    cursor = db_conn.cursor()
    cursor.execute("SELECT name, type FROM sqlite_master WHERE type IN ('table', 'view');")
    names = {row["name"]: row["type"] for row in cursor.fetchall()}

    expected_tables = [
        "users",
        "domains",
        "user_preferences",
        "sources",
        "articles",
        "topics",
        "article_analysis",
        "reports",
        "report_articles",
        "report_developments",
        "report_sources",
        "delivery_logs",
        "pipeline_runs",
    ]
    for table in expected_tables:
        assert table in names, f"Missing table: {table}"
        assert names[table] == "table"

    assert "email_logs" in names
    assert names["email_logs"] == "view"


def test_reports_table_has_headline(db_conn):
    """Verify reports table contains the headline column expected by the worker."""
    cursor = db_conn.cursor()
    cursor.execute("PRAGMA table_info(reports);")
    columns = {row["name"] for row in cursor.fetchall()}
    assert "headline" in columns, "Column 'headline' is missing from 'reports' table"
    assert "r2_key" in columns
    assert "article_count" in columns
    assert "executive_summary" in columns


def test_worker_get_active_subscribers_query(db_conn):
    """Test worker getActiveSubscribers query execution."""
    cursor = db_conn.cursor()
    cursor.execute("INSERT INTO domains (id, name) VALUES ('manufacturing', 'Manufacturing');")
    cursor.execute(
        "INSERT INTO users (id, email, name, timezone, status) VALUES ('u1', 'sub@example.com', 'Sub One', 'UTC', 'active');"
    )
    cursor.execute(
        "INSERT INTO user_preferences (id, user_id, domain_id, custom_keywords, delivery_time_utc, email_enabled) "
        "VALUES ('pref_1', 'u1', 'manufacturing', '[\"robotics\"]', '06:00', 1);"
    )

    query = """
      SELECT u.id, u.email, u.name, u.timezone, up.custom_keywords, up.delivery_time_utc
      FROM users u
      JOIN user_preferences up ON u.id = up.user_id
      WHERE u.status = 'active'
        AND up.email_enabled = 1
        AND up.domain_id = ?
      LIMIT 10;
    """
    cursor.execute(query, ("manufacturing",))
    rows = cursor.fetchall()
    assert len(rows) == 1
    assert rows[0]["email"] == "sub@example.com"
    assert rows[0]["delivery_time_utc"] == "06:00"


def test_worker_update_user_preferences_upsert(db_conn):
    """Test worker updateUserPreferences UPSERT query."""
    cursor = db_conn.cursor()
    cursor.execute("INSERT INTO domains (id, name) VALUES ('manufacturing', 'Manufacturing');")
    cursor.execute("INSERT INTO users (id, email, name, status) VALUES ('u1', 'sub@example.com', 'Sub One', 'active');")

    query = """
      INSERT INTO user_preferences (id, user_id, domain_id, custom_keywords, email_enabled, updated_at)
      VALUES (?, ?, ?, ?, ?, datetime('now'))
      ON CONFLICT(user_id, domain_id) DO UPDATE SET
        custom_keywords = excluded.custom_keywords,
        email_enabled = excluded.email_enabled,
        updated_at = datetime('now');
    """
    # Insert
    cursor.execute(query, ("pref_u1_manufacturing", "u1", "manufacturing", json.dumps(["ai"]), 1))
    db_conn.commit()

    cursor.execute("SELECT custom_keywords, email_enabled FROM user_preferences WHERE user_id = 'u1';")
    row = cursor.fetchone()
    assert json.loads(row["custom_keywords"]) == ["ai"]
    assert row["email_enabled"] == 1

    # Upsert (update)
    cursor.execute(query, ("pref_u1_manufacturing", "u1", "manufacturing", json.dumps(["robotics", "automation"]), 0))
    db_conn.commit()

    cursor.execute("SELECT custom_keywords, email_enabled FROM user_preferences WHERE user_id = 'u1';")
    row = cursor.fetchone()
    assert json.loads(row["custom_keywords"]) == ["robotics", "automation"]
    assert row["email_enabled"] == 0


def test_worker_report_and_developments_queries(db_conn):
    """Test worker getLatestReport, getReportsCalendar, and getReportById queries."""
    cursor = db_conn.cursor()
    cursor.execute("INSERT INTO domains (id, name) VALUES ('manufacturing', 'Manufacturing');")
    cursor.execute(
        "INSERT INTO reports (id, domain_id, report_date, headline, status, r2_key, article_count, executive_summary) "
        "VALUES ('rep_1', 'manufacturing', '2026-09-28', 'Daily Manufacturing Brief', 'archived', 'reports/2026-09-28.html', 42, 'Executive summary content');"
    )
    cursor.execute(
        "INSERT INTO report_developments (id, report_id, headline, what_changed, why_it_matters, what_to_watch, topic_label, relevance_score) "
        "VALUES ('dev_1', 'rep_1', 'Robotics in Auto Plants', 'Deployments up 30%', 'Increases throughput', 'Q4 earnings', 'Robotics', 0.95);"
    )
    cursor.execute(
        "INSERT INTO report_sources (id, development_id, article_id, source_name, title, url) "
        "VALUES ('src_1', 'dev_1', 'art_101', 'NIST', 'Robotics Deployment Study', 'https://example.com/robotics');"
    )
    db_conn.commit()

    # Test getReportsCalendar query
    calendar_query = """
      SELECT id, report_date, headline, article_count, r2_key, created_at
      FROM reports
      WHERE domain_id = ?
      ORDER BY report_date DESC
      LIMIT ?;
    """
    cursor.execute(calendar_query, ("manufacturing", 30))
    cal_rows = cursor.fetchall()
    assert len(cal_rows) == 1
    assert cal_rows[0]["headline"] == "Daily Manufacturing Brief"
    assert cal_rows[0]["article_count"] == 42

    # Test getLatestReport developments query with JSON aggregation
    devs_query = """
      SELECT rd.*, 
             json_group_array(
               json_object('article_id', rs.article_id, 'source_name', rs.source_name, 'title', rs.title, 'url', rs.url)
             ) as sources_json
      FROM report_developments rd
      LEFT JOIN report_sources rs ON rd.id = rs.development_id
      WHERE rd.report_id = ?
      GROUP BY rd.id
      ORDER BY rd.relevance_score DESC;
    """
    cursor.execute(devs_query, ("rep_1",))
    dev_rows = cursor.fetchall()
    assert len(dev_rows) == 1
    dev = dict(dev_rows[0])
    assert dev["headline"] == "Robotics in Auto Plants"
    sources = json.loads(dev["sources_json"])
    assert len(sources) == 1
    assert sources[0]["url"] == "https://example.com/robotics"
    assert sources[0]["source_name"] == "NIST"


def test_worker_log_delivery_and_email_logs_view(db_conn):
    """Test worker logDelivery insert into delivery_logs and querying email_logs view."""
    cursor = db_conn.cursor()
    cursor.execute("INSERT INTO domains (id, name) VALUES ('manufacturing', 'Manufacturing');")
    cursor.execute("INSERT INTO users (id, email, name, status) VALUES ('u1', 'sub@example.com', 'Sub One', 'active');")
    cursor.execute(
        "INSERT INTO reports (id, domain_id, report_date, headline, status, r2_key, article_count) "
        "VALUES ('rep_1', 'manufacturing', '2026-09-28', 'Daily Brief', 'delivered', 'r2/key', 10);"
    )

    delivery_insert = """
      INSERT INTO delivery_logs (id, user_id, report_id, recipient_email, delivery_status, provider_message_id, error_message, delivered_at)
      VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'));
    """
    cursor.execute(delivery_insert, ("del_123", "u1", "rep_1", "sub@example.com", "delivered", "msg_abc_456", None))
    db_conn.commit()

    # Query delivery_logs directly
    cursor.execute("SELECT * FROM delivery_logs WHERE id = 'del_123';")
    del_row = cursor.fetchone()
    assert del_row["recipient_email"] == "sub@example.com"
    assert del_row["delivery_status"] == "delivered"
    assert del_row["provider_message_id"] == "msg_abc_456"

    # Query legacy email_logs view
    cursor.execute("SELECT * FROM email_logs WHERE id = 'del_123';")
    view_row = cursor.fetchone()
    assert view_row is not None
    assert view_row["recipient_email"] == "sub@example.com"
    assert view_row["status"] == "delivered"
    assert view_row["sent_at"] is not None


def test_cascade_delete_report(db_conn):
    """Verify that deleting a report cascades to report_developments and report_sources."""
    cursor = db_conn.cursor()
    cursor.execute("INSERT INTO domains (id, name) VALUES ('manufacturing', 'Manufacturing');")
    cursor.execute(
        "INSERT INTO reports (id, domain_id, report_date, headline, status, r2_key) "
        "VALUES ('rep_del', 'manufacturing', '2026-09-28', 'Test Brief', 'pending', 'r2/k');"
    )
    cursor.execute(
        "INSERT INTO report_developments (id, report_id, headline, what_changed, why_it_matters, what_to_watch) "
        "VALUES ('dev_del', 'rep_del', 'H', 'WC', 'WIM', 'WTW');"
    )
    cursor.execute(
        "INSERT INTO report_sources (id, development_id, title, url) "
        "VALUES ('src_del', 'dev_del', 'T', 'https://example.com');"
    )
    db_conn.commit()

    cursor.execute("DELETE FROM reports WHERE id = 'rep_del';")
    db_conn.commit()

    cursor.execute("SELECT count(*) as c FROM report_developments WHERE id = 'dev_del';")
    assert cursor.fetchone()["c"] == 0

    cursor.execute("SELECT count(*) as c FROM report_sources WHERE id = 'src_del';")
    assert cursor.fetchone()["c"] == 0


def test_insert_report_idempotency(db_conn):
    """Verify upserting a report and replacing its developments is idempotent."""
    cursor = db_conn.cursor()
    cursor.execute("INSERT INTO domains (id, name) VALUES ('manufacturing', 'Manufacturing');")

    def insert_report(headline, n_devs):
        cursor.execute(
            """
            INSERT INTO reports (id, domain_id, report_date, headline, status, r2_key, article_count, executive_summary)
            VALUES ('rep_idempotent', 'manufacturing', '2026-09-28', ?, 'archived', 'reports/key.html', 50, 'Exec sum')
            ON CONFLICT(id) DO UPDATE SET
              headline = excluded.headline,
              status = 'archived',
              r2_key = excluded.r2_key,
              article_count = excluded.article_count,
              executive_summary = excluded.executive_summary;
            """,
            (headline,),
        )
        cursor.execute("DELETE FROM report_developments WHERE report_id = 'rep_idempotent';")
        for i in range(n_devs):
            dev_id = f"dev_idem_{i}"
            cursor.execute(
                """
                INSERT INTO report_developments (id, report_id, headline, what_changed, why_it_matters, what_to_watch, topic_label, relevance_score)
                VALUES (?, 'rep_idempotent', ?, 'WC', 'WIM', 'WTW', 'Topic', 0.9);
                """,
                (dev_id, f"Dev {i}"),
            )
            cursor.execute(
                """
                INSERT INTO report_sources (id, development_id, article_id, source_name, title, url)
                VALUES (?, ?, 'art_1', 'Source', 'Title', 'https://example.com/1');
                """,
                (f"src_idem_{i}", dev_id),
            )
        db_conn.commit()

    # First run: 2 developments
    insert_report("Initial Headline", 2)
    cursor.execute("SELECT headline FROM reports WHERE id = 'rep_idempotent';")
    assert cursor.fetchone()["headline"] == "Initial Headline"
    cursor.execute("SELECT count(*) as c FROM report_developments WHERE report_id = 'rep_idempotent';")
    assert cursor.fetchone()["c"] == 2

    # Second run (re-execution with 3 developments)
    insert_report("Updated Headline", 3)
    cursor.execute("SELECT headline FROM reports WHERE id = 'rep_idempotent';")
    assert cursor.fetchone()["headline"] == "Updated Headline"
    cursor.execute("SELECT count(*) as c FROM report_developments WHERE report_id = 'rep_idempotent';")
    assert cursor.fetchone()["c"] == 3
    cursor.execute("SELECT count(*) as c FROM report_sources WHERE development_id LIKE 'dev_idem_%';")
    assert cursor.fetchone()["c"] == 3


def test_subscriber_quota_enforcement(db_conn):
    """Verify that invite flow enforces maximum 10 active/invited subscribers."""
    cursor = db_conn.cursor()
    cursor.execute("INSERT INTO domains (id, name) VALUES ('manufacturing', 'Manufacturing');")

    def invite(email):
        cursor.execute("SELECT count(*) as count FROM users WHERE status IN ('active', 'invited');")
        count = cursor.fetchone()["count"]
        if count >= 10:
            raise ValueError(f"Pilot quota exceeded: max 10 subscribers allowed (current: {count})")
        u_id = f"user_{count + 1}"
        cursor.execute("INSERT INTO users (id, email, status) VALUES (?, ?, 'invited');", (u_id, email))
        db_conn.commit()

    for i in range(10):
        invite(f"sub{i}@example.com")

    cursor.execute("SELECT count(*) as c FROM users WHERE status IN ('active', 'invited');")
    assert cursor.fetchone()["c"] == 10

    # 11th invite must raise quota exceeded error
    with pytest.raises(ValueError, match="Pilot quota exceeded"):
        invite("sub11@example.com")


def test_pipeline_runs_tracking(db_conn):
    """Verify recording and updating pipeline_runs."""
    cursor = db_conn.cursor()
    cursor.execute("INSERT INTO domains (id, name) VALUES ('manufacturing', 'Manufacturing');")

    upsert_query = """
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
    """
    cursor.execute(
        upsert_query,
        ("run_01", "manufacturing", "2026-09-29", "started", 100, 0, 0, 0, None, 0.0),
    )
    db_conn.commit()

    cursor.execute("SELECT status, articles_collected FROM pipeline_runs WHERE id = 'run_01';")
    row = cursor.fetchone()
    assert row["status"] == "started"
    assert row["articles_collected"] == 100

    # Complete the run
    cursor.execute(
        upsert_query,
        ("run_01", "manufacturing", "2026-09-29", "completed", 100, 95, 1, 8, None, 7.85),
    )
    db_conn.commit()

    cursor.execute("SELECT status, reports_generated, duration_seconds FROM pipeline_runs WHERE id = 'run_01';")
    row = cursor.fetchone()
    assert row["status"] == "completed"
    assert row["reports_generated"] == 1
    assert row["duration_seconds"] == 7.85

