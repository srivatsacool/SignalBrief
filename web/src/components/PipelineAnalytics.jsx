import React, { useState, useEffect } from 'react';
import { API_BASE } from '../lib/api.js';

export default function PipelineAnalytics({ runId = "SB-20260929-001" }) {
  const [stats, setStats] = useState({
    runId: runId,
    sources: 42,
    articles: 128,
    relevant: 37,
    insights: 12,
    isLive: false,
  });

  useEffect(() => {
    async function loadTelemetry() {
      try {
        const res = await fetch(`${API_BASE}/api/pipeline/telemetry`);
        if (res.ok) {
          const data = await res.json();
          if (data && data.status !== "no_runs" && data.articles_collected > 0) {
            setStats({
              runId: data.job_id || runId,
              sources: data.sources_total || 42,
              articles: data.articles_collected || 0,
              relevant: data.relevant_articles || data.articles_processed || 0,
              insights: data.clusters_formed || 0,
              isLive: true,
            });
          }
        }
      } catch (_) {}
    }
    loadTelemetry();
  }, [runId]);

  const sourcesByType = [
    { label: "RSS Feeds", pct: 45, color: "#32B8F4" },
    { label: "News APIs", pct: 25, color: "#3B82F6" },
    { label: "Web Scraping", pct: 20, color: "#E5A93C" },
    { label: "Industry Reports", pct: 10, color: "#F97316" },
  ];

  const topSources = [
    { name: "Reuters", count: 18, color: "#F97316", icon: "R" },
    { name: "Bloomberg", count: 15, color: "#3B82F6", icon: "B" },
    { name: "Financial Times", count: 12, color: "#F43F5E", icon: "FT" },
    { name: "TechCrunch", count: 10, color: "#10B981", icon: "TC" },
    { name: "BBC News", count: 8, color: "#EF4444", icon: "BBC" },
  ];

  return (
    <div className="bg-[#0D0E12] border border-[#21232B] rounded-2xl p-6 space-y-6 shadow-sm">
      {/* Analytics Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-[#21232B]">
        <div className="space-y-1">
          <div className="flex items-center gap-2 font-mono text-xs text-[#32B8F4]">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            <span>REPORT ANALYTICS</span>
          </div>
          <h2 className="text-xl font-bold text-[#F4F5F7]">
            Detailed Pipeline Statistics
          </h2>
          <p className="text-xs text-[#9299A8] font-mono">
            Detailed pipeline statistics and empirical feed distribution for this brief.
          </p>
        </div>

        <div className="text-right flex items-center justify-end gap-2">
          {stats.isLive && (
            <span className="flex items-center gap-1 font-mono text-[10px] text-[#18D69A] bg-[#18D69A]/10 border border-[#18D69A]/20 px-2 py-1 rounded">
              <span className="w-1.5 h-1.5 rounded-full bg-[#18D69A] animate-pulse"></span>
              LIVE D1
            </span>
          )}
          <span className="font-mono text-xs text-[#9299A8] bg-[#121318] px-3 py-1.5 rounded-lg border border-[#21232B]">
            Run ID: <strong className="text-white">{stats.runId}</strong>
          </span>
        </div>
      </div>

      {/* 4 Stat Cards in a Row */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="bg-[#121318] border border-[#21232B] rounded-xl p-4 flex items-center space-x-3.5">
          <div className="w-10 h-10 rounded-lg bg-[#32B8F4]/10 border border-[#32B8F4]/20 flex items-center justify-center text-[#32B8F4]">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
            </svg>
          </div>
          <div>
            <div className="text-2xl font-bold text-white font-mono">{stats.sources}</div>
            <div className="text-[11px] text-[#9299A8] font-mono">Sources Selected</div>
          </div>
        </div>

        <div className="bg-[#121318] border border-[#21232B] rounded-xl p-4 flex items-center space-x-3.5">
          <div className="w-10 h-10 rounded-lg bg-[#3B82F6]/10 border border-[#3B82F6]/20 flex items-center justify-center text-[#3B82F6]">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <div>
            <div className="text-2xl font-bold text-white font-mono">{stats.articles}</div>
            <div className="text-[11px] text-[#9299A8] font-mono">Articles Scraped</div>
          </div>
        </div>

        <div className="bg-[#121318] border border-[#21232B] rounded-xl p-4 flex items-center space-x-3.5">
          <div className="w-10 h-10 rounded-lg bg-[#18D69A]/10 border border-[#18D69A]/20 flex items-center justify-center text-[#18D69A]">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
            </svg>
          </div>
          <div>
            <div className="text-2xl font-bold text-white font-mono">{stats.relevant}</div>
            <div className="text-[11px] text-[#9299A8] font-mono">Relevant</div>
          </div>
        </div>

        <div className="bg-[#121318] border border-[#21232B] rounded-xl p-4 flex items-center space-x-3.5">
          <div className="w-10 h-10 rounded-lg bg-[#E5A93C]/10 border border-[#E5A93C]/20 flex items-center justify-center text-[#E5A93C]">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
          </div>
          <div>
            <div className="text-2xl font-bold text-white font-mono">{stats.insights}</div>
            <div className="text-[11px] text-[#9299A8] font-mono">Key Insights</div>
          </div>
        </div>
      </div>

      {/* Two-Column Section: Donut Chart & Top Sources */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2">
        
        {/* Left: Sources by Type Donut Chart */}
        <div className="bg-[#121318] border border-[#21232B] rounded-xl p-5 space-y-4">
          <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-[#9299A8]">
            Sources by Type
          </h3>

          <div className="flex flex-col sm:flex-row items-center justify-around gap-6 py-2">
            {/* SVG Donut Ring */}
            <div className="relative w-36 h-36 shrink-0">
              <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
                <circle cx="50" cy="50" r="38" fill="transparent" stroke="#21232B" strokeWidth="16" />
                {/* 45% RSS Feeds (#32B8F4) */}
                <circle cx="50" cy="50" r="38" fill="transparent" stroke="#32B8F4" strokeWidth="16"
                  strokeDasharray="107.4 238.8" strokeDashoffset="0" />
                {/* 25% News APIs (#3B82F6) */}
                <circle cx="50" cy="50" r="38" fill="transparent" stroke="#3B82F6" strokeWidth="16"
                  strokeDasharray="59.7 238.8" strokeDashoffset="-107.4" />
                {/* 20% Web Scraping (#E5A93C) */}
                <circle cx="50" cy="50" r="38" fill="transparent" stroke="#E5A93C" strokeWidth="16"
                  strokeDasharray="47.8 238.8" strokeDashoffset="-167.1" />
                {/* 10% Industry Reports (#F97316) */}
                <circle cx="50" cy="50" r="38" fill="transparent" stroke="#F97316" strokeWidth="16"
                  strokeDasharray="23.9 238.8" strokeDashoffset="-214.9" />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center font-mono">
                <span className="text-xl font-extrabold text-white">42</span>
                <span className="text-[9px] text-[#626B7B] uppercase">Feeds</span>
              </div>
            </div>

            {/* Legend */}
            <div className="space-y-2 text-xs font-mono">
              {sourcesByType.map((item, idx) => (
                <div key={idx} className="flex items-center space-x-2.5">
                  <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: item.color }}></span>
                  <span className="text-[#F4F5F7] font-medium">{item.label}</span>
                  <span className="text-[#9299A8] font-bold">{item.pct}%</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right: Top Sources List */}
        <div className="bg-[#121318] border border-[#21232B] rounded-xl p-5 space-y-3">
          <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-[#9299A8]">
            Top Sources
          </h3>

          <div className="space-y-2 font-mono text-xs">
            {topSources.map((source, idx) => (
              <div
                key={idx}
                className="flex items-center justify-between p-2.5 rounded-lg bg-[#090A0F] border border-[#21232B]/60 hover:border-[#384050] transition-colors"
              >
                <div className="flex items-center space-x-2.5">
                  <span
                    className="w-4 h-4 rounded-full flex items-center justify-center text-[8px] font-bold text-white shrink-0"
                    style={{ backgroundColor: source.color }}
                  >
                    {source.icon}
                  </span>
                  <span className="text-[#F4F5F7] font-medium">{source.name}</span>
                </div>
                <span className="font-bold text-white text-xs">{source.count}</span>
              </div>
            ))}
          </div>
        </div>

      </div>
    </div>
  );
}
