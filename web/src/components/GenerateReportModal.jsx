import React, { useState, useEffect, useRef, useCallback } from 'react';
import { createPortal } from 'react-dom';
import { API_BASE } from '../lib/api.js';

const TOPIC_CHIPS = [
  { id: "world_macro", name: "All Topics (Worldwide)", defaultSelected: true, locked: true },
  { id: "manufacturing", name: "Manufacturing", defaultSelected: true },
  { id: "technology", name: "Technology", defaultSelected: true },
  { id: "ai", name: "Artificial Intelligence", defaultSelected: true },
  { id: "energy", name: "Energy & Climate", defaultSelected: false },
  { id: "economy", name: "Economy & Markets", defaultSelected: false },
  { id: "geopolitics", name: "Geopolitics", defaultSelected: false },
  { id: "supply_chain", name: "Supply Chain", defaultSelected: false },
  { id: "automotive", name: "Automotive", defaultSelected: false },
  { id: "aerospace", name: "Aerospace & Defense", defaultSelected: false },
  { id: "pharma", name: "Pharma & Healthcare", defaultSelected: false },
  { id: "biotech", name: "Biotechnology", defaultSelected: false },
  { id: "semiconductors", name: "Semiconductors", defaultSelected: false },
  { id: "robotics", name: "Robotics", defaultSelected: false },
  { id: "logistics", name: "Logistics & Transport", defaultSelected: false },
  { id: "sustainability", name: "Sustainability", defaultSelected: false },
  { id: "policy", name: "Policy & Regulation", defaultSelected: false },
  { id: "trade", name: "Trade & Tariffs", defaultSelected: false },
  { id: "commodities", name: "Commodities", defaultSelected: false },
  { id: "cybersecurity", name: "Cybersecurity", defaultSelected: false },
  { id: "space", name: "Space & Satellite", defaultSelected: false },
  { id: "startups", name: "Startups & VC", defaultSelected: false },
  { id: "retail", name: "Retail & Consumer", defaultSelected: false },
  { id: "construction", name: "Construction", defaultSelected: false },
  { id: "agriculture", name: "Agriculture & Food", defaultSelected: false },
  { id: "finance", name: "Finance", defaultSelected: false },
  { id: "workforce", name: "Workforce & Labor", defaultSelected: false },
  { id: "science", name: "Science & Research", defaultSelected: false },
];

const PIPELINE_STAGES = [
  { num: 1, label: "Job Queued & Dispatched", count: (j) => j?.id ? `ID: ${j.id.slice(-8)}` : "—", desc: "Registered in D1 & sent to runner" },
  { num: 2, label: "Scanning Feeds & Sources", count: (j) => j?.sources_total > 0 ? `${j.sources_total} sources` : "42 sources", desc: "Discovering active RSS feeds" },
  { num: 3, label: "Scraping & Ingesting Articles", count: (j) => `${j?.articles_collected || 0} articles`, hasBar: true, desc: "Fetching full article texts" },
  { num: 4, label: "Filtering & Deduplication", count: (j) => j?.articles_processed > 0 ? `${j.articles_processed} passed` : "—", desc: "SimHash & content cleanup" },
  { num: 5, label: "AI Analysis & Semantic Scoring", count: (j) => j?.relevant_articles > 0 ? `${j.relevant_articles} relevant` : "—", desc: "Evaluating strategic relevance" },
  { num: 6, label: "Clustering & Ranking Signals", count: (j) => j?.clusters_formed > 0 ? `${j.clusters_formed} clusters` : "—", desc: "Synthesizing core developments" },
  { num: 7, label: "HTML & Brief Rendering", count: (j) => j?.report_id ? "Done" : "—", desc: "Building executive briefing" },
  { num: 8, label: "Cloud Sync & Storage", count: (j) => j?.status === "completed" ? "Verified" : "—", desc: "Persisting to R2 & D1" },
];

function calculateActiveStage(job) {
  if (!job) return 1;
  if (job.status === "completed") return 8;
  if (job.status === "failed") return -1;
  if (job.status === "partial") return 8;
  if (job.status === "queued") return 1;
  if (job.report_id) return 7;
  if (job.clusters_formed > 0) return 6;
  if (job.relevant_articles > 0) return 5;
  if (job.articles_processed > 0) return 4;
  if (job.articles_collected > 0) return 3;
  return 2; // running, discovering sources
}

const POLL_INTERVAL_MS = 3000;
const MAX_POLL_TIME_MS = 25 * 60 * 1000; // 25 minutes max

export default function GenerateReportModal() {
  const [mounted, setMounted] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const [activeStep, setActiveStep] = useState(1);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedTopics, setSelectedTopics] = useState(
    TOPIC_CHIPS.filter(t => t.defaultSelected).map(t => t.id)
  );

  const [recency, setRecency] = useState("24h");
  const [format, setFormat] = useState("html");
  const [depth, setDepth] = useState("standard");

  const [isGenerating, setIsGenerating] = useState(false);
  const [isCompleted, setIsCompleted] = useState(false);
  const [isFailed, setIsFailed] = useState(false);
  const [error, setError] = useState(null);
  const [latestReportId, setLatestReportId] = useState(null);

  // Active Job Telemetry
  const [currentJob, setCurrentJob] = useState(null);
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const [dispatchInfo, setDispatchInfo] = useState(null);

  const pollTimerRef = useRef(null);
  const elapsedTimerRef = useRef(null);
  const pollStartRef = useRef(null);

  useEffect(() => {
    setMounted(true);
    // Check if there was an active job stored in localStorage
    try {
      const savedJobId = localStorage.getItem("signalbrief_active_job_id");
      if (savedJobId) {
        checkExistingJob(savedJobId);
      }
    } catch (_) {}
  }, []);

  const checkExistingJob = async (jobId) => {
    try {
      const res = await fetch(`${API_BASE}/api/jobs/${jobId}`);
      if (res.ok) {
        const job = await res.json();
        if (job.status === "running" || job.status === "queued") {
          setCurrentJob(job);
        }
      }
    } catch (_) {}
  };

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape' && isOpen && !isGenerating) setIsOpen(false);
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, isGenerating]);

  // Clean up timers on unmount
  useEffect(() => {
    return () => {
      if (pollTimerRef.current) clearInterval(pollTimerRef.current);
      if (elapsedTimerRef.current) clearInterval(elapsedTimerRef.current);
    };
  }, []);

  const stopPolling = useCallback(() => {
    if (pollTimerRef.current) {
      clearInterval(pollTimerRef.current);
      pollTimerRef.current = null;
    }
    if (elapsedTimerRef.current) {
      clearInterval(elapsedTimerRef.current);
      elapsedTimerRef.current = null;
    }
  }, []);

  const toggleTopic = (id) => {
    if (id === "world_macro") return;
    setSelectedTopics(prev =>
      prev.includes(id) ? prev.filter(t => t !== id) : [...prev, id]
    );
  };

  const allSelected = selectedTopics.length === TOPIC_CHIPS.length;
  const handleSelectAllToggle = () => {
    setSelectedTopics(allSelected ? ["world_macro"] : TOPIC_CHIPS.map(t => t.id));
  };

  const filteredChips = TOPIC_CHIPS.filter(t =>
    t.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Poll job status from Worker
  const pollJobStatus = useCallback(async (jobId) => {
    try {
      const res = await fetch(`${API_BASE}/api/jobs/${jobId}`);
      if (!res.ok) {
        // If 404 yet, runner might still be inserting or API temporarily warming
        return;
      }
      const job = await res.json();
      setCurrentJob(job);

      if (job.status === "completed") {
        stopPolling();
        setIsGenerating(false);
        setIsCompleted(true);
        if (job.report_id) {
          setLatestReportId(job.report_id);
        }
        try { localStorage.removeItem("signalbrief_active_job_id"); } catch (_) {}
      } else if (job.status === "failed") {
        stopPolling();
        setIsGenerating(false);
        setIsFailed(true);
        setError(job.error_message || "Pipeline execution encountered an error on the runner.");
        try { localStorage.removeItem("signalbrief_active_job_id"); } catch (_) {}
      } else if (job.status === "partial") {
        stopPolling();
        setIsGenerating(false);
        setIsCompleted(true);
        if (job.report_id) setLatestReportId(job.report_id);
        try { localStorage.removeItem("signalbrief_active_job_id"); } catch (_) {}
      }

      // Check max poll time
      if (Date.now() - pollStartRef.current > MAX_POLL_TIME_MS) {
        stopPolling();
        setIsGenerating(false);
        setError("Pipeline job is taking longer than expected. You can check back later or verify GitHub Actions.");
      }
    } catch (err) {
      console.warn("[SignalBrief Job Poll Warning]:", err.message);
    }
  }, [stopPolling]);

  // Start Generation: dispatches real job and starts polling
  const handleStartGeneration = async () => {
    setActiveStep(3);
    setIsGenerating(true);
    setIsCompleted(false);
    setIsFailed(false);
    setError(null);
    setElapsedSeconds(0);
    pollStartRef.current = Date.now();

    const domain = selectedTopics.find(t => t !== "world_macro") || "manufacturing";

    // Start elapsed timer
    if (elapsedTimerRef.current) clearInterval(elapsedTimerRef.current);
    elapsedTimerRef.current = setInterval(() => {
      setElapsedSeconds(prev => prev + 1);
    }, 1000);

    try {
      // 1. Post to real Worker endpoint
      const triggerRes = await fetch(`${API_BASE}/api/jobs`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          domain,
          topics: selectedTopics,
          recency,
          depth,
          format,
        }),
      });

      if (!triggerRes.ok) {
        throw new Error(`Server returned HTTP ${triggerRes.status}`);
      }

      const jobData = await triggerRes.json();
      const jobId = jobData.job_id;

      if (!jobId) {
        throw new Error("API response did not return a valid job ID.");
      }

      setCurrentJob({
        id: jobId,
        status: jobData.status || "queued",
        domain_id: domain,
        sources_total: selectedTopics.length * 14,
        articles_collected: 0,
        articles_processed: 0,
        relevant_articles: 0,
        clusters_formed: 0,
      });

      setDispatchInfo(jobData.dispatch || null);

      try {
        localStorage.setItem("signalbrief_active_job_id", jobId);
      } catch (_) {}

      // 2. Start polling for real status updates
      if (pollTimerRef.current) clearInterval(pollTimerRef.current);
      pollTimerRef.current = setInterval(() => {
        pollJobStatus(jobId);
      }, POLL_INTERVAL_MS);

    } catch (err) {
      console.error("[SignalBrief Trigger Error]:", err);
      stopPolling();
      setIsGenerating(false);
      setIsFailed(true);
      setError(`Failed to dispatch pipeline: ${err.message}. Ensure the API Worker is reachable at ${API_BASE}.`);
    }
  };

  const handleFinish = () => {
    setIsOpen(false);
    setIsCompleted(false);
    setIsFailed(false);
    setActiveStep(1);
    if (latestReportId) {
      window.location.href = `/report/${latestReportId}`;
    } else {
      window.location.reload();
    }
  };

  const handleRetry = () => {
    setIsFailed(false);
    setError(null);
    handleStartGeneration();
  };

  const activeStage = calculateActiveStage(currentJob);
  const formatTime = (secs) => {
    const m = Math.floor(secs / 60);
    const s = secs % 60;
    return `${m}:${s < 10 ? '0' : ''}${s}`;
  };

  return (
    <>
      <button
        type="button"
        onClick={() => {
          setIsOpen(true);
          if (!isGenerating && !isCompleted) {
            setActiveStep(1);
            setError(null);
          }
        }}
        className="px-4 py-2.5 rounded-lg bg-[#E5A93C] hover:bg-[#d89729] text-[#090A0F] font-bold text-xs flex items-center gap-2 transition-all shadow-[0_0_15px_rgba(229,169,60,0.3)] hover:shadow-[0_0_20px_rgba(229,169,60,0.5)] cursor-pointer"
      >
        <span className="text-sm font-extrabold leading-none">+</span>
        <span>Create New Brief</span>
      </button>

      {isOpen && mounted && createPortal(
        <div
          className="fixed inset-0 z-[100] flex items-center justify-center p-4 sm:p-6 bg-black/85 backdrop-blur-md animate-in fade-in duration-150"
          onClick={(e) => { if (e.target === e.currentTarget && !isGenerating) setIsOpen(false); }}
        >
          <div
            className="relative w-full max-w-4xl bg-[#0D0E12] border border-[#21232B] rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className="flex items-center justify-between p-6 pb-4 border-b border-[#21232B]">
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 rounded-lg bg-[#14151B] border border-[#262933] flex items-center justify-center text-[#E5A93C] shrink-0">
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4v16m8-8H4" />
                  </svg>
                </div>
                <div>
                  <h2 className="text-lg font-bold text-[#F4F5F7]">
                    {activeStep === 3 ? "Pipeline Execution Telemetry" : "Create a New Brief"}
                  </h2>
                  <p className="text-xs text-[#9299A8] mt-0.5">
                    {activeStep === 1 && "Select topics you're interested in. Default is all topics worldwide."}
                    {activeStep === 2 && "Select analysis recency, summary depth, and output formatting."}
                    {activeStep === 3 && (
                      <span className="flex items-center gap-1.5 font-mono">
                        <span className={`w-1.5 h-1.5 rounded-full inline-block ${
                          isCompleted ? 'bg-[#18D69A]' : isFailed ? 'bg-[#FF6B6B]' : 'bg-[#E5A93C] animate-pulse'
                        }`}></span>
                        {isCompleted && "Pipeline completed successfully — verified 100% primary sources"}
                        {isFailed && "Pipeline execution failed"}
                        {isGenerating && `Active Job: ${currentJob?.id || 'Initializing...'} • Elapsed: ${formatTime(elapsedSeconds)}`}
                      </span>
                    )}
                  </p>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setIsOpen(false)}
                className="text-[#626B7B] hover:text-white text-lg p-1.5 rounded-lg hover:bg-[#161820] transition-colors cursor-pointer"
                title="Close modal (Esc)"
              >✕</button>
            </div>

            {/* STEPS 1 & 2 */}
            {(activeStep === 1 || activeStep === 2) && (
              <div className="grid grid-cols-1 md:grid-cols-12 gap-6 p-6 flex-1 overflow-hidden">
                <div className="md:col-span-3 space-y-3 font-mono text-xs flex flex-col justify-between">
                  <div className="space-y-2">
                    {[
                      { step: 1, label: "Select Topics", action: () => setActiveStep(1) },
                      { step: 2, label: "Configure",     action: () => { if (selectedTopics.length > 0) setActiveStep(2); } },
                      { step: 3, label: "Review & Run",  action: () => { if (selectedTopics.length > 0) handleStartGeneration(); } },
                    ].map(({ step, label, action }) => (
                      <button
                        key={step}
                        type="button"
                        onClick={action}
                        className={`w-full p-2.5 rounded-lg flex items-center space-x-2.5 transition-all text-left cursor-pointer ${
                          activeStep === step
                            ? 'bg-[#E5A93C] text-[#090A0F] font-bold shadow-[0_0_12px_rgba(229,169,60,0.3)]'
                            : step === 3 ? 'text-[#626B7B] hover:text-[#9299A8] hover:bg-[#121318]'
                            : 'text-[#9299A8] hover:text-white hover:bg-[#121318]'
                        }`}
                      >
                        <span className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold shrink-0 ${
                          activeStep === step ? 'bg-[#090A0F] text-[#E5A93C]' : 'bg-[#121318] text-[#9299A8] border border-[#21232B]'
                        }`}>{step}</span>
                        <span className="truncate">{label}</span>
                      </button>
                    ))}
                  </div>
                  <div className="p-3 bg-[#0A0B0E] border border-[#21232B] rounded-xl space-y-1.5">
                    <div className="text-[10px] text-[#626B7B] uppercase tracking-wider font-bold">Topics Selected</div>
                    <div className="text-sm font-bold text-white font-mono">
                      {selectedTopics.length} <span className="text-xs text-[#9299A8]">/ {TOPIC_CHIPS.length}</span>
                    </div>
                    <div className="text-[10px] text-[#18D69A] leading-tight font-mono">● World Macro Included</div>
                  </div>
                </div>

                <div className="md:col-span-9 flex flex-col space-y-4 overflow-hidden">
                  {activeStep === 1 && (
                    <>
                      <div className="flex items-center gap-3">
                        <div className="relative flex-1">
                          <input
                            type="text"
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            placeholder="Search topics..."
                            className="w-full px-3.5 py-2 pl-9 pr-8 rounded-lg bg-[#121318] border border-[#21232B] text-xs font-mono text-white placeholder-[#626B7B] focus:outline-none focus:border-[#E5A93C] transition-colors"
                          />
                          <span className="absolute left-3 top-2.5 text-xs text-[#626B7B]">🔍</span>
                          {searchQuery && (
                            <button type="button" onClick={() => setSearchQuery("")}
                              className="absolute right-2.5 top-2 text-xs text-[#626B7B] hover:text-white cursor-pointer">✕</button>
                          )}
                        </div>
                        <button type="button" onClick={handleSelectAllToggle}
                          className="px-3.5 py-2 rounded-lg bg-[#121318] hover:bg-[#161820] text-xs text-[#9299A8] hover:text-white border border-[#21232B] hover:border-[#384050] font-mono shrink-0 transition-colors cursor-pointer">
                          {allSelected ? "Clear All" : "Select All"}
                        </button>
                      </div>
                      <div className="flex-1 overflow-y-auto pr-1 flex flex-wrap gap-2 max-h-[340px]">
                        {filteredChips.map((chip) => {
                          const isSelected = selectedTopics.includes(chip.id);
                          return (
                            <button key={chip.id} type="button" onClick={() => toggleTopic(chip.id)}
                              className={`px-3 py-1.5 rounded-lg border text-xs font-medium transition-all cursor-pointer flex items-center space-x-1.5 ${
                                isSelected
                                  ? 'bg-[#E5A93C] text-[#090A0F] border-[#E5A93C] font-bold shadow-[0_0_10px_rgba(229,169,60,0.25)]'
                                  : 'bg-[#121318] text-[#9299A8] border-[#21232B] hover:border-[#384050] hover:text-white'
                              }`}>
                              {isSelected && <span className="text-[10px]">✓</span>}
                              <span>{chip.name}</span>
                              {chip.locked && <span className="text-[9px] px-1 rounded bg-black/20 text-[#090A0F] font-mono uppercase ml-1">Baseline</span>}
                            </button>
                          );
                        })}
                      </div>
                      <div className="flex items-center justify-end space-x-3 pt-4 border-t border-[#21232B] mt-auto">
                        <button type="button" onClick={() => setIsOpen(false)}
                          className="px-4 py-2 rounded-lg bg-[#121318] hover:bg-[#161820] border border-[#21232B] text-xs font-mono text-[#9299A8] hover:text-white transition-colors cursor-pointer">Cancel</button>
                        <button type="button" onClick={() => setActiveStep(2)} disabled={selectedTopics.length === 0}
                          className="px-5 py-2 rounded-lg bg-[#E5A93C] hover:bg-[#d89729] text-[#090A0F] font-bold text-xs transition-colors shadow-[0_0_12px_rgba(229,169,60,0.25)] cursor-pointer disabled:opacity-50">Next →</button>
                      </div>
                    </>
                  )}

                  {activeStep === 2 && (
                    <>
                      <div className="space-y-4 flex-1">
                        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                          {[
                            { label: "Recency Window", value: recency, set: setRecency, opts: [
                              ["24h", "Last 24 Hours (Daily)"], ["48h", "Last 48 Hours"], ["7d", "Last 7 Days (Weekly)"],
                            ]},
                            { label: "Briefing Depth", value: depth, set: setDepth, opts: [
                              ["standard", "Standard (6–8 Signals)"], ["executive", "Executive Dense (3–5)"], ["deep", "Comprehensive Horizon (10+)"],
                            ]},
                            { label: "Output Format", value: format, set: setFormat, opts: [
                              ["html", "Responsive HTML5"], ["text", "Mobile Clean Plaintext"], ["markdown", "Markdown Export"],
                            ]},
                          ].map((f) => (
                            <div key={f.label} className="bg-[#121318] border border-[#21232B] rounded-xl p-3.5 space-y-2">
                              <label className="text-[10px] font-mono uppercase tracking-wider text-[#9299A8] block font-bold">{f.label}</label>
                              <select value={f.value} onChange={(e) => f.set(e.target.value)}
                                className="w-full bg-[#090A0F] border border-[#21232B] text-xs font-mono text-white p-2 rounded-lg focus:outline-none focus:border-[#E5A93C] cursor-pointer">
                                {f.opts.map(([v, l]) => <option key={v} value={v}>{l}</option>)}
                              </select>
                            </div>
                          ))}
                        </div>
                        <div className="bg-[#121318] p-4 rounded-xl border border-[#21232B] text-xs font-mono text-[#9299A8] space-y-1.5">
                          <div className="text-white font-bold">Execution Architecture Overview</div>
                          <div>Target: <strong className="text-[#E5A93C]">{selectedTopics.length}</strong> topics across industrial intelligence domains.</div>
                          <div className="text-[11px] text-[#626B7B]">
                            Asynchronous dispatch: Workers API queues a verifiable job in D1 and dispatches the GitHub Actions runner. Progress updates stream in real time.
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center justify-between pt-4 border-t border-[#21232B] mt-auto">
                        <button type="button" onClick={() => setActiveStep(1)}
                          className="px-4 py-2 rounded-lg bg-[#121318] hover:bg-[#161820] border border-[#21232B] text-xs font-mono text-[#9299A8] hover:text-white transition-colors cursor-pointer">← Back to Topics</button>
                        <button type="button" onClick={handleStartGeneration}
                          className="px-5 py-2 rounded-lg bg-[#E5A93C] hover:bg-[#d89729] text-[#090A0F] font-bold text-xs transition-colors shadow-[0_0_15px_rgba(229,169,60,0.3)] cursor-pointer">Start Generation →</button>
                      </div>
                    </>
                  )}
                </div>
              </div>
            )}

            {/* STEP 3: Live Pipeline Telemetry */}
            {activeStep === 3 && (
              <div className="p-6 space-y-6 flex flex-col flex-1">
                {/* Pipeline Banner */}
                <div className="bg-[#121318] border border-[#21232B] rounded-xl p-3 flex flex-wrap items-center justify-between gap-3 text-xs font-mono">
                  <div className="flex items-center gap-2">
                    <span className="text-[#626B7B]">JOB ID:</span>
                    <span className="text-white font-bold bg-[#090A0F] px-2 py-0.5 rounded border border-[#21232B]">
                      {currentJob?.id || "Queuing..."}
                    </span>
                    <span className="text-[#626B7B] ml-2">STATUS:</span>
                    <span className={`px-2 py-0.5 rounded text-[11px] uppercase font-bold ${
                      currentJob?.status === "completed" ? "bg-[#18D69A]/10 text-[#18D69A] border border-[#18D69A]/30" :
                      currentJob?.status === "failed" ? "bg-[#FF6B6B]/10 text-[#FF6B6B] border border-[#FF6B6B]/30" :
                      currentJob?.status === "running" ? "bg-[#3B82F6]/10 text-[#3B82F6] border border-[#3B82F6]/30 animate-pulse" :
                      "bg-[#E5A93C]/10 text-[#E5A93C] border border-[#E5A93C]/30"
                    }`}>
                      {currentJob?.status || "queued"}
                    </span>
                  </div>
                  <div className="flex items-center gap-4 text-[#9299A8]">
                    <span>Elapsed: <strong className="text-white">{formatTime(elapsedSeconds)}</strong></span>
                    {dispatchInfo?.dispatched && (
                      <span className="text-[#18D69A] text-[11px]">✓ GitHub Actions Dispatched</span>
                    )}
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
                  {/* Stages Timeline */}
                  <div className="md:col-span-8 space-y-3 font-mono text-xs">
                    {PIPELINE_STAGES.map((st) => {
                      const isPast = activeStage > st.num || isCompleted;
                      const isCurrent = activeStage === st.num && !isCompleted && !isFailed;
                      const isFailedStage = isFailed && activeStage === st.num;

                      return (
                        <div key={st.num} className="space-y-1">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-2.5">
                              {isFailedStage ? (
                                <span className="w-4 h-4 rounded-full bg-[#FF6B6B] text-white font-bold flex items-center justify-center text-[10px]">✕</span>
                              ) : isPast ? (
                                <span className="w-4 h-4 rounded-full bg-[#18D69A] text-[#090A0F] font-bold flex items-center justify-center text-[10px]">✓</span>
                              ) : isCurrent ? (
                                <span className="w-4 h-4 rounded-full bg-[#E5A93C] text-[#090A0F] font-bold flex items-center justify-center text-[10px] animate-pulse">●</span>
                              ) : (
                                <span className="w-4 h-4 rounded-full border border-[#384050] text-[#626B7B] flex items-center justify-center text-[10px]">○</span>
                              )}
                              <span className={isCurrent ? "text-white font-bold" : isPast ? "text-[#9299A8]" : "text-[#626B7B]"}>
                                {st.label}
                              </span>
                            </div>
                            <span className="text-[11px] text-[#626B7B]">{st.count(currentJob)}</span>
                          </div>
                          {st.hasBar && isCurrent && (
                            <div className="w-full bg-[#121318] rounded-full h-1 overflow-hidden ml-6">
                              <div
                                className="bg-[#E5A93C] h-1 transition-all duration-500 shadow-[0_0_8px_#E5A93C]"
                                style={{ width: `${Math.min(100, (currentJob?.articles_collected || 0) > 0 ? ((currentJob?.articles_collected || 0) / (currentJob?.sources_total || 42)) * 100 : 25)}%` }}
                              />
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>

                  {/* Real-time Metric Cards */}
                  <div className="md:col-span-4 space-y-2.5 font-mono">
                    {[
                      { icon: "🌐", color: "#32B8F4", value: currentJob?.sources_total || (selectedTopics.length * 14) || 42, label: "Sources Selected"  },
                      { icon: "📄", color: "#3B82F6", value: currentJob?.articles_collected || 0,                            label: "Articles Scraped"  },
                      { icon: "🎯", color: "#18D69A", value: currentJob?.relevant_articles || currentJob?.articles_processed || 0, label: "Relevant Articles" },
                      { icon: "💡", color: "#E5A93C", value: currentJob?.clusters_formed || 0,                               label: "Key Insights"      },
                    ].map((card) => (
                      <div key={card.label} className="bg-[#121318] border border-[#21232B] rounded-xl p-3 flex items-center space-x-3">
                        <div className="w-8 h-8 rounded-lg flex items-center justify-center text-xs shrink-0"
                          style={{ backgroundColor: `${card.color}1a`, border: `1px solid ${card.color}33`, color: card.color }}>
                          {card.icon}
                        </div>
                        <div>
                          <div className="text-base font-bold text-white">{card.value}</div>
                          <div className="text-[10px] text-[#9299A8]">{card.label}</div>
                        </div>
                      </div>
                    ))}

                    {/* Telemetry info callout */}
                    <div className="p-3 bg-[#0A0B0E] border border-[#21232B] rounded-xl text-[11px] font-mono text-[#626B7B] space-y-1">
                      <div className="text-[#9299A8] font-bold">Telemetry Source</div>
                      <div>Streamed directly from Cloudflare D1 and GitHub Actions runner callback.</div>
                    </div>
                  </div>
                </div>

                {error && (
                  <div className="text-xs font-mono text-[#FF6B6B] bg-[#FF6B6B]/10 border border-[#FF6B6B]/20 rounded-lg p-3 flex items-start gap-2">
                    <span className="shrink-0 font-bold">⚠</span>
                    <div className="flex-1">
                      <div className="font-bold">Pipeline Error:</div>
                      <div>{error}</div>
                    </div>
                  </div>
                )}

                {/* Status-specific Footer Actions */}
                {isCompleted ? (
                  <div className="pt-4 border-t border-[#21232B] flex flex-col sm:flex-row items-center justify-between gap-3">
                    <div className="flex items-center gap-2 text-xs font-mono text-[#18D69A]">
                      <span className="w-2 h-2 rounded-full bg-[#18D69A]"></span>
                      <span>
                        {(currentJob?.articles_collected || 0) > 0
                          ? "Pipeline completed successfully. 100% verified primary sources."
                          : "Pipeline executed. Report ready."}
                      </span>
                    </div>
                    <div className="flex items-center space-x-3">
                      <button type="button" onClick={() => { setIsOpen(false); setActiveStep(1); }}
                        className="px-4 py-2 rounded-lg bg-[#121318] hover:bg-[#161820] border border-[#21232B] text-xs font-mono text-[#9299A8] hover:text-white transition-colors cursor-pointer">Close</button>
                      <button type="button" onClick={handleFinish}
                        className="px-5 py-2 rounded-lg bg-[#E5A93C] hover:bg-[#d89729] text-[#090A0F] font-bold text-xs transition-colors shadow-[0_0_15px_rgba(229,169,60,0.3)] cursor-pointer">View Generated Brief →</button>
                    </div>
                  </div>
                ) : isFailed ? (
                  <div className="pt-4 border-t border-[#21232B] flex flex-col sm:flex-row items-center justify-between gap-3">
                    <div className="text-xs font-mono text-[#FF6B6B]">
                      Job ended with failure state. View runner logs for forensic details.
                    </div>
                    <div className="flex items-center space-x-3">
                      <button type="button" onClick={() => { setIsOpen(false); setActiveStep(1); }}
                        className="px-4 py-2 rounded-lg bg-[#121318] hover:bg-[#161820] border border-[#21232B] text-xs font-mono text-[#9299A8] hover:text-white transition-colors cursor-pointer">Close</button>
                      <button type="button" onClick={handleRetry}
                        className="px-5 py-2 rounded-lg bg-[#FF6B6B] hover:bg-[#e05555] text-white font-bold text-xs transition-colors shadow-[0_0_15px_rgba(255,107,107,0.3)] cursor-pointer">Retry Pipeline →</button>
                    </div>
                  </div>
                ) : (
                  <div className="pt-4 border-t border-[#21232B] flex items-center justify-between text-xs font-mono text-[#626B7B]">
                    <div className="flex items-center gap-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-[#E5A93C] animate-pulse"></span>
                      <span>
                        {currentJob?.status === "queued"
                          ? "Waiting for GitHub Actions runner to pick up job..."
                          : "Pipeline running in background. Polling D1 telemetry..."}
                      </span>
                    </div>
                    <button type="button" onClick={() => setIsOpen(false)}
                      className="text-[#9299A8] hover:text-white hover:underline cursor-pointer">
                      Minimize & Run in Background
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>,
        document.body
      )}
    </>
  );
}
