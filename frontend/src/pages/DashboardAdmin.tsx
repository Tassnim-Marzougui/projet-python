import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../AuthContext';
import api from '../api';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip,
  ResponsiveContainer, Cell
} from 'recharts';

const CLASS_COLORS: Record<string, string> = {
  recommend:  '#22c55e',
  very_recom: '#4ade80',
  priority:   '#f59e0b',
  spec_prior: '#38bdf8',
  not_recom:  '#ef4444',
};

export default function DashboardAdmin() {
  const { nom, logout } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [toggling, setToggling] = useState<number | null>(null);

  const fetchStats = async () => {
    try {
      const res = await api.get('/api/admin/stats');
      setStats(res.data);
    } catch {
      navigate('/login');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  const handleToggle = async (userId: number) => {
    setToggling(userId);
    try {
      await api.put(`/api/admin/moderateurs/${userId}/toggle`);
      await fetchStats();
    } finally {
      setToggling(null);
    }
  };

  const doLogout = () => {
    logout();
    navigate('/login');
  };

  const barData = stats?.distribution
    ? Object.entries(stats.distribution).map(([k, v]) => ({ name: k, value: v }))
    : [];

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-pink-100 via-yellow-50 to-blue-100 flex items-center justify-center">
        <div className="bg-white/70 backdrop-blur-sm rounded-3xl p-8 shadow-xl flex items-center gap-3">
          <span className="text-3xl animate-spin">⏳</span>
          <p className="text-gray-600">Chargement de votre espace admin...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-100 via-yellow-50 to-blue-100 relative overflow-hidden">
      {/* Éléments décoratifs */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-10 left-10 w-32 h-32 bg-white/60 rounded-full blur-3xl"></div>
        <div className="absolute bottom-10 right-10 w-48 h-48 bg-blue-200/50 rounded-full blur-3xl"></div>
        <div className="absolute top-20 right-20 w-40 h-40 bg-pink-200/50 rounded-full blur-2xl"></div>
        <div className="absolute bottom-20 left-20 w-36 h-36 bg-yellow-200/50 rounded-full blur-2xl"></div>
        <div className="absolute top-1/4 left-5 text-6xl opacity-20 rotate-12">☁️</div>
        <div className="absolute bottom-1/3 right-5 text-7xl opacity-20 -rotate-12">☁️</div>
        <div className="absolute top-2/3 left-1/4 text-4xl opacity-10">🐻</div>
        <div className="absolute bottom-1/4 right-1/3 text-5xl opacity-10">🧸</div>
      </div>

      {/* NAVBAR */}
      <nav className="relative z-10 bg-white/70 backdrop-blur-sm border-b border-pink-200 px-6 py-3 flex items-center justify-between shadow-sm">
        <div className="flex items-center gap-3">
          <span className="text-3xl animate-bounce">🐻‍❄️</span>
          <div>
            <p className="font-semibold text-gray-800 text-lg">Nursery ML</p>
            <p className="text-xs text-pink-500">Dashboard administrateur</p>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <span className="text-sm bg-pink-100 text-pink-700 px-4 py-1.5 rounded-full flex items-center gap-1">
            <span>👤</span> {nom}
          </span>
          <span className="text-xs bg-purple-200 text-purple-700 border border-purple-300 px-3 py-1 rounded-full">
            👑 Admin
          </span>
          <button
            onClick={doLogout}
            className="text-sm bg-white border border-pink-300 hover:bg-pink-50 text-pink-600 px-4 py-1.5 rounded-full transition shadow-sm flex items-center gap-1"
          >
            <span>🚪</span> Déconnexion
          </button>
        </div>
      </nav>

      <div className="max-w-6xl mx-auto p-6 space-y-6 relative z-10">
        {/* KPI CARDS */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-4 text-center shadow-lg border border-white/40">
            <div className="text-3xl mb-1">📊</div>
            <p className="text-2xl font-bold text-pink-500">{stats?.total_predictions ?? 0}</p>
            <p className="text-xs text-gray-500 mt-1">Prédictions totales</p>
          </div>
          <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-4 text-center shadow-lg border border-white/40">
            <div className="text-3xl mb-1">🏡</div>
            <p className="text-2xl font-bold text-blue-500">{stats?.total_creches ?? 0}</p>
            <p className="text-xs text-gray-500 mt-1">Crèches enregistrées</p>
          </div>
          <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-4 text-center shadow-lg border border-white/40">
            <div className="text-3xl mb-1">👥</div>
            <p className="text-2xl font-bold text-purple-500">{stats?.total_moderateurs ?? 0}</p>
            <p className="text-xs text-gray-500 mt-1">Modérateurs</p>
          </div>
          <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-4 text-center shadow-lg border border-white/40">
            <div className="text-3xl mb-1">🎯</div>
            <p className="text-2xl font-bold text-yellow-500">
              {stats?.model_info?.metrics?.f1_macro
                ? (stats.model_info.metrics.f1_macro * 100).toFixed(0) + '%'
                : '—'}
            </p>
            <p className="text-xs text-gray-500 mt-1">F1-Score modèle</p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* BAR CHART DISTRIBUTION */}
          <div className="bg-white/80 backdrop-blur-sm rounded-3xl p-6 shadow-xl border border-white/40">
            <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center gap-2">
              <span>📊</span> Distribution globale des prédictions
            </h2>
            {barData.length > 0 ? (
              <ResponsiveContainer width="100%" height={220}>
                <BarChart data={barData} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
                  <XAxis dataKey="name" tick={{ fill: '#4b5563', fontSize: 11 }} />
                  <YAxis tick={{ fill: '#4b5563', fontSize: 11 }} />
                  <Tooltip
                    contentStyle={{
                      background: 'white',
                      border: '1px solid #fbcfe8',
                      borderRadius: 12,
                      boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
                    }}
                    labelStyle={{ color: '#374151', fontWeight: 500 }}
                  />
                  <Bar dataKey="value" radius={[6, 6, 0, 0]}>
                    {barData.map((entry: any) => (
                      <Cell key={entry.name} fill={CLASS_COLORS[entry.name] || '#94a3b8'} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-48 text-gray-500 text-sm">
                Aucune prédiction encore effectuée
              </div>
            )}
          </div>

          {/* MODEL INFO */}
          <div className="bg-white/80 backdrop-blur-sm rounded-3xl p-6 shadow-xl border border-white/40">
            <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center gap-2">
              <span>🤖</span> Modèle ML en production
            </h2>
            {stats?.model_info ? (
              <div className="space-y-3">
                <div className="flex justify-between items-center py-2 border-b border-pink-200">
                  <span className="text-gray-500 text-sm">Modèle</span>
                  <span className="font-semibold text-pink-500">{stats.model_info.model_name}</span>
                </div>
                <div className="flex justify-between items-center py-2 border-b border-pink-200">
                  <span className="text-gray-500 text-sm">Entraîné le</span>
                  <span className="text-sm text-gray-700">{stats.model_info.trained_at}</span>
                </div>
                <div className="flex justify-between items-center py-2 border-b border-pink-200">
                  <span className="text-gray-500 text-sm">Accuracy</span>
                  <span className="text-green-600 font-semibold">
                    {stats.model_info.metrics?.accuracy
                      ? (stats.model_info.metrics.accuracy * 100).toFixed(1) + '%'
                      : '—'}
                  </span>
                </div>
                <div className="flex justify-between items-center py-2 border-b border-pink-200">
                  <span className="text-gray-500 text-sm">F1-Weighted</span>
                  <span className="text-green-600 font-semibold">
                    {stats.model_info.metrics?.f1_weighted
                      ? (stats.model_info.metrics.f1_weighted * 100).toFixed(1) + '%'
                      : '—'}
                  </span>
                </div>
                <div className="flex justify-between items-center py-2 border-b border-pink-200">
                  <span className="text-gray-500 text-sm">F1-Macro</span>
                  <span className="text-green-600 font-semibold">
                    {stats.model_info.metrics?.f1_macro
                      ? (stats.model_info.metrics.f1_macro * 100).toFixed(1) + '%'
                      : '—'}
                  </span>
                </div>
                <div className="mt-3 bg-pink-50/50 rounded-xl p-3">
                  <p className="text-xs text-gray-500 mb-2">Classes gérées</p>
                  <div className="flex flex-wrap gap-2">
                    {stats.model_info.class_order?.map((cls: string) => (
                      <span
                        key={cls}
                        className="text-xs px-3 py-1 rounded-full"
                        style={{
                          backgroundColor: CLASS_COLORS[cls] + '20',
                          color: CLASS_COLORS[cls],
                          border: `1px solid ${CLASS_COLORS[cls]}40`,
                        }}
                      >
                        {cls}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <p className="text-gray-500 text-sm">Informations non disponibles</p>
            )}
          </div>
        </div>

        {/* TABLE MODERATEURS */}
        <div className="bg-white/80 backdrop-blur-sm rounded-3xl p-6 shadow-xl border border-white/40">
          <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center gap-2">
            <span>👥</span> Gestion des modérateurs
          </h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-pink-200">
                  <th className="text-left py-3 px-4 text-gray-500 font-medium">Nom</th>
                  <th className="text-left py-3 px-4 text-gray-500 font-medium">Email</th>
                  <th className="text-left py-3 px-4 text-gray-500 font-medium">Crèche</th>
                  <th className="text-left py-3 px-4 text-gray-500 font-medium">Inscription</th>
                  <th className="text-left py-3 px-4 text-gray-500 font-medium">Statut</th>
                  <th className="text-left py-3 px-4 text-gray-500 font-medium">Action</th>
                </tr>
              </thead>
              <tbody>
                {stats?.moderateurs?.length > 0 ? (
                  stats.moderateurs.map((m: any) => (
                    <tr key={m.id} className="border-b border-pink-100 hover:bg-pink-50/30 transition">
                      <td className="py-3 px-4 font-medium text-gray-800">{m.nom}</td>
                      <td className="py-3 px-4 text-gray-600">{m.email}</td>
                      <td className="py-3 px-4 text-gray-600">{m.creche || '—'}</td>
                      <td className="py-3 px-4 text-gray-500 text-xs">
                        {m.created_at ? new Date(m.created_at).toLocaleDateString('fr-FR') : '—'}
                      </td>
                      <td className="py-3 px-4">
                        <span
                          className={`inline-flex items-center gap-1.5 text-xs px-3 py-1 rounded-full font-medium ${
                            m.actif
                              ? 'bg-green-100 text-green-700 border border-green-200'
                              : 'bg-red-100 text-red-700 border border-red-200'
                          }`}
                        >
                          <span className={`w-1.5 h-1.5 rounded-full ${m.actif ? 'bg-green-500' : 'bg-red-500'}`} />
                          {m.actif ? 'Actif' : 'Inactif'}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        <button
                          onClick={() => handleToggle(m.id)}
                          disabled={toggling === m.id}
                          className={`text-xs px-3 py-1.5 rounded-full transition disabled:opacity-50 flex items-center gap-1 ${
                            m.actif
                              ? 'bg-red-100 text-red-600 hover:bg-red-200 border border-red-200'
                              : 'bg-green-100 text-green-600 hover:bg-green-200 border border-green-200'
                          }`}
                        >
                          {toggling === m.id ? (
                            '⏳'
                          ) : m.actif ? (
                            <>
                              <span>🔒</span> Désactiver
                            </>
                          ) : (
                            <>
                              <span>✅</span> Activer
                            </>
                          )}
                        </button>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={6} className="py-8 text-center text-gray-500 text-sm">
                      Aucun modérateur enregistré
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Message rigolo */}
        <p className="text-center text-gray-500 text-xs mt-4">
          🧸 Vous êtes le super-héros de la crèche ! {stats?.total_predictions ?? 0} prédictions déjà sauvées.
        </p>
      </div>
    </div>
  );
}