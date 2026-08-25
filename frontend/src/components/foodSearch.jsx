import { useState } from 'react';
import { searchFood, recordMeal, getFoodSubstitutions } from '../api/client';

export default function FoodSearch({ userId, onMealLogged }) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [searching, setSearching] = useState(false);
  
  const [selectedFood, setSelectedFood] = useState(null);
  const [portionGrams, setPortionGrams] = useState(100);
  const [substitutions, setSubstitutions] = useState([]);
  const [logging, setLogging] = useState(false);
  const [message, setMessage] = useState('');

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    
    setSearching(true);
    try {
      const res = await searchFood(query);
      setResults(Array.isArray(res.data) ? res.data : []);
    } catch (err) {
      console.error('Search error:', err);
      setResults([]);
    } finally {
      setSearching(false);
    }
  };

  const handleSelectFood = async (food) => {
    setSelectedFood(food);
    setPortionGrams(100);
    setSubstitutions([]);
    setMessage('');

    const foodId = food.fdc_id || food.id;
    if (foodId) {
      try {
        const subRes = await getFoodSubstitutions(foodId);
        setSubstitutions(Array.isArray(subRes.data) ? subRes.data : []);
      } catch (err) {
        console.error('Substitutions error:', err);
      }
    }
  };

  const handleLogMeal = async () => {
    if (!selectedFood) return;

    setLogging(true);
    setMessage('');

    // Field key updated to quantity_grams to match backend Pydantic model
    const mealData = {
      user_id: userId,
      food_id: selectedFood.fdc_id || selectedFood.id,
      quantity_grams: parseFloat(portionGrams) || 100.0,
    };

    try {
      await recordMeal(mealData);
      setMessage('Meal logged successfully!');
      if (onMealLogged) onMealLogged();
      setTimeout(() => setSelectedFood(null), 1200);
    } catch (err) {
      console.error('Error logging meal:', err);
      setMessage('Failed to log meal. Check input parameters.');
    } finally {
      setLogging(false);
    }
  };

  return (
    <div className="space-y-6">
      <form onSubmit={handleSearch} className="flex gap-3">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search for foods (e.g., chicken, rice, salmon)..."
          className="flex-1 bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
        />
        <button
          type="submit"
          disabled={searching}
          className="bg-blue-600 hover:bg-blue-500 text-white font-medium px-6 py-3 rounded-lg transition-colors disabled:opacity-50"
        >
          {searching ? 'Searching...' : 'Search'}
        </button>
      </form>

      {results.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {results.map((item, idx) => {
            const fdcId = item.fdc_id || item.id || idx;
            const name = item.description || item.food_name || item.name || 'Unknown Item';
            const calories = item.Calories ?? item.calories ?? 0;
            const protein = item.Protein ?? item.protein ?? 0;
            const carbs = item.Carbs ?? item.carbs ?? 0;
            const fats = item.Fats ?? item.fats ?? item.fat ?? 0;

            return (
              <div
                key={fdcId}
                className="bg-slate-800 border border-slate-700 p-5 rounded-xl flex flex-col justify-between hover:border-slate-500 transition-colors"
              >
                <div>
                  <h4 className="font-bold text-lg text-white mb-2">{name}</h4>
                  <div className="text-xs text-slate-400 space-y-1">
                    <p>Calories (per 100g): <span className="text-blue-400 font-semibold">{calories} kcal</span></p>
                    <p>
                      Protein: <span className="text-emerald-400 font-semibold">{protein}g</span> | 
                      Carbs: <span className="text-amber-400 font-semibold">{carbs}g</span> | 
                      Fats: <span className="text-purple-400 font-semibold">{fats}g</span>
                    </p>
                  </div>
                </div>

                <button
                  onClick={() => handleSelectFood(item)}
                  className="mt-4 bg-slate-700 hover:bg-slate-600 text-white text-sm font-medium py-2 rounded-lg transition-colors"
                >
                  Select & Log
                </button>
              </div>
            );
          })}
        </div>
      )}

      {selectedFood && (
        <div className="bg-slate-800 border border-blue-500/50 p-6 rounded-xl shadow-lg space-y-4">
          <div className="flex justify-between items-start">
            <div>
              <h3 className="text-xl font-bold text-white">
                Log {selectedFood.description || selectedFood.food_name || selectedFood.name}
              </h3>
              <p className="text-sm text-slate-400 mt-1">
                Base Calories: {selectedFood.Calories ?? selectedFood.calories ?? 0} kcal per 100g
              </p>
            </div>
            <button
              onClick={() => setSelectedFood(null)}
              className="text-slate-400 hover:text-white text-sm"
            >
              ✕ Close
            </button>
          </div>

          <div className="flex items-center gap-4">
            <label className="text-sm text-slate-300 font-medium">Quantity (grams):</label>
            <input
              type="number"
              min="1"
              step="5"
              value={portionGrams}
              onChange={(e) => setPortionGrams(e.target.value)}
              className="bg-slate-900 border border-slate-700 rounded px-3 py-1.5 text-white w-28 focus:outline-none focus:border-blue-500"
            />
            <button
              onClick={handleLogMeal}
              disabled={logging}
              className="bg-emerald-600 hover:bg-emerald-500 text-white font-semibold px-5 py-2 rounded-lg transition-colors disabled:opacity-50"
            >
              {logging ? 'Recording...' : 'Record Meal'}
            </button>
          </div>

          {message && (
            <p className={`text-sm ${message.includes('successfully') ? 'text-emerald-400' : 'text-red-400'}`}>
              {message}
            </p>
          )}

          {substitutions.length > 0 && (
            <div className="mt-4 pt-4 border-t border-slate-700">
              <h4 className="text-xs font-semibold text-amber-400 uppercase tracking-wider mb-2">
                Recommended Substitutions
              </h4>
              <div className="flex flex-wrap gap-2">
                {substitutions.map((sub, i) => (
                  <button
                    key={i}
                    onClick={() => handleSelectFood(sub)}
                    className="bg-slate-700/60 hover:bg-slate-700 border border-slate-600 text-xs text-slate-300 px-3 py-1.5 rounded-md transition-colors"
                  >
                    {sub.description || sub.food_name || sub.name} ({sub.Calories ?? sub.calories ?? 0} kcal)
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}