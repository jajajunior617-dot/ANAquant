# ANAquant

> **Analyse Quantitative de la Bourse Régionale des Valeurs Mobilières (BRVM)**
> Pipeline Python de sélection d'actions basé sur la rentabilité, les dividendes, le risque et la liquidité.

---

## Objectif

ANAquant est un outil d'aide à la décision d'investissement sur la BRVM.
Il évalue chaque action selon cinq axes et génère un classement automatique basé sur une **stratégie mixte équilibrée** :

| Axe | Indicateur | Poids |
|---|---|---|
| Rentabilité | CAGR (croissance annuelle) | 30 % |
| Dividendes | Dividend Yield | 25 % |
| Risque maîtrisé | Faible Volatilité | 20 % |
| Performance/Risque | Ratio de Sharpe | 15 % |
| Liquidité | Volume moyen 30 jours | 10 % |

---

## Structure du projet

```
ANAquant/
├── .env.example          # Modèle de configuration (à copier en .env)
├── requirements.txt      # Dépendances Python
├── conftest.py           # Configuration pytest
├── pytest.ini            # Paramètres pytest
├── clean.py              # Nettoyage des caches de développement
│
├── data/
│   ├── raw/              # Fichiers CSV des cours historiques BRVM (générés par le scraper)
│   └── processed/        # Graphiques et données transformées
│
├── doc/                  # Documentation projet (plan, tâches, walkthrough)
│
├── notebooks/
│   └── 01_brvm_analysis.ipynb   # Tableau de bord interactif (Jupyter)
│
├── src/
│   ├── data/
│   │   ├── brvm_loader.py       # Chargement données (CSV réels ou simulation GBM)
│   │   └── brvm_scraper.py      # Scraper Sika Finance (données réelles BRVM)
│   ├── models/
│   │   └── metrics.py           # Indicateurs financiers (CAGR, Sharpe, Drawdown…)
│   ├── strategies/
│   │   └── scoring.py           # Screener multicritères (stratégie mixte)
│   ├── backtest/
│   │   └── engine.py            # Moteur de backtesting vectorisé (equal-weight)
│   └── utils/
│       ├── config.py            # Configuration et variables d'environnement
│       └── logger.py            # Système de journalisation coloré
│
├── sql/                  # Scripts SQL (connexion PostgreSQL optionnelle)
├── logs/                 # Journaux d'exécution générés automatiquement
└── tests/
    ├── test_metrics.py   # Tests unitaires des indicateurs financiers (pytest)
    ├── test_config.py    # Diagnostic de la configuration
    └── test_env.py       # Smoke test de l'environnement
```

---

## Démarrage rapide

### 1. Configurer l'environnement

```powershell
# Cloner ou télécharger le projet, puis :
py -3.12 -m venv ana_env
.\ana_env\Scripts\activate
pip install -r requirements.txt
```

### 2. Configurer les variables d'environnement

```powershell
Copy-Item .env.example .env
# Éditer .env avec vos propres clés API si besoin
```

### 3. Récupérer les données réelles BRVM

```powershell
# Scrape Sika Finance (~64 jours par ticker, sauvegarde dans data/raw/)
python -c "from src.data.brvm_scraper import scrape_all_tickers; scrape_all_tickers()"
```

> Sans données CSV, le pipeline bascule automatiquement sur une simulation GBM reproductible.

### 4. Lancer l'analyse interactive

```powershell
jupyter lab notebooks/01_brvm_analysis.ipynb
```

### 5. Lancer le backtesting en script

```python
from src.data.brvm_loader import get_historical_data, get_all_tickers
from src.strategies.scoring import evaluate_stock, score_and_rank_stocks
from src.backtest.engine import run_backtest

tickers = get_all_tickers()
prices  = {t: get_historical_data(t) for t in tickers}
metrics = [evaluate_stock(t, prices[t]) for t in tickers]
ranked  = score_and_rank_stocks(metrics)
print(ranked[['Ticker', 'Nom', 'Score_Global', 'CAGR', 'Sharpe_Ratio']])
```

---

## Actions suivies (Univers BRVM)

| Ticker | Nom | Secteur | Pays |
|---|---|---|---|
| SNTS.SN | Sonatel | Télécommunications | Sénégal |
| SGBC.CI | SGBCI | Finance | Côte d'Ivoire |
| CIEC.CI | CIE CI | Énergie | Côte d'Ivoire |
| NSBC.CI | NSIA Banque | Finance | Côte d'Ivoire |
| BOAS.SN | BOA Sénégal | Finance | Sénégal |
| SCRC.CI | Sucrivoire | Agriculture | Côte d'Ivoire |
| ORAC.CI | Orange CI | Télécommunications | Côte d'Ivoire |
| PALC.CI | PalmCI | Agriculture | Côte d'Ivoire |

---

## Tests

```powershell
# Tests unitaires (11 tests — métriques financières)
pytest

# Diagnostic de la configuration
python tests/test_config.py
```

---

## Source de données

Les données de marché proviennent de **[Sika Finance](https://www.sikafinance.com)**, source de référence non officielle pour la BRVM.
Le scraper récupère ~64 jours de données réelles par ticker. Pour un historique multi-années, une solution avec Selenium est envisagée.

---

*Projet développé en Python 3.12 — Environnement virtuel : `ana_env/`*
