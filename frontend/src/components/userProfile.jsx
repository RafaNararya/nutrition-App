import { useState } from 'react';
import { registerUser, updateUserProfile } from '../api/client';

export default function UserProfile({ activeUserId, setActiveUserId }) {
  const [userIdInput, setUserIdInput] = useState(activeUserId);
  const [username, setUsername] = useState('');
  const [calorieGoal, setCalorieGoal] = useState(2000);
  const [proteinGoal, setProteinGoal] = useState(150);
  const [carbsGoal, setCarbsGoal] = useState(200);
  const [fatGoal, setFatGoal] = useState(65);
  const [statusMsg, setStatusMsg] = useState('');

  // Switch Active User Session
  const handleSwitchUser = (e) => {
    e.preventDefault();
    const parsedId = parseInt(userIdInput, 10);
    if (!isNaN(parsedId)) {
      setActiveUserId(parsedId);
      setStatusMsg(`Switched active session to User ID: ${parsedId}`);
    }
  };

  // Register New User
  const handleRegister = async (e) => {
    e.preventDefault();
    setStatusMsg('');
    try {
      const res = await registerUser({ username });
      const newId = res.data.id || res.data.user_id;
      if (newId) {
        setActiveUserId(newId);
        setUserIdInput(newId);
        setStatusMsg(`Created & active user #${newId}: ${username}`);
      } else {
        setStatusMsg('User registered successfully!');
      }
    } catch (err) {
      console.error('Registration failed:', err);
      setStatusMsg('Failed to register user.');
    }
  };

  // Update Macro Targets
  const handleUpdateProfile = async (e) => {
    e.preventDefault();
    setStatusMsg('');
    try {
      await updateUserProfile(activeUserId, {
        calorie_target: parseFloat(calorieGoal),
        protein_target: parseFloat(proteinGoal),
        carbs_target: parseFloat(carbsGoal),
        fat_target: parseFloat(fatGoal),
      });
      setStatusMsg(`Profile targets updated for User #${activeUserId}!`);
    } catch (err) {
      console.error('Profile update failed:', err);
      setStatusMsg('Failed to update profile targets.');
    }
  };

  return (
    <div className="space-y-6 max-w-2xl">
      {/* Active Session Switcher */}
      <div className="bg-slate-800 border border-slate-700 p-6 rounded-xl">
        <h3 className="text-lg font-bold text-white mb-2">Active Session Context</h3>
        <p className="text-xs text-slate-400 mb-4">
          Select which User ID the frontend passes to database query requests.
        </p>
        <form onSubmit={handleSwitchUser} className="flex gap-3">
          <input
            type="number"
            value={userIdInput}
            onChange={(e) => setUserIdInput(e.target.value)}
            className="bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-white w-32 focus:outline-none focus:border-blue-500"
          />
          <button
            type="submit"
            className="bg-blue-600 hover:bg-blue-500 text-white font-medium px-4 py-2 rounded-lg transition-colors text-sm"
          >
            Switch Active User
          </button>
        </form>
      </div>

      {/* User Registration Form */}
      <div className="bg-slate-800 border border-slate-700 p-6 rounded-xl">
        <h3 className="text-lg font-bold text-white mb-4">Register New User</h3>
        <form onSubmit={handleRegister} className="flex gap-3">
          <input
            type="text"
            placeholder="Enter username..."
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="flex-1 bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-blue-500"
          />
          <button
            type="submit"
            className="bg-emerald-600 hover:bg-emerald-500 text-white font-medium px-4 py-2 rounded-lg transition-colors text-sm"
          >
            Register
          </button>
        </form>
      </div>

      {/* Profile Macro Targets Form */}
      <div className="bg-slate-800 border border-slate-700 p-6 rounded-xl">
        <h3 className="text-lg font-bold text-white mb-4">
          Set Nutritional Goals (User #{activeUserId})
        </h3>
        <form onSubmit={handleUpdateProfile} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-xs font-semibold text-slate-400">Calories (kcal)</label>
              <input
                type="number"
                value={calorieGoal}
                onChange={(e) => setCalorieGoal(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 rounded px-3 py-2 text-white mt-1"
              />
            </div>
            <div>
              <label className="text-xs font-semibold text-slate-400">Protein (g)</label>
              <input
                type="number"
                value={proteinGoal}
                onChange={(e) => setProteinGoal(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 rounded px-3 py-2 text-white mt-1"
              />
            </div>
            <div>
              <label className="text-xs font-semibold text-slate-400">Carbs (g)</label>
              <input
                type="number"
                value={carbsGoal}
                onChange={(e) => setCarbsGoal(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 rounded px-3 py-2 text-white mt-1"
              />
            </div>
            <div>
              <label className="text-xs font-semibold text-slate-400">Fat (g)</label>
              <input
                type="number"
                value={fatGoal}
                onChange={(e) => setFatGoal(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 rounded px-3 py-2 text-white mt-1"
              />
            </div>
          </div>
          <button
            type="submit"
            className="bg-purple-600 hover:bg-purple-500 text-white font-medium px-5 py-2 rounded-lg transition-colors text-sm"
          >
            Save Targets
          </button>
        </form>
      </div>

      {statusMsg && (
        <p className="text-sm font-semibold text-blue-400 bg-blue-950/40 border border-blue-800 p-3 rounded-lg">
          {statusMsg}
        </p>
      )}
    </div>
  );
}