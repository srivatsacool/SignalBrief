import React, { useState } from 'react';

export default function CalendarView({ reports = [] }) {
  const [selectedReport, setSelectedReport] = useState(reports[0] || null);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Calendar List */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-6">
        <h2 className="text-base font-bold text-white mb-4 flex items-center justify-between">
          <span>Historical Briefs</span>
          <span className="text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-400 font-normal">
            {reports.length} Reports
          </span>
        </h2>
        <div className="space-y-2 max-h-[500px] overflow-y-auto pr-1">
          {reports.length === 0 ? (
            <p className="text-xs text-slate-500 py-4 text-center">No past reports available.</p>
          ) : (
            reports.map((rep) => {
              const isSelected = selectedReport?.id === rep.id;
              return (
                <button
                  key={rep.id}
                  onClick={() => setSelectedReport(rep)}
                  className={`w-full text-left p-3 rounded-lg border transition-all ${
                    isSelected
                      ? 'bg-sky-950/70 border-sky-600 text-white'
                      : 'bg-slate-950/50 border-slate-800/80 hover:border-slate-700 text-slate-300'
                  }`}
                >
                  <div className="flex items-center justify-between text-xs mb-1">
                    <span className="font-semibold text-sky-400">{rep.report_date}</span>
                    <span className="text-slate-400">{rep.article_count || 0} articles</span>
                  </div>
                  <div className="text-sm font-medium line-clamp-1">
                    {rep.headline || 'Manufacturing Daily Brief'}
                  </div>
                </button>
              );
            })
          )}
        </div>
      </div>

      {/* Report Preview */}
      <div className="lg:col-span-2 bg-slate-900/90 border border-slate-800 rounded-xl p-6">
        {selectedReport ? (
          <div>
            <div className="flex items-center justify-between mb-4 pb-4 border-b border-slate-800">
              <div>
                <span className="text-xs font-semibold text-sky-400 uppercase tracking-wider">
                  {selectedReport.domain_id || 'Manufacturing'} · {selectedReport.report_date}
                </span>
                <h3 className="text-xl font-bold text-white mt-1">
                  {selectedReport.headline || 'Manufacturing Intelligence Brief'}
                </h3>
              </div>
              <a
                href={`/report/${selectedReport.id}`}
                className="px-4 py-2 bg-sky-500 hover:bg-sky-400 text-white font-semibold text-xs rounded-lg transition-colors"
              >
                Open Full Report →
              </a>
            </div>

            <div className="space-y-4">
              <div>
                <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Executive Summary</h4>
                <p className="text-sm text-slate-300 leading-relaxed bg-slate-950/50 p-4 rounded-lg border border-slate-800/80">
                  {selectedReport.executive_summary || 'Comprehensive review of manufacturing developments and supply chain signals.'}
                </p>
              </div>

              {selectedReport.developments && selectedReport.developments.length > 0 && (
                <div>
                  <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Key Highlights</h4>
                  <div className="space-y-2">
                    {selectedReport.developments.map((d, i) => (
                      <div key={i} className="p-3 bg-slate-950/40 rounded-lg border border-slate-800 text-sm">
                        <span className="font-semibold text-white block mb-1">{d.headline}</span>
                        <p className="text-xs text-slate-400">{d.what_changed}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center h-64 text-center">
            <p className="text-slate-400 text-sm">Select a date from the calendar to inspect the briefing.</p>
          </div>
        )}
      </div>
    </div>
  );
}
