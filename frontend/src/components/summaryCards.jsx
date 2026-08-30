import React from 'react';

export default function SummaryCards({ summary }) {
  // Extract daily intakes & user-specific target goals calculated by profileEngine
  const macros = summary?.panels?.macros || {};
  const targets = summary?.targets?.macros || {};

  const calories = Math.round(macros.calories ?? 0);
  const protein = Math.round((macros.protein ?? 0) * 10) / 10;
  const carbs = Math.round((macros.carbs ?? 0) * 10) / 10;
  const fats = Math.round((macros.fats ?? 0) * 10) / 10;

  const targetCal = Math.round(targets.calories ?? 2000);
  const targetProtein = Math.round(targets.protein ?? 150);
  const targetCarbs = Math.round(targets.carbs ?? 250);
  const targetFats = Math.round(targets.fats ?? 70);

  const items = [
    {
      title: 'Calories',
      value: calories,
      target: targetCal,
      unit: 'kcal',
      color: '#60a5fa', // Blue
      borderColor: 'border-blue-500/40',
      badgeBg: 'bg-blue-500/10 text-blue-400',
    },
    {
      title: 'Protein',
      value: protein,
      target: targetProtein,
      unit: 'g',
      color: '#34d399', // Emerald
      borderColor: 'border-emerald-500/40',
      badgeBg: 'bg-emerald-500/10 text-emerald-400',
    },
    {
      title: 'Carbs',
      value: carbs,
      target: targetCarbs,
      unit: 'g',
      color: '#fbbf24', // Amber
      borderColor: 'border-amber-500/40',
      badgeBg: 'bg-amber-500/10 text-amber-400',
    },
    {
      title: 'Fats',
      value: fats,
      target: targetFats,
      unit: 'g',
      color: '#c084fc', // Purple
      borderColor: 'border-purple-500/40',
      badgeBg: 'bg-purple-500/10 text-purple-400',
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
      {items.map((item, idx) => {
        const percent = item.target > 0 ? Math.min(Math.round((item.value / item.target) * 100), 100) : 0;
        
        // SVG Ring setup
        const radius = 28;
        const circumference = 2 * Math.PI * radius;
        const strokeDashoffset = circumference - (percent / 100) * circumference;

        return (
          <div
            key={idx}
            className={`bg-slate-800/90 border ${item.borderColor} p-6 rounded-2xl shadow-xl flex flex-col justify-between relative overflow-hidden`}
          >
            {/* Header section with Circular Progress Ring */}
            <div className="flex justify-between items-start">
              <div>
                <span className="text-xs font-bold text-slate-400 uppercase tracking-widest">
                  {item.title}
                </span>
                <div className="mt-3 flex items-baseline space-x-1">
                  <span className="text-3xl font-extrabold text-white">
                    {item.value}
                  </span>
                  <span className="text-xs text-slate-400 font-medium">
                    / {item.target} {item.unit}
                  </span>
                </div>
              </div>

              {/* Radial Progress Gauge */}
              <div className="relative flex items-center justify-center">
                <svg className="w-16 h-16 transform -rotate-90">
                  <circle
                    cx="32"
                    cy="32"
                    r={radius}
                    stroke="currentColor"
                    strokeWidth="5"
                    fill="transparent"
                    className="text-slate-700/60"
                  />
                  <circle
                    cx="32"
                    cy="32"
                    r={radius}
                    stroke={item.color}
                    strokeWidth="5"
                    strokeDasharray={circumference}
                    strokeDashoffset={strokeDashoffset}
                    strokeLinecap="round"
                    fill="transparent"
                    className="transition-all duration-500 ease-out"
                  />
                </svg>
                <span className="absolute text-[11px] font-extrabold text-white">
                  {percent}%
                </span>
              </div>
            </div>

            {/* Bottom Progress Bar */}
            <div className="mt-5 space-y-1.5">
              <div className="w-full bg-slate-900/80 h-2.5 rounded-full overflow-hidden border border-slate-700/50">
                <div
                  className="h-full rounded-full transition-all duration-500 ease-out"
                  style={{ width: `${percent}%`, backgroundColor: item.color }}
                />
              </div>
              <div className="flex justify-between text-[11px] text-slate-400 pt-1 font-medium">
                <span>Progress</span>
                <span className={item.badgeBg + " px-2 py-0.5 rounded-md font-semibold text-[10px]"}>
                  {item.target - item.value > 0 
                    ? `${Math.round(item.target - item.value)} ${item.unit} remaining`
                    : 'Target Met! 🎉'}
                </span>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}