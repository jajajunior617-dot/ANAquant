# Plan d'Exécution : Analyse Quantitative BRVM

- `[x]` 1. **Préparation de l'environnement**
  - `[x]` Tenter l'installation du package `brvm` (Échec : package indisponible pour cette version de Python).
  - `[/]` Créer un scraper personnalisé pour Sika Finance ou la BRVM officielle.
  - `[ ]` Vérifier le fonctionnement et la fiabilité du package `brvm` avec un script de test.
- `[x]` 2. **Acquisition de Données (`src/data`)**
  - `[x]` Créer `src/data/brvm_loader.py` pour télécharger l'historique des cours et volumes.
- `[x]` 3. **Modélisation et Métriques (`src/models`)**
  - `[x]` Créer `src/models/metrics.py` pour calculer le rendement (CAGR).
  - `[x]` Ajouter le calcul du risque (Volatilité, Max Drawdown, Sharpe).
  - `[x]` Ajouter les indicateurs de Liquidité (Volume moyen) et de Dividendes.
- `[x]` 4. **Système de Notation (`src/strategies`)**
  - `[x]` Créer `src/strategies/scoring.py` basé sur une stratégie mixte (équilibre entre sécurité/dividendes et croissance).
- `[x]` 5. **Analyse Exploratoire (`notebooks`)**
  - `[x]` Construire le notebook `01_brvm_analysis.ipynb` rassemblant tous ces éléments dans un tableau de bord.
