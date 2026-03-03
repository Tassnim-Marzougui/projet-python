"""
tests/test_auth.py
==================
Tests complets pour les endpoints d'authentification :
  POST /api/auth/register
  POST /api/auth/login
  GET  /api/auth/me
"""
import pytest


# ══════════════════════════════════════════════════
#  POST /api/auth/register
# ══════════════════════════════════════════════════

class TestRegister:

    def test_register_success(self, client):
        """Inscription valide d'un nouveau modérateur."""
        resp = client.post("/api/auth/register", json={
            "email":      "nouveau@creche.fr",
            "password":   "Password1!",
            "nom":        "Alice Dupont",
            "nom_creche": "Crèche Arc-en-Ciel",
            "capacite":   25
        })
        assert resp.status_code == 201
        body = resp.json()
        assert body["message"] == "Compte cree avec succes"
        assert body["email"] == "nouveau@creche.fr"

    def test_register_duplicate_email(self, client):
        """Inscription avec un email déjà utilisé → 400."""
        payload = {
            "email":      "doublon@creche.fr",
            "password":   "Password1!",
            "nom":        "Bob Martin",
            "nom_creche": "Crèche Soleil",
            "capacite":   20
        }
        client.post("/api/auth/register", json=payload)
        resp = client.post("/api/auth/register", json=payload)
        assert resp.status_code == 400
        assert "deja utilise" in resp.json()["detail"].lower()

    def test_register_missing_fields(self, client):
        """Inscription avec des champs manquants → 422."""
        resp = client.post("/api/auth/register", json={
            "email": "incomplet@creche.fr"
            # password, nom, nom_creche, capacite manquants
        })
        assert resp.status_code == 422

    def test_register_invalid_email_format(self, client):
        """Email invalide → 422 si Pydantic valide le format, sinon 400 ou 201.
        On vérifie juste que l'API répond sans crash serveur (pas 500)."""
        resp = client.post("/api/auth/register", json={
            "email":      "pas_un_email",
            "password":   "Password1!",
            "nom":        "Test User",
            "nom_creche": "Crèche Test",
            "capacite":   10
        })
        # Accepte 422 (Pydantic strict) ou 201 (pas de validation email dans schema)
        # L'important : pas d'erreur serveur 500
        assert resp.status_code in [201, 400, 422]
        assert resp.status_code != 500

    def test_register_creates_moderateur_role(self, client):
        """Le rôle attribué doit être 'moderateur' (jamais 'admin')."""
        client.post("/api/auth/register", json={
            "email":      "role_check@creche.fr",
            "password":   "Password1!",
            "nom":        "Charlie Role",
            "nom_creche": "Crèche Liberté",
            "capacite":   15
        })
        resp = client.post("/api/auth/login", json={
            "email":    "role_check@creche.fr",
            "password": "Password1!"
        })
        assert resp.status_code == 200
        assert resp.json()["role"] == "moderateur"

    def test_register_creates_associated_creche(self, client):
        """Une crèche est créée et liée au modérateur inscrit."""
        client.post("/api/auth/register", json={
            "email":      "creche_check@creche.fr",
            "password":   "Password1!",
            "nom":        "Dana Creche",
            "nom_creche": "Crèche Papillon",
            "capacite":   40
        })
        login_resp = client.post("/api/auth/login", json={
            "email":    "creche_check@creche.fr",
            "password": "Password1!"
        })
        token = login_resp.json()["access_token"]
        me_resp = client.get("/api/auth/me",
                             headers={"Authorization": f"Bearer {token}"})
        assert me_resp.status_code == 200
        creche = me_resp.json()["creche"]
        assert creche is not None
        assert creche["nom"] == "Crèche Papillon"
        assert creche["capacite"] == 40


# ══════════════════════════════════════════════════
#  POST /api/auth/login
# ══════════════════════════════════════════════════

class TestLogin:

    def test_login_admin_success(self, client):
        """Login admin valide → token JWT retourné."""
        resp = client.post("/api/auth/login", json={
            "email":    "admin@nursery.com",
            "password": "Admin1234!"
        })
        assert resp.status_code == 200
        body = resp.json()
        assert "access_token" in body
        assert body["token_type"] == "bearer"
        assert body["role"] == "admin"

    def test_login_moderateur_success(self, client, moderateur_token):
        """Login modérateur valide → token JWT retourné."""
        resp = client.post("/api/auth/login", json={
            "email":    "mod_test@creche.com",
            "password": "Moderateur1!"
        })
        assert resp.status_code == 200
        body = resp.json()
        assert "access_token" in body
        assert body["role"] == "moderateur"

    def test_login_wrong_password(self, client):
        """Mauvais mot de passe → 401."""
        resp = client.post("/api/auth/login", json={
            "email":    "admin@nursery.com",
            "password": "MauvaisMotDePasse!"
        })
        assert resp.status_code == 401
        assert "incorrect" in resp.json()["detail"].lower()

    def test_login_unknown_email(self, client):
        """Email inexistant → 401."""
        resp = client.post("/api/auth/login", json={
            "email":    "fantome@creche.fr",
            "password": "Password1!"
        })
        assert resp.status_code == 401

    def test_login_returns_nom(self, client):
        """La réponse contient le nom de l'utilisateur."""
        resp = client.post("/api/auth/login", json={
            "email":    "admin@nursery.com",
            "password": "Admin1234!"
        })
        assert "nom" in resp.json()
        assert resp.json()["nom"] == "Administrateur"

    def test_login_inactive_account(self, client, admin_token):
        """Compte désactivé → 403."""
        # 1. Inscrire un nouveau modérateur
        client.post("/api/auth/register", json={
            "email":      "inactif@creche.fr",
            "password":   "Password1!",
            "nom":        "Inactif User",
            "nom_creche": "Crèche Fermée",
            "capacite":   10
        })
        # 2. Récupérer son ID via les stats admin
        stats = client.get("/api/admin/stats",
                           headers={"Authorization": f"Bearer {admin_token}"})
        mods = stats.json()["moderateurs"]
        user = next((m for m in mods if m["email"] == "inactif@creche.fr"), None)
        assert user is not None
        # 3. Désactiver le compte
        client.put(f"/api/admin/moderateurs/{user['id']}/toggle",
                   headers={"Authorization": f"Bearer {admin_token}"})
        # 4. Tentative de login → 403
        resp = client.post("/api/auth/login", json={
            "email":    "inactif@creche.fr",
            "password": "Password1!"
        })
        assert resp.status_code == 403
        assert "desactive" in resp.json()["detail"].lower()

    def test_login_missing_fields(self, client):
        """Champs manquants → 422."""
        resp = client.post("/api/auth/login", json={"email": "admin@nursery.com"})
        assert resp.status_code == 422


# ══════════════════════════════════════════════════
#  GET /api/auth/me
# ══════════════════════════════════════════════════

class TestGetMe:

    def test_me_admin(self, client, auth_headers_admin):
        """Admin connecté → profil correct retourné."""
        resp = client.get("/api/auth/me", headers=auth_headers_admin)
        assert resp.status_code == 200
        body = resp.json()
        assert body["email"] == "admin@nursery.com"
        assert body["role"] == "admin"
        assert "id" in body

    def test_me_moderateur(self, client, auth_headers_mod):
        """Modérateur connecté → profil + crèche retournés."""
        resp = client.get("/api/auth/me", headers=auth_headers_mod)
        assert resp.status_code == 200
        body = resp.json()
        assert body["role"] == "moderateur"
        assert body["creche"] is not None
        assert "nom" in body["creche"]
        assert "capacite" in body["creche"]

    def test_me_no_token(self, client):
        """Sans token → 401."""
        resp = client.get("/api/auth/me")
        assert resp.status_code == 401

    def test_me_invalid_token(self, client):
        """Token invalide → 401."""
        resp = client.get("/api/auth/me",
                          headers={"Authorization": "Bearer token_bidon_xyz"})
        assert resp.status_code == 401

    def test_me_malformed_header(self, client):
        """Header mal formé → 401."""
        resp = client.get("/api/auth/me",
                          headers={"Authorization": "token_sans_bearer"})
        assert resp.status_code == 401


# ══════════════════════════════════════════════════
#  FLUX COMPLET : Register → Login → Me
# ══════════════════════════════════════════════════

class TestFluxComplet:

    def test_register_login_me_flow(self, client):
        """Flux bout-en-bout : inscription → connexion → profil."""
        # 1. Inscription
        reg = client.post("/api/auth/register", json={
            "email":      "flux@creche.fr",
            "password":   "FluxTest1!",
            "nom":        "Flux Utilisateur",
            "nom_creche": "Crèche Flux",
            "capacite":   20
        })
        assert reg.status_code == 201

        # 2. Connexion
        login = client.post("/api/auth/login", json={
            "email":    "flux@creche.fr",
            "password": "FluxTest1!"
        })
        assert login.status_code == 200
        token = login.json()["access_token"]
        assert token is not None

        # 3. Profil
        me = client.get("/api/auth/me",
                        headers={"Authorization": f"Bearer {token}"})
        assert me.status_code == 200
        body = me.json()
        assert body["email"] == "flux@creche.fr"
        assert body["nom"] == "Flux Utilisateur"
        assert body["role"] == "moderateur"
        assert body["creche"]["nom"] == "Crèche Flux"