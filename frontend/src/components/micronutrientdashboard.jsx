import React, { useState } from 'react';

const NUTRIENT_UNITS = {
  // Minerals
  calcium: 'mg', iron: 'mg', magnesium: 'mg', phosphorus: 'mg',
  potassium: 'mg', sodium: 'mg', zinc: 'mg', selenium: 'mcg',
  // B-Vitamins
  thiamin: 'mg', riboflavin: 'mg', niacin: 'mg', pantothenic_acid: 'mg',
  vitamin_b6: 'mg', folate: 'mcg', vitamin_b12: 'mcg',
  // Antioxidants
  vitamin_a: 'mcg', vitamin_c: 'mg', vitamin_e: 'mg'
};

const PANEL_TITLES = {
  minerals: '🧪 Minerals',
  b_vitamins: '💧 B-Complex',
  antioxidants: '🛡️ Antioxidants & Vitamins'
};

export default function MicronutrientDashboard({ summary }) {
  const [activeTab, setActiveTab] = useState('minerals');

  const panels = summary?.panels || {};
  const targets = summary?.targets || {};

  return (
    <div className="bg-slate-800 border border-slate-700 p-6 rounded-xl shadow-md mb-8">
      <div className="flex items-center justify-between border-b border-slate-700 pb-4 mb-4">
        <h3 className="text-lg font-bold text-white">Micronutrient Breakdown</h3>
        
        {/* Navigation Tabs */}
        <div className="flex space-x-2">
          {Object.keys(PANEL_TITLES).map((panelKey) => (
            <button
              key={panelKey}
              onClick={() => setActiveTab(panelKey)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                activeTab === panelKey
                  ? 'bg-blue-600 text-white'
                  : 'bg-slate-900/60 text-slate-400 hover:text-slate-200'
              }`}
            >
              {PANEL_TITLES[panelKey]}
            </button>
          ))}
        </div>
      </div>

      {/* Grid of Nutrients */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {panels[activeTab] &&
          Object.entries(panels[activeTab]).map(([nutrientKey, rawValue]) => {
            const value = Math.round(rawValue * 10) / 10;
            const target = targets[activeTab]?.[nutrientKey] || 0;
            const unit = NUTRIENT_UNITS[nutrientKey] || '';
            const percent = target > 0 ? Math.min(Math.round((value / target) * 100), 100) : 0;

            return (
              <div key={nutrientKey} className="bg-slate-900/50 p-4 rounded-lg border border-slate-700/50">
                <div className="flex justify-between items-center mb-1">
                  <span className="capitalize text-xs font-medium text-slate-300">
                    {nutrientKey.replace('_', ' ')}
                  </span>
                  <span className="text-xs text-slate-400">
                    <strong className="text-blue-400">{value}</strong> / {target} {unit}
                  </span>
                </div>

                <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden mt-2 border border-slate-700">
                  <div
                    className="bg-blue-500 h-full transition-all duration-300 rounded-full"
                    style={{ width: `${percent}%` }}
                  />
                </div>
                <div className="text-right text-[10px] text-slate-400 mt-1">{percent}% RDA</div>
              </div>
            );
          })}
      </div>
    </div>
  );
}