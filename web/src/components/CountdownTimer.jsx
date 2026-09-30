import React, { useState, useEffect } from 'react';

export default function CountdownTimer() {
  const [timeLeft, setTimeLeft] = useState({ hours: '14', minutes: '32', seconds: '18' });
  const [isCalculated, setIsCalculated] = useState(false);

  useEffect(() => {
    const updateCountdown = () => {
      const now = new Date();
      // Target schedule: 02:00 UTC daily
      const nextRun = new Date(Date.UTC(
        now.getUTCFullYear(),
        now.getUTCMonth(),
        now.getUTCDate(),
        2, 0, 0, 0
      ));

      if (now.getTime() >= nextRun.getTime()) {
        nextRun.setUTCDate(nextRun.getUTCDate() + 1);
      }

      const diff = Math.max(0, nextRun.getTime() - now.getTime());
      const hours = Math.floor(diff / (1000 * 60 * 60));
      const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
      const seconds = Math.floor((diff % (1000 * 60)) / 1000);

      setTimeLeft({
        hours: String(hours).padStart(2, '0'),
        minutes: String(minutes).padStart(2, '0'),
        seconds: String(seconds).padStart(2, '0')
      });
      setIsCalculated(true);
    };

    updateCountdown();
    const interval = setInterval(updateCountdown, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-[#121318] border border-[#21232B] rounded-xl p-5 space-y-4">
      <div className="flex items-center gap-2">
        <svg className="w-4 h-4 text-[#E5A93C]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <circle cx="12" cy="12" r="10" strokeWidth="2" />
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6v6l4 2" />
        </svg>
        <h3 className="text-sm font-semibold text-[#F4F5F7] tracking-tight">Next Run</h3>
      </div>

      <div className="grid grid-cols-3 gap-3 text-center">
        <div className="bg-[#0A0B0E] border border-[#21232B] rounded-lg p-3">
          <div className="text-2xl sm:text-3xl font-bold text-white tracking-tight font-mono">
            {isCalculated ? timeLeft.hours : '14'}
          </div>
          <div className="text-[11px] text-[#9299A8] mt-1 font-medium">Hours</div>
        </div>
        <div className="bg-[#0A0B0E] border border-[#21232B] rounded-lg p-3">
          <div className="text-2xl sm:text-3xl font-bold text-white tracking-tight font-mono">
            {isCalculated ? timeLeft.minutes : '32'}
          </div>
          <div className="text-[11px] text-[#9299A8] mt-1 font-medium">Minutes</div>
        </div>
        <div className="bg-[#0A0B0E] border border-[#21232B] rounded-lg p-3">
          <div className="text-2xl sm:text-3xl font-bold text-[#E5A93C] tracking-tight font-mono">
            {isCalculated ? timeLeft.seconds : '18'}
          </div>
          <div className="text-[11px] text-[#9299A8] mt-1 font-medium">Seconds</div>
        </div>
      </div>

      <p className="text-xs text-[#626B7B] font-mono text-center">
        Next briefing will be generated automatically
      </p>
    </div>
  );
}
