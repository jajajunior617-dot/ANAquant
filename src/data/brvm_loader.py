"""
Module de chargement et de simulation de données boursières pour la BRVM.

Stratégie d'acquisition :
  1. Si un fichier CSV historique existe dans data/, il est utilisé.
  2. Sinon, des données réalistes sont générées via un modèle de Brownian Motion.
"""

import numpy as np
import pandas as pd
from datetime import datetime
from pathlib import Path

from src.utils.config import settings
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

# Répertoire des données brutes
DATA_DIR = settings.RAW_DATA_DIR

# ──────────────────────────────────────────────────────────────────────────────
# Univers des actions BRVM suivies
# Sources de référence : Sika Finance (sikafinance.com), BRVM officielle
# ──────────────────────────────────────────────────────────────────────────────
BRVM_UNIVERSE: dict[str, dict] = {
    "SNTS.SN": {
        "name": "Sonatel",
        "country": "Sénégal",
        "sector": "Télécommunications",
        "start_price": 17_000,
        "vol": 0.010,
        "div_yield": 0.08,
    },
    "SGBC.CI": {
        "name": "SGBCI",
        "country": "Côte d'Ivoire",
        "sector": "Finance",
        "start_price": 16_000,
        "vol": 0.015,
        "div_yield": 0.07,
    },
    "CIEC.CI": {
        "name": "CIE CI",
        "country": "Côte d'Ivoire",
        "sector": "Énergie",
        "start_price": 2_000,
        "vol": 0.020,
        "div_yield": 0.05,
    },
    "NSBC.CI": {
        "name": "NSIA Banque",
        "country": "Côte d'Ivoire",
        "sector": "Finance",
        "start_price": 5_000,
        "vol": 0.025,
        "div_yield": 0.06,
    },
    "BOAS.SN": {
        "name": "BOA Sénégal",
        "country": "Sénégal",
        "sector": "Finance",
        "start_price": 3_000,
        "vol": 0.018,
        "div_yield": 0.09,
    },
    "SCRC.CI": {
        "name": "Sucrivoire",
        "country": "Côte d'Ivoire",
        "sector": "Agriculture",
        "start_price": 800,
        "vol": 0.030,
        "div_yield": 0.02,
    },
    "ORAC.CI": {
        "name": "Orange CI",
        "country": "Côte d'Ivoire",
        "sector": "Télécommunications",
        "start_price": 12_000,
        "vol": 0.012,
        "div_yield": 0.06,
    },
    "PALC.CI": {
        "name": "PalmCI",
        "country": "Côte d'Ivoire",
        "sector": "Agriculture",
        "start_price": 7_000,
        "vol": 0.022,
        "div_yield": 0.04,
    },
}


def generate_mock_data(
    ticker: str,
    start_date: str = "2020-01-01",
    end_date: str | None = None,
) -> pd.DataFrame:
    """
    Génère des données OHLCV réalistes pour un ticker BRVM (Geometric Brownian Motion).

    Utilisé comme fallback en l'absence de données CSV réelles.

    Args:
        ticker:     Code du titre (ex: 'SNTS.SN').
        start_date: Date de début de la série (format 'YYYY-MM-DD').
        end_date:   Date de fin (défaut : aujourd'hui).

    Returns:
        DataFrame avec colonnes Open, High, Low, Close, Volume, indexé par Date.
    """
    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")

    dates = pd.date_range(start=start_date, end=end_date, freq="B")
    n = len(dates)

    params = BRVM_UNIVERSE.get(
        ticker, {"start_price": 1_000, "vol": 0.020, "div_yield": 0.05}
    )
    start_price: float = params["start_price"]
    volatility: float = params["vol"]

    # Seed déterministe basé sur le ticker → reproductibilité garantie
    rng = np.random.default_rng(seed=abs(hash(ticker)) % (2**32 - 1))

    daily_rets = rng.normal(loc=0.0001, scale=volatility, size=n)
    close = start_price * np.exp(np.cumsum(daily_rets))

    noise_open = rng.uniform(-0.01, 0.01, n)
    noise_high = rng.uniform(0.00, 0.02, n)
    noise_low  = rng.uniform(0.00, 0.02, n)

    df = pd.DataFrame(
        {
            "Open":   close * (1 + noise_open),
            "High":   close * (1 + noise_high),
            "Low":    close * (1 - noise_low),
            "Close":  close,
            "Volume": rng.lognormal(mean=10, sigma=1, size=n).astype(int),
        },
        index=pd.Index(dates, name="Date"),
    )

    logger.debug("Données mock générées pour %s (%d jours)", ticker, n)
    return df


def get_historical_data(ticker: str) -> pd.DataFrame:
    """
    Charge les données historiques d'un titre.

    Ordre de priorité :
      1. Fichier CSV local ``data/raw/<TICKER>.csv``
      2. Simulation via Geometric Brownian Motion

    Args:
        ticker: Code du titre (ex: 'SNTS.SN').

    Returns:
        DataFrame OHLCV indexé par Date.
    """
    csv_path = DATA_DIR / f"{ticker}.csv"
    if csv_path.exists():
        logger.info("Chargement CSV pour %s depuis %s", ticker, csv_path)
        return pd.read_csv(csv_path, index_col="Date", parse_dates=True)

    logger.warning(
        "Aucun CSV trouvé pour %s — utilisation des données simulées.", ticker
    )
    return generate_mock_data(ticker)


def get_dividend_yield(ticker: str) -> float:
    """
    Retourne le rendement du dividende estimé pour un ticker BRVM.

    Args:
        ticker: Code du titre.

    Returns:
        Dividend Yield (ex: 0.08 = 8 %).
    """
    return BRVM_UNIVERSE.get(ticker, {}).get("div_yield", 0.05)


def get_all_tickers() -> list[str]:
    """Retourne la liste complète des tickers suivis dans l'univers BRVM."""
    return list(BRVM_UNIVERSE.keys())


def get_ticker_info(ticker: str) -> dict:
    """Retourne les métadonnées d'un titre (nom, pays, secteur)."""
    return BRVM_UNIVERSE.get(ticker, {})
