export default function SummaryCards({ summary }) {
  // Extract macros directly from backend nested panel response structure
  const macros = summary?.panels?.macros || {};

  const calories = macros.calories ?? 0;
  const protein = macros.protein ?? 0;
  const carbs = macros.carbs ?? 0;
  const fats = macros.fats ?? 0;

  const cards = [
    { title: 'Calories', value: `${calories} kcal`, color: 'text-blue-400', border: 'border-blue-500/30' },
    { title: 'Protein', value: `${protein} g`, color: 'text-emerald-400', border: 'border-emerald-500/30' },
    { title: 'Carbs', value: `${carbs} g`, color: 'text-amber-400', border: 'border-amber-500/30' },
    { title: 'Fats', value: `${fats} g`, color: 'text-purple-400', border: 'border-purple-500/30' },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
      {cards.map((card, idx) => (
        <div
          key={idx}
          className={`bg-slate-800 border ${card.border} p-5 rounded-xl shadow-md`}
        >
          <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
            {card.title}
          </p>
          <p className={`text-2xl font-bold mt-2 ${card.color}`}>
            {card.value}
          </p>
        </div>
      ))}
    </div>
  );
}