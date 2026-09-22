import React, { useState, useEffect } from 'react';
import { Play, Pause, RotateCcw, Bell } from 'lucide-react';
import confetti from 'canvas-confetti';

interface CookingTimerProps {
  initialMinutes: number;
  stepTitle?: string;
}

export const CookingTimer: React.FC<CookingTimerProps> = ({
  initialMinutes,
  stepTitle,
}) => {
  const totalSeconds = initialMinutes * 60;
  const [timeLeft, setTimeLeft] = useState(totalSeconds);
  const [isRunning, setIsRunning] = useState(false);

  useEffect(() => {
    setTimeLeft(initialMinutes * 60);
    setIsRunning(false);
  }, [initialMinutes]);

  useEffect(() => {
    let interval: any = null;
    if (isRunning && timeLeft > 0) {
      interval = setInterval(() => {
        setTimeLeft((prev) => prev - 1);
      }, 1000);
    } else if (timeLeft === 0 && isRunning) {
      setIsRunning(false);
      // Trigger confetti celebration!
      confetti({
        particleCount: 80,
        spread: 70,
        origin: { y: 0.6 },
      });
      // Sound or toast
      try {
        const audio = new Audio('https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3');
        audio.play().catch(() => {});
      } catch {}
    }
    return () => clearInterval(interval);
  }, [isRunning, timeLeft]);

  const toggleRun = () => setIsRunning(!isRunning);
  const resetTimer = () => {
    setIsRunning(false);
    setTimeLeft(totalSeconds);
  };

  const minutes = Math.floor(timeLeft / 60);
  const seconds = timeLeft % 60;
  const progressPercent = totalSeconds > 0 ? ((totalSeconds - timeLeft) / totalSeconds) * 100 : 0;

  return (
    <div className="flex items-center gap-4 p-3 rounded-2xl bg-amber-50/80 border border-amber-200/70 shadow-xs">
      {/* Circle / Icon */}
      <div className="relative flex items-center justify-center w-12 h-12 rounded-xl bg-white text-brand-600 shadow-sm">
        <Bell className={`w-5 h-5 ${isRunning ? 'animate-bounce text-amber-500' : 'text-neutral-400'}`} />
      </div>

      {/* Timer display */}
      <div className="flex-1">
        <div className="text-[11px] font-semibold text-neutral-500 uppercase tracking-wider">
          {stepTitle || 'Đồng hồ hẹn giờ nấu'}
        </div>
        <div className="text-xl font-mono font-bold text-neutral-900">
          {String(minutes).padStart(2, '0')}:{String(seconds).padStart(2, '0')}
        </div>
      </div>

      {/* Controls */}
      <div className="flex items-center gap-1.5">
        <button
          onClick={toggleRun}
          className={`p-2.5 rounded-xl font-medium text-xs transition shadow-xs flex items-center gap-1 ${
            isRunning
              ? 'bg-amber-500 text-white hover:bg-amber-600'
              : 'bg-brand-600 text-white hover:bg-brand-700'
          }`}
        >
          {isRunning ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
          <span className="hidden sm:inline">{isRunning ? 'Tạm dừng' : 'Bắt đầu'}</span>
        </button>

        <button
          onClick={resetTimer}
          className="p-2.5 rounded-xl bg-white text-neutral-500 hover:text-neutral-800 hover:bg-neutral-100 border border-neutral-200 transition"
          title="Đặt lại"
        >
          <RotateCcw className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
