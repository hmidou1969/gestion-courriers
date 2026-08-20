from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from functools import wraps
from database import db, init_db, Utilisateur, Expediteur, Destinataire, Categorie, CourrierEntrant, CourrierSortant, Observation, Historique, Statistique
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///gestion_courriers.db')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# ======================== GESTION DES SESSIONS ========================
users_session = {}

def login_required(f):
    """Décorateur pour vérifier si l'utilisateur est connecté"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in users_session:
            flash('Veuillez vous connecter d\'abord', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Décorateur pour vérifier si l'utilisateur est administrateur"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in users_session:
            flash('Veuillez vous connecter d\'abord', 'warning')
            return redirect(url_for('login'))
        
        utilisateur = Utilisateur.query.get(users_session['user_id'])
        if not utilisateur or utilisateur.role != 'admin':
            flash('Accès refusé : administrateur requis', 'danger')
            return redirect(url_for('dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function

# ======================== AUTHENTIFICATION ========================
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Page de connexion"""
    if request.method == 'POST':
        email = request.form.get('email')
        utilisateur = Utilisateur.query.filter_by(email=email, actif=True).first()
        
        if utilisateur:
            users_session['user_id'] = utilisateur.id
            users_session['user_name'] = utilisateur.nom_complet()
            users_session['user_role'] = utilisateur.role
            
            # Enregistrer dans l'historique
            historique = Historique(
                action='Connexion',
                description=f'Utilisateur {utilisateur.nom_complet()} connecté',
                utilisateur=utilisateur.nom_complet(),
                date_action=datetime.utcnow()
            )
            db.session.add(historique)
            db.session.commit()
            
            flash(f'Bienvenue {utilisateur.nom_complet()}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Email invalide ou utilisateur inactif', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Déconnexion"""
    if 'user_id' in users_session:
        utilisateur = Utilisateur.query.get(users_session['user_id'])
        if utilisateur:
            historique = Historique(
                action='Déconnexion',
                description=f'Utilisateur {utilisateur.nom_complet()} déconnecté',
                utilisateur=utilisateur.nom_complet(),
                date_action=datetime.utcnow()
            )
            db.session.add(historique)
            db.session.commit()
        
        users_session.clear()
        flash('Vous avez été déconnecté', 'info')
    
    return redirect(url_for('login'))

# ======================== DASHBOARD ========================
@app.route('/')
@login_required
def dashboard():
    """Tableau de bord principal"""
    utilisateur = Utilisateur.query.get(users_session['user_id'])
    
    # Statistiques
    total_entrants = CourrierEntrant.query.count()
    total_sortants = CourrierSortant.query.count()
    entrants_traites = CourrierEntrant.query.filter_by(statut='traité').count()
    sortants_envoyes = CourrierSortant.query.filter_by(statut='envoyé').count()
    urgents = CourrierEntrant.query.filter_by(priorite='urgent').count()
    
    # Quantités par catégorie
    categories = Categorie.query.all()
    stats_categories = []
    for cat in categories:
        entrants = CourrierEntrant.query.filter_by(categorie_id=cat.id).count()
        sortants = CourrierSortant.query.filter_by(categorie_id=cat.id).count()
        stats_categories.append({
            'nom': cat.nom,
            'entrants': entrants,
            'sortants': sortants,
            'total': entrants + sortants,
            'couleur': cat.couleur
        })
    
    # Courriers récents
    courriers_recents_entrants = CourrierEntrant.query.order_by(CourrierEntrant.date_creation.desc()).limit(5).all()
    courriers_recents_sortants = CourrierSortant.query.order_by(CourrierSortant.date_creation.desc()).limit(5).all()
    
    # Balance
    balance = {
        'entrants': total_entrants,
        'sortants': total_sortants,
        'difference': total_entrants - total_sortants,
        'traites': entrants_traites,
        'envoyes': sortants_envoyes,
        'en_attente': total_entrants - entrants_traites
    }
    
    return render_template('dashboard.html', 
                          utilisateur=utilisateur,
                          total_entrants=total_entrants,
                          total_sortants=total_sortants,
                          entrants_traites=entrants_traites,
                          sortants_envoyes=sortants_envoyes,
                          urgents=urgents,
                          stats_categories=stats_categories,
                          courriers_recents_entrants=courriers_recents_entrants,
                          courriers_recents_sortants=courriers_recents_sortants,
                          balance=balance)

# ======================== GESTION DES UTILISATEURS ========================
@app.route('/utilisateurs')
@admin_required
def utilisateurs():
    """Liste des utilisateurs"""
    page = request.args.get('page', 1, type=int)
    utilisateurs_list = Utilisateur.query.paginate(page=page, per_page=10)
    
    return render_template('utilisateurs/liste.html', utilisateurs=utilisateurs_list)

@app.route('/utilisateurs/nouveau', methods=['GET', 'POST'])
@admin_required
def nouveau_utilisateur():
    """Créer un nouvel utilisateur"""
    if request.method == 'POST':
        try:
            utilisateur = Utilisateur(
                nom=request.form.get('nom'),
                prenom=request.form.get('prenom'),
                email=request.form.get('email'),
                departement=request.form.get('departement'),
                role=request.form.get('role', 'utilisateur'),
                actif=request.form.get('actif') == 'on'
            )
            
            # Vérifier si l'email existe déjà
            if Utilisateur.query.filter_by(email=utilisateur.email).first():
                flash('Cet email existe déjà', 'danger')
                return render_template('utilisateurs/formulaire.html')
            
            db.session.add(utilisateur)
            db.session.commit()
            
            # Historique
            historique = Historique(
                action='Création utilisateur',
                description=f'Nouvel utilisateur créé : {utilisateur.nom_complet()}',
                utilisateur=users_session.get('user_name', 'Système'),
                date_action=datetime.utcnow()
            )
            db.session.add(historique)
            db.session.commit()
            
            flash(f'Utilisateur {utilisateur.nom_complet()} créé avec succès', 'success')
            return redirect(url_for('utilisateurs'))
        except Exception as e:
            flash(f'Erreur : {str(e)}', 'danger')
    
    return render_template('utilisateurs/formulaire.html')

@app.route('/utilisateurs/<user_id>/modifier', methods=['GET', 'POST'])
@admin_required
def modifier_utilisateur(user_id):
    """Modifier un utilisateur"""
    utilisateur = Utilisateur.query.get_or_404(user_id)
    
    if request.method == 'POST':
        try:
            ancien_nom = utilisateur.nom_complet()
            
            utilisateur.nom = request.form.get('nom')
            utilisateur.prenom = request.form.get('prenom')
            utilisateur.email = request.form.get('email')
            utilisateur.departement = request.form.get('departement')
            utilisateur.role = request.form.get('role')
            utilisateur.actif = request.form.get('actif') == 'on'
            
            db.session.commit()
            
            # Historique
            historique = Historique(
                action='Modification utilisateur',
                description=f'Utilisateur {ancien_nom} modifié',
                utilisateur=users_session.get('user_name', 'Système'),
                date_action=datetime.utcnow()
            )
            db.session.add(historique)
            db.session.commit()
            
            flash(f'Utilisateur {utilisateur.nom_complet()} modifié avec succès', 'success')
            return redirect(url_for('utilisateurs'))
        except Exception as e:
            flash(f'Erreur : {str(e)}', 'danger')
    
    return render_template('utilisateurs/formulaire.html', utilisateur=utilisateur)

@app.route('/utilisateurs/<user_id>/supprimer', methods=['POST'])
@admin_required
def supprimer_utilisateur(user_id):
    """Supprimer un utilisateur (désactivation)"""
    utilisateur = Utilisateur.query.get_or_404(user_id)
    nom_complet = utilisateur.nom_complet()
    
    utilisateur.actif = False
    db.session.commit()
    
    # Historique
    historique = Historique(
        action='Suppression utilisateur',
        description=f'Utilisateur {nom_complet} supprimé',
        utilisateur=users_session.get('user_name', 'Système'),
        date_action=datetime.utcnow()
    )
    db.session.add(historique)
    db.session.commit()
    
    flash(f'Utilisateur {nom_complet} supprimé', 'success')
    return redirect(url_for('utilisateurs'))

# ======================== COURRIERS ENTRANTS ========================
@app.route('/courriers-entrants')
@login_required
def courriers_entrants():
    """Liste des courriers entrants"""
    page = request.args.get('page', 1, type=int)
    recherche = request.args.get('recherche', '')
    filtre_statut = request.args.get('statut', '')
    
    query = CourrierEntrant.query
    
    if recherche:
        query = query.filter(
            (CourrierEntrant.numero.ilike(f'%{recherche}%')) |
            (CourrierEntrant.designation.ilike(f'%{recherche}%'))
        )
    
    if filtre_statut:
        query = query.filter_by(statut=filtre_statut)
    
    courriers = query.order_by(CourrierEntrant.date_entree.desc()).paginate(page=page, per_page=10)
    
    return render_template('courriers_entrants/liste.html', courriers=courriers, recherche=recherche)

@app.route('/courriers-entrants/nouveau', methods=['GET', 'POST'])
@login_required
def nouveau_courrier_entrant():
    """Créer un nouveau courrier entrant"""
    expediteurs = Expediteur.query.all()
    categories = Categorie.query.all()
    utilisateurs = Utilisateur.query.all()
    
    if request.method == 'POST':
        try:
            courrier = CourrierEntrant(
                numero=request.form.get('numero'),
                date_entree=datetime.strptime(request.form.get('date_entree'), '%Y-%m-%d').date(),
                date_document=datetime.strptime(request.form.get('date_document'), '%Y-%m-%d').date() if request.form.get('date_document') else None,
                expediteur_id=request.form.get('expediteur_id'),
                recepteur_id=request.form.get('recepteur_id'),
                categorie_id=request.form.get('categorie_id'),
                designation=request.form.get('designation'),
                description=request.form.get('description'),
                statut=request.form.get('statut', 'reçu'),
                priorite=request.form.get('priorite', 'normal'),
                numero_reference=request.form.get('numero_reference'),
                documents_joints=int(request.form.get('documents_joints', 0))
            )
            
            db.session.add(courrier)
            db.session.commit()
            
            # Historique
            historique = Historique(
                action='Création courrier entrant',
                description=f'Nouveau courrier entrant créé : {courrier.numero}',
                courrier_entrant_id=courrier.id,
                utilisateur=users_session.get('user_name', 'Système'),
                date_action=datetime.utcnow()
            )
            db.session.add(historique)
            db.session.commit()
            
            flash(f'Courrier {courrier.numero} créé avec succès', 'success')
            return redirect(url_for('courriers_entrants'))
        except Exception as e:
            flash(f'Erreur : {str(e)}', 'danger')
    
    return render_template('courriers_entrants/formulaire.html', 
                          expediteurs=expediteurs, 
                          categories=categories,
                          utilisateurs=utilisateurs)

@app.route('/courriers-entrants/<courrier_id>/modifier', methods=['GET', 'POST'])
@login_required
def modifier_courrier_entrant(courrier_id):
    """Modifier un courrier entrant"""
    courrier = CourrierEntrant.query.get_or_404(courrier_id)
    expediteurs = Expediteur.query.all()
    categories = Categorie.query.all()
    utilisateurs = Utilisateur.query.all()
    observations = Observation.query.filter_by(courrier_entrant_id=courrier_id).all()
    
    if request.method == 'POST':
        try:
            ancien_statut = courrier.statut
            
            courrier.numero = request.form.get('numero')
            courrier.date_entree = datetime.strptime(request.form.get('date_entree'), '%Y-%m-%d').date()
            courrier.date_document = datetime.strptime(request.form.get('date_document'), '%Y-%m-%d').date() if request.form.get('date_document') else None
            courrier.expediteur_id = request.form.get('expediteur_id')
            courrier.recepteur_id = request.form.get('recepteur_id')
            courrier.categorie_id = request.form.get('categorie_id')
            courrier.designation = request.form.get('designation')
            courrier.description = request.form.get('description')
            courrier.statut = request.form.get('statut', 'reçu')
            courrier.priorite = request.form.get('priorite', 'normal')
            courrier.numero_reference = request.form.get('numero_reference')
            courrier.documents_joints = int(request.form.get('documents_joints', 0))
            
            if courrier.statut == 'traité' and ancien_statut != 'traité':
                courrier.date_traitement = datetime.utcnow()
            
            db.session.commit()
            
            # Historique
            if ancien_statut != courrier.statut:
                historique = Historique(
                    action='Modification statut',
                    description=f'Statut changé de {ancien_statut} à {courrier.statut}',
                    courrier_entrant_id=courrier.id,
                    ancienne_valeur=ancien_statut,
                    nouvelle_valeur=courrier.statut,
                    champ_modifie='statut',
                    utilisateur=users_session.get('user_name', 'Système'),
                    date_action=datetime.utcnow()
                )
                db.session.add(historique)
                db.session.commit()
            
            flash(f'Courrier {courrier.numero} modifié avec succès', 'success')
            return redirect(url_for('courriers_entrants'))
        except Exception as e:
            flash(f'Erreur : {str(e)}', 'danger')
    
    return render_template('courriers_entrants/modifier.html', 
                          courrier=courrier, 
                          expediteurs=expediteurs, 
                          categories=categories,
                          utilisateurs=utilisateurs,
                          observations=observations)

@app.route('/courriers-entrants/<courrier_id>/observation', methods=['POST'])
@login_required
def ajouter_observation_entrant(courrier_id):
    """Ajouter une observation à un courrier entrant"""
    try:
        observation = Observation(
            contenu=request.form.get('contenu'),
            auteur_id=users_session['user_id'],
            courrier_entrant_id=courrier_id,
            type=request.form.get('type', 'note')
        )
        db.session.add(observation)
        db.session.commit()
        flash('Observation ajoutée', 'success')
    except Exception as e:
        flash(f'Erreur : {str(e)}', 'danger')
    
    return redirect(url_for('modifier_courrier_entrant', courrier_id=courrier_id))

# ======================== COURRIERS SORTANTS ========================
@app.route('/courriers-sortants')
@login_required
def courriers_sortants():
    """Liste des courriers sortants"""
    page = request.args.get('page', 1, type=int)
    recherche = request.args.get('recherche', '')
    filtre_statut = request.args.get('statut', '')
    
    query = CourrierSortant.query
    
    if recherche:
        query = query.filter(
            (CourrierSortant.numero.ilike(f'%{recherche}%')) |
            (CourrierSortant.designation.ilike(f'%{recherche}%'))
        )
    
    if filtre_statut:
        query = query.filter_by(statut=filtre_statut)
    
    courriers = query.order_by(CourrierSortant.date_courrier.desc()).paginate(page=page, per_page=10)
    
    return render_template('courriers_sortants/liste.html', courriers=courriers, recherche=recherche)

@app.route('/courriers-sortants/nouveau', methods=['GET', 'POST'])
@login_required
def nouveau_courrier_sortant():
    """Créer un nouveau courrier sortant"""
    destinataires = Destinataire.query.all()
    categories = Categorie.query.all()
    
    if request.method == 'POST':
        try:
            courrier = CourrierSortant(
                numero=request.form.get('numero'),
                date_courrier=datetime.strptime(request.form.get('date_courrier'), '%Y-%m-%d').date(),
                date_envoi=datetime.strptime(request.form.get('date_envoi'), '%Y-%m-%d').date() if request.form.get('date_envoi') else None,
                createur_id=users_session['user_id'],
                destinataire_id=request.form.get('destinataire_id'),
                categorie_id=request.form.get('categorie_id'),
                designation=request.form.get('designation'),
                description=request.form.get('description'),
                statut=request.form.get('statut', 'brouillon'),
                priorite=request.form.get('priorite', 'normal'),
                type_envoi=request.form.get('type_envoi'),
                numero_suivi=request.form.get('numero_suivi'),
                documents_joints=int(request.form.get('documents_joints', 0))
            )
            
            db.session.add(courrier)
            db.session.commit()
            
            # Historique
            historique = Historique(
                action='Création courrier sortant',
                description=f'Nouveau courrier sortant créé : {courrier.numero}',
                courrier_sortant_id=courrier.id,
                utilisateur=users_session.get('user_name', 'Système'),
                date_action=datetime.utcnow()
            )
            db.session.add(historique)
            db.session.commit()
            
            flash(f'Courrier {courrier.numero} créé avec succès', 'success')
            return redirect(url_for('courriers_sortants'))
        except Exception as e:
            flash(f'Erreur : {str(e)}', 'danger')
    
    return render_template('courriers_sortants/formulaire.html', 
                          destinataires=destinataires, 
                          categories=categories)

@app.route('/courriers-sortants/<courrier_id>/modifier', methods=['GET', 'POST'])
@login_required
def modifier_courrier_sortant(courrier_id):
    """Modifier un courrier sortant"""
    courrier = CourrierSortant.query.get_or_404(courrier_id)
    destinataires = Destinataire.query.all()
    categories = Categorie.query.all()
    observations = Observation.query.filter_by(courrier_sortant_id=courrier_id).all()
    
    if request.method == 'POST':
        try:
            ancien_statut = courrier.statut
            
            courrier.numero = request.form.get('numero')
            courrier.date_courrier = datetime.strptime(request.form.get('date_courrier'), '%Y-%m-%d').date()
            courrier.date_envoi = datetime.strptime(request.form.get('date_envoi'), '%Y-%m-%d').date() if request.form.get('date_envoi') else None
            courrier.destinataire_id = request.form.get('destinataire_id')
            courrier.categorie_id = request.form.get('categorie_id')
            courrier.designation = request.form.get('designation')
            courrier.description = request.form.get('description')
            courrier.statut = request.form.get('statut', 'brouillon')
            courrier.priorite = request.form.get('priorite', 'normal')
            courrier.type_envoi = request.form.get('type_envoi')
            courrier.numero_suivi = request.form.get('numero_suivi')
            courrier.documents_joints = int(request.form.get('documents_joints', 0))
            
            db.session.commit()
            
            # Historique
            if ancien_statut != courrier.statut:
                historique = Historique(
                    action='Modification statut',
                    description=f'Statut changé de {ancien_statut} à {courrier.statut}',
                    courrier_sortant_id=courrier.id,
                    ancienne_valeur=ancien_statut,
                    nouvelle_valeur=courrier.statut,
                    champ_modifie='statut',
                    utilisateur=users_session.get('user_name', 'Système'),
                    date_action=datetime.utcnow()
                )
                db.session.add(historique)
                db.session.commit()
            
            flash(f'Courrier {courrier.numero} modifié avec succès', 'success')
            return redirect(url_for('courriers_sortants'))
        except Exception as e:
            flash(f'Erreur : {str(e)}', 'danger')
    
    return render_template('courriers_sortants/modifier.html', 
                          courrier=courrier, 
                          destinataires=destinataires, 
                          categories=categories,
                          observations=observations)

@app.route('/courriers-sortants/<courrier_id>/observation', methods=['POST'])
@login_required
def ajouter_observation_sortant(courrier_id):
    """Ajouter une observation à un courrier sortant"""
    try:
        observation = Observation(
            contenu=request.form.get('contenu'),
            auteur_id=users_session['user_id'],
            courrier_sortant_id=courrier_id,
            type=request.form.get('type', 'note')
        )
        db.session.add(observation)
        db.session.commit()
        flash('Observation ajoutée', 'success')
    except Exception as e:
        flash(f'Erreur : {str(e)}', 'danger')
    
    return redirect(url_for('modifier_courrier_sortant', courrier_id=courrier_id))

# ======================== STATISTIQUES ET BALANCE ========================
@app.route('/statistiques')
@login_required
def statistiques():
    """Page des statistiques et balance"""
    # Statistiques générales
    total_entrants = CourrierEntrant.query.count()
    total_sortants = CourrierSortant.query.count()
    entrants_traites = CourrierEntrant.query.filter_by(statut='traité').count()
    sortants_envoyes = CourrierSortant.query.filter_by(statut='envoyé').count()
    urgents = CourrierEntrant.query.filter_by(priorite='urgent').count()
    
    # Statistiques par catégorie
    categories = Categorie.query.all()
    stats_par_categorie = []
    for cat in categories:
        entrants = CourrierEntrant.query.filter_by(categorie_id=cat.id).count()
        sortants = CourrierSortant.query.filter_by(categorie_id=cat.id).count()
        stats_par_categorie.append({
            'nom': cat.nom,
            'entrants': entrants,
            'sortants': sortants,
            'balance': entrants - sortants,
            'couleur': cat.couleur
        })
    
    # Statistiques par utilisateur
    utilisateurs = Utilisateur.query.filter_by(actif=True).all()
    stats_par_utilisateur = []
    for user in utilisateurs:
        created = CourrierSortant.query.filter_by(createur_id=user.id).count()
        received = CourrierEntrant.query.filter_by(recepteur_id=user.id).count()
        stats_par_utilisateur.append({
            'nom': user.nom_complet(),
            'created': created,
            'received': received,
            'total': created + received
        })
    
    # Statistiques par expéditeur
    expediteurs = Expediteur.query.all()
    stats_expediteurs = []
    for exp in expediteurs:
        count = CourrierEntrant.query.filter_by(expediteur_id=exp.id).count()
        if count > 0:
            stats_expediteurs.append({'nom': exp.nom, 'count': count})
    stats_expediteurs.sort(key=lambda x: x['count'], reverse=True)
    
    # Statistiques par destinataire
    destinataires = Destinataire.query.all()
    stats_destinataires = []
    for dest in destinataires:
        count = CourrierSortant.query.filter_by(destinataire_id=dest.id).count()
        if count > 0:
            stats_destinataires.append({'nom': dest.nom, 'count': count})
    stats_destinataires.sort(key=lambda x: x['count'], reverse=True)
    
    # Balance générale
    balance = {
        'total_entrants': total_entrants,
        'total_sortants': total_sortants,
        'difference': total_entrants - total_sortants,
        'traites': entrants_traites,
        'envoyes': sortants_envoyes,
        'en_attente': total_entrants - entrants_traites,
        'urgents': urgents,
        'pourcentage_traite': (entrants_traites / total_entrants * 100) if total_entrants > 0 else 0,
        'pourcentage_envoye': (sortants_envoyes / total_sortants * 100) if total_sortants > 0 else 0
    }
    
    return render_template('statistiques.html',
                          balance=balance,
                          stats_par_categorie=stats_par_categorie,
                          stats_par_utilisateur=stats_par_utilisateur,
                          stats_expediteurs=stats_expediteurs,
                          stats_destinataires=stats_destinataires)

# ======================== HISTORIQUE ========================
@app.route('/historique')
@admin_required
def historique():
    """Afficher l'historique complet"""
    page = request.args.get('page', 1, type=int)
    recherche = request.args.get('recherche', '')
    
    query = Historique.query
    
    if recherche:
        query = query.filter(
            (Historique.action.ilike(f'%{recherche}%')) |
            (Historique.description.ilike(f'%{recherche}%')) |
            (Historique.utilisateur.ilike(f'%{recherche}%'))
        )
    
    historique = query.order_by(Historique.date_action.desc()).paginate(page=page, per_page=20)
    
    return render_template('historique.html', historique=historique, recherche=recherche)

# ======================== API JSON ========================
@app.route('/api/balance')
@login_required
def api_balance():
    """API pour obtenir la balance"""
    total_entrants = CourrierEntrant.query.count()
    total_sortants = CourrierSortant.query.count()
    entrants_traites = CourrierEntrant.query.filter_by(statut='traité').count()
    sortants_envoyes = CourrierSortant.query.filter_by(statut='envoyé').count()
    
    return jsonify({
        'entrants': total_entrants,
        'sortants': total_sortants,
        'difference': total_entrants - total_sortants,
        'traites': entrants_traites,
        'envoyes': sortants_envoyes,
        'en_attente': total_entrants - entrants_traites
    })

# ======================== GESTION DES ERREURS ========================
@app.errorhandler(404)
def page_not_found(error):
    return render_template('erreur.html', error='Page non trouvée (404)'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('erreur.html', error='Erreur serveur (500)'), 500

# ======================== INITIALISATION ========================
if __name__ == '__main__':
    init_db(app)
    app.run(debug=True, host='0.0.0.0', port=5000)
