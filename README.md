# Gestion Courriers

## Description

Application web complète pour la gestion et le suivi des courriers entrants et sortants. Développée avec **Flask**, **SQLite** et **Bootstrap 5**.

### Fonctionnalités principales

✅ **Gestion des courriers entrants**
- Ajouter, modifier, supprimer des courriers entrants
- Enregistrement : numéro, date d'entrée, expéditeur, désignation, observations

✅ **Gestion des courriers sortants**
- Ajouter, modifier, supprimer des courriers sortants
- Enregistrement : numéro, date du courrier, destinataire, désignation, observations

✅ **Recherche avancée**
- Recherche par numéro de courrier
- Recherche par expéditeur/destinataire
- Recherche par désignation
- Filtrage par type (entrants/sortants/tous)

✅ **Tableau de bord**
- Statistiques globales
- Derniers courriers ajoutés
- Vue d'ensemble rapide

✅ **Interface intuitive**
- Design responsive avec Bootstrap 5
- Navigation facile
- Messagerie flash pour les actions

---

## Installation

### Prérequis
- Python 3.8+
- pip (gestionnaire de paquets Python)
- Git

### Étapes d'installation

1. **Cloner le repository**
```bash
git clone https://github.com/hmidou1969/gestion-courriers.git
cd gestion-courriers
```

2. **Créer un environnement virtuel**
```bash
python -m venv venv
```

3. **Activer l'environnement virtuel**

**Sur Linux/Mac :**
```bash
source venv/bin/activate
```

**Sur Windows :**
```bash
venv\Scripts\activate
```

4. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

5. **Initialiser la base de données**
```bash
python -c "from app import app; from database import init_db; init_db(app)"
```

6. **Lancer l'application**
```bash
python app.py
```

7. **Accéder à l'application**
- Ouvrez votre navigateur et allez à : `http://localhost:5000`

---

## Structure du projet

```
gestion-courriers/
├── app.py                      # Application Flask principale
├── database.py                 # Modèles SQLAlchemy
├── config.py                   # Configuration
├── requirements.txt            # Dépendances Python
├── courriers.db               # Base de données SQLite (créée automatiquement)
├── templates/
│   ├── base.html              # Template de base
│   ├── index.html             # Page d'accueil
│   ├── courriers_entrants.html
│   ├── courriers_sortants.html
│   ├── ajouter_entrant.html
│   ├── ajouter_sortant.html
│   ├── modifier_entrant.html
│   ├── modifier_sortant.html
│   ├── recherche.html
│   └── erreur.html
├── static/
│   ├── css/
│   │   └── style.css          # Styles personnalisés
│   └── js/
│       └── script.js          # Scripts JavaScript
└── README.md                   # Documentation
```

---

## Utilisation

### 1. Accueil
La page d'accueil affiche :
- Nombre total de courriers
- Nombre de courriers entrants
- Nombre de courriers sortants
- Derniers courriers ajoutés

### 2. Courriers Entrants
- **Consulter** : Liste tous les courriers entrants avec pagination
- **Ajouter** : Formulaire pour enregistrer un nouveau courrier
- **Modifier** : Éditer les informations d'un courrier existant
- **Supprimer** : Supprimer un courrier avec confirmation

### 3. Courriers Sortants
Mêmes fonctionnalités que les courriers entrants.

### 4. Recherche
- Tapez un terme de recherche
- Sélectionnez le type de courrier
- Les résultats s'affichent par catégorie

---

## Configuration

### Variables d'environnement
Créez un fichier `.env` à la racine du projet :

```env
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-here
```

### Base de données
La base de données SQLite est créée automatiquement au premier lancement. Elle se trouve dans le même répertoire que `app.py`.

---

## Déploiement en production

### 1. Changer la configuration
```python
# Dans app.py
app.config.from_object(config['production'])
```

### 2. Utiliser un serveur WSGI
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### 3. Avec Docker
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:app"]
```

---

## Fonctionnalités futures

- 📊 Rapports et statistiques avancées
- 📧 Notifications par email
- 👥 Gestion des utilisateurs et permissions
- 📄 Export en PDF/Excel
- 📱 Application mobile
- 🔐 Authentification deux facteurs
- 📎 Attachement de fichiers
- 🔍 Reconnaissance optique de caractères (OCR)

---

## Support et contribution

Pour toute question ou suggestion :
- 📧 Email : hmidou1969@gmail.com
- 🐛 Issues : [GitHub Issues](https://github.com/hmidou1969/gestion-courriers/issues)
- 🔀 Pull Requests : Bienvenues !

---

## Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

---

## Remerciements

- [Flask](https://flask.palletsprojects.com/) - Framework web Python
- [Bootstrap](https://getbootstrap.com/) - Framework CSS
- [SQLAlchemy](https://www.sqlalchemy.org/) - ORM Python

---

**Version :** 1.0.0  
**Dernière mise à jour :** 2024  
**Auteur :** hmidou1969
