import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../AuthContext';
import api from '../api';

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const res = await api.post('/api/auth/login', { email, password });
      login(res.data.access_token, res.data.role, res.data.nom);
      if (res.data.role === 'admin') navigate('/admin/dashboard');
      else navigate('/moderateur/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erreur de connexion');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-100 via-yellow-50 to-blue-100 flex items-center justify-center p-4 relative overflow-hidden">
      {/* Éléments décoratifs : nuages et formes */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-10 left-10 w-32 h-32 bg-white/60 rounded-full blur-3xl"></div>
        <div className="absolute bottom-10 right-10 w-48 h-48 bg-blue-200/50 rounded-full blur-3xl"></div>
        <div className="absolute top-20 right-20 w-40 h-40 bg-pink-200/50 rounded-full blur-2xl"></div>
        <div className="absolute bottom-20 left-20 w-36 h-36 bg-yellow-200/50 rounded-full blur-2xl"></div>
        {/* Petits nuages avec des emojis (alternatives simples) */}
        <div className="absolute top-1/4 left-5 text-6xl opacity-20 rotate-12">☁️</div>
        <div className="absolute bottom-1/3 right-5 text-7xl opacity-20 -rotate-12">☁️</div>
      </div>

      <div className="w-full max-w-md relative z-10">
        {/* Logo et titre avec une mascotte */}
        <div className="text-center mb-8">
          <div className="text-7xl mb-2 animate-bounce">🐻‍❄️</div>
          <h1 className="text-3xl font-bold text-gray-800 font-comfortaa">
            Nursery ML
          </h1>
          <p className="text-gray-600 text-sm mt-1 bg-white/60 px-4 py-1 rounded-full inline-block backdrop-blur-sm">
            L'aventure des tout-petits
          </p>
        </div>

        {/* Carte de connexion */}
        <div className="bg-white/90 backdrop-blur-sm rounded-3xl p-8 shadow-2xl border border-white/40">
          <h2 className="text-2xl font-semibold text-gray-800 mb-2 flex items-center gap-2">
            <span>🔐</span> Connexion
          </h2>
          <p className="text-gray-500 text-sm mb-6">
            Heureux de vous revoir ! Remplissez vos petites informations.
          </p>

          {error && (
            <div className="bg-red-100 border border-red-300 text-red-700 rounded-xl px-4 py-3 mb-6 text-sm flex items-center gap-2">
              <span>❌</span> {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-gray-700 text-sm font-medium mb-1 flex items-center gap-1">
                <span>📧</span> Email
              </label>
              <div className="relative">
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="admin@nursery.com"
                  required
                  className="w-full bg-gray-50 border border-gray-200 rounded-2xl px-5 py-3 text-gray-800 text-sm focus:outline-none focus:ring-2 focus:ring-pink-300 focus:border-transparent transition pl-10"
                />
                <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">📨</span>
              </div>
            </div>

            <div>
              <label className="block text-gray-700 text-sm font-medium mb-1 flex items-center gap-1">
                <span>🔒</span> Mot de passe
              </label>
              <div className="relative">
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                  className="w-full bg-gray-50 border border-gray-200 rounded-2xl px-5 py-3 text-gray-800 text-sm focus:outline-none focus:ring-2 focus:ring-pink-300 focus:border-transparent transition pl-10"
                />
                <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">🔑</span>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-pink-400 to-blue-400 hover:from-pink-500 hover:to-blue-500 text-white font-bold rounded-2xl py-3 text-sm transition transform hover:scale-105 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 shadow-lg flex items-center justify-center gap-2"
            >
              {loading ? (
                <>⏳ Connexion en cours...</>
              ) : (
                <>
                  <span>🚀</span> Se connecter
                </>
              )}
            </button>
          </form>

          <div className="flex items-center justify-between mt-6 text-sm">
            <Link
              to="/register"
              className="text-pink-500 hover:text-pink-700 font-medium flex items-center gap-1"
            >
              <span>✨</span> Créer un compte
            </Link>
            <span className="text-gray-400">|</span>
            <button
              type="button"
              onClick={() => alert('Mot de passe oublié ? Contactez votre admin 😊')}
              className="text-blue-500 hover:text-blue-700 font-medium flex items-center gap-1"
            >
              <span>🪄</span> Mot de passe oublié ?
            </button>
          </div>

          {/* Compte de test avec style plus mignon */}
          <div className="mt-6 bg-yellow-50/80 rounded-2xl p-4 border border-yellow-200 flex items-start gap-3">
            <span className="text-2xl">🧸</span>
            <div>
              <p className="text-xs text-yellow-700 font-medium mb-1">
                Compte de test (admin) :
              </p>
              <p className="text-xs text-gray-600 font-mono bg-white/60 p-1 rounded">
                admin@nursery.com / Admin1234!
              </p>
              <p className="text-xs text-gray-500 mt-1">
                (Amusez-vous à explorer !)
              </p>
            </div>
          </div>
        </div>

        {/* Petit message rigolo en bas */}
        <p className="text-center text-gray-500 text-xs mt-4">
          🍼 Des bisous et des câlins garantis après connexion !
        </p>
      </div>
    </div>
  );
}