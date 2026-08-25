import { useState } from 'react';
import { registerUser, updateUserProfile } from '../api/client';

export default function UserProfile({ activeUserId, setActiveUserId }) {
  const [userIdInput, setUserIdInput] = useState(activeUserId);
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  
  // Biometric state matching backend user model
  const [age, setAge] = useState(22);
  const [gender, setGender] = useState('male');
  const [weightKg, setWeightKg] = useState(70);
  const [heightCm, setHeightCm] = useState(175);
  const [activityLevel, setActivityLevel] = useState('sedentary');

  const [statusMsg, setStatusMsg] = useState('');

  const handleSwitchUser = (e) => {
    e.preventDefault();
    const parsedId = parseInt(userIdInput, 10);
    if (!isNaN(parsedId)) {
      setActiveUserId(parsedId);
      setStatusMsg(`Switched active session to User ID: ${parsedId}`);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setStatusMsg('');
    try {
      const res = await registerUser({ username, email });
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

  const handleUpdateProfile = async (e) => {
    e.preventDefault();
    setStatusMsg('');
    try {
      await updateUserProfile(activeUserId, {
        age: parseInt(age, 10),
        gender,
        weight_kg: parseFloat(weightKg),
        height_cm: parseFloat(heightCm),
        activity_level: activityLevel
      });
      setStatusMsg(`Biometrics updated for User #${activeUserId}! targets recalculated.`);
    } catch (err) {
      console.error('Profile update failed:', err);
      setStatusMsg('Failed to update biometrics.');
    }
  };

  return (
    <div className="space-y-6 max-w-2xl">
      <div className="bg-slate-800 border border-slate-700 p-6 rounded-xl">
        <h3 className="text-lg font-bold text-white mb-2">Active Session Context</h3>
        <form onSubmit={handleSwitchUser} className="flex gap-3">
          <input
            type="number"
            value={userIdInput}
            onChange={(e) => setUserIdInput(e.target.value)}
            className="bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-white w-32 focus:outline-none focus:border-blue-500"
          />
          <button type="submit" className="bg-blue-600 hover:bg-blue-500 text-white font-medium px-4 py-2 rounded-lg transition-colors text-sm">
            Switch Active User
          </button>
        </form>
      </div>

      <div className="bg-slate-800 border border-slate-700 p-6 rounded-xl">
        <h3 className="text-lg font-bold text-white mb-4">Register New User</h3>
        <form onSubmit={handleRegister} className="flex flex-col gap-3">
          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-blue-500"
          />
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-blue-500"
          />
          <button type="submit" className="bg-emerald-600 hover:bg-emerald-500 text-white font-medium px-4 py-2 rounded-lg transition-colors text-sm self-start">
            Register User
          </button>
        </form>
      </div>

      <div className="bg-slate-800 border border-slate-700 p-6 rounded-xl">
        <h3 className="text-lg font-bold text-white mb-4">Update Biometrics (User #{activeUserId})</h3>
        <form onSubmit={handleUpdateProfile} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-xs font-semibold text-slate-400">Age</label>
              <input type="number" value={age} onChange={(e) => setAge(e.target.value)} className="w-full bg-slate-900 border border-slate-700 rounded px-3 py-2 text-white mt-1" />
            </div>
            <div>
              <label className="text-xs font-semibold text-slate-400">Gender</label>
              <select value={gender} onChange={(e) => setGender(e.target.value)} className="w-full bg-slate-900 border border-slate-700 rounded px-3 py-2 text-white mt-1">
                <option value="male">Male</option>
                <option value="female">Female</option>
              </select>
            </div>
            <div>
              <label className="text-xs font-semibold text-slate-400">Weight (kg)</label>
              <input type="number" value={weightKg} onChange={(e) => setWeightKg(e.target.value)} className="w-full bg-slate-900 border border-slate-700 rounded px-3 py-2 text-white mt-1" />
            </div>
            <div>
              <label className="text-xs font-semibold text-slate-400">Height (cm)</label>
              <input type="number" value={heightCm} onChange={(e) => setHeightCm(e.target.value)} className="w-full bg-slate-900 border border-slate-700 rounded px-3 py-2 text-white mt-1" />
            </div>
          </div>
          <div>
            <label className="text-xs font-semibold text-slate-400">Activity Level</label>
            <select value={activityLevel} onChange={(e) => setActivityLevel(e.target.value)} className="w-full bg-slate-900 border border-slate-700 rounded px-3 py-2 text-white mt-1">
              <option value="sedentary">Sedentary</option>
              <option value="lightly_active">Lightly Active</option>
              <option value="moderately_active">Moderately Active</option>
              <option value="heavily_active">Heavily Active</option>
            </select>
          </div>
          <button type="submit" className="bg-purple-600 hover:bg-purple-500 text-white font-medium px-5 py-2 rounded-lg transition-colors text-sm">
            Save Biometrics
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