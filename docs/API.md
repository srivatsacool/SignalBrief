# SignalBrief REST API Reference

The SignalBrief Edge API is deployed as a Cloudflare Worker providing report browsing, historical calendar archives, subscriber preferences, internal report ingestion, and delivery auditing.

Base URLs:
- **Local Development**: `http://localhost:8787`
- **Production Edge**: `https://signalbrief-worker.<your-subdomain>.workers.dev`

---

## 1. Authentication & Security

| Type | Header | Endpoints Protected |
| :--- | :--- | :--- |
| **Public** | None | `/api/health`, `/api/domains`, `/api/reports`, `/api/reports/latest`, `/api/reports/:id`, `/api/reports/:id/html`, `/api/calendar` |
| **Subscriber** | `userId` query parameter | `GET /api/preferences`, `PUT /api/preferences` |
| **Internal Pipeline** | `Authorization: Bearer <SIGNALBRIEF_INTERNAL_KEY>` | `POST /api/internal/report` |
| **Admin** | `Authorization: Bearer <ADMIN_SECRET_KEY>` | `POST /api/subscribers/invite` |

---

## 2. API Endpoints

### 2.1 Health Check
**`GET /api/health`**
Returns service status, environment configuration, database connection state, and storage connectivity.

**Response (200 OK):**
```json
{
  "status": "healthy",
  "service": "signalbrief-api",
  "environment": "development",
  "timestamp": "2026-09-29T02:15:00.000Z",
  "database_connected": true,
  "storage_connected": true,
  "default_domain": "manufacturing",
  "max_subscribers": 10
}
```

---

### 2.2 Domains Catalog
**`GET /api/domains`**
Lists all monitored domains.

**Response (200 OK):**
```json
{
  "domains": [
    {
      "id": "manufacturing",
      "name": "Manufacturing",
      "description": "Industrial AI, smart factories, robotics automation, and supply chain resilience.",
      "active": true,
      "max_subscribers": 10
    }
  ]
}
```

---

### 2.3 List Reports (Paginated)
**`GET /api/reports`**
Query parameters:
- `domain` (optional, default: `manufacturing`)
- `limit` (optional, default: `30`, max: `100`)
- `offset` (optional, default: `0`)

**Response (200 OK):**
```json
{
  "domain": "manufacturing",
  "limit": 30,
  "offset": 0,
  "count": 1,
  "reports": [
    {
      "id": "rep_20260929_manufacturing",
      "domain_id": "manufacturing",
      "report_date": "2026-09-29",
      "headline": "Standards & Governance: NIST Awards $30 Million for MEP Centers",
      "status": "archived",
      "r2_key": "reports/2026/09/29/rep_20260929_manufacturing.html",
      "article_count": 84,
      "executive_summary": "Today's manufacturing brief highlights federal robotics grants...",
      "created_at": "2026-09-29 02:00:00"
    }
  ]
}
```

---

### 2.4 Latest Report
**`GET /api/reports/latest`**
Query parameters:
- `domain` (optional, default: `manufacturing`)

**Response (200 OK):**
Returns the most recent report record joined with its structured developments and citations.

---

### 2.5 Report Details by ID
**`GET /api/reports/:id`**
Fetches complete report metadata, triadic developments, and source links.

**Response (200 OK):**
```json
{
  "id": "rep_20260929_manufacturing",
  "domain_id": "manufacturing",
  "report_date": "2026-09-29",
  "headline": "Manufacturing Daily Intelligence Brief",
  "executive_summary": "Key advancements in industrial AI and facility robotics...",
  "developments": [
    {
      "id": "dev_01",
      "headline": "Robotics Deployment Across Tier-1 Suppliers",
      "what_changed": "Autonomous mobile robots adopted in 12 facilities.",
      "why_it_matters": "Increases throughput by 22% while cutting assembly cycle time.",
      "what_to_watch": "Quarterly earnings reports and supply chain deliveries.",
      "topic_label": "Robotics",
      "relevance_score": 0.94,
      "sources": [
        {
          "article_id": "nist_01",
          "source_name": "NIST",
          "title": "Smart Factory Technology Benchmark",
          "url": "https://www.nist.gov/article-1"
        }
      ]
    }
  ]
}
```

---

### 2.6 Raw HTML Report Archive
**`GET /api/reports/:id/html`**
Streams the rendered, standalone HTML5 report stored in Cloudflare R2.

**Response (200 OK):**
- `Content-Type: text/html; charset=utf-8`
- Body: Complete HTML5 document (<20 KB).

---

### 2.7 Calendar View
**`GET /api/calendar`**
Query parameters:
- `domain` (default: `manufacturing`)
- `limit` (default: `30`)

Returns historical dates, headlines, and article counts for calendar navigation.

---

### 2.8 Subscriber Preferences
**`GET /api/preferences?userId=<id>&domainId=manufacturing`**
Retrieves subscriber focus keywords and email delivery toggle.

**`PUT /api/preferences`**
Updates focus keywords and delivery schedule.
**Request Body:**
```json
{
  "userId": "usr_subscriber_1",
  "domainId": "manufacturing",
  "custom_keywords": ["robotics", "supply chain", "sensors"],
  "email_enabled": true
}
```

---

### 2.9 Subscriber Invitation (10-User Quota)
**`POST /api/subscribers/invite`**
Headers: `Authorization: Bearer <ADMIN_SECRET_KEY>`
**Request Body:**
```json
{
  "email": "newuser@example.com",
  "name": "Jane Doe",
  "domainId": "manufacturing"
}
```
*Note*: The API strictly enforces a maximum of 10 invited/active subscribers on the server. If the quota is exceeded, HTTP 400 is returned with `Pilot subscriber quota exceeded`.

---

### 2.10 Internal Report Ingestion
**`POST /api/internal/report`**
Headers: `Authorization: Bearer <SIGNALBRIEF_INTERNAL_KEY>`
Ingests generated report artifacts directly from the Python analytics pipeline runner.

**Request Body:**
```json
{
  "report": {
    "id": "rep_20260929_manufacturing",
    "domain_id": "manufacturing",
    "domain_name": "Manufacturing",
    "report_date": "2026-09-29",
    "executive_summary": "Daily brief...",
    "article_count": 84,
    "developments": [
      {
        "id": "dev_01",
        "headline": "Robotics Expansion",
        "what_changed": "...",
        "why_it_matters": "...",
        "what_to_watch": "...",
        "topic_label": "Robotics",
        "relevance_score": 0.95,
        "sources": [
          { "source_name": "NIST", "title": "Study", "url": "https://example.com" }
        ]
      }
    ]
  },
  "html": "<!DOCTYPE html><html>...</html>",
  "dispatch_email": false
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "report_id": "rep_20260929_manufacturing",
  "r2_key": "reports/2026/09/29/rep_20260929_manufacturing.html",
  "storage_stored": true,
  "database_stored": true,
  "email_dispatched": false,
  "message": "Report successfully ingested and archived"
}
```

---

### 2.11 Delivery Status Logs
**`GET /api/delivery-status`**
Query parameters: `limit` (default: 50).
Returns delivery audit trail from `delivery_logs`.
