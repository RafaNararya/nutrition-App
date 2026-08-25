import { useEffect, useState, useCallback } from 'react';
import Navbar from './components/Navbar';
import SummaryCards from './components/summaryCards';
import MealLogs from './components/mealLogs';
import FoodSearch from './components/foodSearch';
import UserProfile from './components/userProfile';
import { getUserSummary, getUserLogs } from './api/client';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [activeUserId, setActiveUserId] = useState(1);
  const [summary, setSummary] = useState(null);
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchDashboardData = useCallback(() => {
    setLoading(true);
    Promise.all([
      getUserSummary(activeUserId),
      getUserLogs(activeUserId)
    ])
      .then(([summaryRes, logsRes]) => {
        setSummary(summaryRes.data);
        setLogs(Array.isArray(logsRes.data) ? logsRes.data : []);
        setLoading(false);
      })
      .catch((err) => {
        console.error('Error fetching dashboard data:', err);
        setLoading(false);
      });
  }, [activeUserId]);

  useEffect(() => {
    fetchDashboardData();
  }, [fetchDashboardData]);

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 flex flex-col font-sans">
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />

      <main className="flex-1 max-w-6xl w-full mx-auto p-6">
        {activeTab === 'dashboard' && (
          <div>
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold text-white">Daily Overview</h2>
              <span className="text-xs bg-slate-800 border border-slate-700 text-slate-300 px-3 py-1.5 rounded-lg">
                Active User ID: <span className="text-blue-400 font-bold">{activeUserId}</span>
              </span>
            </div>

            {loading ? (
              <div className="text-slate-400 animate-pulse">Loading dashboard data...</div>
            ) : (
              <>
                <SummaryCards summary={summary} />
                <MealLogs logs={logs} userId={activeUserId} onLogDeleted={fetchDashboardData} />
              </>
            )}
          </div>
        )}

        {activeTab === 'search' && (
          <div>
            <h2 className="text-2xl font-bold mb-6 text-white">Search & Log Foods</h2>
            <FoodSearch userId={activeUserId} onMealLogged={fetchDashboardData} />
          </div>
        )}

        {activeTab === 'profile' && (
          <div>
            <h2 className="text-2xl font-bold mb-6 text-white">User Profile & Settings</h2>
            <UserProfile activeUserId={activeUserId} setActiveUserId={setActiveUserId} />
          </div>
        )}
      </main>
    </div>
  );
}