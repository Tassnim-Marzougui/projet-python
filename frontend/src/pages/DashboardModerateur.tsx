import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../AuthContext';
import api from '../api';
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const FIELDS = {
  parents:  { label: '👨‍👩‍👧 Situation des parents', options: [['usual','Situation normale'],['pretentious','Prétentieux'],['great_pret','Très prétentieux']] },
  has_nurs: { label: '🏫 Qualité garderie', options: [['proper','Bonne'],['less_proper','Acceptable'],['improper','Inadaptée'],['critical','Critique'],['very_crit','Très critique']] },
  form:     { label: '👪 Structure familiale', options: [['complete','Famille complète'],['completed','Recomposée'],['incomplete','Incomplète'],['foster',"D'accueil"]] },
  children: { label: '👶 Nombre d\'enfants', options: [['1','1 enfant'],['2','2 enfants'],['3','3 enfants'],['more','Plus de 3']] },
  housing:  { label: '🏠 Logement', options: [['convenient','Convenable'],['less_conv','Peu convenable'],['critical','Critique']] },
  finance:  { label: '💰 Finances', options: [['convenient','Stables'],['inconv','Difficultés']] },
  social:   { label: '🌍 Conditions sociales', options: [['nonprob','Pas de problème'],['slightly_prob','Légèrement problématique'],['problematic','Problématique']] },
  health:   { label: '❤️ Santé enfant', options: [['recommended','Bonne santé'],['priority','Priorité médicale'],['not_recom','Non recommandé']] },
};

const CLASS_COLORS: Record<string, string> = {
  recommend:  '#22c55e',
  very_recom: '#4ade80',
  priority:   '#f59e0b',
  spec_prior: '#38bdf8',
  not_recom:  '#ef4444',
};

const CLASS_LABELS: Record<string, string> = {
  recommend:  '✅ Recommandé',
  very_recom: '⭐ Très recommandé',
  priority:   '🟠 Prioritaire',
  spec_prior: '🔵 Priorité spéciale',
  not_recom:  '❌ Non recommandé',
};

export default function DashboardModerateur() {
  const { nom, logout } = useAuth();
  const navigate = useNavigate();

  const [stats, setStats]       = useState<any>(null);
  const [result, setResult]     = useState<any>(null);
  const [loading, setLoading]   = useState(false);
  const [error, setError]       = useState('');
  const [csvFile, setCsvFile]   = useState<File | null>(null);
  const [batchMsg, setBatchMsg] = useState('');

  const [form, setForm] = useState<Record<string, string>>({
    parents: 'usual', has_nurs: 'proper', form: 'complete',
    children: '1', housing: 'convenient', finance: 'convenient',
    social: 'nonprob', health: 'recommended'
  });

  useEffect(() => {
    api.get('/api/moderateur/stats').then(r => setStats(r.data)).catch(() => {});
  }, [result]);

  const handlePredict = async () => {
    setLoading(true);
    setError('');
    setResult(null);
    try {
      const res = await api.post('/api/predict', form);
      setResult(res.data);
    } catch (e: any) {
      setError(e.response?.data?.detail || 'Erreur de prédiction');
    } finally {
      setLoading(false);
    }
  };

  const handleBatch = async () => {
    if (!csvFile) return;
    setBatchMsg('');
    const fd = new FormData();
    fd.append('file', csvFile);
    try {
      const res = await api.post('/api/predict-batch', fd, { responseType: 'blob' });
      const url = URL.createObjectURL(res.data);
      const a = document.createElement('a');
      a.href = url; a.download = 'predictions.csv'; a.click();
      setBatchMsg('✅ Fichier téléchargé !');
    } catch {
      setBatchMsg('❌ Erreur lors du traitement');
    }
  };

  const doLogout = () => { logout(); navigate('/login'); };

  const pieData = stats?.distribution
    ? Object.entries(stats.distribution).map(([k, v]) => ({ name: k, value: v }))
    : [];

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
          <span className="text-3xl animate-bounce">🐣</span>
          <div>
            <p className="font-semibold text-gray-800 text-lg">Nursery ML</p>
            <p className="text-xs text-pink-500">Dashboard modérateur</p>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <span className="text-sm bg-pink-100 text-pink-700 px-4 py-1.5 rounded-full flex items-center gap-1">
            <span>👤</span> {nom}
          </span>
          <button onClick={doLogout}
            className="text-sm bg-white border border-pink-300 hover:bg-pink-50 text-pink-600 px-4 py-1.5 rounded-full transition shadow-sm flex items-center gap-1">
            <span>🚪</span> Déconnexion
          </button>
        </div>
      </nav>

      <div className="max-w-6xl mx-auto p-6 space-y-6 relative z-10">

        {/* KPI CARDS */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-4 text-center shadow-lg border border-white/40">
            <div className="text-3xl mb-1">📊</div>
            <p className="text-2xl font-bold text-pink-500">{stats?.total_predictions ?? '...'}</p>
            <p className="text-xs text-gray-500 mt-1">Prédictions totales</p>
          </div>
          <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-4 text-center shadow-lg border border-white/40">
            <div className="text-3xl mb-1">🏡</div>
            <p className="text-2xl font-bold text-blue-500">{stats?.creche?.capacite ?? '...'}</p>
            <p className="text-xs text-gray-500 mt-1">Capacité crèche</p>
          </div>
          <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-4 text-center shadow-lg border border-white/40">
            <div className="text-3xl mb-1">🏷️</div>
            <p className="text-lg font-bold text-purple-500 truncate">{stats?.creche?.nom ?? '...'}</p>
            <p className="text-xs text-gray-500 mt-1">Ma crèche</p>
          </div>
          <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-4 text-center shadow-lg border border-white/40">
            <div className="text-3xl mb-1">📈</div>
            <p className="text-2xl font-bold text-yellow-500">
              {stats?.distribution
                ? Math.round(((stats.distribution['recommend'] || 0) + (stats.distribution['very_recom'] || 0)) / Math.max(stats.total_predictions, 1) * 100)
                : '...'}%
            </p>
            <p className="text-xs text-gray-500 mt-1">Taux d'acceptation</p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

          {/* FORMULAIRE PREDICTION */}
          <div className="bg-white/80 backdrop-blur-sm rounded-3xl p-6 shadow-xl border border-white/40">
            <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center gap-2">
              <span>🤖</span> Prédiction d'admission
            </h2>

            <div className="grid grid-cols-2 gap-4">
              {Object.entries(FIELDS).map(([key, field]) => (
                <div key={key}>
                  <label className="block text-xs text-gray-600 mb-1 flex items-center gap-1">
                    {field.label}
                  </label>
                  <select
                    value={form[key]}
                    onChange={e => setForm({ ...form, [key]: e.target.value })}
                    className="w-full bg-gray-50 border border-gray-200 rounded-xl px-3 py-2 text-sm text-gray-700 focus:outline-none focus:ring-2 focus:ring-pink-300 focus:border-transparent"
                  >
                    {field.options.map(([val, label]) => (
                      <option key={val} value={val}>{label}</option>
                    ))}
                  </select>
                </div>
              ))}
            </div>

            {error && <p className="text-red-500 text-sm mt-3 flex items-center gap-1">❌ {error}</p>}

            <button onClick={handlePredict} disabled={loading}
              className="mt-4 w-full bg-gradient-to-r from-pink-400 to-blue-400 hover:from-pink-500 hover:to-blue-500 text-white font-bold rounded-2xl py-3 text-sm transition transform hover:scale-105 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg flex items-center justify-center gap-2">
              {loading ? '⏳ Analyse en cours...' : '🔮 Obtenir la recommandation'}
            </button>

            {/* RESULTAT */}
            {result && (
              <div className="mt-4 rounded-2xl p-4 text-center border-2"
                style={{ borderColor: CLASS_COLORS[result.prediction] || '#64748b',
                         backgroundColor: (CLASS_COLORS[result.prediction] || '#64748b') + '15' }}>
                <p className="text-2xl font-bold mb-1" style={{ color: CLASS_COLORS[result.prediction] }}>
                  {CLASS_LABELS[result.prediction] || result.prediction}
                </p>
                <p className="text-gray-600 text-sm mb-3">
                  Confiance : {(result.confidence * 100).toFixed(1)}%
                </p>
                {Object.entries(result.probabilities).map(([cls, prob]: any) => (
                  <div key={cls} className="flex items-center gap-2 text-xs mb-1">
                    <span className="w-24 text-right text-gray-500">{cls}</span>
                    <div className="flex-1 bg-gray-200 rounded-full h-2">
                      <div className="h-2 rounded-full transition-all"
                        style={{ width: `${(prob*100).toFixed(1)}%`, backgroundColor: CLASS_COLORS[cls] || '#64748b' }} />
                    </div>
                    <span className="w-10 text-gray-700">{(prob*100).toFixed(1)}%</span>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* STATS + PIE CHART */}
          <div className="bg-white/80 backdrop-blur-sm rounded-3xl p-6 shadow-xl border border-white/40">
            <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center gap-2">
              <span>📊</span> Distribution des prédictions
            </h2>
            {pieData.length > 0 ? (
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie data={pieData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={90} label>
                    {pieData.map((entry: any) => (
                      <Cell key={entry.name} fill={CLASS_COLORS[entry.name] || '#64748b'} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-48 text-gray-500 text-sm">
                Aucune prédiction encore effectuée
              </div>
            )}

            {/* BATCH */}
            <div className="mt-4 border-t border-pink-200 pt-4">
              <h3 className="text-md font-semibold text-gray-700 mb-3 flex items-center gap-1">
                <span>📁</span> Prédiction par lot (CSV)
              </h3>
              <div className="relative">
                <input type="file" accept=".csv"
                  onChange={e => setCsvFile(e.target.files?.[0] || null)}
                  className="w-full text-sm text-gray-600 bg-gray-50 border border-gray-200 rounded-xl px-4 py-2.5 cursor-pointer file:mr-3 file:py-1 file:px-3 file:rounded-full file:border-0 file:bg-pink-100 file:text-pink-600 file:text-sm hover:file:bg-pink-200"
                />
              </div>
              {batchMsg && <p className="text-sm mt-2 text-green-600 flex items-center gap-1">{batchMsg}</p>}
              <button onClick={handleBatch} disabled={!csvFile}
                className="mt-3 w-full bg-white border border-pink-300 hover:bg-pink-50 text-pink-600 rounded-xl py-2.5 text-sm transition disabled:opacity-40 disabled:cursor-not-allowed shadow-sm flex items-center justify-center gap-2">
                <span>⬇️</span> Lancer et télécharger
              </button>
            </div>
          </div>
        </div>

        {/* Message rigolo */}
        <p className="text-center text-gray-500 text-xs mt-4">
          🧸 Plus de 1000 prédictions déjà réalisées par notre équipe de nounours !
        </p>
      </div>
    </div>
  );
}