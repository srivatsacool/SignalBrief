import React, { useState } from 'react';

const DEFAULT_STAGES = [
  {
    id: 1,
    name: "Feed Discovery",
    tag: "18 Feeds",
    desc: "Active RSS/API endpoints scanned across government, academic, and industrial journals.",
    metric: "18 Feeds Monitored",
    status: "completed",
  },
  {
    id: 2,
    name: "Scraping",
    tag: "240 Ingested",
    desc: "Multi-source raw HTTP extraction with DOM boilerplate and ad removal.",
    metric: "240 Ingested",
    status: "completed",
  },
  {
    id: 3,
    name: "Cleaning & Dedup",
    tag: "89 Pruned",
    desc: "Regex HTML normalization, language validation, and MinHash cosine deduplication.",
    metric: "89 Pruned (37%)",
    status: "completed",
  },
  {
    id: 4,
    name: "DBSCAN Clustering",
    tag: "7 Clusters",
    desc: "TF-IDF n-gram vectorization and density-based spatial clustering (eps=0.45).",
    metric: "7 Thematic Clusters",
    status: "completed",
  },
  {
    id: 5,
    name: "Extractive Synthesis",
    tag: "3.8s Latency",
    desc: "Centroid sentence extraction with 'What Changed' and 'Why It Matters' synthesis.",
    metric: "3.8s Pipeline Latency",
    status: "completed",
  },
  {
    id: 6,
    name: "Source Verification",
    tag: "100% Sourced",
    desc: "Direct URL validation ensuring every development has attached primary source citations.",
    metric: "100% Citation Pass",
    status: "completed",
  },
];

export default function PipelineVisualizer({ stages = DEFAULT_STAGES, activeStageIndex = 3, engineStatus = "Verified" }) {
  const [selectedStage, setSelectedStage] = useState(stages[activeStageIndex] || stages[0]);

  const getStatusBadge = (status) => {
    switch (status) {
      case 'completed':
        return <span className="w-1.5 h-1.5 rounded-full bg-[#18D69A] shadow-[0_0_6px_#18D69A]"></span>;
      case 'running':
        return <span className="w-1.5 h-1.5 rounded-full bg-[#32B8F4] animate-ping"></span>;
      case 'failed':
        return <span className="w-1.5 h-1.5 rounded-full bg-rose-500"></span>;
      default:
        return <span className="w-1.5 h-1.5 rounded-full bg-[#626B7B]"></span>;
    }
  };

  return (
    <div className="bg-[#0D0E12] border border-[#252832] rounded-xl p-5 space-y-4 shadow-sm">
      {/* HUD Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-[#252832]">
        <div className="flex items-center space-x-2.5">
          <span className="w-2 h-2 rounded-full bg-[#18D69A] animate-pulse shadow-[0_0_8px_#18D69A]"></span>
          <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-[#F4F5F7]">
            Pipeline Transparency HUD
          </h3>
        </div>
        <div className="flex items-center gap-3 font-mono text-[11px] text-[#9299A8]">
          <span>Cadence: <strong>02:00 UTC</strong></span>
          <span>•</span>
          <span>Engine Status: <strong className="text-[#18D69A]">{engineStatus}</strong></span>
        </div>
      </div>

      {/* 6-Stage Stepper Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2">
        {stages.map((s, idx) => {
          const isSelected = selectedStage.id === s.id;
          const isCompleted = s.status === 'completed';
          const isRunning = s.status === 'running';

          return (
            <button
              key={s.id}
              onClick={() => setSelectedStage(s)}
              className={`p-3 rounded-lg text-left transition-all border font-mono cursor-pointer ${
                isSelected
                  ? 'bg-[#171920] border-[#32B8F4]/70 shadow-[0_0_12px_rgba(50,184,244,0.15)] ring-1 ring-[#32B8F4]/40'
                  : 'bg-[#121318] border-[#252832] hover:border-[#384050] hover:bg-[#15161C]'
              }`}
            >
              <div className="flex items-center justify-between mb-1.5">
                <span className="text-[10px] text-[#626B7B] font-bold">0{s.id}</span>
                {getStatusBadge(s.status)}
              </div>
              <div className="text-xs font-semibold text-[#F4F5F7] truncate">{s.name}</div>
              <div className={`text-[10px] mt-1 font-mono ${
                isRunning ? 'text-[#32B8F4]' : isCompleted ? 'text-[#18D69A]' : 'text-[#626B7B]'
              }`}>
                {s.tag || 'Unavailable'}
              </div>
            </button>
          );
        })}
      </div>

      {/* Selected Stage Detail Drawer */}
      <div className="p-3.5 rounded-lg bg-[#121318] border border-[#252832] flex flex-col md:flex-row md:items-center justify-between gap-3 text-xs">
        <div className="flex items-start md:items-center gap-2.5">
          <span className="font-mono text-[#32B8F4] font-bold shrink-0">
            [Stage 0{selectedStage.id}: {selectedStage.name}]
          </span>
          <span className="text-[#9299A8] leading-relaxed">{selectedStage.desc}</span>
        </div>
        <div className="shrink-0 font-mono text-[11px] text-[#9299A8] bg-[#090A0F] px-3 py-1 rounded border border-[#252832] self-start md:self-auto">
          Metric: <span className="text-[#F4F5F7] font-semibold">{selectedStage.metric || 'Unavailable'}</span>
        </div>
      </div>
    </div>
  );
}
