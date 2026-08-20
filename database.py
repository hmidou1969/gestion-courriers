from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class CourrierEntrant(db.Model):
    """Modèle pour les courriers entrants"""
    __tablename__ = 'courriers_entrants'
    
    id = db.Column(db.Integer, primary_key=True)
    numero_courrier = db.Column(db.String(50), unique=True, nullable=False, index=True)
    date_entree = db.Column(db.Date, nullable=False, index=True)
    expediteur = db.Column(db.String(255), nullable=False, index=True)
    designation = db.Column(db.String(500), nullable=False)
    observations = db.Column(db.Text)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    date_modification = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<CourrierEntrant {self.numero_courrier}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'numero_courrier': self.numero_courrier,
            'date_entree': self.date_entree.strftime('%d/%m/%Y') if self.date_entree else '',
            'expediteur': self.expediteur,
            'designation': self.designation,
            'observations': self.observations,
            'date_creation': self.date_creation.strftime('%d/%m/%Y %H:%M') if self.date_creation else '',
        }

class CourrierSortant(db.Model):
    """Modèle pour les courriers sortants"""
    __tablename__ = 'courriers_sortants'
    
    id = db.Column(db.Integer, primary_key=True)
    numero_courrier = db.Column(db.String(50), unique=True, nullable=False, index=True)
    date_courrier = db.Column(db.Date, nullable=False, index=True)
    destinataire = db.Column(db.String(255), nullable=False, index=True)
    designation = db.Column(db.String(500), nullable=False)
    observations = db.Column(db.Text)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    date_modification = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<CourrierSortant {self.numero_courrier}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'numero_courrier': self.numero_courrier,
            'date_courrier': self.date_courrier.strftime('%d/%m/%Y') if self.date_courrier else '',
            'destinataire': self.destinataire,
            'designation': self.designation,
            'observations': self.observations,
            'date_creation': self.date_creation.strftime('%d/%m/%Y %H:%M') if self.date_creation else '',
        }

def init_db(app):
    """Initialiser la base de données"""
    with app.app_context():
        db.create_all()
        print("✓ Base de données initialisée avec succès !")
