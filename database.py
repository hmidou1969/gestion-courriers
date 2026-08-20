from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()

class Utilisateur(db.Model):
    """Modèle pour les utilisateurs du système"""
    __tablename__ = 'utilisateurs'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    departement = db.Column(db.String(100))
    role = db.Column(db.String(50), default='utilisateur')  # admin, manager, utilisateur
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    actif = db.Column(db.Boolean, default=True)
    
    # Relations
    courriers_entrants = db.relationship('CourrierEntrant', backref='recepteur', lazy=True)
    courriers_sortants = db.relationship('CourrierSortant', backref='createur', lazy=True)
    observations = db.relationship('Observation', backref='auteur', lazy=True)
    
    def __repr__(self):
        return f'<Utilisateur {self.email}>'
    
    def nom_complet(self):
        return f"{self.prenom} {self.nom}"


class Expediteur(db.Model):
    """Modèle pour les expéditeurs des courriers"""
    __tablename__ = 'expediteurs'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nom = db.Column(db.String(200), nullable=False, unique=True)
    type = db.Column(db.String(50))  # personne, entreprise, gouvernement
    adresse = db.Column(db.String(300))
    telephone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relations
    courriers = db.relationship('CourrierEntrant', backref='expediteur', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Expediteur {self.nom}>'


class Destinataire(db.Model):
    """Modèle pour les destinataires des courriers"""
    __tablename__ = 'destinataires'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nom = db.Column(db.String(200), nullable=False, unique=True)
    type = db.Column(db.String(50))  # personne, entreprise, gouvernement
    adresse = db.Column(db.String(300))
    telephone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relations
    courriers = db.relationship('CourrierSortant', backref='destinataire', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Destinataire {self.nom}>'


class Categorie(db.Model):
    """Modèle pour les catégories de courriers"""
    __tablename__ = 'categories'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nom = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    couleur = db.Column(db.String(7), default='#0d6efd')  # Couleur hex
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relations
    courriers_entrants = db.relationship('CourrierEntrant', backref='categorie', lazy=True)
    courriers_sortants = db.relationship('CourrierSortant', backref='categorie', lazy=True)
    
    def __repr__(self):
        return f'<Categorie {self.nom}>'


class CourrierEntrant(db.Model):
    """Modèle pour les courriers entrants"""
    __tablename__ = 'courriers_entrants'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    numero = db.Column(db.String(50), unique=True, nullable=False)
    date_entree = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    date_document = db.Column(db.Date)
    expediteur_id = db.Column(db.String(36), db.ForeignKey('expediteurs.id'), nullable=False)
    recepteur_id = db.Column(db.String(36), db.ForeignKey('utilisateurs.id'))
    categorie_id = db.Column(db.String(36), db.ForeignKey('categories.id'))
    designation = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)
    statut = db.Column(db.String(50), default='reçu')  # reçu, traité, en attente, archivé
    priorite = db.Column(db.String(20), default='normal')  # urgent, normal, faible
    numero_reference = db.Column(db.String(100))  # Référence du courrier original
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    date_modification = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    date_traitement = db.Column(db.DateTime)
    documents_joints = db.Column(db.Integer, default=0)  # Nombre de documents
    
    # Relations
    observations = db.relationship('Observation', backref='courrier_entrant', lazy=True, cascade='all, delete-orphan')
    historique = db.relationship('Historique', backref='courrier_entrant', lazy=True, cascade='all, delete-orphan', 
                                  foreign_keys='Historique.courrier_entrant_id')
    
    def __repr__(self):
        return f'<CourrierEntrant {self.numero}>'
    
    def jours_depuis_entree(self):
        """Calcule le nombre de jours depuis l'entrée du courrier"""
        delta = datetime.utcnow() - self.date_creation
        return delta.days


class CourrierSortant(db.Model):
    """Modèle pour les courriers sortants"""
    __tablename__ = 'courriers_sortants'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    numero = db.Column(db.String(50), unique=True, nullable=False)
    date_courrier = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    date_envoi = db.Column(db.Date)
    createur_id = db.Column(db.String(36), db.ForeignKey('utilisateurs.id'), nullable=False)
    destinataire_id = db.Column(db.String(36), db.ForeignKey('destinataires.id'), nullable=False)
    categorie_id = db.Column(db.String(36), db.ForeignKey('categories.id'))
    designation = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)
    statut = db.Column(db.String(50), default='brouillon')  # brouillon, envoyé, reçu, archivé
    priorite = db.Column(db.String(20), default='normal')  # urgent, normal, faible
    type_envoi = db.Column(db.String(50))  # email, courrier postal, coursier, etc.
    numero_suivi = db.Column(db.String(100))  # Numéro de suivi si applicable
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    date_modification = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    documents_joints = db.Column(db.Integer, default=0)
    
    # Relations
    observations = db.relationship('Observation', backref='courrier_sortant', lazy=True, cascade='all, delete-orphan')
    historique = db.relationship('Historique', backref='courrier_sortant', lazy=True, cascade='all, delete-orphan',
                                  foreign_keys='Historique.courrier_sortant_id')
    
    def __repr__(self):
        return f'<CourrierSortant {self.numero}>'


class Observation(db.Model):
    """Modèle pour les observations/commentaires sur les courriers"""
    __tablename__ = 'observations'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    contenu = db.Column(db.Text, nullable=False)
    auteur_id = db.Column(db.String(36), db.ForeignKey('utilisateurs.id'), nullable=False)
    courrier_entrant_id = db.Column(db.String(36), db.ForeignKey('courriers_entrants.id'))
    courrier_sortant_id = db.Column(db.String(36), db.ForeignKey('courriers_sortants.id'))
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    date_modification = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    type = db.Column(db.String(50), default='note')  # note, action, suivi
    
    def __repr__(self):
        return f'<Observation {self.id}>'


class Historique(db.Model):
    """Modèle pour l'historique des modifications"""
    __tablename__ = 'historique'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    courrier_entrant_id = db.Column(db.String(36), db.ForeignKey('courriers_entrants.id'))
    courrier_sortant_id = db.Column(db.String(36), db.ForeignKey('courriers_sortants.id'))
    action = db.Column(db.String(200), nullable=False)  # créé, modifié, supprimé, archivé, etc.
    description = db.Column(db.Text)
    ancienne_valeur = db.Column(db.Text)
    nouvelle_valeur = db.Column(db.Text)
    champ_modifie = db.Column(db.String(100))
    utilisateur = db.Column(db.String(200))
    date_action = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Historique {self.id}>'


class Statistique(db.Model):
    """Modèle pour stocker les statistiques"""
    __tablename__ = 'statistiques'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    date = db.Column(db.Date, default=datetime.utcnow, unique=True)
    total_courriers_entrants = db.Column(db.Integer, default=0)
    total_courriers_sortants = db.Column(db.Integer, default=0)
    courriers_entrants_traites = db.Column(db.Integer, default=0)
    courriers_sortants_envoyes = db.Column(db.Integer, default=0)
    courriers_urgents = db.Column(db.Integer, default=0)
    derniere_mise_a_jour = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Statistique {self.date}>'


def init_db(app):
    """Initialise la base de données avec les tables et données de base"""
    with app.app_context():
        db.create_all()
        
        # Créer les catégories par défaut si elles n'existent pas
        if Categorie.query.count() == 0:
            categories_par_defaut = [
                Categorie(nom='Administration', couleur='#0d6efd'),
                Categorie(nom='Ressources Humaines', couleur='#198754'),
                Categorie(nom='Financier', couleur='#ffc107'),
                Categorie(nom='Juridique', couleur='#dc3545'),
                Categorie(nom='Technique', couleur='#17a2b8'),
                Categorie(nom='Commercial', couleur='#6f42c1'),
            ]
            for cat in categories_par_defaut:
                db.session.add(cat)
            db.session.commit()
            print("✅ Catégories par défaut créées")
        
        # Créer un utilisateur administrateur par défaut
        if Utilisateur.query.count() == 0:
            admin = Utilisateur(
                nom='Admin',
                prenom='Système',
                email='admin@gestion-courriers.local',
                departement='Administration',
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
            print("✅ Utilisateur administrateur créé")
        
        print("✅ Base de données initialisée avec succès!")
