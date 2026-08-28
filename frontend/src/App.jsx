import { useEffect, useState, useCallback } from 'react';
import Navbar from './components/Navbar';
import SummaryCards from './components/summaryCards';
import MealLogs from './components/mealLogs';
import FoodSearch from './components/foodSearch';
import AuthModal from './components/AuthModal';
import UserProfile from './components/userProfile';
import { getUserSummary, getUserLogs } from './api/client';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [activeUser, setActiveUser] = useState(() => {
    const saved = localStorage.getItem('nt_active_user');
    return saved ? JSON.parse(saved) : null;
  });
  
  const [summary, setSummary] = useState(null);
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchDashboardData = useCallback(() => {
    if (!activeUser?.id) return;
    setLoading(true);

    Promise.all([
      getUserSummary(activeUser.id),
      getUserLogs(activeUser.id)
    ])
      .then(([summaryRes, logsRes]) => {
        setSummary(summaryRes.data || null);
        setLogs(Array.isArray(logsRes.data) ? logsRes.data : []);
      })
      .catch((err) => console.error('Error fetching dashboard data:', err))
      .finally(() => setLoading(false));
  }, [activeUser]);

  useEffect(() => {
    if (activeUser) {
      localStorage.setItem('nt_active_user', JSON.stringify(activeUser));
      fetchDashboardData();
    } else {
      localStorage.removeItem('nt_active_user');
    }
  }, [activeUser, fetchDashboardData]);

  const handleLogout = () => {
    setActiveUser(null);
    setSummary(null);
    setLogs([]);
  };

  if (!activeUser) {
    return <AuthModal onAuthSuccess={(user) => setActiveUser(user)} />;
  }

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 flex flex-col font-sans">
      <Navbar 
        activeTab={activeTab} 
        setActiveTab={setActiveTab} 
        username={activeUser.username}
        onLogout={handleLogout}
      />

      <main className="flex-1 max-w-6xl w-full mx-auto p-6">
        {activeTab === 'dashboard' && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <div>
                <h2 className="text-2xl font-bold text-white">Daily Overview</h2>
                <p className="text-xs text-slate-400">Welcome back, {activeUser.username}</p>
              </div>
              <button 
                onClick={fetchDashboardData}
                className="text-xs bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 px-3 py-1.5 rounded-lg transition-colors"
              >
                🔄 Refresh
              </button>
            </div>

            {loading && !summary ? (
              <div className="text-slate-400 animate-pulse">Loading dashboard data...</div>
            ) : (
              <>
                <SummaryCards summary={summary} />
                <MealLogs logs={logs} userId={activeUser.id} onLogDeleted={fetchDashboardData} />
              </>
            )}
          </div>
        )}

        {activeTab === 'search' && (
          <div>
            <h2 className="text-2xl font-bold mb-6 text-white">Search & Log Foods</h2>
            <FoodSearch userId={activeUser.id} onMealLogged={fetchDashboardData} />
          </div>
        )}

        {activeTab === 'profile' && (
          <div>
            <h2 className="text-2xl font-bold mb-6 text-white">My Profile & Biometrics</h2>
            <UserProfile activeUser={activeUser} />
          </div>
        )}
      </main>
    </div>
  );
}