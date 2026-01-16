@echo off
REM ====================================================================
REM DUBAI REAL ESTATE INTELLIGENCE - Démarrage rapide (Windows)
REM ====================================================================

echo.
echo ========================================
echo Dubai Real Estate Intelligence
echo ========================================
echo.

REM Vérifier Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [X] Python non trouvé. Installez Python 3.11+
    pause
    exit /b 1
)

echo [OK] Python trouvé

REM Vérifier .env
if not exist .env (
    echo [!] Fichier .env non trouvé
    echo Copie de env.example vers .env...
    copy env.example .env
    echo [OK] Fichier .env créé. Éditez-le avec vos clés API.
    echo.
    echo Variables à configurer :
    echo   - DATABASE_URL
    echo   - OPENAI_API_KEY
    echo   - DLD_API_KEY (optionnel pour test)
    echo.
    pause
)

REM Vérifier venv
if not exist venv (
    echo Installation de l'environnement virtuel...
    python -m venv venv
    echo [OK] Environnement virtuel créé
)

REM Activer venv
echo Activation de l'environnement virtuel...
call venv\Scripts\activate.bat

REM Installer dépendances
echo Installation des dépendances...
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
echo [OK] Dépendances installées

REM Créer dossier logs
if not exist logs mkdir logs
echo [OK] Dossier logs créé

echo.
echo ========================================
echo Prêt à démarrer !
echo ========================================
echo.
echo Commandes disponibles :
echo.
echo   1. Lancer Streamlit :
echo      streamlit run app.py
echo.
echo   2. Initialiser la base (première fois) :
echo      Aller dans Streamlit ^> Admin ^> Initialiser le schéma DB
echo.
echo   3. Exécuter le pipeline quotidien :
echo      python jobs\daily_run.py
echo.
echo   4. Démarrer le poller temps réel :
echo      python realtime\poller.py
echo.
echo ========================================
echo.

REM Proposer de lancer Streamlit
set /p launch="Lancer Streamlit maintenant ? (o/n) "
if /i "%launch%"=="o" (
    echo Lancement de Streamlit...
    streamlit run app.py
)
