.PHONY: help install run pipeline poller init-db clean test

help:
	@echo "Dubai Real Estate Intelligence - Commandes disponibles :"
	@echo ""
	@echo "  make install    - Installer les dépendances"
	@echo "  make run        - Lancer Streamlit"
	@echo "  make pipeline   - Exécuter le pipeline quotidien"
	@echo "  make poller     - Démarrer le poller temps réel"
	@echo "  make init-db    - Initialiser la base de données"
	@echo "  make clean      - Nettoyer les fichiers temporaires"
	@echo "  make test       - Tester le système"
	@echo ""

install:
	@echo "📦 Installation des dépendances..."
	python3 -m venv venv
	. venv/bin/activate && pip install --upgrade pip
	. venv/bin/activate && pip install -r requirements.txt
	@echo "✅ Installation terminée"

run:
	@echo "🚀 Lancement de Streamlit..."
	. venv/bin/activate && streamlit run app.py

pipeline:
	@echo "🔄 Exécution du pipeline quotidien..."
	. venv/bin/activate && python jobs/daily_run.py

poller:
	@echo "⏰ Démarrage du poller temps réel..."
	. venv/bin/activate && python realtime/poller.py

init-db:
	@echo "🔧 Initialisation de la base de données..."
	createdb dubai_real_estate || true
	@echo "✅ Base créée (ou déjà existante)"
	@echo "⚠️  Allez dans Streamlit > Admin > Initialiser le schéma DB"

clean:
	@echo "🧹 Nettoyage..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Nettoyage terminé"

test:
	@echo "🧪 Test du système..."
	@echo "1. Vérification Python..."
	@python3 --version
	@echo "2. Vérification PostgreSQL..."
	@psql --version || echo "⚠️  PostgreSQL non trouvé"
	@echo "3. Vérification .env..."
	@test -f .env && echo "✅ .env trouvé" || echo "⚠️  .env manquant"
	@echo "4. Vérification venv..."
	@test -d venv && echo "✅ venv trouvé" || echo "⚠️  venv manquant (run: make install)"
	@echo ""
	@echo "✅ Tests terminés"
