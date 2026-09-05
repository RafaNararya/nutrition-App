import { useState, useEffect } from 'react';
import { updateUserProfile } from '../api/client';

export default function UserProfile({ activeUser, onProfileUpdated }) {
  const [unitSystem, setUnitSystem] = useState('imperial');

  // Helper function to safely extract a clean string string for activity_level
  const parseActivityLevel = (user) => {
    if (!user || !user.activity_level) return 'sedentary';
    const raw = typeof user.activity_level === 'object' ? user.activity_level.value : user.activity_level;
    return String(raw).toLowerCase().replace(/.*\.(\w+)/, '$1'); // handles Enum strings like 'ActivityLevel.moderately_active'
  };

  // State definitions
  const [age, setAge] = useState(activeUser?.age || 22);
  const [gender, setGender] = useState(activeUser?.gender || 'male');
  const [weightKg, setWeightKg] = useState(activeUser?.weight_kg || 70);
  const [heightCm, setHeightCm] = useState(activeUser?.height_cm || 175);

  // Imperial display state
  const [weightLbs, setWeightLbs] = useState(
    activeUser?.weight_lbs ?? Math.round((activeUser?.weight_kg || 70) * 2.20462)
  );
  const [heightFt, setHeightFt] = useState(
    activeUser?.height_ft ?? Math.floor(((activeUser?.height_cm || 175) / 2.54) / 12)
  );
  const [heightIn, setHeightIn] = useState(
    activeUser?.height_in ?? Math.round(((activeUser?.height_cm || 175) / 2.54) % 12)
  );

  const [activityLevel, setActivityLevel] = useState(parseActivityLevel(activeUser));
  const [statusMsg, setStatusMsg] = useState('');
  const [saving, setSaving] = useState(false);

  // Keep state synchronized whenever activeUser prop updates
  useEffect(() => {
    if (activeUser) {
      if (activeUser.age) setAge(activeUser.age);
      if (activeUser.gender) setGender(activeUser.gender);
      
      setActivityLevel(parseActivityLevel(activeUser));

      if (activeUser.weight_kg) {
        setWeightKg(activeUser.weight_kg);
        setWeightLbs(
          activeUser.weight_lbs ?? Math.round(activeUser.weight_kg * 2.20462)
        );
      }
      if (activeUser.height_cm) {
        setHeightCm(activeUser.height_cm);
        const totalInches = activeUser.height_cm / 2.54;
        setHeightFt(activeUser.height_ft ?? Math.floor(totalInches / 12));
        setHeightIn(activeUser.height_in ?? Math.round(totalInches % 12));
      }
    }
  }, [activeUser]);

  const handleUnitToggle = (system) => {
    if (system === unitSystem) return;

    if (system === 'imperial') {
      const lbs = Math.round(weightKg * 2.20462);
      setWeightLbs(lbs);

      const totalInches = heightCm / 2.54;
      const feet = Math.floor(totalInches / 12);
      const inches = Math.round(totalInches % 12);
      setHeightFt(feet);
      setHeightIn(inches);
    } else {
      const kg = Math.round((weightLbs / 2.20462) * 10) / 10;
      setWeightKg(kg);

      const cm = Math.round(((heightFt * 12) + parseFloat(heightIn || 0)) * 2.54);
      setHeightCm(cm);
    }

    setUnitSystem(system);
  };

  const handleUpdateProfile = async (e) => {
    e.preventDefault();
    setStatusMsg('');
    setSaving(true);

    if (!activeUser || !activeUser.id) {
      setStatusMsg('Error: No active user ID found.');
      setSaving(false);
      return;
    }

    let finalKg = parseFloat(weightKg);
    let finalCm = parseFloat(heightCm);

    const lbsVal = parseFloat(weightLbs) || 0;
    const ftVal = parseInt(heightFt, 10) || 0;
    const inVal = parseFloat(heightIn) || 0;

    if (unitSystem === 'imperial') {
      finalKg = Math.round((lbsVal / 2.20462) * 10) / 10;
      const totalInches = (ftVal * 12) + inVal;
      finalCm = Math.round(totalInches * 2.54 * 10) / 10;
    }

    const payload = {
      age: parseInt(age, 10),
      gender: gender.toLowerCase(),
      weight_kg: finalKg,
      height_cm: finalCm,
      activity_level: activityLevel
    };

    try {
      const res = await updateUserProfile(activeUser.id, payload);
      setStatusMsg('Biometrics updated successfully! Macro targets recalculated.');
      
      if (onProfileUpdated) {
        onProfileUpdated({
          ...res.data,
          activity_level: activityLevel, // Explicitly pass the selected string
          weight_lbs: lbsVal,
          height_ft: ftVal,
          height_in: inVal
        });
      }
    } catch (err) {
      console.error('Profile update failed:', err);
      const detail = err.response?.data?.detail;
      if (Array.isArray(detail)) {
        setStatusMsg(`Validation Error: ${detail.map(d => d.msg).join(', ')}`);
      } else if (typeof detail === 'string') {
        setStatusMsg(`Error: ${detail}`);
      } else {
        setStatusMsg('Failed to update biometrics. Check backend logs.');
      }
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-6 max-w-2xl">
      <div className="bg-slate-800 border border-slate-700 p-6 rounded-xl">
        <h3 className="text-lg font-bold text-white">Account Details</h3>
        <div className="mt-3 text-sm space-y-1 text-slate-300">
          <p><span className="text-slate-400">Username:</span> {activeUser?.username}</p>
          {activeUser?.email && <p><span className="text-slate-400">Email:</span> {activeUser.email}</p>}
        </div>
      </div>

      <div className="bg-slate-800 border border-slate-700 p-6 rounded-xl">
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-lg font-bold text-white">Update Biometrics</h3>
          
          <div className="bg-slate-900 p-1 rounded-lg border border-slate-700 flex text-xs font-semibold">
            <button
              type="button"
              onClick={() => handleUnitToggle('metric')}
              className={`px-3 py-1 rounded-md transition-colors ${
                unitSystem === 'metric' 
                  ? 'bg-blue-600 text-white' 
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              Metric (kg / cm)
            </button>
            <button
              type="button"
              onClick={() => handleUnitToggle('imperial')}
              className={`px-3 py-1 rounded-md transition-colors ${
                unitSystem === 'imperial' 
                  ? 'bg-blue-600 text-white' 
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              Imperial (lbs / in)
            </button>
          </div>
        </div>

        <form onSubmit={handleUpdateProfile} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-xs font-semibold text-slate-400">Age</label>
              <input 
                type="number" 
                value={age} 
                onChange={(e) => setAge(e.target.value)} 
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white mt-1 focus:outline-none focus:border-blue-500" 
              />
            </div>

            <div>
              <label className="text-xs font-semibold text-slate-400">Gender</label>
              <select 
                value={gender} 
                onChange={(e) => setGender(e.target.value)} 
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white mt-1 focus:outline-none focus:border-blue-500"
              >
                <option value="male">Male</option>
                <option value="female">Female</option>
              </select>
            </div>

            {unitSystem === 'metric' ? (
              <>
                <div>
                  <label className="text-xs font-semibold text-slate-400">Weight (kg)</label>
                  <input 
                    type="number" 
                    step="0.1" 
                    value={weightKg} 
                    onChange={(e) => setWeightKg(e.target.value)} 
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white mt-1 focus:outline-none focus:border-blue-500" 
                  />
                </div>
                <div>
                  <label className="text-xs font-semibold text-slate-400">Height (cm)</label>
                  <input 
                    type="number" 
                    step="0.1" 
                    value={heightCm} 
                    onChange={(e) => setHeightCm(e.target.value)} 
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white mt-1 focus:outline-none focus:border-blue-500" 
                  />
                </div>
              </>
            ) : (
              <>
                <div>
                  <label className="text-xs font-semibold text-slate-400">Weight (lbs)</label>
                  <input 
                    type="number" 
                    step="0.1" 
                    value={weightLbs} 
                    onChange={(e) => setWeightLbs(e.target.value)} 
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white mt-1 focus:outline-none focus:border-blue-500" 
                  />
                </div>
                <div>
                  <label className="text-xs font-semibold text-slate-400">Height (Feet & Inches)</label>
                  <div className="grid grid-cols-2 gap-2 mt-1">
                    <input 
                      type="number" 
                      placeholder="ft" 
                      value={heightFt} 
                      onChange={(e) => setHeightFt(e.target.value)} 
                      className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-blue-500" 
                    />
                    <input 
                      type="number" 
                      placeholder="in" 
                      value={heightIn} 
                      onChange={(e) => setHeightIn(e.target.value)} 
                      className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-blue-500" 
                    />
                  </div>
                </div>
              </>
            )}
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-400">Activity Level</label>
            <select 
              value={activityLevel} 
              onChange={(e) => setActivityLevel(e.target.value)} 
              className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white mt-1 focus:outline-none focus:border-blue-500"
            >
              <option value="sedentary">Sedentary</option>
              <option value="lightly_active">Lightly Active</option>
              <option value="moderately_active">Moderately Active</option>
              <option value="heavily_active">Heavily Active</option>
            </select>
          </div>

          <button 
            type="submit" 
            disabled={saving} 
            className="bg-purple-600 hover:bg-purple-500 text-white font-medium px-5 py-2 rounded-lg transition-colors text-sm disabled:opacity-50"
          >
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