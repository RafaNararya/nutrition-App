import { useEffect, useState } from 'react';
import { getStatus } from './api/client';

export default function App() {
  const [status, setStatus] = useState('Connecting...');

  useEffect(() => {
    getStatus()
      .then((res) => setStatus(JSON.stringify(res.data)))
      .catch((err) => setStatus(`Error connecting: ${err.message}`));
  }, []);

  return (
    <div className="min-h-screen bg-slate-900 text-white flex flex-col items-center justify-center p-4">
      <h1 className="text-3xl font-bold underline text-blue-400 mb-4">
        Nutrition Tracker
      </h1>
      <div className="bg-slate-800 p-4 rounded-lg shadow border border-slate-700">
        <p className="text-sm font-semibold text-slate-400">Backend Status:</p>
        <p className="font-mono text-green-400 mt-1">{status}</p>
      </div>
    </div>
  );
}