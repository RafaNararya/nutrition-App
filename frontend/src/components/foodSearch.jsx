import { useState } from 'react';
import { searchFood, recordMeal, getFoodSubstitutions } from '../api/client';

export default function FoodSearch({ userId, onMealLogged }) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [searching, setSearching] = useState(false);
  
  const [selectedFood, setSelectedFood] = useState(null); // For logging modal
  const [infoFood, setInfoFood] = useState(null); // For micronutrient breakdown view modal
  const [activeMicroTab, setActiveMicroTab] = useState('minerals');

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
        const subsList = subRes.data?.recommendations || subRes.data?.reccommendations || [];
        setSubstitutions(Array.isArray(subsList) ? subsList : []);
      } catch (err) {
        console.error('Substitutions error:', err);
        setSubstitutions([]);
      }
    }
  };

  const handleLogMeal = async () => {
    if (!selectedFood) return;

    setLogging(true);
    setMessage('');

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

                <div className="mt-4 flex gap-2">
                  <button
                    onClick={() => {
                      setInfoFood(item);
                      setActiveMicroTab('minerals');
                    }}
                    className="flex-1 bg-slate-700 hover:bg-slate-600 text-slate-200 text-xs font-semibold py-2 rounded-lg transition-colors border border-slate-600"
                  >
                    ℹ️ Info
                  </button>
                  <button
                    onClick={() => handleSelectFood(item)}
                    className="flex-1 bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold py-2 rounded-lg transition-colors"
                  >
                    Select & Log
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* TABBED MICRONUTRIENT MODAL */}
      {infoFood && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-700 w-full max-w-xl p-6 rounded-xl shadow-2xl space-y-4 relative">
            <div className="flex justify-between items-start border-b border-slate-800 pb-3">
              <div>
                <h3 className="text-lg font-bold text-white">
                  {infoFood.description || infoFood.food_name || infoFood.name}
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">Nutritional profile per 100g</p>
              </div>
              <button
                onClick={() => setInfoFood(null)}
                className="text-slate-400 hover:text-white text-sm font-semibold"
              >
                ✕ Close
              </button>
            </div>

            {/* Macros Summary */}
            <div className="grid grid-cols-4 gap-2 text-center bg-slate-800/60 p-3 rounded-lg border border-slate-700/50">
              <div>
                <p className="text-[10px] text-slate-400 uppercase font-semibold">Calories</p>
                <p className="text-sm font-bold text-blue-400">{infoFood.Calories ?? 0} kcal</p>
              </div>
              <div>
                <p className="text-[10px] text-slate-400 uppercase font-semibold">Protein</p>
                <p className="text-sm font-bold text-emerald-400">{infoFood.Protein ?? 0}g</p>
              </div>
              <div>
                <p className="text-[10px] text-slate-400 uppercase font-semibold">Carbs</p>
                <p className="text-sm font-bold text-amber-400">{infoFood.Carbs ?? 0}g</p>
              </div>
              <div>
                <p className="text-[10px] text-slate-400 uppercase font-semibold">Fats</p>
                <p className="text-sm font-bold text-purple-400">{infoFood.Fats ?? 0}g</p>
              </div>
            </div>

            {/* Category Tabs Header */}
            <div className="flex justify-between items-center pt-2">
              <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
                Micronutrient Breakdown
              </h4>
              <div className="flex gap-1 bg-slate-800 p-1 rounded-lg border border-slate-700">
                <button
                  type="button"
                  onClick={() => setActiveMicroTab('minerals')}
                  className={`text-[11px] font-semibold px-2.5 py-1 rounded-md transition-colors ${
                    activeMicroTab === 'minerals'
                      ? 'bg-blue-600 text-white'
                      : 'text-slate-400 hover:text-white'
                  }`}
                >
                  🧪 Minerals
                </button>
                <button
                  type="button"
                  onClick={() => setActiveMicroTab('bcomplex')}
                  className={`text-[11px] font-semibold px-2.5 py-1 rounded-md transition-colors ${
                    activeMicroTab === 'bcomplex'
                      ? 'bg-blue-600 text-white'
                      : 'text-slate-400 hover:text-white'
                  }`}
                >
                  💧 B-Complex
                </button>
                <button
                  type="button"
                  onClick={() => setActiveMicroTab('antioxidants')}
                  className={`text-[11px] font-semibold px-2.5 py-1 rounded-md transition-colors ${
                    activeMicroTab === 'antioxidants'
                      ? 'bg-blue-600 text-white'
                      : 'text-slate-400 hover:text-white'
                  }`}
                >
                  🛡️ Vitamins
                </button>
              </div>
            </div>

            {/* Tab Content Grid */}
            <div className="grid grid-cols-2 gap-2 text-xs pt-1">
              {activeMicroTab === 'minerals' && (
                <>
                  <div className="bg-slate-800 p-2.5 rounded-md flex justify-between border border-slate-700/40">
                    <span className="text-slate-400">Calcium</span>
                    <span className="font-semibold text-slate-200">{infoFood.calcium ?? 0} mg</span>
                  </div>
                  <div className="bg-slate-800 p-2.5 rounded-md flex justify-between border border-slate-700/40">
                    <span className="text-slate-400">Iron</span>
                    <span className="font-semibold text-slate-200">{infoFood.iron ?? 0} mg</span>
                  </div>
                  <div className="bg-slate-800 p-2.5 rounded-md flex justify-between border border-slate-700/40">
                    <span className="text-slate-400">Magnesium</span>
                    <span className="font-semibold text-slate-200">{infoFood.magnesium ?? 0} mg</span>
                  </div>
                  <div className="bg-slate-800 p-2.5 rounded-md flex justify-between border border-slate-700/40">
                    <span className="text-slate-400">Phosphorus</span>
                    <span className="font-semibold text-slate-200">{infoFood.phosphorus ?? 0} mg</span>
                  </div>
                  <div className="bg-slate-800 p-2.5 rounded-md flex justify-between border border-slate-700/40">
                    <span className="text-slate-400">Potassium</span>
                    <span className="font-semibold text-slate-200">{infoFood.potassium ?? 0} mg</span>
                  </div>
                  <div className="bg-slate-800 p-2.5 rounded-md flex justify-between border border-slate-700/40">
                    <span className="text-slate-400">Sodium</span>
                    <span className="font-semibold text-slate-200">{infoFood.sodium ?? 0} mg</span>
                  </div>
                  <div className="bg-slate-800 p-2.5 rounded-md flex justify-between border border-slate-700/40">
                    <span className="text-slate-400">Zinc</span>
                    <span className="font-semibold text-slate-200">{infoFood.zinc ?? 0} mg</span>
                  </div>
                  <div className="bg-slate-800 p-2.5 rounded-md flex justify-between border border-slate-700/40">
                    <span className="text-slate-400">Selenium</span>
                    <span className="font-semibold text-slate-200">{infoFood.selenium ?? 0} mcg</span>
                  </div>
                </>
              )}

              {activeMicroTab === 'bcomplex' && (
                <>
                  <div className="bg-slate-800 p-2.5 rounded-md flex justify-between border border-slate-700/40">
                    <span className="text-slate-400">Thiamin (B1)</span>
                    <span className="font-semibold text-slate-200">{infoFood.thiamin ?? 0} mg</span>
                  </div>
                  <div className="bg-slate-800 p-2.5 rounded-md flex justify-between border border-slate-700/40">
                    <span className="text-slate-400">Riboflavin (B2)</span>
                    <span className="font-semibold text-slate-200">{infoFood.riboflavin ?? 0} mg</span>
                  </div>
                  <div className="bg-slate-800 p-2.5 rounded-md flex justify-between border border-slate-700/40">
                    <span className="text-slate-400">Niacin (B3)</span>
                    <span className="font-semibold text-slate-200">{infoFood.niacin ?? 0} mg</span>
                  </div>
                  <div className="bg-slate-800 p-2.5 rounded-md flex justify-between border border-slate-700/40">
                    <span className="text-slate-400">Pantothenic Acid (B5)</span>
                    <span className="font-semibold text-slate-200">{infoFood.pantothenic_acid ?? 0} mg</span>
                  </div>
                  <div className="bg-slate-800 p-2.5 rounded-md flex justify-between border border-slate-700/40">
                    <span className="text-slate-400">Vitamin B6</span>
                    <span className="font-semibold text-slate-200">{infoFood.vitamin_b6 ?? 0} mg</span>
                  </div>
                  <div className="bg-slate-800 p-2.5 rounded-md flex justify-between border border-slate-700/40">
                    <span className="text-slate-400">Folate (B9)</span>
                    <span className="font-semibold text-slate-200">{infoFood.folate ?? 0} mcg</span>
                  </div>
                  <div className="bg-slate-800 p-2.5 rounded-md flex justify-between border border-slate-700/40">
                    <span className="text-slate-400">Vitamin B12</span>
                    <span className="font-semibold text-slate-200">{infoFood.vitamin_b12 ?? 0} mcg</span>
                  </div>
                </>
              )}

              {activeMicroTab === 'antioxidants' && (
                <>
                  <div className="bg-slate-800 p-2.5 rounded-md flex justify-between border border-slate-700/40">
                    <span className="text-slate-400">Vitamin A</span>
                    <span className="font-semibold text-slate-200">{infoFood.vitamin_a ?? 0} mcg</span>
                  </div>
                  <div className="bg-slate-800 p-2.5 rounded-md flex justify-between border border-slate-700/40">
                    <span className="text-slate-400">Vitamin C</span>
                    <span className="font-semibold text-slate-200">{infoFood.vitamin_c ?? 0} mg</span>
                  </div>
                  <div className="bg-slate-800 p-2.5 rounded-md flex justify-between border border-slate-700/40">
                    <span className="text-slate-400">Vitamin E</span>
                    <span className="font-semibold text-slate-200">{infoFood.vitamin_e ?? 0} mg</span>
                  </div>
                </>
              )}
            </div>

            <div className="pt-2 flex justify-end">
              <button
                onClick={() => {
                  const foodToLog = infoFood;
                  setInfoFood(null);
                  handleSelectFood(foodToLog);
                }}
                className="w-full bg-blue-600 hover:bg-blue-500 text-white font-semibold py-2 rounded-lg text-xs transition-colors"
              >
                Log This Item
              </button>
            </div>
          </div>
        </div>
      )}

      {/* RECORD MEAL POPUP MODAL */}
      {selectedFood && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-700 w-full max-w-xl p-6 rounded-xl shadow-2xl space-y-4 relative">
            <div className="flex justify-between items-start border-b border-slate-800 pb-3">
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
                className="text-slate-400 hover:text-white text-sm font-semibold p-1"
              >
                ✕ Close
              </button>
            </div>

            <div className="flex items-center gap-4 py-2">
              <label className="text-sm text-slate-300 font-medium">Quantity (grams):</label>
              <input
                type="number"
                min="1"
                step="5"
                value={portionGrams}
                onChange={(e) => setPortionGrams(e.target.value)}
                className="bg-slate-800 border border-slate-700 rounded px-3 py-2 text-white w-28 text-center focus:outline-none focus:border-blue-500 font-semibold"
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
              <div className="mt-4 pt-4 border-t border-slate-800">
                <h4 className="text-xs font-semibold text-amber-400 uppercase tracking-wider mb-2">
                  Recommended Alternatives
                </h4>
                <div className="flex flex-wrap gap-2 max-h-40 overflow-y-auto pr-1">
                  {substitutions.map((sub, i) => (
                    <button
                      key={i}
                      onClick={() => handleSelectFood(sub)}
                      className="bg-slate-800 hover:bg-slate-700 border border-slate-700 text-xs text-slate-300 px-3 py-1.5 rounded-md transition-colors text-left"
                    >
                      {sub.description || sub.food_name || sub.name} ({sub.Calories ?? sub.calories ?? 0} kcal)
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}