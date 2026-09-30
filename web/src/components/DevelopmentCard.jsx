import React, { useState } from 'react';

export default function DevelopmentCard({ development }) {
  const [copied, setCopied] = useState(false);
  const [expanded, setExpanded] = useState(false);

  const {
    headline,
    topic_label,
    what_changed,
    why_it_matters,
    business_implications,
    what_to_watch,
    sources = [],
    time_ago = "4 hours ago",
    thumbnail_url,
  } = development;

  const handleCopy = () => {
    let text = `${headline}\n\nWhat Happened:\n${what_changed}\n\nWhy It Matters:\n${why_it_matters}`;
    if (business_implications) {
      text += `\n\nBusiness Implications:\n${business_implications}`;
    }
    if (what_to_watch) {
      text += `\n\nWhat to Watch:\n${what_to_watch}`;
    }
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const primarySource = sources && sources.length > 0 ? sources[0] : null;

  // Derive source icon badge
  const getSourceMeta = (sourceName = '') => {
    const s = sourceName.toLowerCase();
    if (s.includes('bloomberg')) {
      return { label: 'Bloomberg', color: '#3B82F6', icon: 'B' };
    }
    if (s.includes('techcrunch')) {
      return { label: 'TechCrunch', color: '#10B981', icon: 'TC' };
    }
    if (s.includes('financial times') || s.includes('ft')) {
      return { label: 'Financial Times', color: '#F43F5E', icon: 'FT' };
    }
    if (s.includes('reuters')) {
      return { label: 'Reuters', color: '#F97316', icon: 'R' };
    }
    if (s.includes('nist')) {
      return { label: 'NIST', color: '#32B8F4', icon: 'N' };
    }
    return { label: sourceName || 'Verified Source', color: '#18D69A', icon: '↗' };
  };

  const sourceMeta = getSourceMeta(primarySource?.source_name);

  // SVG default abstract thumbnail if no image provided
  const defaultThumb = (
    <div className="w-full h-full bg-[#161820] flex items-center justify-center border-r border-[#21232B]">
      <svg className="w-8 h-8 text-[#384050]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
      </svg>
    </div>
  );

  return (
    <article className="bg-[#121318] border border-[#21232B] rounded-xl overflow-hidden hover:border-[#333846] transition-all group flex flex-col sm:flex-row">
      {/* Left Thumbnail */}
      <div className="w-full sm:w-44 md:w-52 h-36 sm:h-auto shrink-0 relative overflow-hidden bg-[#161820]">
        {thumbnail_url ? (
          <img
            src={thumbnail_url}
            alt={headline}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
          />
        ) : (
          defaultThumb
        )}
      </div>

      {/* Right Content Column */}
      <div className="p-4 sm:p-5 flex-1 flex flex-col justify-between space-y-3">
        <div className="space-y-2">
          <div className="flex items-center justify-between text-[11px] text-[#626B7B] font-mono">
            <div className="flex items-center gap-2">
              {topic_label && (
                <span className="text-[#9299A8] font-medium uppercase text-[10px]">
                  {topic_label}
                </span>
              )}
              <span>•</span>
              <span>{time_ago}</span>
            </div>
            <button
              onClick={handleCopy}
              className="text-[#626B7B] hover:text-[#F4F5F7] transition-colors"
              title="Copy development"
            >
              {copied ? '✓ Copied' : 'Copy'}
            </button>
          </div>

          <h3 className="text-sm sm:text-base font-bold text-[#F4F5F7] group-hover:text-white leading-snug">
            {headline}
          </h3>

          <p className="text-xs text-[#cbd5e1] leading-relaxed">
            {what_changed}
          </p>

          {/* Expandable Intelligence Briefing */}
          {expanded ? (
            <div className="pt-2.5 mt-2 border-t border-[#21232B] space-y-2.5 text-xs animate-fadeIn">
              {why_it_matters && (
                <div>
                  <span className="font-mono text-[10px] font-bold text-[#18D69A] tracking-wider uppercase block">
                    Strategic Significance
                  </span>
                  <p className="text-[#cbd5e1] mt-0.5 leading-relaxed">{why_it_matters}</p>
                </div>
              )}
              {business_implications && (
                <div>
                  <span className="font-mono text-[10px] font-bold text-[#32B8F4] tracking-wider uppercase block">
                    Business Implications
                  </span>
                  <p className="text-[#cbd5e1] mt-0.5 leading-relaxed">{business_implications}</p>
                </div>
              )}
              {what_to_watch && (
                <div>
                  <span className="font-mono text-[10px] font-bold text-[#E5A93C] tracking-wider uppercase block">
                    Forward Catalysts & What to Watch
                  </span>
                  <p className="text-[#cbd5e1] mt-0.5 leading-relaxed">{what_to_watch}</p>
                </div>
              )}
              <button
                onClick={() => setExpanded(false)}
                className="text-[11px] font-mono text-[#626B7B] hover:text-[#9299A8] transition-colors pt-1 block"
              >
                ▴ Collapse Briefing
              </button>
            </div>
          ) : (
            <button
              onClick={() => setExpanded(true)}
              className="text-[11px] font-mono text-[#32B8F4] hover:text-[#52c8ff] transition-colors inline-flex items-center gap-1 pt-1"
            >
              <span>View Full Intelligence Analysis</span>
              <span>▾</span>
            </button>
          )}
        </div>

        {/* Source Attribution Bar */}
        {primarySource && (
          <div className="pt-2 flex items-center justify-between border-t border-[#21232B]/60">
            <a
              href={primarySource.url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center space-x-1.5 text-xs text-[#9299A8] hover:text-white group/source transition-colors"
            >
              <span
                className="w-3.5 h-3.5 rounded-full flex items-center justify-center text-[9px] font-bold text-white shrink-0"
                style={{ backgroundColor: sourceMeta.color }}
              >
                {sourceMeta.icon}
              </span>
              <span className="font-medium text-[#F4F5F7]">{sourceMeta.label}</span>
              <span className="text-[#626B7B] group-hover/source:text-white transition-colors">↗</span>
            </a>

            {primarySource.title && (
              <span className="text-[10px] text-[#626B7B] font-mono truncate max-w-[220px] hidden md:inline">
                {primarySource.title}
              </span>
            )}
          </div>
        )}
      </div>
    </article>
  );
}
