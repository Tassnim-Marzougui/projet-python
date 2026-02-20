import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
import pandas as pd
import numpy as np
import joblib
import json
import io

from database import get_db, create_tables, Utilisateur, Creche, DemandeAdmission
from auth import (hash_password, verify_password, create_access_token,
                  get_current_user, require_admin, require_moderateur)
from schemas import (RegisterRequest, LoginRequest, TokenResponse,
                     PredictionInput, PredictionOutput, StatsResponse, UserResponse)

# ── CHARGEMENT DU MODELE ──────────────────────────
MODEL       = None
CLASS_ORDER = None
ENCODER     = None
LABEL_ENC   = None
MODEL_INFO  = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global MODEL, CLASS_ORDER, ENCODER, LABEL_ENC, MODEL_INFO
    print("Chargement du modele ML...")
    MODEL       = joblib.load("data/models/best_model.pkl")
    ENCODER     = joblib.load("data/models/encoders/feature_encoder.pkl")
    LABEL_ENC   = joblib.load("data/models/encoders/label_encoder.pkl")
    CLASS_ORDER = joblib.load("data/models/encoders/class_order.pkl")
    with open("data/models/model_info.json") as f:
        MODEL_INFO = json.load(f)
    print(f"Modele charge : {MODEL_INFO['model_name']}")
    create_tables()
    from database import SessionLocal
    db = SessionLocal()
    admin = db.query(Utilisateur).filter(Utilisateur.email == "admin@nursery.com").first()
    if not admin:
        admin_user = Utilisateur(
            email="admin@nursery.com",
            mot_de_passe_hash=hash_password("Admin1234!"),
            nom="Administrateur",
            role="admin"
        )
        db.add(admin_user)
        db.commit()
        print("Compte admin cree : admin@nursery.com / Admin1234!")
    db.close()
    yield
    print("Arret de l'API")

app = FastAPI(
    title="Nursery ML API",
    description="API de prediction d'admission en creche",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/swagger",
    redoc_url=None
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── FONCTION PREDICTION ───────────────────────────
def predict_single(data: dict):
    features = ['parents','has_nurs','form','children','housing','finance','social','health']
    df = pd.DataFrame([[data[f] for f in features]], columns=features)
    X_enc         = ENCODER.transform(df)
    proba         = MODEL.predict_proba(X_enc)[0]
    pred_idx      = int(np.argmax(proba))
    prediction    = CLASS_ORDER[pred_idx]
    confidence    = float(proba[pred_idx])
    probabilities = {CLASS_ORDER[i]: round(float(p), 4) for i, p in enumerate(proba)}
    return prediction, confidence, probabilities

# ══════════════════════════════════════════════════
#  PAGE DOCUMENTATION INTERACTIVE
# ══════════════════════════════════════════════════
@app.get("/docs", response_class=HTMLResponse, include_in_schema=False)
def custom_docs():
    # Cherche le fichier HTML dans le dossier backend/
    html_path = os.path.join(os.path.dirname(__file__), "docs_custom.html")
    if os.path.exists(html_path):
        with open(html_path, encoding="utf-8") as f:
            return f.read()
    # Fallback : page simple si fichier absent
    return """
<!DOCTYPE html>
<html lang="fr">
<head><meta charset="UTF-8"><title>Nursery ML API</title>
<style>body{font-family:sans-serif;background:#0f172a;color:#e2e8f0;padding:40px;text-align:center}
h1{color:#38bdf8;margin-bottom:16px}p{color:#94a3b8}a{color:#38bdf8}</style></head>
<body>
<h1>🍼 Nursery ML API v1.0.0</h1>
<p>Fichier <strong>docs_custom.html</strong> introuvable dans le dossier backend/</p>
<p>Place le fichier docs_custom.html dans le dossier <strong>backend/</strong> et recharge.</p>
<p><a href="/swagger">Utiliser Swagger a la place</a></p>
</body></html>
"""

# ══════════════════════════════════════════════════
#  ENDPOINTS AUTH
# ══════════════════════════════════════════════════
@app.post("/api/auth/register", status_code=201)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(Utilisateur).filter(Utilisateur.email == req.email).first():
        raise HTTPException(status_code=400, detail="Email deja utilise")
    user = Utilisateur(
        email=req.email,
        mot_de_passe_hash=hash_password(req.password),
        nom=req.nom,
        role="moderateur"
    )
    db.add(user)
    db.flush()
    creche = Creche(nom=req.nom_creche, capacite=req.capacite, moderateur_id=user.id)
    db.add(creche)
    db.commit()
    return {"message": "Compte cree avec succes", "email": req.email}

@app.post("/api/auth/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(Utilisateur).filter(Utilisateur.email == req.email).first()
    if not user or not verify_password(req.password, user.mot_de_passe_hash):
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")
    if not user.actif:
        raise HTTPException(status_code=403, detail="Compte desactive")
    token = create_access_token({"sub": user.email, "role": user.role})
    return {"access_token": token, "token_type": "bearer", "role": user.role, "nom": user.nom}

@app.get("/api/auth/me")
def get_me(current_user: Utilisateur = Depends(get_current_user)):
    creche_info = None
    if current_user.creche:
        creche_info = {"nom": current_user.creche.nom, "capacite": current_user.creche.capacite}
    return {
        "id":     current_user.id,
        "email":  current_user.email,
        "nom":    current_user.nom,
        "role":   current_user.role,
        "creche": creche_info
    }

# ══════════════════════════════════════════════════
#  ENDPOINTS ML
# ══════════════════════════════════════════════════
@app.get("/api/health")
def health():
    return {"status": "ok", "model": MODEL_INFO["model_name"]}

@app.get("/api/model-info")
def model_info():
    return MODEL_INFO

@app.post("/api/predict", response_model=PredictionOutput)
def predict(
    data: PredictionInput,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(require_moderateur)
):
    prediction, confidence, probabilities = predict_single(data.dict())
    creche_id = current_user.creche.id if current_user.creche else None
    demande = DemandeAdmission(
        **data.dict(),
        prediction_ml=prediction,
        confidence=confidence,
        utilisateur_id=current_user.id,
        creche_id=creche_id
    )
    db.add(demande)
    db.commit()
    return {"prediction": prediction, "confidence": confidence, "probabilities": probabilities}

@app.post("/api/predict-batch")
async def predict_batch(
    file: UploadFile = File(...),
    current_user: Utilisateur = Depends(require_moderateur)
):
    content = await file.read()
    df = pd.read_csv(io.StringIO(content.decode("utf-8")))
    features = ['parents','has_nurs','form','children','housing','finance','social','health']
    for col in features:
        if col not in df.columns:
            raise HTTPException(status_code=400, detail=f"Colonne manquante : {col}")
    X_enc        = ENCODER.transform(df[features])
    probas       = MODEL.predict_proba(X_enc)
    pred_indices = np.argmax(probas, axis=1)
    df['prediction'] = [CLASS_ORDER[i] for i in pred_indices]
    df['confidence'] = [round(float(probas[i, idx]), 4) for i, idx in enumerate(pred_indices)]
    output = io.StringIO()
    df.to_csv(output, index=False)
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=predictions.csv"}
    )

# ══════════════════════════════════════════════════
#  ENDPOINTS STATS
# ══════════════════════════════════════════════════
@app.get("/api/moderateur/stats")
def moderateur_stats(
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(require_moderateur)
):
    demandes = db.query(DemandeAdmission).filter(
        DemandeAdmission.utilisateur_id == current_user.id
    ).all()
    distribution = {}
    for d in demandes:
        distribution[d.prediction_ml] = distribution.get(d.prediction_ml, 0) + 1
    creche_info = None
    if current_user.creche:
        creche_info = {"nom": current_user.creche.nom, "capacite": current_user.creche.capacite}
    return {
        "total_predictions": len(demandes),
        "distribution":      distribution,
        "creche":            creche_info
    }

@app.get("/api/admin/stats")
def admin_stats(
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(require_admin)
):
    total_predictions = db.query(DemandeAdmission).count()
    total_creches     = db.query(Creche).count()
    total_moderateurs = db.query(Utilisateur).filter(Utilisateur.role == "moderateur").count()
    all_demandes      = db.query(DemandeAdmission).all()
    distribution = {}
    for d in all_demandes:
        distribution[d.prediction_ml] = distribution.get(d.prediction_ml, 0) + 1
    moderateurs = db.query(Utilisateur).filter(Utilisateur.role == "moderateur").all()
    mods_list = []
    for m in moderateurs:
        mods_list.append({
            "id":         m.id,
            "nom":        m.nom,
            "email":      m.email,
            "actif":      m.actif,
            "created_at": str(m.created_at),
            "creche":     m.creche.nom if m.creche else None
        })
    return {
        "total_predictions": total_predictions,
        "total_creches":     total_creches,
        "total_moderateurs": total_moderateurs,
        "distribution":      distribution,
        "moderateurs":       mods_list,
        "model_info":        MODEL_INFO
    }

@app.put("/api/admin/moderateurs/{user_id}/toggle")
def toggle_moderateur(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(require_admin)
):
    user = db.query(Utilisateur).filter(Utilisateur.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouve")
    user.actif = not user.actif
    db.commit()
    return {"message": f"Compte {'active' if user.actif else 'desactive'}", "actif": user.actif}