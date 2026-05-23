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

# Endpoint confirmé : retourne ~64 jours de données réelles (headers + tableau OHLCV)
# Pour un historique multi-années, Selenium serait nécessaire (données chargées via WS)
BASE_URL = "https://www.sikafinance.com/marches/historiques"

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
# Format Sika Finance : minuscule du pays (ex: SNTS.sn, CIEC.ci)
# ──────────────────────────────────────────────────────────────────────────────
TICKER_TO_SIKA: dict[str, str] = {
    "SNTS.SN": "SNTS.sn",
    "SGBC.CI": "SGBC.ci",
    "CIEC.CI": "CIEC.ci",
    "NSBC.CI": "NSBC.ci",
    "BOAS.SN": "BOAS.sn",
    "SCRC.CI": "SCRC.ci",
    "ORAC.CI": "ORAC.ci",
    "PALC.CI": "PALC.ci",
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
    Parse le tableau HTML de la page /marches/historiques/<code> de Sika Finance.

    Colonnes réelles confirmées :
      Date | Clôture | Plus bas | Plus haut | Ouverture | Volume Titres | Volume FCFA | Variation %

    Returns:
        DataFrame OHLCV indexé par Date, ou None si parsing échoue.
    """
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table")
    if table is None:
        logger.error("Aucun tableau trouvé dans la page Sika Finance pour %s.", ticker)
        return None

    try:
        rows = table.find_all("tr")
        headers_row = [th.get_text(strip=True) for th in rows[0].find_all(["th", "td"])]
        data = []
        for row in rows[1:]:
            cells = [td.get_text(strip=True) for td in row.find_all("td")]
            if cells:
                data.append(cells)
        df = pd.DataFrame(data, columns=headers_row)
    except Exception as exc:
        logger.error("Erreur parsing tableau HTML pour %s : %s", ticker, exc)
        return None

    # Renommage des colonnes Sika Finance → OHLCV standard
    rename = {
        "Date":           "Date",
        "Clôture":        "Close",
        "Plus bas":       "Low",
        "Plus haut":      "High",
        "Ouverture":      "Open",
        "Volume Titres":  "Volume",
    }
    df = df.rename(columns=rename)

    missing = [c for c in ["Date", "Open", "High", "Low", "Close", "Volume"] if c not in df.columns]
    if missing:
        logger.error("Colonnes manquantes pour %s : %s. Colonnes reçues : %s",
                     ticker, missing, df.columns.tolist())
        return None

    df = df[["Date", "Open", "High", "Low", "Close", "Volume"]].copy()

    # Nettoyage : espaces insécables (\xa0), virgules décimales, conversion numérique
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
    for col in ["Open", "High", "Low", "Close", "Volume"]:
        df[col] = pd.to_numeric(
            df[col].astype(str)
                   .str.replace("\xa0", "", regex=False)
                   .str.replace(" ", "", regex=False)
                   .str.replace(",", ".", regex=False),
            errors="coerce",
        )

    df = df.dropna().set_index("Date").sort_index()
    logger.info("Données récupérées pour %s : %d lignes.", ticker, len(df))
    return df


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
