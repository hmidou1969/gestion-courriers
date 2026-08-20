# Contribution à Gestion Courriers

Merci de votre intérêt pour contribuer à ce projet ! 🎉

## Code de conduite

Ce projet et tous les participants sont régis par notre [Code de Conduite](CODE_OF_CONDUCT.md). En participant, vous acceptez de respecter ce code.

## Comment contribuer ?

### Signaler un bug 🐛

1. Vérifiez d'abord que le bug n'a pas déjà été signalé dans les [Issues](https://github.com/hmidou1969/gestion-courriers/issues)
2. Si le bug est nouveau, créez une nouvelle issue avec :
   - Un titre descriptif
   - Une description détaillée du comportement observé
   - Les étapes pour reproduire le bug
   - Le comportement attendu
   - Votre environnement (OS, version Python, etc.)

### Suggérer une amélioration 💡

1. Vérifiez que l'amélioration n'a pas déjà été suggérée
2. Créez une nouvelle issue avec le label `enhancement`
3. Décrivez clairement votre idée et pourquoi elle serait utile

### Soumettre une Pull Request 📝

1. **Fork le repository**
   ```bash
   git clone https://github.com/votre-username/gestion-courriers.git
   cd gestion-courriers
   ```

2. **Créez une branche pour votre feature**
   ```bash
   git checkout -b feature/ma-nouvelle-feature
   ```

3. **Faites vos modifications**
   - Suivez le style de code existant
   - Écrivez des messages de commit clairs et descriptifs
   - Ajoutez des commentaires pour les parties complexes

4. **Testez vos modifications**
   ```bash
   python app.py
   ```

5. **Commitez vos changements**
   ```bash
   git commit -m "Ajouter: description de la fonctionnalité"
   ```

6. **Poussez vers votre fork**
   ```bash
   git push origin feature/ma-nouvelle-feature
   ```

7. **Ouvrez une Pull Request**
   - Décrivez clairement les changements
   - Référencez les issues pertinentes
   - Attendez la review

## Directives de développement

### Style de code

- Utilisez Python 3.8+
- Respectez [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Les noms de variables doivent être explicites
- Ajoutez des docstrings aux fonctions

### Structure des commits

```
Type: Description courte

Description détaillée si nécessaire.

Type peut être :
- Feat: Nouvelle fonctionnalité
- Fix: Correction de bug
- Docs: Modification de documentation
- Style: Formatage, pas de changement de logique
- Refactor: Réorganisation du code
- Test: Ajout ou modification de tests
```

Exemple :
```
Feat: Ajouter la fonction de recherche avancée

Permet aux utilisateurs de rechercher par date, expediteur et designation.
Utilise SQLAlchemy pour les requêtes optimisées.
```

### Branches

- `main` : Branche de production (stable)
- `develop` : Branche de développement
- `feature/*` : Branches pour les nouvelles fonctionnalités
- `fix/*` : Branches pour les corrections de bugs

## Configuration locale

```bash
# Cloner le fork
git clone https://github.com/votre-username/gestion-courriers.git
cd gestion-courriers

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate sur Windows

# Installer les dépendances
pip install -r requirements.txt

# Initialiser la base de données
python -c "from app import app; from database import init_db; init_db(app)"

# Lancer l'application
python app.py
```

## Processus de review

1. Une fois votre PR soumise, un mainteneur la reviendra
2. Des demandes de changement peuvent être faites
3. Apportez les changements et poussez-les
4. Une fois approuvée, votre PR sera fusionnée

## Conventions de nommage

### Fonctions
```python
def get_courrier_by_id(courrier_id):
    """Récupérer un courrier par son ID"""
    pass
```

### Classes
```python
class CourrierEntrant(db.Model):
    """Modèle pour les courriers entrants"""
    pass
```

### Variables
```python
monnaie_totale = 100.00
date_creation = datetime.now()
is_valid = True
```

## Documentation

- Mettez à jour le README si vous ajoutez une nouvelle fonctionnalité
- Documentez les fonctions avec des docstrings
- Ajoutez des commentaires pour les parties complexes

## Questions ?

- Consultez la [documentation](README.md)
- Ouvrez une issue pour discuter
- Envoyez un email à : hmidou1969@gmail.com

## Crédits

Tous les contributeurs seront crédités dans le README et dans le fichier CONTRIBUTORS.md

---

**Merci pour votre contribution ! 🙏**
