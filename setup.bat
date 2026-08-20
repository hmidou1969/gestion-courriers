@echo off
REM Script de configuration pour Windows

echo ====================================="
echo Gestion Courriers - Installation
echo ====================================="
echo.

REM Vérifier Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python n'est pas installé
    exit /b 1
)

echo ✓ Python trouvé

REM Créer l'environnement virtuel
if not exist "venv" (
    echo 📦 Création de l'environnement virtuel...
    python -m venv venv
)

REM Activer l'environnement virtuel
echo ✓ Activation de l'environnement virtuel...
call venv\Scripts\activate.bat

REM Installer les dépendances
echo 📥 Installation des dépendances...
pip install -r requirements.txt

REM Copier le fichier .env
if not exist ".env" (
    echo ⚙️  Création du fichier .env...
    copy .env.example .env
)

echo.
echo ====================================="
echo ✅ Installation terminée !
echo ====================================="
echo.
echo Pour démarrer l'application :
echo   1. venv\Scripts\activate.bat
echo   2. python app.py
echo.
echo Accédez à : http://localhost:5000
echo.
pause
