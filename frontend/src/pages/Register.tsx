import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import api from '../api';

export default function Register() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    email: '',
    password: '',
    nom: '',
    nom_creche: '',
    capacite: '',
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      await api.post('/api/auth/register', {
        ...form,
        capacite: parseInt(form.capacite),
      });
      setSuccess('Compte créé avec succès ! Redirection...');
      setTimeout(() => navigate('/login'), 2000);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Erreur lors de l'inscription");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-100 via-yellow-50 to-blue-100 flex items-center justify-center p-4 relative overflow-hidden">
      {/* Éléments décoratifs */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-10 left-10 w-32 h-32 bg-white/60 rounded-full blur-3xl"></div>
        <div className="absolute bottom-10 right-10 w-48 h-48 bg-blue-200/50 rounded-full blur-3xl"></div>
        <div className="absolute top-20 right-20 w-40 h-40 bg-pink-200/50 rounded-full blur-2xl"></div>
        <div className="absolute bottom-20 left-20 w-36 h-36 bg-yellow-200/50 rounded-full blur-2xl"></div>
        <div className="absolute top-1/4 left-5 text-6xl opacity-20 rotate-12">☁️</div>
        <div className="absolute bottom-1/3 right-5 text-7xl opacity-20 -rotate-12">☁️</div>
      </div>

      <div className="w-full max-w-md relative z-10">
        {/* Logo et mascotte */}
        <div className="text-center mb-8">
          <div className="text-7xl mb-2 animate-bounce">🐣</div>
          <h1 className="text-3xl font-bold text-gray-800 font-comfortaa">
            Nursery ML
          </h1>
          <p className="text-gray-600 text-sm mt-1 bg-white/60 px-4 py-1 rounded-full inline-block backdrop-blur-sm">
            Rejoignez notre aventure
          </p>
        </div>

        {/* Carte d'inscription */}
        <div className="bg-white/90 backdrop-blur-sm rounded-3xl p-8 shadow-2xl border border-white/40">
          <h2 className="text-2xl font-semibold text-gray-800 mb-2 flex items-center gap-2">
            <span>📝</span> Inscription
          </h2>
          <p className="text-gray-500 text-sm mb-6">
            Créez votre compte pour gérer votre crèche.
          </p>

          {error && (
            <div className="bg-red-100 border border-red-300 text-red-700 rounded-xl px-4 py-3 mb-6 text-sm flex items-center gap-2">
              <span>❌</span> {error}
            </div>
          )}
          {success && (
            <div className="bg-green-100 border border-green-300 text-green-700 rounded-xl px-4 py-3 mb-6 text-sm flex items-center gap-2">
              <span>✅</span> {success}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-gray-700 text-sm font-medium mb-1 flex items-center gap-1">
                <span>👤</span> Nom complet
              </label>
              <div className="relative">
                <input
                  name="nom"
                  value={form.nom}
                  onChange={handleChange}
                  required
                  className="w-full bg-gray-50 border border-gray-200 rounded-2xl px-5 py-3 text-gray-800 text-sm focus:outline-none focus:ring-2 focus:ring-pink-300 focus:border-transparent transition pl-10"
                />
                <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">🧸</span>
              </div>
            </div>

            <div>
              <label className="block text-gray-700 text-sm font-medium mb-1 flex items-center gap-1">
                <span>📧</span> Email
              </label>
              <div className="relative">
                <input
                  name="email"
                  type="email"
                  value={form.email}
                  onChange={handleChange}
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
                  name="password"
                  type="password"
                  value={form.password}
                  onChange={handleChange}
                  required
                  minLength={8}
                  className="w-full bg-gray-50 border border-gray-200 rounded-2xl px-5 py-3 text-gray-800 text-sm focus:outline-none focus:ring-2 focus:ring-pink-300 focus:border-transparent transition pl-10"
                />
                <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">🔑</span>
              </div>
            </div>

            <div>
              <label className="block text-gray-700 text-sm font-medium mb-1 flex items-center gap-1">
                <span>🏠</span> Nom de la crèche
              </label>
              <div className="relative">
                <input
                  name="nom_creche"
                  value={form.nom_creche}
                  onChange={handleChange}
                  required
                  className="w-full bg-gray-50 border border-gray-200 rounded-2xl px-5 py-3 text-gray-800 text-sm focus:outline-none focus:ring-2 focus:ring-pink-300 focus:border-transparent transition pl-10"
                />
                <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">🏡</span>
              </div>
            </div>

            <div>
              <label className="block text-gray-700 text-sm font-medium mb-1 flex items-center gap-1">
                <span>👶</span> Capacité maximale
              </label>
              <div className="relative">
                <input
                  name="capacite"
                  type="number"
                  value={form.capacite}
                  onChange={handleChange}
                  required
                  min={1}
                  className="w-full bg-gray-50 border border-gray-200 rounded-2xl px-5 py-3 text-gray-800 text-sm focus:outline-none focus:ring-2 focus:ring-pink-300 focus:border-transparent transition pl-10"
                />
                <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">📊</span>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-pink-400 to-blue-400 hover:from-pink-500 hover:to-blue-500 text-white font-bold rounded-2xl py-3 text-sm transition transform hover:scale-105 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 shadow-lg flex items-center justify-center gap-2 mt-2"
            >
              {loading ? (
                <>⏳ Inscription en cours...</>
              ) : (
                <>
                  <span>✨</span> Créer mon compte
                </>
              )}
            </button>
          </form>

          <div className="flex items-center justify-center mt-6 text-sm">
            <span className="text-gray-500">Déjà un compte ?</span>
            <Link
              to="/login"
              className="text-pink-500 hover:text-pink-700 font-medium ml-2 flex items-center gap-1"
            >
              <span>🔐</span> Se connecter
            </Link>
          </div>

          {/* Petit message rassurant */}
          <div className="mt-6 bg-blue-50/80 rounded-2xl p-3 border border-blue-200 flex items-start gap-2">
            <span className="text-xl">🌟</span>
            <p className="text-xs text-blue-700">
              Rejoignez notre communauté de crèches et facilitez vos admissions grâce à la prédiction intelligente.
            </p>
          </div>
        </div>

        {/* Message rigolo */}
        <p className="text-center text-gray-500 text-xs mt-4">
          🍼 Prêt à prédire l'avenir des petits bouts ?
        </p>
      </div>
    </div>
  );
}