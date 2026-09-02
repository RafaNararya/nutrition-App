export default function Navbar({ activeTab, setActiveTab, username, onLogout }) {
  const tabs = [
    { id: 'dashboard', label: 'Dashboard' },
    { id: 'search', label: 'Food Search' },
    { id: 'history', label: 'Meal History' },
    { id: 'profile', label: 'Profile' },
  ];

  return (
    <nav className="bg-slate-800 border-b border-slate-700 px-6 py-4 flex items-center justify-between">
      <div className="flex items-center space-x-3">
        <div className="bg-blue-500 text-white p-2 rounded-lg font-bold text-xl">
          NT
        </div>
        <span className="text-xl font-bold text-white tracking-wide">
          Nutrition Tracker
        </span>
      </div>

      <div className="flex items-center space-x-4">
        <div className="flex space-x-2">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2 rounded-md font-medium text-sm transition-colors ${
                activeTab === tab.id
                  ? 'bg-blue-600 text-white'
                  : 'text-slate-400 hover:text-white hover:bg-slate-700'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        <div className="h-6 w-px bg-slate-700" />

        <div className="flex items-center space-x-3">
          <span className="text-xs text-slate-300 font-medium">{username}</span>
          <button
            onClick={onLogout}
            className="text-xs text-slate-400 hover:text-red-400 transition-colors"
          >
            Sign Out
          </button>
        </div>
      </div>
    </nav>
  );
}