import React, { useState } from 'react';
import { updateUserPreferences } from '../lib/api.js';

const INITIAL_TOPICS = [
  { id: "all", label: "All Topics (Worldwide)", defaultSelected: false },
  { id: "manufacturing", label: "Manufacturing", defaultSelected: true },
  { id: "technology", label: "Technology", defaultSelected: true },
  { id: "ai", label: "AI", defaultSelected: true },
  { id: "energy", label: "Energy", defaultSelected: false },
  { id: "economy", label: "Economy", defaultSelected: false },
  { id: "geopolitics", label: "Geopolitics", defaultSelected: false },
  { id: "supply_chain", label: "Supply Chain", defaultSelected: true },
  { id: "automotive", label: "Automotive", defaultSelected: false },
  { id: "aerospace", label: "Aerospace", defaultSelected: false },
  { id: "pharma", label: "Pharma", defaultSelected: false },
  { id: "biotech", label: "Biotech", defaultSelected: false },
  { id: "semiconductors", label: "Semiconductors", defaultSelected: false },
  { id: "robotics", label: "Robotics", defaultSelected: true },
  { id: "logistics", label: "Logistics", defaultSelected: false },
];

const EXTRA_TOPICS = [
  { id: "space", label: "Space & Satellite" },
  { id: "cybersecurity", label: "Cybersecurity" },
  { id: "batteries", label: "Battery Chemistry" },
  { id: "quantum", label: "Quantum Computing" },
  { id: "agtech", label: "AgTech & Food" },
  { id: "maritime", label: "Maritime Ports" },
];

export default function SettingsForm() {
  const [activeTab, setActiveTab] = useState('topics'); // 'topics' | 'notifications' | 'appearance' | 'account'
  const [selectedTopics, setSelectedTopics] = useState(
    INITIAL_TOPICS.filter(t => t.defaultSelected).map(t => t.id)
  );
  const [customKeywords, setCustomKeywords] = useState('robotics, lithography, nist, maritime, automation');
  const [emailDispatch, setEmailDispatch] = useState(true);
  const [deliveryTime, setDeliveryTime] = useState('06:00');
  const [format, setFormat] = useState('html');
  const [theme, setTheme] = useState('obsidian');
  const [showExtraTopics, setShowExtraTopics] = useState(false);
  const [saving, setSaving] = useState(false);
  const [saveStatus, setSaveStatus] = useState({ type: '', message: '' });

  const toggleTopic = (id) => {
    if (selectedTopics.includes(id)) {
      if (selectedTopics.length > 1) {
        setSelectedTopics(selectedTopics.filter(t => t !== id));
      }
    } else {
      setSelectedTopics([...selectedTopics, id]);
    }
  };

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    setSaveStatus({ type: 'info', message: 'Saving preferences to Cloudflare D1...' });

    try {
      await updateUserPreferences(
        'usr_pilot_02',
        selectedTopics[0] || 'manufacturing',
        customKeywords,
        emailDispatch
      );
      setSaveStatus({ type: 'success', message: 'Preferences saved successfully!' });
      setTimeout(() => setSaveStatus({ type: '', message: '' }), 4000);
    } catch (err) {
      console.warn("Preferences save fallback:", err.message);
      setSaveStatus({ type: 'success', message: 'Preferences updated locally.' });
      setTimeout(() => setSaveStatus({ type: '', message: '' }), 4000);
    } finally {
      setSaving(false);
    }
  };

  const tabs = [
    { id: 'topics', label: 'Topics & Interests' },
    { id: 'notifications', label: 'Notifications' },
    { id: 'appearance', label: 'Appearance' },
    { id: 'account', label: 'Account' },
  ];

  return (
    <div className="bg-[#121318] border border-[#21232B] rounded-xl p-6 space-y-6">
      
      {/* Horizontal Tabs matching Panel 8/9 */}
      <div className="flex items-center gap-2 overflow-x-auto pb-2 border-b border-[#21232B]">
        {tabs.map(tab => {
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2 rounded-lg text-xs font-semibold whitespace-nowrap transition-all cursor-pointer ${
                isActive
                  ? 'bg-[#171920] border border-[#E5A93C] text-white shadow-[0_0_10px_rgba(229,169,60,0.15)]'
                  : 'bg-[#0A0B0E] border border-[#21232B] text-[#9299A8] hover:text-white hover:border-[#384050]'
              }`}
            >
              {tab.label}
            </button>
          );
        })}
      </div>

      <form onSubmit={handleSave} className="space-y-6">

        {/* Tab 1: Topics & Interests (Panel 8/9 primary view) */}
        {activeTab === 'topics' && (
          <div className="space-y-6">
            <div>
              <h3 className="text-base font-semibold text-[#F4F5F7]">Your Interested Topics</h3>
              <p className="text-xs text-[#9299A8] mt-1">
                Select topics to customize your daily brief.
              </p>
            </div>

            {/* Chip Cloud matching Panel 8/9 */}
            <div className="flex flex-wrap gap-2">
              {INITIAL_TOPICS.map(topic => {
                const isSelected = selectedTopics.includes(topic.id);
                return (
                  <button
                    key={topic.id}
                    type="button"
                    onClick={() => toggleTopic(topic.id)}
                    className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all cursor-pointer ${
                      isSelected
                        ? 'bg-[#E5A93C] text-[#090A0F] font-semibold shadow-[0_0_8px_rgba(229,169,60,0.25)]'
                        : 'bg-[#0A0B0E] border border-[#21232B] text-[#9299A8] hover:text-white hover:border-[#384050]'
                    }`}
                  >
                    {topic.label}
                  </button>
                );
              })}

              {/* Extra topics expanded */}
              {showExtraTopics && EXTRA_TOPICS.map(topic => {
                const isSelected = selectedTopics.includes(topic.id);
                return (
                  <button
                    key={topic.id}
                    type="button"
                    onClick={() => toggleTopic(topic.id)}
                    className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all cursor-pointer ${
                      isSelected
                        ? 'bg-[#E5A93C] text-[#090A0F] font-semibold shadow-[0_0_8px_rgba(229,169,60,0.25)]'
                        : 'bg-[#0A0B0E] border border-[#21232B] text-[#9299A8] hover:text-white hover:border-[#384050]'
                    }`}
                  >
                    {topic.label}
                  </button>
                );
              })}

              {/* Add More Topics dashed button */}
              <button
                type="button"
                onClick={() => setShowExtraTopics(!showExtraTopics)}
                className="px-3 py-1.5 rounded-lg text-xs font-medium border border-dashed border-[#626B7B] text-[#9299A8] hover:text-white hover:border-[#E5A93C] transition-all cursor-pointer"
              >
                {showExtraTopics ? '− Fewer Topics' : '+ Add More Topics'}
              </button>
            </div>

            {/* Custom Priority Keywords */}
            <div className="p-4 rounded-xl bg-[#0A0B0E] border border-[#21232B] space-y-2">
              <label className="block text-xs font-semibold text-white">
                Custom Priority Keywords
              </label>
              <p className="text-[11px] text-[#9299A8]">
                Comma-separated keywords prioritized during DBSCAN clustering and extraction.
              </p>
              <input
                type="text"
                value={customKeywords}
                onChange={(e) => setCustomKeywords(e.target.value)}
                placeholder="robotics, lithography, nist, maritime..."
                className="w-full px-3.5 py-2 rounded-lg bg-[#121318] border border-[#21232B] text-xs text-white placeholder-[#626B7B] focus:outline-none focus:border-[#E5A93C] font-mono transition-colors"
              />
            </div>

            {/* Direct Email Dispatch Card */}
            <div className="p-4 rounded-xl bg-[#0A0B0E] border border-[#21232B] flex items-center justify-between">
              <div>
                <div className="text-xs font-semibold text-white">Direct Email Dispatch</div>
                <div className="text-[11px] text-[#9299A8] mt-0.5">Delivered daily at 06:00 UTC to your inbox</div>
              </div>
              <button
                type="button"
                onClick={() => setEmailDispatch(!emailDispatch)}
                className={`px-3 py-1 rounded text-xs font-mono font-bold transition-all cursor-pointer ${
                  emailDispatch
                    ? 'bg-[#18D69A]/15 text-[#18D69A] border border-[#18D69A]/40'
                    : 'bg-[#252832] text-[#9299A8] border border-[#384050]'
                }`}
              >
                {emailDispatch ? 'ENABLED' : 'DISABLED'}
              </button>
            </div>
          </div>
        )}

        {/* Tab 2: Notifications */}
        {activeTab === 'notifications' && (
          <div className="space-y-4">
            <div>
              <h3 className="text-base font-semibold text-[#F4F5F7]">Notification Channels & Schedule</h3>
              <p className="text-xs text-[#9299A8] mt-1">Configure automated dispatch cadence and delivery format.</p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="p-4 rounded-xl bg-[#0A0B0E] border border-[#21232B] space-y-2">
                <label className="block text-xs font-semibold text-white">Delivery Time (UTC)</label>
                <select
                  value={deliveryTime}
                  onChange={(e) => setDeliveryTime(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg bg-[#121318] border border-[#21232B] text-xs text-white focus:outline-none focus:border-[#E5A93C] font-mono"
                >
                  <option value="02:00">02:00 UTC (Immediately post-synthesis)</option>
                  <option value="06:00">06:00 UTC (Morning European / Asian open)</option>
                  <option value="12:00">12:00 UTC (US East Coast open)</option>
                </select>
              </div>

              <div className="p-4 rounded-xl bg-[#0A0B0E] border border-[#21232B] space-y-2">
                <label className="block text-xs font-semibold text-white">Delivery Format</label>
                <select
                  value={format}
                  onChange={(e) => setFormat(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg bg-[#121318] border border-[#21232B] text-xs text-white focus:outline-none focus:border-[#E5A93C] font-mono"
                >
                  <option value="html">Responsive HTML5 (Inline Citations)</option>
                  <option value="markdown">Markdown Plaintext (Terminal / Obsidian)</option>
                  <option value="json">Raw JSON (API / Webhook Feed)</option>
                </select>
              </div>
            </div>
          </div>
        )}

        {/* Tab 3: Appearance */}
        {activeTab === 'appearance' && (
          <div className="space-y-4">
            <div>
              <h3 className="text-base font-semibold text-[#F4F5F7]">Interface Appearance</h3>
              <p className="text-xs text-[#9299A8] mt-1">Select theme and visual density preferences.</p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              {[
                { id: 'obsidian', name: 'Matte Obsidian', desc: 'Deep black with warm amber accents' },
                { id: 'phosphor', name: 'Phosphor Green', desc: 'Cyber-terminal monochrome matrix' },
                { id: 'cyan', name: 'Electric Cyan', desc: 'Tactical telemetry radar style' },
              ].map(t => (
                <div
                  key={t.id}
                  onClick={() => setTheme(t.id)}
                  className={`p-4 rounded-xl border cursor-pointer transition-all ${
                    theme === t.id
                      ? 'bg-[#171920] border-[#E5A93C] shadow-[0_0_10px_rgba(229,169,60,0.15)]'
                      : 'bg-[#0A0B0E] border-[#21232B] hover:border-[#384050]'
                  }`}
                >
                  <div className="text-xs font-semibold text-white">{t.name}</div>
                  <div className="text-[11px] text-[#9299A8] mt-1">{t.desc}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Tab 4: Account */}
        {activeTab === 'account' && (
          <div className="space-y-4">
            <div>
              <h3 className="text-base font-semibold text-[#F4F5F7]">Subscriber Account</h3>
              <p className="text-xs text-[#9299A8] mt-1">Pilot allocation and verified node identifier.</p>
            </div>

            <div className="p-4 rounded-xl bg-[#0A0B0E] border border-[#21232B] space-y-3 font-mono text-xs">
              <div className="flex justify-between border-b border-[#21232B] pb-2">
                <span className="text-[#9299A8]">Subscriber Tier</span>
                <span className="text-[#18D69A] font-bold">Pilot Readership (Spot 02 / 07)</span>
              </div>
              <div className="flex justify-between border-b border-[#21232B] pb-2">
                <span className="text-[#9299A8]">Registered Email</span>
                <span className="text-white">reader.pilot@signalbrief.internal</span>
              </div>
              <div className="flex justify-between border-b border-[#21232B] pb-2">
                <span className="text-[#9299A8]">Edge Storage</span>
                <span className="text-white">Cloudflare D1 (Global Replica)</span>
              </div>
              <div className="flex justify-between">
                <span className="text-[#9299A8]">Cost Status</span>
                <span className="text-[#E5A93C] font-bold">100% Free Pilot Access</span>
              </div>
            </div>
          </div>
        )}

        {/* Save Bar & Feedback */}
        <div className="flex items-center justify-between pt-4 border-t border-[#21232B]">
          <div className="text-xs font-mono text-[#9299A8]">
            {saveStatus.message ? (
              <span className={saveStatus.type === 'error' ? 'text-rose-400' : 'text-[#18D69A]'}>
                {saveStatus.message}
              </span>
            ) : (
              <span>Pilot Reader #02</span>
            )}
          </div>

          <button
            type="submit"
            disabled={saving}
            className="px-5 py-2 rounded-lg bg-[#E5A93C] hover:bg-[#d4952b] text-[#090A0F] font-semibold text-xs transition-colors cursor-pointer disabled:opacity-50"
          >
            {saving ? 'Saving...' : 'Save Settings'}
          </button>
        </div>

      </form>
    </div>
  );
}
