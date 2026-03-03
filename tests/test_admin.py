"""
tests/test_admin.py
===================
Tests complets pour les endpoints admin & modérateur :
  GET  /api/admin/stats
  PUT  /api/admin/moderateurs/{id}/toggle
  GET  /api/moderateur/stats
  GET  /api/health
  GET  /api/model-info
"""
import pytest


# ══════════════════════════════════════════════════
#  GET /api/health
# ══════════════════════════════════════════════════

class TestHealth:

    def test_health_ok(self, client):
        """L'endpoint health retourne status ok."""
        resp = client.get("/api/health")
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "ok"
        assert "model" in body

    def test_health_no_auth_required(self, client):
        """Health est public, pas besoin de token."""
        resp = client.get("/api/health")
        assert resp.status_code == 200


# ══════════════════════════════════════════════════
#  GET /api/model-info
# ══════════════════════════════════════════════════

class TestModelInfo:

    def test_model_info_returns_data(self, client):
        """model-info retourne les métriques du modèle."""
        resp = client.get("/api/model-info")
        assert resp.status_code == 200
        body = resp.json()
        assert "model_name" in body
        assert "accuracy" in body

    def test_model_info_public(self, client):
        """model-info est accessible sans authentification."""
        resp = client.get("/api/model-info")
        assert resp.status_code == 200


# ══════════════════════════════════════════════════
#  GET /api/admin/stats
# ══════════════════════════════════════════════════

class TestAdminStats:

    def test_admin_stats_success(self, client, auth_headers_admin):
        """Admin → stats globales retournées correctement."""
        resp = client.get("/api/admin/stats", headers=auth_headers_admin)
        assert resp.status_code == 200
        body = resp.json()
        assert "total_predictions" in body
        assert "total_creches" in body
        assert "total_moderateurs" in body
        assert "distribution" in body
        assert "moderateurs" in body
        assert "model_info" in body

    def test_admin_stats_moderateur_forbidden(self, client, auth_headers_mod):
        """Modérateur → accès à /admin/stats refusé (403)."""
        resp = client.get("/api/admin/stats", headers=auth_headers_mod)
        assert resp.status_code == 403
        assert "administrateur" in resp.json()["detail"].lower()

    def test_admin_stats_no_token(self, client):
        """Sans token → 401."""
        resp = client.get("/api/admin/stats")
        assert resp.status_code == 401

    def test_admin_stats_invalid_token(self, client):
        """Token invalide → 401."""
        resp = client.get("/api/admin/stats",
                          headers={"Authorization": "Bearer faux_token"})
        assert resp.status_code == 401

    def test_admin_stats_contains_moderateurs_list(self, client, auth_headers_admin):
        """La liste des modérateurs contient les bons champs."""
        resp = client.get("/api/admin/stats", headers=auth_headers_admin)
        mods = resp.json()["moderateurs"]
        assert isinstance(mods, list)
        if mods:
            mod = mods[0]
            assert "id" in mod
            assert "nom" in mod
            assert "email" in mod
            assert "actif" in mod
            assert "created_at" in mod

    def test_admin_stats_total_moderateurs_correct(self, client, auth_headers_admin):
        """Le compteur de modérateurs correspond à la liste retournée."""
        resp = client.get("/api/admin/stats", headers=auth_headers_admin)
        body = resp.json()
        assert body["total_moderateurs"] == len(body["moderateurs"])


# ══════════════════════════════════════════════════
#  PUT /api/admin/moderateurs/{id}/toggle
# ══════════════════════════════════════════════════

class TestToggleMoerateur:

    def _get_moderateur_id(self, client, auth_headers_admin, email):
        """Helper : récupère l'ID d'un modérateur par email."""
        stats = client.get("/api/admin/stats", headers=auth_headers_admin)
        mods = stats.json()["moderateurs"]
        user = next((m for m in mods if m["email"] == email), None)
        return user["id"] if user else None

    def test_toggle_desactive_compte(self, client, auth_headers_admin):
        """Admin peut désactiver un compte modérateur."""
        # Créer un modérateur dédié
        client.post("/api/auth/register", json={
            "email":      "toggle_test@creche.fr",
            "password":   "Password1!",
            "nom":        "Toggle User",
            "nom_creche": "Crèche Toggle",
            "capacite":   10
        })
        user_id = self._get_moderateur_id(client, auth_headers_admin, "toggle_test@creche.fr")
        assert user_id is not None

        resp = client.put(f"/api/admin/moderateurs/{user_id}/toggle",
                          headers=auth_headers_admin)
        assert resp.status_code == 200
        body = resp.json()
        assert body["actif"] is False
        assert "desactive" in body["message"].lower()

    def test_toggle_reactive_compte(self, client, auth_headers_admin):
        """Admin peut réactiver un compte désactivé."""
        client.post("/api/auth/register", json={
            "email":      "reactiver@creche.fr",
            "password":   "Password1!",
            "nom":        "Reactiver User",
            "nom_creche": "Crèche React",
            "capacite":   10
        })
        user_id = self._get_moderateur_id(client, auth_headers_admin, "reactiver@creche.fr")

        # Désactiver
        client.put(f"/api/admin/moderateurs/{user_id}/toggle", headers=auth_headers_admin)
        # Réactiver
        resp = client.put(f"/api/admin/moderateurs/{user_id}/toggle",
                          headers=auth_headers_admin)
        assert resp.status_code == 200
        assert resp.json()["actif"] is True
        assert "active" in resp.json()["message"].lower()

    def test_toggle_user_not_found(self, client, auth_headers_admin):
        """ID inexistant → 404."""
        resp = client.put("/api/admin/moderateurs/99999/toggle",
                          headers=auth_headers_admin)
        assert resp.status_code == 404
        assert "non trouve" in resp.json()["detail"].lower()

    def test_toggle_moderateur_forbidden(self, client, auth_headers_mod):
        """Un modérateur ne peut pas utiliser cet endpoint → 403."""
        resp = client.put("/api/admin/moderateurs/1/toggle",
                          headers=auth_headers_mod)
        assert resp.status_code == 403

    def test_toggle_no_token(self, client):
        """Sans token → 401."""
        resp = client.put("/api/admin/moderateurs/1/toggle")
        assert resp.status_code == 401

    def test_toggle_desactive_empeche_login(self, client, auth_headers_admin):
        """Après désactivation, le modérateur ne peut plus se connecter."""
        # Créer
        client.post("/api/auth/register", json={
            "email":      "bloque@creche.fr",
            "password":   "Password1!",
            "nom":        "Bloque User",
            "nom_creche": "Crèche Bloquée",
            "capacite":   10
        })
        user_id = self._get_moderateur_id(client, auth_headers_admin, "bloque@creche.fr")

        # Désactiver
        client.put(f"/api/admin/moderateurs/{user_id}/toggle", headers=auth_headers_admin)

        # Tentative login
        resp = client.post("/api/auth/login", json={
            "email":    "bloque@creche.fr",
            "password": "Password1!"
        })
        assert resp.status_code == 403


# ══════════════════════════════════════════════════
#  GET /api/moderateur/stats
# ══════════════════════════════════════════════════

class TestModerateurStats:

    def test_moderateur_stats_success(self, client, auth_headers_mod):
        """Modérateur connecté → ses stats retournées."""
        resp = client.get("/api/moderateur/stats", headers=auth_headers_mod)
        assert resp.status_code == 200
        body = resp.json()
        assert "total_predictions" in body
        assert "distribution" in body
        assert "creche" in body

    def test_moderateur_stats_creche_info(self, client, auth_headers_mod):
        """Les infos de crèche sont incluses dans les stats."""
        resp = client.get("/api/moderateur/stats", headers=auth_headers_mod)
        creche = resp.json()["creche"]
        assert creche is not None
        assert "nom" in creche
        assert "capacite" in creche

    def test_moderateur_stats_no_token(self, client):
        """Sans token → 401."""
        resp = client.get("/api/moderateur/stats")
        assert resp.status_code == 401

    def test_moderateur_stats_invalid_token(self, client):
        """Token invalide → 401."""
        resp = client.get("/api/moderateur/stats",
                          headers={"Authorization": "Bearer invalid"})
        assert resp.status_code == 401

    def test_moderateur_stats_counts_predictions(
        self, client, auth_headers_mod, valid_prediction_input
    ):
        """Le compteur de prédictions augmente après une prédiction."""
        # Nombre initial
        before = client.get("/api/moderateur/stats",
                            headers=auth_headers_mod).json()["total_predictions"]
        # Faire une prédiction
        client.post("/api/predict", json=valid_prediction_input,
                    headers=auth_headers_mod)
        # Nombre après
        after = client.get("/api/moderateur/stats",
                           headers=auth_headers_mod).json()["total_predictions"]
        assert after == before + 1

    def test_moderateur_stats_distribution_updated(
        self, client, auth_headers_mod, valid_prediction_input
    ):
        """La distribution ML est mise à jour après une prédiction."""
        client.post("/api/predict", json=valid_prediction_input,
                    headers=auth_headers_mod)
        resp = client.get("/api/moderateur/stats", headers=auth_headers_mod)
        distribution = resp.json()["distribution"]
        assert isinstance(distribution, dict)
        assert len(distribution) > 0


# ══════════════════════════════════════════════════
#  FLUX COMPLET ADMIN
# ══════════════════════════════════════════════════

class TestFluxAdmin:

    def test_full_admin_flow(self, client, auth_headers_admin):
        """Flux : créer modérateur → voir dans stats → désactiver → vérifier login bloqué."""
        # 1. Créer un modérateur
        client.post("/api/auth/register", json={
            "email":      "full_flow@creche.fr",
            "password":   "FullFlow1!",
            "nom":        "Full Flow",
            "nom_creche": "Crèche FullFlow",
            "capacite":   20
        })

        # 2. Vérifier qu'il apparaît dans les stats admin
        stats = client.get("/api/admin/stats", headers=auth_headers_admin)
        assert stats.status_code == 200
        mods = stats.json()["moderateurs"]
        user = next((m for m in mods if m["email"] == "full_flow@creche.fr"), None)
        assert user is not None
        assert user["actif"] is True

        # 3. Désactiver le compte
        toggle = client.put(f"/api/admin/moderateurs/{user['id']}/toggle",
                            headers=auth_headers_admin)
        assert toggle.status_code == 200
        assert toggle.json()["actif"] is False

        # 4. Le modérateur ne peut plus se connecter
        login_blocked = client.post("/api/auth/login", json={
            "email":    "full_flow@creche.fr",
            "password": "FullFlow1!"
        })
        assert login_blocked.status_code == 403