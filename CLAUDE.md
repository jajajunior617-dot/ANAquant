# ANAquant — Contexte pour Claude Code

## Présentation

Pipeline Python 3.12 d'aide à la décision d'investissement sur la **BRVM**
(Bourse Régionale des Valeurs Mobilières — 8 pays UEMOA, zone franc CFA).
Screener multicritères + backtesting vectorisé sur 8 actions cotées.

---

## Commandes essentielles

```powershell
# Activer l'environnement virtuel
.\ana_env\Scripts\activate

# Lancer les tests
pytest                                      # 11 tests unitaires

# Récupérer les données réelles (Sika Finance)
python -c "from src.data.brvm_scraper import scrape_all_tickers; scrape_all_tickers()"

# Diagnostic de configuration
python tests/test_config.py

# Nettoyer les caches (__pycache__, .pytest_cache…)
python clean.py

# Lancer JupyterLab
jupyter lab notebooks/01_brvm_analysis.ipynb
```

---

## Architecture

```
src/
├── data/
│   ├── brvm_loader.py     # get_historical_data(ticker) → DataFrame OHLCV
│   │                      #   1. Cherche data/raw/<TICKER>.csv
│   │                      #   2. Fallback : simulation GBM déterministe (seed=hash(ticker))
│   └── brvm_scraper.py    # scrape_all_tickers() → CSV dans data/raw/
│                          #   Source : sikafinance.com/marches/historiques/<ticker.pays>
│                          #   Donne ~64 jours de données réelles par ticker
├── models/
│   └── metrics.py         # calculate_cagr / _volatility / _max_drawdown / _sharpe_ratio / _average_volume
├── strategies/
│   └── scoring.py         # evaluate_stock(ticker, df) → dict métriques
│                          # score_and_rank_stocks(metrics_list) → DataFrame classé
├── backtest/
│   └── engine.py          # run_backtest(prices, scores, top_n) → BacktestResult
│                          #   Backtesting vectorisé equal-weight, rebalancement mensuel
└── utils/
    ├── config.py          # Settings singleton — chemins, clés API, DB URL
    └── logger.py          # Logger ANSI couleur + RotatingFileHandler
```

---

## Stratégie de scoring (balanced)

Normalisation Min-Max [0,1] sur l'univers entier, puis pondération :

| Score | Métrique source | Poids | Sens |
|---|---|---|---|
| Score_Croissance | CAGR | 30 % | ↑ plus = meilleur |
| Score_Dividende | Dividend_Yield | 25 % | ↑ plus = meilleur |
| Score_Risque | Volatility | 20 % | `1 - normalize` — moins = meilleur |
| Score_Sharpe | Sharpe_Ratio | 15 % | ↑ plus = meilleur |
| Score_Liquidite | Volume_30d | 10 % | ↑ plus = meilleur |

Score_Global = somme pondérée × 100 (note sur 100).

---

## Univers BRVM (8 actions)

| Ticker | Nom | Secteur | div_yield | vol simulée |
|---|---|---|---|---|
| SNTS.SN | Sonatel | Télécoms | 8 % | 1.0 % |
| SGBC.CI | SGBCI | Finance | 7 % | 1.5 % |
| CIEC.CI | CIE CI | Énergie | 5 % | 2.0 % |
| NSBC.CI | NSIA Banque | Finance | 6 % | 2.5 % |
| BOAS.SN | BOA Sénégal | Finance | 9 % | 1.8 % |
| SCRC.CI | Sucrivoire | Agriculture | 2 % | 3.0 % |
| ORAC.CI | Orange CI | Télécoms | 6 % | 1.2 % |
| PALC.CI | PalmCI | Agriculture | 4 % | 2.2 % |

---

## Source de données réelles

**Sika Finance** — `https://www.sikafinance.com`

- URL confirmée : `/marches/historiques/<TICKER.pays>` (ex: `SNTS.sn`, `CIEC.ci`)
- Colonnes HTML : `Date | Clôture | Plus bas | Plus haut | Ouverture | Volume Titres | Volume FCFA | Variation %`
- Limite : ~64 jours par requête (pas de pagination active côté serveur)
- L'historique multi-années nécessite Selenium (données chargées via WebSocket `/api/charting/`)
- Mapping ticker → code Sika dans `TICKER_TO_SIKA` dans `brvm_scraper.py`

---

## Environnement & dépendances

- Python 3.12.8 AMD64, venv `ana_env/`
- **Attention** : numpy et pandas avaient des `.pyd` manquants (installation corrompue OneDrive).
  Réparé en extrayant manuellement le wheel numpy depuis pip cache.
- VS Code doit pointer sur `.\ana_env\Scripts\python.exe` (pas Python 3.14 système)
- `cffi`/`curl_cffi` (dépendance yfinance) peut être corrompu — ne pas en dépendre pour l'instant

---

## Constantes financières BRVM/UEMOA

- **Taux sans risque** : 5.5 % (`UEMOA_RISK_FREE_RATE`) — OAT États zone UEMOA
- **Jours de bourse/an** : 252 (`TRADING_DAYS_PER_YEAR`)
- **Ticker par défaut** : `SNTS.SN` (Sonatel)
- **Benchmark** : `BRVMC` (BRVM Composite)

---

## Tests

```
tests/test_metrics.py   # 11 tests pytest — métriques financières
tests/test_config.py    # Diagnostic complet configuration (runner custom)
tests/test_env.py       # Smoke test environnement — EXCLU de pytest (import yfinance cassé)
```

`conftest.py` exclut `test_env.py` de la collection pytest.
`pytest.ini` → `testpaths = tests`.

---

## Points d'attention pour futures modifications

1. **Ajouter un ticker** : mettre à jour `BRVM_UNIVERSE` dans `brvm_loader.py` ET `TICKER_TO_SIKA` dans `brvm_scraper.py`
2. **Changer les poids** : modifier `BALANCED_WEIGHTS` dans `scoring.py` — la somme doit faire 1.0
3. **Nouvelle stratégie** : ajouter une branche dans `score_and_rank_stocks()` avec son propre dict de poids
4. **Backtesting** : `run_backtest()` prend un dict `{ticker: score}` — utiliser les valeurs numériques, pas les formatées
5. **Base de données** : fallback SQLite automatique si `DB_PASSWORD` vide — voir `config.py:DATABASE_URL`
6. **Données CSV** : format attendu — index `Date`, colonnes `Open High Low Close Volume`

---

## Git

- Branche : `main`
- Remote : `https://github.com/jajajunior617-dot/ANAquant.git`
- Les `data/raw/*.csv` sont gitignorés (à regénérer via le scraper)
- Les `logs/` sont gitignorés
