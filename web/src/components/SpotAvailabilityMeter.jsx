import React from 'react';

const SPOTS = [
  { id: 1, role: "Admin Account", status: "admin", label: "Owner / Host" },
  { id: 2, role: "Pilot Reader", status: "occupied", label: "Manufacturing Lead" },
  { id: 3, role: "Pilot Reader", status: "occupied", label: "Supply Chain Director" },
  { id: 4, role: "Pilot Reader", status: "occupied", label: "Industrial AI Architect" },
  { id: 5, role: "Pilot Reader", status: "occupied", label: "Automation VP" },
  { id: 6, role: "Pilot Reader", status: "occupied", label: "Energy Analyst" },
  { id: 7, role: "Pilot Reader", status: "available", label: "Waitlist Seat" }
];

export default function SpotAvailabilityMeter({ occupiedCount = 6, totalCapacity = 7 }) {
  const adminReserved = 1;
  const activeSubscribers = occupiedCount;
  const spotsLeft = Math.max(0, totalCapacity - activeSubscribers - adminReserved);

  return (
    <div className="bg-[#121318] border border-[#21232B] rounded-xl p-6 space-y-6">
      <div className="flex items-center justify-between pb-3 border-b border-[#21232B]">
        <h3 className="text-base font-semibold text-[#F4F5F7]">Subscription Status</h3>
        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#18D69A]/10 text-[#18D69A] border border-[#18D69A]/30">
          Pilot Active
        </span>
      </div>

      {/* 4 Status Rows matching Panel 6/9 */}
      <div className="space-y-3.5">
        {/* Active Subscribers */}
        <div className="flex items-center justify-between p-3 rounded-lg bg-[#0A0B0E] border border-[#21232B]">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-emerald-500/10 flex items-center justify-center text-[#18D69A]">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
            </div>
            <div>
              <div className="text-sm font-semibold text-white">Active Subscribers</div>
              <div className="text-[11px] text-[#9299A8]">Enrolled industrial recipients</div>
            </div>
          </div>
          <span className="text-sm font-bold font-mono text-[#18D69A]">{activeSubscribers} Active</span>
        </div>

        {/* Spots Left */}
        <div className="flex items-center justify-between p-3 rounded-lg bg-[#0A0B0E] border border-[#21232B]">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-rose-500/10 flex items-center justify-center text-rose-400">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
              </svg>
            </div>
            <div>
              <div className="text-sm font-semibold text-white">Spots Left</div>
              <div className="text-[11px] text-[#9299A8]">Remaining allocation quota</div>
            </div>
          </div>
          <span className={`text-sm font-bold font-mono ${spotsLeft === 0 ? 'text-rose-400' : 'text-[#32B8F4]'}`}>
            {spotsLeft} Spots Left
          </span>
        </div>

        {/* Reserved (Admin) */}
        <div className="flex items-center justify-between p-3 rounded-lg bg-[#0A0B0E] border border-[#21232B]">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-[#E5A93C]/10 flex items-center justify-center text-[#E5A93C]">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
            </div>
            <div>
              <div className="text-sm font-semibold text-white">Reserved (Admin)</div>
              <div className="text-[11px] text-[#9299A8]">Infrastructure anchor node</div>
            </div>
          </div>
          <span className="text-sm font-bold font-mono text-[#E5A93C]">1 Reserved</span>
        </div>

        {/* Total Capacity */}
        <div className="flex items-center justify-between p-3 rounded-lg bg-[#0A0B0E] border border-[#21232B]">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-slate-800 flex items-center justify-center text-[#9299A8]">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
              </svg>
            </div>
            <div>
              <div className="text-sm font-semibold text-white">Total Capacity</div>
              <div className="text-[11px] text-[#9299A8]">Strict pilot threshold</div>
            </div>
          </div>
          <span className="text-sm font-bold font-mono text-white">{totalCapacity} Total</span>
        </div>
      </div>

      {/* 7-Slot Scarcity Matrix */}
      <div className="pt-2 border-t border-[#21232B] space-y-2.5">
        <div className="text-[11px] font-mono text-[#9299A8] uppercase tracking-wider">
          7-Slot Capacity Matrix
        </div>
        <div className="grid grid-cols-7 gap-1.5">
          {SPOTS.map((s, idx) => {
            const isAdmin = idx === 0;
            const isOccupied = idx < (adminReserved + activeSubscribers);
            return (
              <div
                key={s.id}
                className={`py-2 px-1 rounded text-center border font-mono transition-all ${
                  isAdmin
                    ? 'bg-[#E5A93C]/10 border-[#E5A93C]/40 text-[#E5A93C]'
                    : isOccupied
                    ? 'bg-[#0A0B0E] border-[#21232B] text-[#9299A8]'
                    : 'bg-[#18D69A]/10 border-[#18D69A]/40 text-[#18D69A]'
                }`}
              >
                <div className="text-[10px] font-bold">0{s.id}</div>
                <div className="text-[8px] uppercase tracking-tighter truncate mt-0.5">
                  {isAdmin ? 'Admin' : isOccupied ? 'Active' : 'Open'}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
