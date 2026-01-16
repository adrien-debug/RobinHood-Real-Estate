#!/bin/bash

# ====================================================================
# DUBAI REAL ESTATE INTELLIGENCE - Démarrage rapide
# ====================================================================

echo "🏢 Dubai Real Estate Intelligence"
echo "=================================="
echo ""

# Vérifier Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 non trouvé. Installez Python 3.11+"
    exit 1
fi

echo "✅ Python trouvé: $(python3 --version)"

# Vérifier PostgreSQL
if ! command -v psql &> /dev/null; then
    echo "⚠️  PostgreSQL non trouvé. Assurez-vous qu'il est installé."
fi

# Vérifier .env
if [ ! -f .env ]; then
    echo "⚠️  Fichier .env non trouvé"
    echo "📝 Copie de env.example vers .env..."
    cp env.example .env
    echo "✅ Fichier .env créé. Éditez-le avec vos clés API."
    echo ""
    echo "Variables à configurer :"
    echo "  - DATABASE_URL"
    echo "  - OPENAI_API_KEY"
    echo "  - DLD_API_KEY (optionnel pour test)"
    echo ""
    read -p "Appuyez sur Entrée pour continuer..."
fi

# Vérifier venv
if [ ! -d "venv" ]; then
    echo "📦 Création de l'environnement virtuel..."
    python3 -m venv venv
    echo "✅ Environnement virtuel créé"
fi

# Activer venv
echo "🔄 Activation de l'environnement virtuel..."
source venv/bin/activate

# Installer dépendances
echo "📦 Installation des dépendances..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "✅ Dépendances installées"

# Créer dossier logs
mkdir -p logs
echo "✅ Dossier logs créé"

echo ""
echo "=================================="
echo "🚀 Prêt à démarrer !"
echo "=================================="
echo ""
echo "Commandes disponibles :"
echo ""
echo "  1. Lancer Streamlit :"
echo "     streamlit run app.py"
echo ""
echo "  2. Initialiser la base (première fois) :"
echo "     Aller dans Streamlit > Admin > Initialiser le schéma DB"
echo ""
echo "  3. Exécuter le pipeline quotidien :"
echo "     python jobs/daily_run.py"
echo ""
echo "  4. Démarrer le poller temps réel :"
echo "     python realtime/poller.py"
echo ""
echo "=================================="
echo ""

# Proposer de lancer Streamlit
read -p "Lancer Streamlit maintenant ? (o/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Oo]$ ]]; then
    echo "🚀 Lancement de Streamlit..."
    streamlit run app.py
fi
