import { useEffect, useState, useCallback } from 'react';
import { getMealHistory, recordMeal } from '../api/client';

export default function MealHistory({ userId, onMealRelogged }) {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [reloggingId, setReloggingId] = useState(null);
  const [statusMsg, setStatusMsg] = useState('');

  const fetchHistory = useCallback(async () => {
    if (!userId) return;
    setLoading(true);
    try {
      const res = await getMealHistory(userId);
      setHistory(Array.isArray(res.data) ? res.data : []);
    } catch (err) {
      console.error('Error fetching meal history:', err);
    } finally {
      setLoading(false);
    }
  }, [userId]);

  useEffect(() => {
    fetchHistory();
  }, [fetchHistory]);

  const handleRelog = async (item) => {
    const logId = item.id || item.meal_log_id;
    setReloggingId(logId);
    setStatusMsg('');

    const mealData = {
      user_id: userId,
      food_id: item.food_id,
      quantity_grams: parseFloat(item.quantity_grams || 100.0)
    };

    try {
      await recordMeal(mealData);
      setStatusMsg(`Re-logged "${item.food_name || 'Item'}" to today's dashboard!`);
      fetchHistory(); // Refresh history list
      if (onMealRelogged) onMealRelogged();
    } catch (err) {
      console.error('Error re-logging meal:', err);
      setStatusMsg('Failed to re-log meal.');
    } finally {
      setReloggingId(null);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-white">Meal History & Quick Re-Log</h2>
          <p className="text-xs text-slate-400">View past unique entries and quickly re-add favorite items to today</p>
        </div>
        <button 
          onClick={fetchHistory}
          className="text-xs bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 px-3 py-1.5 rounded-lg transition-colors"
        >
          🔄 Refresh
        </button>
      </div>

      {statusMsg && (
        <div className={`p-3 rounded-lg border text-sm font-semibold ${statusMsg.includes('Re-logged') ? 'bg-emerald-950/40 border-emerald-800 text-emerald-400' : 'bg-red-950/40 border-red-800 text-red-400'}`}>
          {statusMsg}
        </div>
      )}

      {loading && history.length === 0 ? (
        <div className="text-slate-400 animate-pulse">Loading history...</div>
      ) : history.length === 0 ? (
        <div className="bg-slate-800 border border-slate-700 p-8 rounded-xl text-center text-slate-400">
          No meal history found. Log foods from Search to populate this list!
        </div>
      ) : (
        <div className="bg-slate-800 border border-slate-700 rounded-xl overflow-hidden shadow-md">
          <div className="divide-y divide-slate-700/60">
            {history.map((item) => {
              const itemKey = item.id || item.meal_log_id;
              const dateStr = item.created_at ? new Date(item.created_at).toLocaleDateString() : '';

              return (
                <div key={itemKey} className="p-4 flex items-center justify-between hover:bg-slate-750 transition-colors">
                  <div>
                    <p className="font-semibold text-white">{item.food_name || `Food Item #${item.food_id}`}</p>
                    <p className="text-xs text-slate-400 mt-1">
                      Last Portion: <span className="text-slate-300">{item.quantity_grams}g</span>
                      {dateStr && <span className="ml-3 text-slate-500">Last logged: {dateStr}</span>}
                    </p>
                  </div>

                  <button
                    onClick={() => handleRelog(item)}
                    disabled={reloggingId === itemKey}
                    className="text-xs bg-emerald-600 hover:bg-emerald-500 text-white font-semibold px-3.5 py-1.5 rounded-md transition-colors disabled:opacity-50 flex items-center gap-1"
                  >
                    {reloggingId === itemKey ? 'Adding...' : '➕ Re-log Today'}
                  </button>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}