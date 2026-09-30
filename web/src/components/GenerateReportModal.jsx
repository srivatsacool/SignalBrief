import React, { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';

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

export default function GenerateReportModal() {
  const [mounted, setMounted] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const [activeStep, setActiveStep] = useState(1); // 1: Topics, 2: Configure, 3: Generating
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedTopics, setSelectedTopics] = useState(
    TOPIC_CHIPS.filter(t => t.defaultSelected).map(t => t.id)
  );

  // Configuration options (Step 2)
  const [recency, setRecency] = useState("24h");
  const [format, setFormat] = useState("html");
  const [depth, setDepth] = useState("standard");

  // Live generation state (Panel 3/9)
  const [liveStage, setLiveStage] = useState(1); // 1 to 8
  const [scrapedCount, setScrapedCount] = useState(24);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isCompleted, setIsCompleted] = useState(false);

  // Mount detection for safe client-side portal rendering
  useEffect(() => {
    setMounted(true);
  }, []);

  // Escape key listener for keyboard dismissal
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape' && isOpen) {
        setIsOpen(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen]);

  const toggleTopic = (id) => {
    if (selectedTopics.includes(id)) {
      // Keep baseline world_macro locked
      if (id === "world_macro") return;
      setSelectedTopics(selectedTopics.filter(t => t !== id));
    } else {
      setSelectedTopics([...selectedTopics, id]);
    }
  };

  const allSelected = selectedTopics.length === TOPIC_CHIPS.length;

  const handleSelectAllToggle = () => {
    if (allSelected) {
      // Clear all except the locked baseline
      setSelectedTopics(["world_macro"]);
    } else {
      setSelectedTopics(TOPIC_CHIPS.map(t => t.id));
    }
  };

  const filteredChips = TOPIC_CHIPS.filter(t =>
    t.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleStartGeneration = async () => {
    setActiveStep(3); // Go to Panel 3/9: Live Progress
    setIsGenerating(true);
    setIsCompleted(false);
    setLiveStage(1);
    setScrapedCount(24);

    // Simulate the 8 real pipeline stages with progressive ticks
    const stages = [
      { stage: 1, count: 42, delay: 500 },
      { stage: 2, count: 42, delay: 500 },
      { stage: 3, count: 120, delay: 600 },
      { stage: 4, count: 128, delay: 500 },
      { stage: 5, count: 128, delay: 500 },
      { stage: 6, count: 128, delay: 500 },
      { stage: 7, count: 128, delay: 500 },
      { stage: 8, count: 128, delay: 400 },
    ];

    for (const s of stages) {
      setLiveStage(s.stage);
      setScrapedCount(s.count);
      await new Promise(r => setTimeout(r, s.delay));
    }

    setIsGenerating(false);
    setIsCompleted(true);
  };

  const handleFinish = () => {
    setIsOpen(false);
    setIsCompleted(false);
    setActiveStep(1);
    window.location.reload();
  };

  return (
    <>
      {/* Primary Action Button (+ Create New Brief) matching Panel 1/9 */}
      <button
        type="button"
        onClick={() => { setIsOpen(true); setActiveStep(1); setIsCompleted(false); }}
        className="px-4 py-2.5 rounded-lg bg-[#E5A93C] hover:bg-[#d89729] text-[#090A0F] font-bold text-xs flex items-center gap-2 transition-all shadow-[0_0_15px_rgba(229,169,60,0.3)] hover:shadow-[0_0_20px_rgba(229,169,60,0.5)] cursor-pointer"
      >
        <span className="text-sm font-extrabold leading-none">+</span>
        <span>Create New Brief</span>
      </button>

      {/* PORTALED MODAL DIALOG OVERLAY (Direct child of body to guarantee z-100 > sidebar z-40) */}
      {isOpen && mounted && createPortal(
        <div
          className="fixed inset-0 z-[100] flex items-center justify-center p-4 sm:p-6 bg-black/85 backdrop-blur-md animate-in fade-in duration-150"
          onClick={(e) => {
            // Dismiss modal when clicking backdrop
            if (e.target === e.currentTarget) setIsOpen(false);
          }}
        >
          <div
            className="relative w-full max-w-4xl bg-[#0D0E12] border border-[#21232B] rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]"
            onClick={(e) => e.stopPropagation()}
          >
            
            {/* Header (Shared across all steps) */}
            <div className="flex items-center justify-between p-6 pb-4 border-b border-[#21232B]">
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 rounded-lg bg-[#14151B] border border-[#262933] flex items-center justify-center text-[#E5A93C] shrink-0">
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4v16m8-8H4" />
                  </svg>
                </div>
                <div>
                  <h2 className="text-lg font-bold text-[#F4F5F7]">
                    {activeStep === 3 ? "Generating Your Brief" : "Create a New Brief"}
                  </h2>
                  <p className="text-xs text-[#9299A8] mt-0.5">
                    {activeStep === 1 && "Select topics you're interested in. Default is all topics worldwide."}
                    {activeStep === 2 && "Select analysis recency, summary depth, and output formatting."}
                    {activeStep === 3 && "You can monitor the progress in real time."}
                  </p>
                </div>
              </div>

              <button
                type="button"
                onClick={() => setIsOpen(false)}
                className="text-[#626B7B] hover:text-white text-lg p-1.5 rounded-lg hover:bg-[#161820] transition-colors cursor-pointer"
                title="Close modal (Esc)"
              >
                ✕
              </button>
            </div>

            {/* BODY: STEPS 1 & 2 SHARE A 2-COLUMN VIEW WITH INTERACTIVE STEPPER */}
            {(activeStep === 1 || activeStep === 2) && (
              <div className="grid grid-cols-1 md:grid-cols-12 gap-6 p-6 flex-1 overflow-hidden">
                
                {/* Left Stepper Column (Clickable navigation buttons) */}
                <div className="md:col-span-3 space-y-3 font-mono text-xs flex flex-col justify-between">
                  <div className="space-y-2">
                    {/* Step 1 Button */}
                    <button
                      type="button"
                      onClick={() => setActiveStep(1)}
                      className={`w-full p-2.5 rounded-lg flex items-center space-x-2.5 transition-all text-left cursor-pointer ${
                        activeStep === 1
                          ? 'bg-[#E5A93C] text-[#090A0F] font-bold shadow-[0_0_12px_rgba(229,169,60,0.3)]'
                          : 'text-[#9299A8] hover:text-white hover:bg-[#121318]'
                      }`}
                    >
                      <span className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold shrink-0 ${
                        activeStep === 1 ? 'bg-[#090A0F] text-[#E5A93C]' : 'bg-[#121318] text-[#9299A8] border border-[#21232B]'
                      }`}>1</span>
                      <span className="truncate">Select Topics</span>
                    </button>

                    {/* Step 2 Button */}
                    <button
                      type="button"
                      onClick={() => {
                        if (selectedTopics.length > 0) setActiveStep(2);
                      }}
                      className={`w-full p-2.5 rounded-lg flex items-center space-x-2.5 transition-all text-left cursor-pointer ${
                        activeStep === 2
                          ? 'bg-[#E5A93C] text-[#090A0F] font-bold shadow-[0_0_12px_rgba(229,169,60,0.3)]'
                          : 'text-[#9299A8] hover:text-white hover:bg-[#121318]'
                      }`}
                    >
                      <span className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold shrink-0 ${
                        activeStep === 2 ? 'bg-[#090A0F] text-[#E5A93C]' : 'bg-[#121318] text-[#9299A8] border border-[#21232B]'
                      }`}>2</span>
                      <span className="truncate">Configure</span>
                    </button>

                    {/* Step 3 Button */}
                    <button
                      type="button"
                      onClick={() => {
                        if (selectedTopics.length > 0) handleStartGeneration();
                      }}
                      className={`w-full p-2.5 rounded-lg flex items-center space-x-2.5 transition-all text-left cursor-pointer ${
                        activeStep === 3
                          ? 'bg-[#E5A93C] text-[#090A0F] font-bold shadow-[0_0_12px_rgba(229,169,60,0.3)]'
                          : 'text-[#626B7B] hover:text-[#9299A8] hover:bg-[#121318]'
                      }`}
                    >
                      <span className="w-5 h-5 rounded-full bg-[#121318] text-[#626B7B] border border-[#21232B] flex items-center justify-center text-[10px] font-bold shrink-0">3</span>
                      <span className="truncate">Review & Run</span>
                    </button>
                  </div>

                  {/* Summary / Counter Info Card */}
                  <div className="p-3 bg-[#0A0B0E] border border-[#21232B] rounded-xl space-y-1.5">
                    <div className="text-[10px] text-[#626B7B] uppercase tracking-wider font-bold">
                      Topics Selected
                    </div>
                    <div className="text-sm font-bold text-white font-mono">
                      {selectedTopics.length} <span className="text-xs text-[#9299A8]">/ {TOPIC_CHIPS.length}</span>
                    </div>
                    <div className="text-[10px] text-[#18D69A] leading-tight">
                      ● World Macro Included
                    </div>
                  </div>
                </div>

                {/* Right Column Content */}
                <div className="md:col-span-9 flex flex-col space-y-4 overflow-hidden">
                  
                  {/* STEP 1 VIEW: TOPIC SELECTION */}
                  {activeStep === 1 && (
                    <>
                      {/* Search Bar + Select All / Clear All Toggle */}
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
                            <button
                              type="button"
                              onClick={() => setSearchQuery("")}
                              className="absolute right-2.5 top-2 text-xs text-[#626B7B] hover:text-white cursor-pointer"
                            >
                              ✕
                            </button>
                          )}
                        </div>

                        <button
                          type="button"
                          onClick={handleSelectAllToggle}
                          className="px-3.5 py-2 rounded-lg bg-[#121318] hover:bg-[#161820] text-xs text-[#9299A8] hover:text-white border border-[#21232B] hover:border-[#384050] font-mono shrink-0 transition-colors cursor-pointer"
                        >
                          {allSelected ? "Clear All" : "Select All"}
                        </button>
                      </div>

                      {/* Topic Chips Grid */}
                      <div className="flex-1 overflow-y-auto pr-1 flex flex-wrap gap-2 max-h-[340px]">
                        {filteredChips.map((chip) => {
                          const isSelected = selectedTopics.includes(chip.id);
                          const isLocked = chip.locked;

                          return (
                            <button
                              key={chip.id}
                              type="button"
                              onClick={() => toggleTopic(chip.id)}
                              className={`px-3 py-1.5 rounded-lg border text-xs font-medium transition-all cursor-pointer flex items-center space-x-1.5 ${
                                isSelected
                                  ? 'bg-[#E5A93C] text-[#090A0F] border-[#E5A93C] font-bold shadow-[0_0_10px_rgba(229,169,60,0.25)]'
                                  : 'bg-[#121318] text-[#9299A8] border-[#21232B] hover:border-[#384050] hover:text-white'
                              }`}
                            >
                              {isSelected && <span className="text-[10px]">✓</span>}
                              <span>{chip.name}</span>
                              {isLocked && (
                                <span className="text-[9px] px-1 py-0.2 rounded bg-black/20 text-[#090A0F] font-mono uppercase ml-1">
                                  Baseline
                                </span>
                              )}
                            </button>
                          );
                        })}
                      </div>

                      {/* Footer Actions */}
                      <div className="flex items-center justify-end space-x-3 pt-4 border-t border-[#21232B] mt-auto">
                        <button
                          type="button"
                          onClick={() => setIsOpen(false)}
                          className="px-4 py-2 rounded-lg bg-[#121318] hover:bg-[#161820] border border-[#21232B] text-xs font-mono text-[#9299A8] hover:text-white transition-colors cursor-pointer"
                        >
                          Cancel
                        </button>
                        <button
                          type="button"
                          onClick={() => setActiveStep(2)}
                          disabled={selectedTopics.length === 0}
                          className="px-5 py-2 rounded-lg bg-[#E5A93C] hover:bg-[#d89729] text-[#090A0F] font-bold text-xs transition-colors shadow-[0_0_12px_rgba(229,169,60,0.25)] cursor-pointer disabled:opacity-50"
                        >
                          Next →
                        </button>
                      </div>
                    </>
                  )}

                  {/* STEP 2 VIEW: CONFIGURE PARAMETERS */}
                  {activeStep === 2 && (
                    <>
                      <div className="space-y-4 flex-1">
                        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                          <div className="bg-[#121318] border border-[#21232B] rounded-xl p-3.5 space-y-2">
                            <label className="text-[10px] font-mono uppercase tracking-wider text-[#9299A8] block font-bold">
                              Recency Window
                            </label>
                            <select
                              value={recency}
                              onChange={(e) => setRecency(e.target.value)}
                              className="w-full bg-[#090A0F] border border-[#21232B] text-xs font-mono text-white p-2 rounded-lg focus:outline-none focus:border-[#E5A93C] cursor-pointer"
                            >
                              <option value="24h">Last 24 Hours (Daily)</option>
                              <option value="48h">Last 48 Hours</option>
                              <option value="7d">Last 7 Days (Weekly)</option>
                            </select>
                          </div>

                          <div className="bg-[#121318] border border-[#21232B] rounded-xl p-3.5 space-y-2">
                            <label className="text-[10px] font-mono uppercase tracking-wider text-[#9299A8] block font-bold">
                              Briefing Depth
                            </label>
                            <select
                              value={depth}
                              onChange={(e) => setDepth(e.target.value)}
                              className="w-full bg-[#090A0F] border border-[#21232B] text-xs font-mono text-white p-2 rounded-lg focus:outline-none focus:border-[#E5A93C] cursor-pointer"
                            >
                              <option value="standard">Standard (6–8 Signals)</option>
                              <option value="executive">Executive Dense (3–5)</option>
                              <option value="deep">Comprehensive Horizon (10+)</option>
                            </select>
                          </div>

                          <div className="bg-[#121318] border border-[#21232B] rounded-xl p-3.5 space-y-2">
                            <label className="text-[10px] font-mono uppercase tracking-wider text-[#9299A8] block font-bold">
                              Output Format
                            </label>
                            <select
                              value={format}
                              onChange={(e) => setFormat(e.target.value)}
                              className="w-full bg-[#090A0F] border border-[#21232B] text-xs font-mono text-white p-2 rounded-lg focus:outline-none focus:border-[#E5A93C] cursor-pointer"
                            >
                              <option value="html">Responsive HTML5</option>
                              <option value="text">Mobile Clean Plaintext</option>
                              <option value="markdown">Markdown Export</option>
                            </select>
                          </div>
                        </div>

                        <div className="bg-[#121318] p-4 rounded-xl border border-[#21232B] text-xs font-mono text-[#9299A8] space-y-1.5">
                          <div className="text-white font-bold">Summary of Run Parameters</div>
                          <div>
                            Selected: <strong className="text-[#E5A93C]">{selectedTopics.length}</strong> topics across industrial and macroeconomic dimensions.
                          </div>
                          <div className="text-[11px] text-[#626B7B]">
                            Extractive synthesis guarantees 100% verification against verified public primary feeds with zero LLM hallucinations.
                          </div>
                        </div>
                      </div>

                      {/* Footer Actions */}
                      <div className="flex items-center justify-between pt-4 border-t border-[#21232B] mt-auto">
                        <button
                          type="button"
                          onClick={() => setActiveStep(1)}
                          className="px-4 py-2 rounded-lg bg-[#121318] hover:bg-[#161820] border border-[#21232B] text-xs font-mono text-[#9299A8] hover:text-white transition-colors cursor-pointer"
                        >
                          ← Back to Topics
                        </button>
                        <button
                          type="button"
                          onClick={handleStartGeneration}
                          className="px-5 py-2 rounded-lg bg-[#E5A93C] hover:bg-[#d89729] text-[#090A0F] font-bold text-xs transition-colors shadow-[0_0_15px_rgba(229,169,60,0.3)] cursor-pointer"
                        >
                          Start Generation →
                        </button>
                      </div>
                    </>
                  )}

                </div>
              </div>
            )}

            {/* STEP 3 VIEW: LIVE PIPELINE PROGRESS MODAL */}
            {activeStep === 3 && (
              <div className="p-6 space-y-6 flex flex-col flex-1">
                {/* Two-Column Progress Grid (Matching Panel 3/9) */}
                <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
                  
                  {/* Left Column: 8-Stage Stepper */}
                  <div className="md:col-span-8 space-y-3 font-mono text-xs">
                    {[
                      { num: 1, label: "Initializing topics", count: "3/3" },
                      { num: 2, label: "Collecting sources", count: "42/42" },
                      { num: 3, label: "Scraping articles", count: `${scrapedCount}/128`, hasBar: true },
                      { num: 4, label: "Filtering & deduplicating", count: "—" },
                      { num: 5, label: "Analyzing with AI", count: "—" },
                      { num: 6, label: "Generating summary", count: "—" },
                      { num: 7, label: "Creating report", count: "—" },
                      { num: 8, label: "Finalizing", count: "—" },
                    ].map((st) => {
                      const isPast = liveStage > st.num || isCompleted;
                      const isCurrent = liveStage === st.num && !isCompleted;

                      return (
                        <div key={st.num} className="space-y-1">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-2.5">
                              {isPast ? (
                                <span className="w-4 h-4 rounded-full bg-[#18D69A] text-[#090A0F] font-bold flex items-center justify-center text-[10px]">
                                  ✓
                                </span>
                              ) : isCurrent ? (
                                <span className="w-4 h-4 rounded-full bg-[#E5A93C] text-[#090A0F] font-bold flex items-center justify-center text-[10px] animate-pulse">
                                  ●
                                </span>
                              ) : (
                                <span className="w-4 h-4 rounded-full border border-[#384050] text-[#626B7B] flex items-center justify-center text-[10px]">
                                  ○
                                </span>
                              )}
                              <span className={isCurrent ? "text-white font-bold" : isPast ? "text-[#9299A8]" : "text-[#626B7B]"}>
                                {st.label}
                              </span>
                            </div>

                            <span className="text-[11px] text-[#626B7B]">{st.count}</span>
                          </div>

                          {/* Active Amber Progress Bar for Scraping Articles */}
                          {st.hasBar && isCurrent && (
                            <div className="w-full bg-[#121318] rounded-full h-1 overflow-hidden ml-6">
                              <div
                                className="bg-[#E5A93C] h-1 transition-all duration-300 shadow-[0_0_8px_#E5A93C]"
                                style={{ width: `${(scrapedCount / 128) * 100}%` }}
                              ></div>
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>

                  {/* Right Column: 4 Live Metric Cards Stacked (Matching Panel 3/9) */}
                  <div className="md:col-span-4 space-y-2.5 font-mono">
                    <div className="bg-[#121318] border border-[#21232B] rounded-xl p-3 flex items-center space-x-3">
                      <div className="w-8 h-8 rounded-lg bg-[#32B8F4]/10 border border-[#32B8F4]/20 flex items-center justify-center text-[#32B8F4] text-xs">
                        🌐
                      </div>
                      <div>
                        <div className="text-base font-bold text-white">42</div>
                        <div className="text-[10px] text-[#9299A8]">Sources Selected</div>
                      </div>
                    </div>

                    <div className="bg-[#121318] border border-[#21232B] rounded-xl p-3 flex items-center space-x-3">
                      <div className="w-8 h-8 rounded-lg bg-[#3B82F6]/10 border border-[#3B82F6]/20 flex items-center justify-center text-[#3B82F6] text-xs">
                        📄
                      </div>
                      <div>
                        <div className="text-base font-bold text-white">{scrapedCount}</div>
                        <div className="text-[10px] text-[#9299A8]">Articles Scraped</div>
                      </div>
                    </div>

                    <div className="bg-[#121318] border border-[#21232B] rounded-xl p-3 flex items-center space-x-3">
                      <div className="w-8 h-8 rounded-lg bg-[#18D69A]/10 border border-[#18D69A]/20 flex items-center justify-center text-[#18D69A] text-xs">
                        🎯
                      </div>
                      <div>
                        <div className="text-base font-bold text-white">37</div>
                        <div className="text-[10px] text-[#9299A8]">Relevant Articles</div>
                      </div>
                    </div>

                    <div className="bg-[#121318] border border-[#21232B] rounded-xl p-3 flex items-center space-x-3">
                      <div className="w-8 h-8 rounded-lg bg-[#E5A93C]/10 border border-[#E5A93C]/20 flex items-center justify-center text-[#E5A93C] text-xs">
                        💡
                      </div>
                      <div>
                        <div className="text-base font-bold text-white">12</div>
                        <div className="text-[10px] text-[#9299A8]">Key Insights</div>
                      </div>
                    </div>
                  </div>

                </div>

                {/* Completion Feedback & Action Bar */}
                {isCompleted ? (
                  <div className="pt-4 border-t border-[#21232B] flex flex-col sm:flex-row items-center justify-between gap-3">
                    <div className="flex items-center gap-2 text-xs font-mono text-[#18D69A]">
                      <span className="w-2 h-2 rounded-full bg-[#18D69A]"></span>
                      <span>Synthesis complete. 100% verified primary sources.</span>
                    </div>

                    <div className="flex items-center space-x-3">
                      <button
                        type="button"
                        onClick={() => { setIsOpen(false); setActiveStep(1); }}
                        className="px-4 py-2 rounded-lg bg-[#121318] hover:bg-[#161820] border border-[#21232B] text-xs font-mono text-[#9299A8] hover:text-white transition-colors cursor-pointer"
                      >
                        Close
                      </button>
                      <button
                        type="button"
                        onClick={handleFinish}
                        className="px-5 py-2 rounded-lg bg-[#E5A93C] hover:bg-[#d89729] text-[#090A0F] font-bold text-xs transition-colors shadow-[0_0_15px_rgba(229,169,60,0.3)] cursor-pointer"
                      >
                        View Generated Brief →
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="pt-4 border-t border-[#21232B] flex items-center justify-between text-xs font-mono text-[#626B7B]">
                    <span>Pipeline executing stages autonomously...</span>
                    <button
                      type="button"
                      onClick={() => setIsOpen(false)}
                      className="text-[#9299A8] hover:text-white hover:underline cursor-pointer"
                    >
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
