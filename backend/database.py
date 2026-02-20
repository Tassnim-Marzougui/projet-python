from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

DATABASE_URL = "sqlite:///./data/creche.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Utilisateur(Base):
    __tablename__ = "utilisateurs"
    id            = Column(Integer, primary_key=True, index=True)
    email         = Column(String, unique=True, index=True, nullable=False)
    mot_de_passe_hash = Column(String, nullable=False)
    nom           = Column(String, nullable=False)
    role          = Column(String, default="moderateur")  # admin ou moderateur
    actif         = Column(Boolean, default=True)
    created_at    = Column(DateTime, default=datetime.utcnow)
    creche        = relationship("Creche", back_populates="moderateur", uselist=False)
    demandes      = relationship("DemandeAdmission", back_populates="utilisateur")

class Creche(Base):
    __tablename__ = "creches"
    id             = Column(Integer, primary_key=True, index=True)
    nom            = Column(String, nullable=False)
    capacite       = Column(Integer, nullable=False)
    moderateur_id  = Column(Integer, ForeignKey("utilisateurs.id"))
    moderateur     = relationship("Utilisateur", back_populates="creche")
    demandes       = relationship("DemandeAdmission", back_populates="creche")

class DemandeAdmission(Base):
    __tablename__ = "demandes_admission"
    id             = Column(Integer, primary_key=True, index=True)
    parents        = Column(String)
    has_nurs       = Column(String)
    form           = Column(String)
    children       = Column(String)
    housing        = Column(String)
    finance        = Column(String)
    social         = Column(String)
    health         = Column(String)
    prediction_ml  = Column(String)
    confidence     = Column(Float)
    created_at     = Column(DateTime, default=datetime.utcnow)
    utilisateur_id = Column(Integer, ForeignKey("utilisateurs.id"))
    creche_id      = Column(Integer, ForeignKey("creches.id"))
    utilisateur    = relationship("Utilisateur", back_populates="demandes")
    creche         = relationship("Creche", back_populates="demandes")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    Base.metadata.create_all(bind=engine)