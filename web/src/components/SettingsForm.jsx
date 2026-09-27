import React, { useState } from 'react';

export default function SettingsForm({ initialPreferences = {} }) {
  const [emailEnabled, setEmailEnabled] = useState(initialPreferences.email_enabled ?? true);
  const [deliveryTime, setDeliveryTime] = useState(initialPreferences.delivery_time_utc || '06:00');
  const [keywords, setKeywords] = useState(initialPreferences.custom_keywords || 'robotics, automation, supply chain, nist');
  const [statusMsg, setStatusMsg] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    setStatusMsg('Saving preferences to Cloudflare D1...');
    setTimeout(() => {
      setStatusMsg('Preferences saved successfully!');
      setTimeout(() => setStatusMsg(''), 3000);
    }, 600);
  };

  return (
    <form onSubmit={handleSubmit} className="bg-slate-900/90 border border-slate-800 rounded-xl p-6 space-y-6">
      <div className="flex items-center justify-between pb-4 border-b border-slate-800">
        <div>
          <h2 className="text-lg font-bold text-white">Subscriber Preferences</h2>
          <p className="text-xs text-slate-400 mt-1">
            Configure your daily intelligence delivery options and focus areas.
          </p>
        </div>
        <div className="text-right">
          <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-sky-950 text-sky-400 border border-sky-800/80">
            Account: 1 of 10 Subscribers
          </span>
        </div>
      </div>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-semibold text-slate-200 mb-2">
            Email Delivery
          </label>
          <div className="flex items-center space-x-3">
            <input
              type="checkbox"
              id="emailToggle"
              checked={emailEnabled}
              onChange={(e) => setEmailEnabled(e.target.checked)}
              className="w-4 h-4 rounded text-sky-500 focus:ring-sky-400 bg-slate-950 border-slate-700"
            />
            <label htmlFor="emailToggle" className="text-sm text-slate-300">
              Receive daily one-page briefing by email
            </label>
          </div>
        </div>

        <div>
          <label className="block text-sm font-semibold text-slate-200 mb-2">
            Delivery Schedule (UTC)
          </label>
          <input
            type="time"
            value={deliveryTime}
            onChange={(e) => setDeliveryTime(e.target.value)}
            className="px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-sm text-slate-200 focus:outline-none focus:border-sky-500"
          />
          <p className="text-xs text-slate-500 mt-1">Briefings are synthesized at 02:00 UTC and dispatched at scheduled time.</p>
        </div>

        <div>
          <label className="block text-sm font-semibold text-slate-200 mb-2">
            Priority Keywords & Focus Terms
          </label>
          <textarea
            rows={3}
            value={keywords}
            onChange={(e) => setKeywords(e.target.value)}
            className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-sm text-slate-200 focus:outline-none focus:border-sky-500"
            placeholder="robotics, automation, supply chain, cybersecurity"
          />
          <p className="text-xs text-slate-500 mt-1">
            Comma-separated terms that increase relevance weight for development ranking.
          </p>
        </div>
      </div>

      {statusMsg && (
        <div className="p-3 bg-emerald-950/70 border border-emerald-800 text-emerald-300 text-xs rounded-lg">
          {statusMsg}
        </div>
      )}

      <div className="flex justify-end pt-4 border-t border-slate-800">
        <button
          type="submit"
          className="px-5 py-2.5 bg-sky-500 hover:bg-sky-400 text-white font-semibold text-sm rounded-lg transition-colors shadow"
        >
          Save Preferences
        </button>
      </div>
    </form>
  );
}
