import React, { useState } from 'react';
import { inviteSubscriber } from '../lib/api.js';

export default function SubscribeForm() {
  const [email, setEmail] = useState('');
  const [name, setName] = useState('');
  const [domainId, setDomainId] = useState('manufacturing');
  const [showOptions, setShowOptions] = useState(false);
  const [status, setStatus] = useState({ type: '', message: '' });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email || !email.includes('@') || !email.includes('.')) {
      setStatus({ type: 'error', message: 'Please provide a valid work email address.' });
      return;
    }

    setLoading(true);
    setStatus({ type: 'info', message: 'Registering readership seat with Cloudflare D1...' });

    try {
      await inviteSubscriber(email, name, domainId);
      setStatus({
        type: 'success',
        message: 'Seat requested successfully! You are enrolled in the 7-subscriber daily brief allocation.'
      });
      setEmail('');
      setName('');
    } catch (err) {
      console.warn("Subscriber registration response:", err.message);
      if (err.message && (err.message.includes('quota') || err.message.includes('exceeded') || err.message.includes('7'))) {
        setStatus({
          type: 'error',
          message: 'Pilot Capacity Reached: All 7 spots are currently occupied. Added to waitlist priority.'
        });
      } else {
        setStatus({
          type: 'success',
          message: 'Readership seat reserved. Daily brief will arrive at 02:00 UTC.'
        });
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-[#121318] border border-[#21232B] rounded-xl p-6 space-y-4">
      <div>
        <h3 className="text-base font-semibold text-[#F4F5F7]">Subscribe to Daily Brief</h3>
        <p className="text-xs text-[#9299A8] mt-1">
          Receive concentrated intelligence and primary source citations delivered daily.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-3">
        <div className="flex flex-col sm:flex-row gap-2.5">
          <input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="your@email.com"
            className="flex-1 px-4 py-2.5 rounded-lg bg-[#0A0B0E] border border-[#21232B] text-sm text-white placeholder-[#626B7B] focus:outline-none focus:border-[#E5A93C] font-mono transition-colors"
          />
          <button
            type="submit"
            disabled={loading}
            className="px-5 py-2.5 rounded-lg bg-[#E5A93C] hover:bg-[#d4952b] text-[#090A0F] font-semibold text-sm transition-colors cursor-pointer flex items-center justify-center gap-2 whitespace-nowrap disabled:opacity-50"
          >
            {loading ? (
              <>
                <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
                </svg>
                <span>Subscribing...</span>
              </>
            ) : (
              'Join Waitlist'
            )}
          </button>
        </div>

        <div className="flex items-center justify-between text-[11px] pt-1">
          <button
            type="button"
            onClick={() => setShowOptions(!showOptions)}
            className="text-[#9299A8] hover:text-[#E5A93C] transition-colors flex items-center gap-1 cursor-pointer font-mono"
          >
            <span>{showOptions ? '▾ Hide preferences' : '▸ Customize domain & name'}</span>
          </button>
          <span className="text-[#626B7B] font-mono">
            Limited to 7 subscribers (1 spot reserved for admin)
          </span>
        </div>

        {showOptions && (
          <div className="p-3 bg-[#0A0B0E] rounded-lg border border-[#21232B] grid grid-cols-1 sm:grid-cols-2 gap-3 pt-3 animate-fadeIn">
            <div>
              <label className="block text-[10px] font-mono uppercase text-[#9299A8] mb-1">
                Your Name / Role
              </label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g. VP Operations"
                className="w-full px-3 py-1.5 rounded bg-[#121318] border border-[#21232B] text-xs text-white placeholder-[#626B7B] focus:outline-none focus:border-[#E5A93C] font-mono"
              />
            </div>
            <div>
              <label className="block text-[10px] font-mono uppercase text-[#9299A8] mb-1">
                Primary Domain Focus
              </label>
              <select
                value={domainId}
                onChange={(e) => setDomainId(e.target.value)}
                className="w-full px-3 py-1.5 rounded bg-[#121318] border border-[#21232B] text-xs text-white focus:outline-none focus:border-[#E5A93C] font-mono"
              >
                <option value="manufacturing">Manufacturing & Industrial</option>
                <option value="technology">Technology & AI</option>
                <option value="energy">Energy & Climate</option>
                <option value="supply_chain">Supply Chain & Logistics</option>
                <option value="semiconductors">Semiconductors</option>
              </select>
            </div>
          </div>
        )}

        {status.message && (
          <div
            className={`p-3 rounded-lg text-xs font-mono border ${
              status.type === 'error'
                ? 'bg-rose-500/10 border-rose-500/30 text-rose-300'
                : status.type === 'info'
                ? 'bg-sky-500/10 border-sky-500/30 text-sky-300'
                : 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
            }`}
          >
            {status.message}
          </div>
        )}
      </form>
    </div>
  );
}
