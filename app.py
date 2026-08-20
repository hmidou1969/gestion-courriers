from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from database import db, CourrierEntrant, CourrierSortant, init_db
from config import config
from datetime import datetime
import os

# Initialiser l'application Flask
app = Flask(__name__)
app.config.from_object(config[os.environ.get('FLASK_ENV', 'development')])

# Initialiser la base de données
db.init_app(app)

with app.app_context():
    init_db(app)

# ================== ROUTES PRINCIPALES ==================

@app.route('/')
def index():
    """Page d'accueil avec statistiques"""
    total_entrants = CourrierEntrant.query.count()
    total_sortants = CourrierSortant.query.count()
    total_courriers = total_entrants + total_sortants
    
    # Derniers courriers
    derniers_entrants = CourrierEntrant.query.order_by(CourrierEntrant.date_entree.desc()).limit(5).all()
    derniers_sortants = CourrierSortant.query.order_by(CourrierSortant.date_courrier.desc()).limit(5).all()
    
    return render_template('index.html', 
                         total_entrants=total_entrants,
                         total_sortants=total_sortants,
                         total_courriers=total_courriers,
                         derniers_entrants=derniers_entrants,
                         derniers_sortants=derniers_sortants)

# ================== COURRIERS ENTRANTS ==================

@app.route('/courriers-entrants')
def courriers_entrants():
    """Liste tous les courriers entrants"""
    page = request.args.get('page', 1, type=int)
    courriers = CourrierEntrant.query.order_by(CourrierEntrant.date_entree.desc()).paginate(page=page, per_page=10)
    return render_template('courriers_entrants.html', courriers=courriers)

@app.route('/ajouter-entrant', methods=['GET', 'POST'])
def ajouter_entrant():
    """Ajouter un nouveau courrier entrant"""
    if request.method == 'POST':
        try:
            # Vérifier que le numéro n'existe pas déjà
            if CourrierEntrant.query.filter_by(numero_courrier=request.form['numero_courrier']).first():
                flash('Ce numéro de courrier existe déjà !', 'danger')
                return redirect(url_for('ajouter_entrant'))
            
            courrier = CourrierEntrant(
                numero_courrier=request.form['numero_courrier'],
                date_entree=datetime.strptime(request.form['date_entree'], '%Y-%m-%d').date(),
                expediteur=request.form['expediteur'],
                designation=request.form['designation'],
                observations=request.form.get('observations', '')
            )
            
            db.session.add(courrier)
            db.session.commit()
            
            flash(f'Courrier entrant {courrier.numero_courrier} ajouté avec succès !', 'success')
            return redirect(url_for('courriers_entrants'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur : {str(e)}', 'danger')
            return redirect(url_for('ajouter_entrant'))
    
    return render_template('ajouter_entrant.html')

@app.route('/modifier-entrant/<int:id>', methods=['GET', 'POST'])
def modifier_entrant(id):
    """Modifier un courrier entrant"""
    courrier = CourrierEntrant.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            courrier.numero_courrier = request.form['numero_courrier']
            courrier.date_entree = datetime.strptime(request.form['date_entree'], '%Y-%m-%d').date()
            courrier.expediteur = request.form['expediteur']
            courrier.designation = request.form['designation']
            courrier.observations = request.form.get('observations', '')
            
            db.session.commit()
            flash(f'Courrier {courrier.numero_courrier} modifié avec succès !', 'success')
            return redirect(url_for('courriers_entrants'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur : {str(e)}', 'danger')
    
    return render_template('modifier_entrant.html', courrier=courrier)

@app.route('/supprimer-entrant/<int:id>', methods=['POST'])
def supprimer_entrant(id):
    """Supprimer un courrier entrant"""
    courrier = CourrierEntrant.query.get_or_404(id)
    
    try:
        numero = courrier.numero_courrier
        db.session.delete(courrier)
        db.session.commit()
        flash(f'Courrier {numero} supprimé avec succès !', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur : {str(e)}', 'danger')
    
    return redirect(url_for('courriers_entrants'))

# ================== COURRIERS SORTANTS ==================

@app.route('/courriers-sortants')
def courriers_sortants():
    """Liste tous les courriers sortants"""
    page = request.args.get('page', 1, type=int)
    courriers = CourrierSortant.query.order_by(CourrierSortant.date_courrier.desc()).paginate(page=page, per_page=10)
    return render_template('courriers_sortants.html', courriers=courriers)

@app.route('/ajouter-sortant', methods=['GET', 'POST'])
def ajouter_sortant():
    """Ajouter un nouveau courrier sortant"""
    if request.method == 'POST':
        try:
            # Vérifier que le numéro n'existe pas déjà
            if CourrierSortant.query.filter_by(numero_courrier=request.form['numero_courrier']).first():
                flash('Ce numéro de courrier existe déjà !', 'danger')
                return redirect(url_for('ajouter_sortant'))
            
            courrier = CourrierSortant(
                numero_courrier=request.form['numero_courrier'],
                date_courrier=datetime.strptime(request.form['date_courrier'], '%Y-%m-%d').date(),
                destinataire=request.form['destinataire'],
                designation=request.form['designation'],
                observations=request.form.get('observations', '')
            )
            
            db.session.add(courrier)
            db.session.commit()
            
            flash(f'Courrier sortant {courrier.numero_courrier} ajouté avec succès !', 'success')
            return redirect(url_for('courriers_sortants'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur : {str(e)}', 'danger')
            return redirect(url_for('ajouter_sortant'))
    
    return render_template('ajouter_sortant.html')

@app.route('/modifier-sortant/<int:id>', methods=['GET', 'POST'])
def modifier_sortant(id):
    """Modifier un courrier sortant"""
    courrier = CourrierSortant.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            courrier.numero_courrier = request.form['numero_courrier']
            courrier.date_courrier = datetime.strptime(request.form['date_courrier'], '%Y-%m-%d').date()
            courrier.destinataire = request.form['destinataire']
            courrier.designation = request.form['designation']
            courrier.observations = request.form.get('observations', '')
            
            db.session.commit()
            flash(f'Courrier {courrier.numero_courrier} modifié avec succès !', 'success')
            return redirect(url_for('courriers_sortants'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur : {str(e)}', 'danger')
    
    return render_template('modifier_sortant.html', courrier=courrier)

@app.route('/supprimer-sortant/<int:id>', methods=['POST'])
def supprimer_sortant(id):
    """Supprimer un courrier sortant"""
    courrier = CourrierSortant.query.get_or_404(id)
    
    try:
        numero = courrier.numero_courrier
        db.session.delete(courrier)
        db.session.commit()
        flash(f'Courrier {numero} supprimé avec succès !', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur : {str(e)}', 'danger')
    
    return redirect(url_for('courriers_sortants'))

# ================== RECHERCHE ==================

@app.route('/recherche')
def recherche():
    """Rechercher des courriers"""
    query = request.args.get('q', '').strip()
    type_recherche = request.args.get('type', 'tous')
    resultats_entrants = []
    resultats_sortants = []
    
    if query:
        if type_recherche in ['tous', 'entrants']:
            resultats_entrants = CourrierEntrant.query.filter(
                db.or_(
                    CourrierEntrant.numero_courrier.ilike(f'%{query}%'),
                    CourrierEntrant.expediteur.ilike(f'%{query}%'),
                    CourrierEntrant.designation.ilike(f'%{query}%')
                )
            ).all()
        
        if type_recherche in ['tous', 'sortants']:
            resultats_sortants = CourrierSortant.query.filter(
                db.or_(
                    CourrierSortant.numero_courrier.ilike(f'%{query}%'),
                    CourrierSortant.destinataire.ilike(f'%{query}%'),
                    CourrierSortant.designation.ilike(f'%{query}%')
                )
            ).all()
    
    return render_template('recherche.html', 
                         query=query,
                         type_recherche=type_recherche,
                         resultats_entrants=resultats_entrants,
                         resultats_sortants=resultats_sortants)

# ================== GESTION DES ERREURS ==================

@app.errorhandler(404)
def page_non_trouvee(error):
    return render_template('erreur.html', code=404, message='Page non trouvée'), 404

@app.errorhandler(500)
def erreur_serveur(error):
    return render_template('erreur.html', code=500, message='Erreur serveur'), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
