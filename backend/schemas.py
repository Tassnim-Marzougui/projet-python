from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# ── AUTH ──────────────────────────────────────────
class RegisterRequest(BaseModel):
    email:        str
    password:     str
    nom:          str
    nom_creche:   str
    capacite:     int

class LoginRequest(BaseModel):
    email:    str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type:   str
    role:         str
    nom:          str

class UserResponse(BaseModel):
    id:         int
    email:      str
    nom:        str
    role:       str
    actif:      bool
    created_at: datetime
    class Config:
        from_attributes = True

# ── PREDICTION ────────────────────────────────────
class PredictionInput(BaseModel):
    parents:  str
    has_nurs: str
    form:     str
    children: str
    housing:  str
    finance:  str
    social:   str
    health:   str

class PredictionOutput(BaseModel):
    prediction:    str
    confidence:    float
    probabilities: dict

# ── STATS ─────────────────────────────────────────
class StatsResponse(BaseModel):
    total_predictions: int
    distribution:      dict
    creche_nom:        Optional[str] = None
    capacite:          Optional[int] = None