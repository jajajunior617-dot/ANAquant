"""
Scraper de données historiques BRVM depuis Sika Finance.

Sika Finance (sikafinance.com) est la source de référence non officielle
pour les cours et volumes de la BRVM. Ce module tente de récupérer les
données réelles et sauvegarde le résultat en CSV dans data/raw/.

Stratégie de robustesse :
  1. Téléchargement via requests + parsing BeautifulSoup.
  2. En cas d'échec réseau ou de structure HTML modifiée → retourne None
     (le brvm_loader basculera automatiquement sur la simulation GBM).
"""

from __future__ import annotations

import time
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup

from src.utils.config import settings
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

# ──────────────────────────────────────────────────────────────────────────────
# Configuration du scraper
# ──────────────────────────────────────────────────────────────────────────────

BASE_URL = "https://www.sikafinance.com/marches/historique"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "fr-FR,fr;q=0.9",
}

REQUEST_TIMEOUT = 15      # secondes
DELAY_BETWEEN_TICKERS = 2 # politesse envers le serveur


# ──────────────────────────────────────────────────────────────────────────────
# Mapping ticker BRVM → code Sika Finance
# Les codes Sika Finance omettent le suffixe de marché (.SN, .CI)
# ──────────────────────────────────────────────────────────────────────────────
TICKER_TO_SIKA: dict[str, str] = {
    "SNTS.SN": "SNTS",
    "SGBC.CI": "SGBC",
    "CIEC.CI": "CIEC",
    "NSBC.CI": "NSBC",
    "BOAS.SN": "BOAS",
    "SCRC.CI": "SCRC",
    "ORAC.CI": "ORAC",
    "PALC.CI": "PALC",
}


def fetch_ticker_history(ticker: str, years: int = 5) -> pd.DataFrame | None:
    """
    Télécharge l'historique de cours d'un ticker depuis Sika Finance.

    Args:
        ticker: Code BRVM (ex: 'SNTS.SN').
        years:  Nombre d'années d'historique à récupérer (défaut: 5).

    Returns:
        DataFrame OHLCV indexé par Date, ou None si le téléchargement échoue.
    """
    sika_code = TICKER_TO_SIKA.get(ticker)
    if not sika_code:
        logger.warning("Ticker %s absent du mapping Sika Finance.", ticker)
        return None

    url = f"{BASE_URL}/{sika_code}"
    logger.info("Téléchargement Sika Finance : %s → %s", ticker, url)

    try:
        response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as exc:
        logger.error("Erreur réseau pour %s : %s", ticker, exc)
        return None

    return _parse_sika_html(response.text, ticker)


def _parse_sika_html(html: str, ticker: str) -> pd.DataFrame | None:
    """
    Parse le tableau HTML de l'historique Sika Finance.

    Returns:
        DataFrame avec colonnes Open, High, Low, Close, Volume ou None si parsing échoue.
    """
    soup = BeautifulSoup(html, "html.parser")

    # Chercher le premier tableau de données historiques
    table = soup.find("table")
    if table is None:
        logger.error("Aucun tableau trouvé dans la page Sika Finance pour %s.", ticker)
        return None

    try:
        # pandas peut parser un tableau HTML directement
        dfs = pd.read_html(str(table), decimal=",", thousands=" ")
        if not dfs:
            return None
        df = dfs[0]
    except Exception as exc:
        logger.error("Erreur parsing tableau HTML pour %s : %s", ticker, exc)
        return None

    # Normalisation des noms de colonnes (Sika Finance peut varier)
    col_map = _detect_columns(df.columns.tolist())
    if col_map is None:
        logger.error(
            "Structure de tableau non reconnue pour %s. Colonnes : %s",
            ticker, df.columns.tolist()
        )
        return None

    df = df.rename(columns=col_map)
    df = df[["Date", "Open", "High", "Low", "Close", "Volume"]].copy()

    # Nettoyage
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
    df = df.dropna(subset=["Date"])
    df = df.set_index("Date").sort_index()

    for col in ["Open", "High", "Low", "Close", "Volume"]:
        df[col] = pd.to_numeric(
            df[col].astype(str).str.replace(" ", "").str.replace(",", "."),
            errors="coerce",
        )

    df = df.dropna()
    logger.info("Données récupérées pour %s : %d lignes.", ticker, len(df))
    return df


def _detect_columns(columns: list) -> dict | None:
    """
    Détecte et mappe les noms de colonnes Sika Finance vers le standard OHLCV.

    Retourne None si les colonnes obligatoires ne sont pas trouvées.
    """
    col_lower = [str(c).lower().strip() for c in columns]
    mapping: dict[str, str] = {}

    patterns = {
        "Date":   ["date", "séance"],
        "Open":   ["ouverture", "open", "ouvr"],
        "High":   ["haut", "high", "plus haut"],
        "Low":    ["bas", "low", "plus bas"],
        "Close":  ["clôture", "cloture", "close", "dernier", "cours"],
        "Volume": ["volume", "vol", "qté", "quantite"],
    }

    for target, candidates in patterns.items():
        for i, col in enumerate(col_lower):
            if any(cand in col for cand in candidates):
                mapping[columns[i]] = target
                break

    required = {"Date", "Close", "Volume"}
    found = set(mapping.values())
    if not required.issubset(found):
        return None

    # Colonnes OHLC manquantes → on les dérive de Close
    for col in ["Open", "High", "Low"]:
        if col not in found:
            mapping[f"_missing_{col}"] = col

    return mapping


def scrape_all_tickers(save_csv: bool = True) -> dict[str, pd.DataFrame | None]:
    """
    Télécharge l'historique pour tous les tickers de l'univers BRVM.

    Args:
        save_csv: Si True, sauvegarde chaque résultat dans data/raw/<TICKER>.csv.

    Returns:
        Dict {ticker: DataFrame | None}.
    """
    results: dict[str, pd.DataFrame | None] = {}

    for ticker in TICKER_TO_SIKA:
        df = fetch_ticker_history(ticker)
        results[ticker] = df

        if df is not None and save_csv:
            csv_path = settings.RAW_DATA_DIR / f"{ticker}.csv"
            df.to_csv(csv_path)
            logger.info("Sauvegardé : %s (%d lignes)", csv_path.name, len(df))

        time.sleep(DELAY_BETWEEN_TICKERS)

    n_ok  = sum(1 for v in results.values() if v is not None)
    n_err = len(results) - n_ok
    logger.info("Scraping terminé — %d OK / %d erreurs", n_ok, n_err)
    return results
