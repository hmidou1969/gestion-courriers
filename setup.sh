#!/bin/bash

# Script de configuration initiale

echo "====================================="
echo "Gestion Courriers - Installation"
echo "====================================="
echo ""

# Vérifier Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé"
    exit 1
fi

echo "✓ Python 3 trouvé"

# Créer l'environnement virtuel
if [ ! -d "venv" ]; then
    echo "📦 Création de l'environnement virtuel..."
    python3 -m venv venv
fi

# Activer l'environnement virtuel
echo "✓ Activation de l'environnement virtuel..."
source venv/bin/activate

# Installer les dépendances
echo "📥 Installation des dépendances..."
pip install -r requirements.txt

# Copier le fichier .env
if [ ! -f ".env" ]; then
    echo "⚙️  Création du fichier .env..."
    cp .env.example .env
fi

echo ""
echo "====================================="
echo "✅ Installation terminée !"
echo "====================================="
echo ""
echo "Pour démarrer l'application :"
echo "  1. source venv/bin/activate"
echo "  2. python app.py"
echo ""
echo "Accédez à : http://localhost:5000"
echo ""
