---
name: report-craft
description: "Dedicated intelligence report artisan skill utilizing /paint and /genjutsu design principles. Crafts premium, matte black, section-wise executive briefings with visible pipeline telemetry, immediate inline source attribution, and interactive topic customization."
allowed-tools: Bash, Read, Edit, Write, Grep, Glob, Artifact
---

# ReportCraft — The Intelligence Report Artisan

> Combines the art-direction of `/paint` and the interaction motion of `/genjutsu` to generate high-density, anti-AI-slop intelligence briefings.
> This skill governs the visual architecture, data presentation, and interaction rules for SignalBrief intelligence reports.

---

## 1. Visual Identity & Design Tokens

Reports created under this skill MUST strictly adhere to the matte black executive palette:

```css
:root {
  /* Surfaces */
  --sb-bg-canvas: #090A0F;        /* Deep matte void background */
  --sb-bg-sidebar: #0D0E12;       /* Secondary structural background */
  --sb-bg-card: #121318;          /* Base card container */
  --sb-bg-elevated: #171920;      /* Hovered, active, or focused cards */
  --sb-border-subtle: #252832;    /* Refined hairline borders */

  /* Typography */
  --sb-text-primary: #F4F5F7;     /* High-contrast crisp headlines & facts */
  --sb-text-secondary: #9299A8;   /* Body copy, analysis, context */
  --sb-text-muted: #626B7B;       /* Timestamps, metadata, labels */

  /* Accents */
  --sb-accent-phosphor: #18D69A;  /* Pipeline success, verified citations, live status */
  --sb-accent-cyan: #32B8F4;      /* Active domain, section tags, primary CTAs */
  --sb-accent-amber: #E5A93C;     /* Horizon alerts, watch indicators, warnings */

  /* Typography Stacks */
  --sb-font-editorial: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --sb-font-mono: 'JetBrains Mono', 'Fira Code', 'SF Mono', ui-monospace, monospace;
}
```

**Anti-AI-Slop Doctrine:**
- No bright multi-color gradients across content cards.
- No excessive glow or heavy glassmorphism blurs.
- Hairline `1px` borders only (`#252832`).
- Restrained, intentional use of Phosphor Green (`#18D69A`) and Electric Cyan (`#32B8F4`).

---

## 2. Mandatory Section 01: World & Global Macro News

Every generated daily brief MUST begin with **Section 01 — World & Global Macro News**, regardless of which specific industry domains the user has selected.

- **Purpose:** Provide macroeconomic, geopolitical, trade treaty, maritime freight, and cross-border regulatory context.
- **Placement:** Always placed immediately beneath the Executive Summary and above all domain sections.
- **Composition:** 2–3 high-impact geopolitical developments with immediate inline primary source links.

---

## 3. User-Selected Domain Sections (Section 02+)

Following World & Global Macro News, organize developments into individual domain sections matching the user's selected topics:

- Supported domain clusters include:
  - *Manufacturing & Industrial AI*
  - *Technology & Compute*
  - *Artificial Intelligence & Autonomous Systems*
  - *Energy & Climate Transition*
  - *Economy & Global Markets*
  - *Geopolitics & Sanctions*
  - *Supply Chain & Maritime Logistics*
  - *Automotive & Electric Mobility*
  - *Aerospace & Defense Automation*
  - *Pharma & Healthcare*
  - *Biotechnology & Genomics*
  - *Semiconductors & Lithography*
  - *Robotics & Factory Automation*
  - *Logistics & Freight Transport*
  - *Sustainability & Circular Economy*
  - *Policy & Regulatory Governance*
  - *Trade & Tariffs*
  - *Commodities & Critical Minerals*
  - *Cybersecurity & Defense Networks*
  - *Space & Satellite Infrastructure*
  - *Startups & Venture Capital*
  - *Retail & Consumer Dynamics*
  - *Construction & Heavy Engineering*
  - *Agriculture & AgTech*
  - *Finance & Capital Markets*
  - *Workforce & Labor Automation*
  - *Science & Fundamental Research*
- Each selected domain must render as a distinct sectional card group with its own domain pill and metadata summary.

---

## 4. Consistent Report Hierarchy

Every report conforms to this structural sequence:
1. **Report Header:** Date, "Today's Brief" title, synthesis timestamp, and execution status.
2. **Pipeline Transparency HUD:** Interactive 6-stage stepper showing data flow.
3. **Run Telemetry HUD:** 6 metric cards (Pages chosen, articles scraped, duplicates pruned, clusters formed, latency, source verification).
4. **Executive Overview:** 2–3 sentence executive summary synthesizing the day's meta-signals.
5. **Section 01 — World & Global Macro News**
6. **Section 02 — Domain Intelligence (User Selections)**
7. **Section 03 — Horizon Scan ("What to Watch Next"):** 3 forward-looking deterministic indicators (next 7–30 days).

---

## 5. Five-Part Intelligence Framework & Quality Standards

Every synthesized news development MUST follow the 5-part analytical intelligence framework:

1. **Headline:** Specific, informative, and factual. Clean of trailing ellipses (`...` or `…`) and source suffixes (`- Reuters`). Format: `[Domain / Subtopic]: [Specific Factual Occurrence]`.
2. **What Happened (`what_happened` / `what_changed`):** A concise summary of the actual event, preserving organizations, dates, locations, metrics ($M, $B, %), and outcomes.
3. **Why It Matters (`why_it_matters`):** Explains strategic significance and operational/financial impact without repeating the headline or the event lead.
4. **Business Implications (`business_implications`):** Concrete operational, financial, technological, regulatory, or supply chain takeaways tailored to the domain.
5. **What To Watch (`what_to_watch`):** Specific, plausible future catalysts, regulatory filing deadlines, commissioning milestones, or measurable indicators, clearly framed as forward-looking analysis.
6. **Sources:** Immediate clickable inline citations directly linked to canonical reporting URLs.

### Banned Boilerplate Doctrine (Zero "Mad-Libs" Policy)
The following generic phrases are strictly banned from synthesis output:
- ❌ *"Signals accelerating momentum in [subtopic], impacting strategic capital allocation and operational efficiency..."*
- ❌ *"Implementation timelines, vendor integration benchmarks, and regulatory compliance updates..."*
- ❌ Trailing ellipses at the end of headlines (e.g. `...`)
- ❌ Journalistic stopwords in cluster theme labels (e.g. `Said & Manufacturing & Facility`)
- ❌ Verbatim recycling of the centroid title into the "What changed" body without factual grounding.

---

## 6. Immediate Source Attribution Rule

> **CRITICAL RULE:** Place the source attribution immediately after the relevant news item or factual claim.

- Never bury all sources in a detached bibliography at the bottom of the page.
- Direct inline citation badge format:
  ```html
  <a href="https://example.com" target="_blank" rel="noopener noreferrer" class="inline-source-badge">
    <span class="source-name">[Reuters / Supply Chain Dive]</span>
    <span class="verification-tag">Verified ↗</span>
  </a>
  ```
- Make all publication names directly clickable to the canonical source URL.

---

## 7. Source Link Behavior

- All outbound evidence links must open in a new tab (`target="_blank"` with `rel="noopener noreferrer"`).
- Source titles must truncate gracefully on mobile without breaking layout.
- Centroid URL fallback: If an individual sentence extraction misses a direct URL, fall back to the cluster centroid's primary verified article URL.

---

## 8. Run Metrics & Pipeline Transparency

Every report generation run outputs machine-readable telemetry rendered in a prominent HUD:
- **Pages / Feeds Chosen:** Total RSS/API feeds evaluated.
- **Raw Articles Scraped:** Ingested content bodies.
- **Duplicates Pruned:** Exact count and percentage of redundant stories filtered out.
- **Clusters Formed:** Density-based clusters discovered via DBSCAN.
- **Pipeline Latency:** Total seconds from collection trigger to report rendering.
- **Source Verification:** 100% citation pass rate verification.

---

## 9. Empty, Loading, Partial, and Failure States

- **Loading State:** Monospaced active stage indicator with pulsing phosphor green light; never a generic spinning wheel without status copy.
- **Partial State:** When certain feeds timeout, log the warning, continue with remaining sources, and render an amber indicator: `16 of 18 Feeds Ingested (2 Timed Out)`.
- **Empty State:** Clean matte black container (`#121318`) with monospaced instructions: `No developments recorded for this date. Trigger an on-demand brief or select another date.`
- **Failure State:** Clear technical error message with retry CTA and zero silent degradation.

---

## 10. Responsive Report Layout

- Desktop: Multi-column high-density layout with compact telemetry cards and side-by-side metric grids.
- Tablet / Mobile: Stacks gracefully into single-column editorial cards with thumb-friendly touch targets (min 44px) and collapsible pipeline drawers.

---

## 11. Accessibility & Keyboard Navigation

- Semantic HTML5 tags (`<header>`, `<nav>`, `<main>`, `<section>`, `<article>`, `<footer>`).
- Contrast ratio: Primary text (`#F4F5F7`) on background (`#090A0F`) has a contrast ratio of > 17:1 (exceeds WCAG AAA).
- Focus states: Clear electric cyan outline (`2px solid #32B8F4`) on all interactive controls.
- Screen readers: ARIA labels on all modal dialogs, status badges, and expandable drawers.

---

## 12. Integrity Rule: Zero Fabricated Sources, Details, or Metrics

- Never invent fake sources, authors, publication dates, or article URLs.
- If run telemetry is unavailable from the engine, display `"Unavailable"` rather than fabricating numbers.
- Maintain an empirical, auditable data trail from raw RSS ingest to final executive briefing.
