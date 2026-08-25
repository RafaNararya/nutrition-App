import { useState } from 'react';
import { removeMealLog } from '../api/client';

export default function MealLogs({ logs, userId, onLogDeleted }) {
  const [deletingId, setDeletingId] = useState(null);

  const handleDelete = async (mealLogId) => {
    setDeletingId(mealLogId);
    try {
      await removeMealLog(userId, mealLogId);
      onLogDeleted(); // Triggers a parent state refresh
    } catch (err) {
      console.error('Error deleting meal log:', err);
    } finally {
      setDeletingId(null);
    }
  };

  if (!logs || logs.length === 0) {
    return (
      <div className="bg-slate-800 border border-slate-700 p-8 rounded-xl text-center text-slate-400">
        No meals logged for today yet. Head to the <span className="text-blue-400 font-semibold">Food Search</span> tab to record your first meal!
      </div>
    );
  }

  return (
    <div className="bg-slate-800 border border-slate-700 rounded-xl overflow-hidden shadow-md">
      <div className="p-4 border-b border-slate-700 flex justify-between items-center">
        <h3 className="font-semibold text-lg text-white">Logged Meals</h3>
        <span className="text-xs bg-slate-700 text-slate-300 px-2.5 py-1 rounded-full font-mono">
          {logs.length} {logs.length === 1 ? 'Entry' : 'Entries'}
        </span>
      </div>

      <div className="divide-y divide-slate-700/60">
        {logs.map((log) => (
          <div key={log.id || log.meal_log_id} className="p-4 flex items-center justify-between hover:bg-slate-750 transition-colors">
            <div>
              <p className="font-semibold text-white">{log.food_name || log.name || `Food Item #${log.food_id}`}</p>
              <p className="text-xs text-slate-400 mt-1">
                Portion: <span className="text-slate-300">{log.quantity || log.portion || 1} serving</span> | Calories: <span className="text-blue-400">{log.calories || 0} kcal</span>
              </p>
            </div>

            <button
              onClick={() => handleDelete(log.id || log.meal_log_id)}
              disabled={deletingId === (log.id || log.meal_log_id)}
              className="text-xs text-red-400 hover:text-red-300 hover:bg-red-500/10 border border-red-500/20 px-3 py-1.5 rounded-md transition-colors disabled:opacity-50"
            >
              {deletingId === (log.id || log.meal_log_id) ? 'Removing...' : 'Delete'}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}