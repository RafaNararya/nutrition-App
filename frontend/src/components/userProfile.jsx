import { useState } from 'react';
import { updateUserProfile } from '../api/client';

export default function UserProfile({ activeUser }) {
  const [age, setAge] = useState(22);
  const [gender, setGender] = useState('male');
  const [weightKg, setWeightKg] = useState(70);
  const [heightCm, setHeightCm] = useState(175);
  const [activityLevel, setActivityLevel] = useState('sedentary');
  const [statusMsg, setStatusMsg] = useState('');
  const [saving, setSaving] = useState(false);

  const handleUpdateProfile = async (e) => {
    e.preventDefault();
    setStatusMsg('');
    setSaving(true);
    try {
      await updateUserProfile(activeUser.id, {
        age: parseInt(age, 10),
        gender,
        weight_kg: parseFloat(weightKg),
        height_cm: parseFloat(heightCm),
        activity_level: activityLevel
      });
      setStatusMsg(`Biometrics updated successfully! Daily macro targets recalculated.`);
    } catch (err) {
      console.error('Profile update failed:', err);
      setStatusMsg('Failed to update biometrics. Ensure all fields are filled.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-6 max-w-2xl">
      <div className="bg-slate-800 border border-slate-700 p-6 rounded-xl">
        <h3 className="text-lg font-bold text-white">Account Details</h3>
        <div className="mt-3 text-sm space-y-1 text-slate-300">
          <p><span className="text-slate-400">Username:</span> {activeUser.username}</p>
          {activeUser.email && <p><span className="text-slate-400">Email:</span> {activeUser.email}</p>}
        </div>
      </div>

      <div className="bg-slate-800 border border-slate-700 p-6 rounded-xl">
        <h3 className="text-lg font-bold text-white mb-4">Update Biometrics</h3>
        <form onSubmit={handleUpdateProfile} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-xs font-semibold text-slate-400">Age</label>
              <input type="number" value={age} onChange={(e) => setAge(e.target.value)} className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white mt-1 focus:outline-none focus:border-blue-500" />
            </div>
            <div>
              <label className="text-xs font-semibold text-slate-400">Gender</label>
              <select value={gender} onChange={(e) => setGender(e.target.value)} className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white mt-1 focus:outline-none focus:border-blue-500">
                <option value="male">Male</option>
                <option value="female">Female</option>
              </select>
            </div>
            <div>
              <label className="text-xs font-semibold text-slate-400">Weight (kg)</label>
              <input type="number" step="0.1" value={weightKg} onChange={(e) => setWeightKg(e.target.value)} className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white mt-1 focus:outline-none focus:border-blue-500" />
            </div>
            <div>
              <label className="text-xs font-semibold text-slate-400">Height (cm)</label>
              <input type="number" step="0.1" value={heightCm} onChange={(e) => setHeightCm(e.target.value)} className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white mt-1 focus:outline-none focus:border-blue-500" />
            </div>
          </div>
          <div>
            <label className="text-xs font-semibold text-slate-400">Activity Level</label>
            <select value={activityLevel} onChange={(e) => setActivityLevel(e.target.value)} className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white mt-1 focus:outline-none focus:border-blue-500">
              <option value="sedentary">Sedentary</option>
              <option value="lightly_active">Lightly Active</option>
              <option value="moderately_active">Moderately Active</option>
              <option value="heavily_active">Heavily Active</option>
            </select>
          </div>
          <button type="submit" disabled={saving} className="bg-purple-600 hover:bg-purple-500 text-white font-medium px-5 py-2 rounded-lg transition-colors text-sm disabled:opacity-50">
            {saving ? 'Saving...' : 'Save Biometrics'}
          </button>
        </form>
      </div>

      {statusMsg && (
        <p className={`text-sm font-semibold p-3 rounded-lg border ${statusMsg.includes('successfully') ? 'bg-emerald-950/40 border-emerald-800 text-emerald-400' : 'bg-red-950/40 border-red-800 text-red-400'}`}>
          {statusMsg}
        </p>
      )}
    </div>
  );
}