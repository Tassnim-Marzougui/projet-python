import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

import pytest
import joblib
import json
import numpy as np
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base, get_db, Utilisateur, Creche, DemandeAdmission
from auth import hash_password

# ── BASE DE DONNÉES EN MÉMOIRE POUR LES TESTS ────
SQLALCHEMY_TEST_URL = "sqlite:///./test_nursery.db"
engine_test = create_engine(SQLALCHEMY_TEST_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── MOCK DU MODELE ML ─────────────────────────────
CLASS_ORDER_TEST = ["not_recom", "priority", "recommend", "spec_prior", "very_recom"]

def make_mock_model():
    model = MagicMock()
    proba = np.array([[0.05, 0.10, 0.70, 0.10, 0.05]])
    model.predict_proba.return_value = proba
    return model

def make_mock_encoder():
    enc = MagicMock()
    enc.transform.return_value = np.zeros((1, 8))
    return enc

def make_mock_label_enc():
    le = MagicMock()
    le.classes_ = CLASS_ORDER_TEST
    return le


@pytest.fixture(scope="session", autouse=True)
def setup_mocks():
    """Patch joblib.load et open pour éviter de charger les vrais fichiers ML."""
    mock_model   = make_mock_model()
    mock_encoder = make_mock_encoder()
    mock_label   = make_mock_label_enc()
    mock_info    = {
        "model_name": "XGBoost",
        "accuracy": 0.97,
        "f1_score": 0.96,
        "trained_at": "2024-01-01"
    }

    def joblib_side_effect(path):
        if "best_model" in path:
            return mock_model
        elif "feature_encoder" in path:
            return mock_encoder
        elif "label_encoder" in path:
            return mock_label
        elif "class_order" in path:
            return CLASS_ORDER_TEST
        return MagicMock()

    with patch("joblib.load", side_effect=joblib_side_effect), \
         patch("builtins.open", unittest_mock_open(mock_info)):
        yield


def unittest_mock_open(json_data):
    """Helper pour mocker open() avec du JSON."""
    import unittest.mock as um
    m = um.mock_open(read_data=json.dumps(json_data))
    return m


@pytest.fixture(scope="session")
def client(setup_mocks):
    """Client HTTP de test avec DB en mémoire."""
    # Import app APRÈS les mocks
    import main as app_module
    app_module.app.dependency_overrides[get_db] = override_get_db

    # Injecter les mocks directement dans le module
    app_module.MODEL       = make_mock_model()
    app_module.ENCODER     = make_mock_encoder()
    app_module.LABEL_ENC   = make_mock_label_enc()
    app_module.CLASS_ORDER = CLASS_ORDER_TEST
    app_module.MODEL_INFO  = {
        "model_name": "XGBoost",
        "accuracy": 0.97,
        "f1_score": 0.96,
        "trained_at": "2024-01-01"
    }

    Base.metadata.create_all(bind=engine_test)
    _seed_admin()

    with TestClient(app_module.app) as c:
        yield c

    Base.metadata.drop_all(bind=engine_test)
    engine_test.dispose()  # Ferme toutes les connexions avant suppression (fix Windows)
    import time, gc
    gc.collect()
    time.sleep(0.5)
    if os.path.exists("./test_nursery.db"):
        try:
            os.remove("./test_nursery.db")
        except PermissionError:
            pass  # Windows : ignoré, le fichier sera écrasé au prochain run


def _seed_admin():
    """Crée le compte admin dans la DB de test."""
    db = TestingSessionLocal()
    if not db.query(Utilisateur).filter(Utilisateur.email == "admin@nursery.com").first():
        admin = Utilisateur(
            email="admin@nursery.com",
            mot_de_passe_hash=hash_password("Admin1234!"),
            nom="Administrateur",
            role="admin",
            actif=True
        )
        db.add(admin)
        db.commit()
    db.close()


# ── FIXTURES TOKENS ───────────────────────────────
@pytest.fixture(scope="session")
def admin_token(client):
    """Retourne un token JWT valide pour l'admin."""
    resp = client.post("/api/auth/login", json={
        "email": "admin@nursery.com",
        "password": "Admin1234!"
    })
    assert resp.status_code == 200
    return resp.json()["access_token"]


@pytest.fixture(scope="session")
def moderateur_token(client):
    """Inscrit un modérateur de test et retourne son token."""
    client.post("/api/auth/register", json={
        "email": "mod_test@creche.com",
        "password": "Moderateur1!",
        "nom": "Modérateur Test",
        "nom_creche": "Crèche Les Étoiles",
        "capacite": 30
    })
    resp = client.post("/api/auth/login", json={
        "email": "mod_test@creche.com",
        "password": "Moderateur1!"
    })
    assert resp.status_code == 200
    return resp.json()["access_token"]


@pytest.fixture
def auth_headers_admin(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def auth_headers_mod(moderateur_token):
    return {"Authorization": f"Bearer {moderateur_token}"}


# ── DONNÉES DE TEST ML ────────────────────────────
@pytest.fixture
def valid_prediction_input():
    return {
        "parents":  "usual",
        "has_nurs": "proper",
        "form":     "complete",
        "children": "1to2",
        "housing":  "convenient",
        "finance":  "convenient",
        "social":   "slightly_prob",
        "health":   "recommended"
    }