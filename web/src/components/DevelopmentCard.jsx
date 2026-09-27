import React, { useState } from 'react';

export default function DevelopmentCard({ development }) {
  const [copied, setCopied] = useState(false);
  const { headline, topic_label, what_changed, why_it_matters, what_to_watch, sources, relevance_score } = development;

  const handleCopy = () => {
    const text = `${headline}\n\nWhat Changed:\n${what_changed}\n\nWhy It Matters:\n${why_it_matters}\n\nWhat To Watch:\n${what_to_watch}`;
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <article className="bg-slate-900/90 border border-slate-800 rounded-xl p-6 shadow-sm hover:border-slate-700 transition-all">
      <div className="flex items-start justify-between gap-4 mb-4">
        <div>
          {topic_label && (
            <span className="inline-block text-xs font-semibold uppercase tracking-wider text-sky-400 bg-sky-950/80 border border-sky-800/60 px-2.5 py-0.5 rounded-full mb-2">
              {topic_label}
            </span>
          )}
          <h3 className="text-lg font-bold text-white leading-snug">{headline}</h3>
        </div>
        <div className="flex items-center gap-2 flex-shrink-0">
          {relevance_score !== undefined && (
            <span className="text-xs font-medium px-2 py-1 rounded bg-slate-800 text-slate-300 border border-slate-700">
              Score: {(relevance_score * 100).toFixed(0)}%
            </span>
          )}
          <button
            onClick={handleCopy}
            className="text-xs px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors"
            title="Copy summary"
          >
            {copied ? 'Copied!' : 'Copy'}
          </button>
        </div>
      </div>

      <div className="space-y-3 text-sm leading-relaxed mb-5">
        <div className="bg-slate-950/60 rounded-lg p-3 border border-slate-800/80">
          <span className="font-bold text-sky-300 block text-xs uppercase tracking-wide mb-1">What Changed</span>
          <p className="text-slate-200">{what_changed}</p>
        </div>

        <div className="bg-slate-950/60 rounded-lg p-3 border border-slate-800/80">
          <span className="font-bold text-indigo-300 block text-xs uppercase tracking-wide mb-1">Why It Matters</span>
          <p className="text-slate-300">{why_it_matters}</p>
        </div>

        <div className="bg-slate-950/60 rounded-lg p-3 border border-slate-800/80">
          <span className="font-bold text-amber-300 block text-xs uppercase tracking-wide mb-1">What To Watch</span>
          <p className="text-slate-300">{what_to_watch}</p>
        </div>
      </div>

      {sources && sources.length > 0 && (
        <div className="pt-4 border-t border-slate-800/80 flex flex-wrap items-center gap-2 text-xs text-slate-400">
          <span className="font-semibold text-slate-500">Sources:</span>
          {sources.map((src, i) => (
            <a
              key={i}
              href={src.url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-slate-800/80 hover:bg-sky-950 hover:text-sky-300 text-slate-300 transition-colors border border-slate-700/60"
            >
              <span>[{src.source_name || 'Source'}]</span>
              <span className="truncate max-w-[200px]">{src.title}</span>
              <span className="text-[10px]">↗</span>
            </a>
          ))}
        </div>
      )}
    </article>
  );
}
