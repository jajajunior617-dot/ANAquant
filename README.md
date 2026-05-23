# ANAquant

> **Analyse Quantitative de la Bourse Régionale des Valeurs Mobilières (BRVM)**
> Pipeline Python de sélection d'actions basé sur la rentabilité, les dividendes, le risque et la liquidité.

---

## Objectif

ANAquant est un outil d'aide à la décision d'investissement sur la BRVM.
Il évalue chaque action selon quatre axes et génère un classement automatique basé sur une **stratégie mixte équilibrée** :

| Axe | Indicateur | Poids |
|---|---|---|
| Rentabilité | CAGR (croissance annuelle) | 30 % |
| Dividendes | Dividend Yield | 30 % |
| Risque maîtrisé | Faible Volatilité | 20 % |
| Performance/Risque | Ratio de Sharpe | 20 % |

---

## Structure du projet

```
ANAquant/
├── .env.example          # Modèle de configuration (à copier en .env)
├── requirements.txt      # Dépendances Python
├── clean.py              # Nettoyage des caches de développement
│
├── data/
│   ├── raw/              # Fichiers CSV des cours historiques BRVM
│   └── processed/        # Données transformées et enrichies
│
├── doc/                  # Documentation projet (plan, tâches, walkthrough)
│
├── notebooks/
│   └── 01_brvm_analysis.ipynb   # Tableau de bord interactif (Jupyter)
│
├── src/
│   ├── data/
│   │   └── brvm_loader.py       # Chargement données (CSV ou simulation GBM)
│   ├── models/
│   │   └── metrics.py           # Indicateurs financiers (CAGR, Sharpe, etc.)
│   ├── strategies/
│   │   └── scoring.py           # Screener multicritères (stratégie mixte)
│   ├── backtest/                 # (À développer) Moteur de backtesting
│   └── utils/
│       ├── config.py             # Configuration et variables d'environnement
│       └── logger.py             # Système de journalisation coloré
│
├── sql/                  # Scripts SQL (connexion PostgreSQL optionnelle)
├── logs/                 # Journaux d'exécution générés automatiquement
└── tests/
    ├── test_config.py    # Validation de la configuration
    └── test_env.py       # Validation des variables d'environnement
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

### 3. Lancer l'analyse interactive

```powershell
# Démarrer JupyterLab
jupyter lab notebooks/01_brvm_analysis.ipynb
```

### 4. Alimenter avec des données réelles (optionnel)

Déposez vos fichiers CSV dans `data/raw/` au format suivant :

```
Date,Open,High,Low,Close,Volume
2024-01-02,17000,17200,16900,17100,12000
...
```

Le nom du fichier doit correspondre au ticker : ex. `SNTS.SN.csv`.
Le système le détectera automatiquement et remplacera la simulation.

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

## Validation

```powershell
# Lancer les tests de configuration
python tests/test_config.py
```

---

*Projet développé en Python 3.12 — Environnement virtuel : `ana_env/`*
