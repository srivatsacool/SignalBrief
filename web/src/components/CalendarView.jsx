import React, { useState } from 'react';

export default function CalendarView({ reports = [] }) {
  const [currentYear, setCurrentYear] = useState(2026);
  const [currentMonth, setCurrentMonth] = useState(8); // 0-indexed: 8 is September
  const [selectedDate, setSelectedDate] = useState('2026-09-29');
  const [selectedBriefType, setSelectedBriefType] = useState('daily'); // 'daily' or 'domain'

  const months = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
  ];

  const handlePrevMonth = () => {
    if (currentMonth === 0) {
      setCurrentMonth(11);
      setCurrentYear(currentYear - 1);
    } else {
      setCurrentMonth(currentMonth - 1);
    }
  };

  const handleNextMonth = () => {
    if (currentMonth === 11) {
      setCurrentMonth(0);
      setCurrentYear(currentYear + 1);
    } else {
      setCurrentMonth(currentMonth + 1);
    }
  };

  const handleToday = () => {
    setCurrentYear(2026);
    setCurrentMonth(8);
    setSelectedDate('2026-09-29');
  };

  // Build calendar matrix for currentMonth, currentYear starting on SUNDAY (matching Panel 7/9)
  const daysInMonth = new Date(currentYear, currentMonth + 1, 0).getDate();
  const firstDayIndex = new Date(currentYear, currentMonth, 1).getDay(); // Sunday = 0

  // Reports data map by date
  const reportsByDate = {
    '2026-09-29': {
      daily: {
        title: "Daily Brief",
        time: "09:00 AM",
        insightsCount: 12,
        dotColor: "#E5A93C",
        headline: "Autonomous Manufacturing & Industrial AI Intelligence Brief",
        summary: "Automated analysis of industrial AI deployment, robotics expansion, and federal standards across verified public sources.",
        developments: [
          {
            title: "Production Tech: NIST Awards $30 Million for Regional MEP Automation",
            source: "NIST",
            url: "https://www.nist.gov"
          },
          {
            title: "Industrial AI: Vision Defect Transformers Deployed in Automotive Tier-1 Lines",
            source: "Manufacturing Dive",
            url: "https://www.manufacturingdive.com"
          }
        ]
      },
      domain: {
        title: "Manufacturing Focus",
        time: "02:00 PM",
        insightsCount: 8,
        dotColor: "#32B8F4",
        headline: "Factory Modernization and Sub-Millimeter Vision QA Benchmarks",
        summary: "Precision robotic workcell deployments and closed-loop computer vision quality metrics across European automotive fabricators.",
        developments: [
          {
            title: "Sub-Millimeter Inspection Precision Achieved Across Stamping Plants",
            source: "Bloomberg",
            url: "https://www.bloomberg.com"
          }
        ]
      }
    },
    '2026-09-28': {
      daily: {
        title: "Daily Brief",
        time: "09:00 AM",
        insightsCount: 10,
        dotColor: "#E5A93C",
        headline: "Maritime Port Automation & Intercontinental Freight Accords",
        summary: "Trans-Pacific shipping corridor logistics review and port gantry crane automation impacts on component lead times.",
        developments: [
          {
            title: "Port Logistics: Rotterdam and Singapore Deploy Autonomous Cranes",
            source: "Supply Chain Dive",
            url: "https://www.supplychaindive.com"
          }
        ]
      }
    },
    '2026-09-25': {
      daily: {
        title: "Daily Brief",
        time: "09:00 AM",
        insightsCount: 11,
        dotColor: "#E5A93C",
        headline: "Collaborative AMR Safety Trials & Factory Automation Synthesis",
        summary: "Evaluation of 500,000 autonomous vehicle operational hours in mixed human-machine industrial workcells.",
        developments: [
          {
            title: "Robotics: Industrial Cobots Achieve Zero Lost-Time Benchmark",
            source: "Robotics Business Review",
            url: "https://www.roboticsbusinessreview.com"
          }
        ]
      }
    },
    '2026-09-24': {
      daily: {
        title: "Daily Brief",
        time: "09:00 AM",
        insightsCount: 9,
        dotColor: "#E5A93C",
        headline: "Critical Mineral Processing Accords & Upstream EV Battery Chains",
        summary: "Multilateral trade treaties eliminating tariffs on battery-grade lithium and rare-earth magnetic alloys.",
        developments: [
          {
            title: "Trade Accords: Duty-Free Lanes Established for Refined Lithium",
            source: "Financial Times",
            url: "https://www.ft.com"
          }
        ]
      }
    }
  };

  const dayData = reportsByDate[selectedDate];
  const activeReport = dayData ? (selectedBriefType === 'daily' ? dayData.daily : dayData.domain || dayData.daily) : null;

  // Format date display: e.g. Sep 29, 2026
  const formatSelectedDate = () => {
    const [y, m, d] = selectedDate.split('-');
    const mName = months[parseInt(m, 10) - 1].slice(0, 3);
    return `${mName} ${parseInt(d, 10)}, ${y}`;
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
      
      {/* Left Column: Calendar Grid matching Panel 7/9 */}
      <div className="lg:col-span-7 bg-[#121318] border border-[#21232B] rounded-xl p-5 space-y-4">
        {/* Month Navigation */}
        <div className="flex items-center justify-between pb-3 border-b border-[#21232B]">
          <div className="flex items-center gap-2">
            <button
              onClick={handlePrevMonth}
              className="p-1.5 rounded-lg bg-[#0A0B0E] border border-[#21232B] text-[#9299A8] hover:text-white hover:border-[#E5A93C] transition-colors cursor-pointer"
              title="Previous Month"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            <h2 className="text-base font-bold text-white tracking-tight px-2">
              {months[currentMonth]} {currentYear}
            </h2>
            <button
              onClick={handleNextMonth}
              className="p-1.5 rounded-lg bg-[#0A0B0E] border border-[#21232B] text-[#9299A8] hover:text-white hover:border-[#E5A93C] transition-colors cursor-pointer"
              title="Next Month"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5l7 7-7 7" />
              </svg>
            </button>
          </div>

          <button
            onClick={handleToday}
            className="px-3 py-1.5 rounded-lg bg-[#0A0B0E] border border-[#21232B] text-xs font-mono text-[#9299A8] hover:text-white hover:border-[#E5A93C] transition-colors cursor-pointer"
          >
            Today
          </button>
        </div>

        {/* Days of Week (Sun - Sat) matching Panel 7/9 */}
        <div className="grid grid-cols-7 text-center font-mono text-[11px] text-[#626B7B] uppercase font-semibold pb-1">
          <span>Sun</span>
          <span>Mon</span>
          <span>Tue</span>
          <span>Wed</span>
          <span>Thu</span>
          <span>Fri</span>
          <span>Sat</span>
        </div>

        {/* Calendar Day Grid */}
        <div className="grid grid-cols-7 gap-y-2 gap-x-1 font-mono text-sm">
          {/* Empty offset days for start of month */}
          {Array.from({ length: firstDayIndex }).map((_, idx) => (
            <div key={`empty-${idx}`} className="h-10 flex items-center justify-center text-[#252832]">
              —
            </div>
          ))}

          {/* Days of month */}
          {Array.from({ length: daysInMonth }).map((_, idx) => {
            const dayNum = idx + 1;
            const dateStr = `${currentYear}-${String(currentMonth + 1).padStart(2, '0')}-${String(dayNum).padStart(2, '0')}`;
            const isSelected = selectedDate === dateStr;
            const hasData = Boolean(reportsByDate[dateStr]);

            return (
              <div key={dayNum} className="h-10 flex flex-col items-center justify-center">
                <button
                  onClick={() => setSelectedDate(dateStr)}
                  className={`w-9 h-9 rounded-full flex flex-col items-center justify-center text-xs transition-all cursor-pointer relative ${
                    isSelected
                      ? 'bg-[#E5A93C] text-[#090A0F] font-extrabold shadow-[0_0_10px_rgba(229,169,60,0.4)]'
                      : hasData
                      ? 'text-white hover:bg-[#1E2028] font-bold'
                      : 'text-[#626B7B] hover:text-[#9299A8] hover:bg-[#15161C]'
                  }`}
                >
                  <span>{dayNum}</span>
                  {/* Indicator dot on dates with published briefings */}
                  {hasData && !isSelected && (
                    <span className="w-1 h-1 rounded-full bg-[#18D69A] absolute bottom-1"></span>
                  )}
                  {hasData && isSelected && (
                    <span className="w-1 h-1 rounded-full bg-[#090A0F] absolute bottom-1"></span>
                  )}
                </button>
              </div>
            );
          })}
        </div>

        <div className="flex items-center justify-between text-[11px] font-mono text-[#626B7B] pt-3 border-t border-[#21232B]">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-[#18D69A]"></span>
            <span>Dates with briefings</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-[#E5A93C]"></span>
            <span>Selected date</span>
          </div>
        </div>
      </div>

      {/* Right Column: Reports on Date matching Panel 7/9 */}
      <div className="lg:col-span-5 bg-[#121318] border border-[#21232B] rounded-xl p-5 space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-[#21232B]">
          <h3 className="text-base font-semibold text-[#F4F5F7]">
            Reports on {formatSelectedDate()}
          </h3>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#E5A93C]/10 text-[#E5A93C] border border-[#E5A93C]/30">
            {dayData ? (dayData.domain ? '2 Reports' : '1 Report') : '0 Reports'}
          </span>
        </div>

        {dayData ? (
          <div className="space-y-3">
            {/* Daily Brief Item */}
            {dayData.daily && (
              <div
                onClick={() => setSelectedBriefType('daily')}
                className={`p-3.5 rounded-lg border cursor-pointer transition-all ${
                  selectedBriefType === 'daily'
                    ? 'bg-[#171920] border-[#E5A93C] shadow-[0_0_10px_rgba(229,169,60,0.1)]'
                    : 'bg-[#0A0B0E] border-[#21232B] hover:border-[#384050]'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2.5">
                    <span className="w-2.5 h-2.5 rounded-full bg-[#E5A93C]"></span>
                    <span className="text-sm font-semibold text-white">{dayData.daily.title}</span>
                  </div>
                  <div className="text-xs font-mono text-[#9299A8] flex items-center gap-1">
                    <span>{dayData.daily.time} • {dayData.daily.insightsCount} insights</span>
                    <span className="text-[#E5A93C]">→</span>
                  </div>
                </div>
              </div>
            )}

            {/* Domain Focus Item */}
            {dayData.domain && (
              <div
                onClick={() => setSelectedBriefType('domain')}
                className={`p-3.5 rounded-lg border cursor-pointer transition-all ${
                  selectedBriefType === 'domain'
                    ? 'bg-[#171920] border-[#32B8F4] shadow-[0_0_10px_rgba(50,184,244,0.1)]'
                    : 'bg-[#0A0B0E] border-[#21232B] hover:border-[#384050]'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2.5">
                    <span className="w-2.5 h-2.5 rounded-full bg-[#32B8F4]"></span>
                    <span className="text-sm font-semibold text-white">{dayData.domain.title}</span>
                  </div>
                  <div className="text-xs font-mono text-[#9299A8] flex items-center gap-1">
                    <span>{dayData.domain.time} • {dayData.domain.insightsCount} insights</span>
                    <span className="text-[#32B8F4]">→</span>
                  </div>
                </div>
              </div>
            )}

            {/* Selected Brief Preview */}
            {activeReport && (
              <div className="pt-3 border-t border-[#21232B] space-y-3">
                <div>
                  <h4 className="text-sm font-semibold text-white leading-snug">
                    {activeReport.headline}
                  </h4>
                  <p className="text-xs text-[#9299A8] mt-1.5 leading-relaxed">
                    {activeReport.summary}
                  </p>
                </div>

                <div className="space-y-1.5 pt-1">
                  <div className="text-[10px] font-mono uppercase text-[#626B7B] font-semibold">
                    Key Citations
                  </div>
                  {activeReport.developments.map((dev, idx) => (
                    <div key={idx} className="p-2 rounded bg-[#0A0B0E] border border-[#21232B] text-xs">
                      <div className="text-white text-[11px] leading-snug">{dev.title}</div>
                      <a
                        href={dev.url}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex items-center gap-1 text-[10px] font-mono text-[#18D69A] hover:underline mt-1"
                      >
                        [{dev.source} ↗]
                      </a>
                    </div>
                  ))}
                </div>

                <div className="pt-2">
                  <a
                    href="/"
                    className="w-full py-2 px-3 rounded-lg bg-[#E5A93C] hover:bg-[#d4952b] text-[#090A0F] font-semibold text-xs flex items-center justify-center gap-1.5 transition-colors"
                  >
                    <span>View Today's Report</span>
                    <span>→</span>
                  </a>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="text-center py-10 space-y-2">
            <div className="w-10 h-10 rounded-full bg-[#0A0B0E] border border-[#21232B] flex items-center justify-center text-[#626B7B] mx-auto">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <circle cx="12" cy="12" r="10" strokeWidth="2" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01" />
              </svg>
            </div>
            <div className="text-sm font-medium text-white">No Reports Published</div>
            <p className="text-xs text-[#626B7B] font-mono max-w-xs mx-auto">
              No autonomous intelligence briefings were scheduled for this date.
            </p>
          </div>
        )}
      </div>

    </div>
  );
}
