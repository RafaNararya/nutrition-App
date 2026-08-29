import { useState } from 'react';
import { registerUser, loginUser } from '../api/client';

export default function AuthModal({ onAuthSuccess }) {
  const [isLogin, setIsLogin] = useState(false);
  
  // Registration form fields
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      let res;
      if (isLogin) {
        res = await loginUser({ username, password });
      } else {
        res = await registerUser({ username, email, password });
      }
      if (onAuthSuccess) {
        onAuthSuccess(res.data);
      }
    } catch (err) {
      console.error('Auth Error:', err);
      setError(
        err.response?.data?.detail || 'Authentication failed. Please check your details.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
      <div className="bg-slate-900 border border-slate-800 w-full max-w-md p-8 rounded-2xl shadow-2xl space-y-6">
        
        <div>
          <h2 className="text-2xl font-bold text-white">
            {isLogin ? 'Sign In to Your Session' : 'Create Account'}
          </h2>
          <p className="text-sm text-slate-400 mt-1">
            {isLogin
              ? 'Enter your credentials to restore your daily tracker.'
              : 'Enter your details to initialize your daily nutrition profile.'}
          </p>
        </div>

        {error && (
          <div className="bg-red-500/10 border border-red-500/30 text-red-400 text-sm p-3 rounded-lg">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-400 uppercase mb-1">
              Username
            </label>
            <input
              type="text"
              required
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="e.g. alex_dev"
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
            />
          </div>

          {!isLogin && (
            <div>
              <label className="block text-xs font-semibold text-slate-400 uppercase mb-1">
                Email
              </label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="alex@example.com"
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
              />
            </div>
          )}

          <div>
            <label className="block text-xs font-semibold text-slate-400 uppercase mb-1">
              Password
            </label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-500 text-white font-semibold py-3 rounded-lg transition-colors disabled:opacity-50 mt-2"
          >
            {loading
              ? 'Processing...'
              : isLogin
              ? 'Sign In'
              : 'Register & Continue'}
          </button>
        </form>

        <div className="text-center pt-2 border-t border-slate-800">
          <button
            type="button"
            onClick={() => {
              setIsLogin(!isLogin);
              setError('');
            }}
            className="text-xs text-slate-400 hover:text-blue-400 transition-colors"
          >
            {isLogin
              ? 'Need an account? Register here'
              : 'Already registered? Sign in with Username'}
          </button>
        </div>

      </div>
    </div>
  );
}