import { useState } from 'react';
import { registerUser } from '../api/client';

export default function AuthModal({ onAuthSuccess }) {
  const [isRegistering, setIsRegistering] = useState(true);
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [userIdInput, setUserIdInput] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (isRegistering) {
      if (!username || !email) {
        setError('Please enter both username and email.');
        return;
      }
      try {
        const res = await registerUser({ username, email });
        const userData = {
          id: res.data.id || res.data.user_id,
          username: res.data.username || username,
          email: res.data.email || email
        };
        onAuthSuccess(userData);
      } catch (err) {
        console.error('Registration failed:', err);
        setError('Failed to create account. Try again.');
      }
    } else {
      const parsedId = parseInt(userIdInput, 10);
      if (isNaN(parsedId) || parsedId <= 0) {
        setError('Please enter a valid numeric User ID.');
        return;
      }
      // Log in with User ID (maps directly to database user)
      onAuthSuccess({ id: parsedId, username: `User #${parsedId}`, email: '' });
    }
  };

  return (
    <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
      <div className="bg-slate-800 border border-slate-700 w-full max-w-md p-6 rounded-xl shadow-2xl">
        <h2 className="text-xl font-bold text-white mb-2">
          {isRegistering ? 'Create Account' : 'Sign In to Your Session'}
        </h2>
        <p className="text-xs text-slate-400 mb-6">
          {isRegistering ? 'Enter your details to initialize your daily nutrition profile.' : 'Enter your assigned User ID to restore your daily tracker.'}
        </p>

        <form onSubmit={handleSubmit} className="space-y-4">
          {isRegistering ? (
            <>
              <div>
                <label className="text-xs font-semibold text-slate-300">Username</label>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="e.g. alex_dev"
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2.5 text-white mt-1 focus:outline-none focus:border-blue-500"
                />
              </div>
              <div>
                <label className="text-xs font-semibold text-slate-300">Email</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="alex@example.com"
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2.5 text-white mt-1 focus:outline-none focus:border-blue-500"
                />
              </div>
            </>
          ) : (
            <div>
              <label className="text-xs font-semibold text-slate-300">User ID</label>
              <input
                type="number"
                value={userIdInput}
                onChange={(e) => setUserIdInput(e.target.value)}
                placeholder="e.g. 1"
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2.5 text-white mt-1 focus:outline-none focus:border-blue-500"
              />
            </div>
          )}

          {error && <p className="text-xs text-red-400 font-medium">{error}</p>}

          <button
            type="submit"
            className="w-full bg-blue-600 hover:bg-blue-500 text-white font-semibold py-2.5 rounded-lg transition-colors"
          >
            {isRegistering ? 'Register & Continue' : 'Sign In'}
          </button>
        </form>

        <div className="mt-4 text-center">
          <button
            onClick={() => { setIsRegistering(!isRegistering); setError(''); }}
            className="text-xs text-blue-400 hover:underline"
          >
            {isRegistering ? 'Already registered? Sign in with User ID' : 'Need an account? Register here'}
          </button>
        </div>
      </div>
    </div>
  );
}