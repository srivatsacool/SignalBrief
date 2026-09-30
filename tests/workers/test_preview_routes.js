import test from 'node:test';
import assert from 'node:assert/strict';
import http from 'node:http';

function fetchUrl(url, options = {}) {
  return new Promise((resolve, reject) => {
    const req = http.request(url, options, (res) => {
      let body = '';
      res.on('data', chunk => { body += chunk; });
      res.on('end', () => {
        resolve({
          statusCode: res.statusCode,
          headers: res.headers,
          body,
        });
      });
    });
    req.on('error', reject);
    if (options.body) {
      req.write(options.body);
    }
    req.end();
  });
}

test('Frontend: Landing page (/) renders correctly with sections and pipeline', async () => {
  const res = await fetchUrl('http://127.0.0.1:4321/');
  assert.equal(res.statusCode, 200, 'Expected status 200 for /');
  assert.ok(res.body.includes('SignalBrief'), 'Expected SignalBrief in HTML');
  assert.ok(res.body.includes('World & Global Macro Intelligence'), 'Expected World Macro news section first');
  assert.ok(res.body.includes('Domain Intelligence'), 'Expected Domain Intelligence section');
  assert.ok(res.body.includes('Generate New Report'), 'Expected Generate New Report button');
  assert.ok(res.body.includes('Pipeline Transparency Stepper'), 'Expected Pipeline Stepper');
});

test('Frontend: Subscribe page (/subscribe) renders 7-spot meter and countdown clock', async () => {
  const res = await fetchUrl('http://127.0.0.1:4321/subscribe');
  assert.equal(res.statusCode, 200, 'Expected status 200 for /subscribe');
  assert.ok(res.body.includes('Strictly 7 Subscribers'), 'Expected 7 subscribers title');
  assert.ok(res.body.includes('7-Spot Scarcity Allocation Meter'), 'Expected allocation meter');
  assert.ok(res.body.includes('Next Automated Synthesis'), 'Expected countdown clock');
  assert.ok(res.body.includes('Claim a Reader Seat'), 'Expected subscribe form');
});

test('Frontend: Calendar archive (/calendar) renders correctly', async () => {
  const res = await fetchUrl('http://127.0.0.1:4321/calendar');
  assert.equal(res.statusCode, 200, 'Expected status 200 for /calendar');
  assert.ok(res.body.includes('Intelligence Calendar'), 'Expected Intelligence Calendar title');
  assert.ok(res.body.includes('Archived Briefings'), 'Expected Archived Briefings list');
});

test('Frontend: Settings page (/settings) renders subscriber form', async () => {
  const res = await fetchUrl('http://127.0.0.1:4321/settings');
  assert.equal(res.statusCode, 200, 'Expected status 200 for /settings');
  assert.ok(res.body.includes('Settings & Preferences'), 'Expected Settings title');
  assert.ok(res.body.includes('7-Spot Exclusive Pilot Readership'), 'Expected 7-spot quota notice');
});

test('Frontend: Report detail page (/report/daily_brief_manufacturing_2026-09-28) renders', async () => {
  const res = await fetchUrl('http://127.0.0.1:4321/report/daily_brief_manufacturing_2026-09-28');
  assert.equal(res.statusCode, 200, 'Expected status 200 for report detail');
  assert.ok(res.body.includes('Intelligence Briefing'), 'Expected briefing title');
  assert.ok(res.body.includes('daily_brief_manufacturing_2026-09-28'), 'Expected report ID');
});

test('Worker API: /api/health responds with healthy status and 7 max subscribers', async () => {
  const res = await fetchUrl('http://127.0.0.1:8787/api/health');
  assert.equal(res.statusCode, 200);
  const data = JSON.parse(res.body);
  assert.equal(data.status, 'healthy');
  assert.equal(data.service, 'signalbrief-api');
  assert.equal(data.max_subscribers, 7);
});

test('Worker API: /api/pipeline/telemetry responds with run metrics', async () => {
  const res = await fetchUrl('http://127.0.0.1:8787/api/pipeline/telemetry');
  assert.equal(res.statusCode, 200);
  const data = JSON.parse(res.body);
  assert.equal(data.pages_chosen, 18);
  assert.equal(data.articles_scraped, 240);
  assert.equal(data.citation_coverage, '100%');
});

test('Worker API: /api/domains responds with manufacturing domain', async () => {
  const res = await fetchUrl('http://127.0.0.1:8787/api/domains');
  assert.equal(res.statusCode, 200);
  const data = JSON.parse(res.body);
  assert.ok(Array.isArray(data.domains));
  assert.ok(data.domains.some(d => d.id === 'manufacturing'));
});

test('Worker API: PUT /api/preferences updates preference successfully', async () => {
  const payload = JSON.stringify({
    userId: 'usr_pilot_subscriber',
    domainId: 'manufacturing',
    custom_keywords: ['robotics', 'automation', 'nist'],
    email_enabled: true
  });
  const res = await fetchUrl('http://127.0.0.1:8787/api/preferences', {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'Origin': 'http://127.0.0.1:4321'
    },
    body: payload
  });
  assert.equal(res.statusCode, 200);
  const data = JSON.parse(res.body);
  assert.equal(data.success, true);
  assert.ok(data.message.includes("Preferences updated successfully"));
});
