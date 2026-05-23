"""
Module de calcul des indicateurs financiers quantitatifs pour la BRVM.

Indicateurs implémentés :
  - Rentabilité  : CAGR (Taux de Croissance Annuel Composé)
  - Risque       : Volatilité annualisée, Max Drawdown
  - Performance  : Ratio de Sharpe (taux sans risque UEMOA ~5 %)
  - Liquidité    : Volume moyen sur fenêtre glissante
"""

import numpy as np
import pandas as pd

# Taux sans risque de référence dans la zone UEMOA (OAT État moyen)
UEMOA_RISK_FREE_RATE: float = 0.055  # 5.5 %
TRADING_DAYS_PER_YEAR: int = 252


def calculate_cagr(
    df: pd.DataFrame,
    column: str = "Close",
    years: float | None = None,
) -> float:
    """
    Calcule le Taux de Croissance Annuel Composé (CAGR).

    Formula: CAGR = (End / Start) ^ (1 / n_years) - 1

    Args:
        df:     DataFrame OHLCV.
        column: Colonne de prix à utiliser (défaut: 'Close').
        years:  Durée en années. Si None, estimée via le nombre de jours de bourse.

    Returns:
        CAGR sous forme décimale (ex: 0.12 = +12 % par an). 0.0 si calcul impossible.
    """
    if df.empty or len(df) < 2:
        return 0.0

    start_val = df[column].iloc[0]
    end_val   = df[column].iloc[-1]

    if years is None:
        years = len(df) / TRADING_DAYS_PER_YEAR

    if years <= 0 or start_val <= 0:
        return 0.0

    return float((end_val / start_val) ** (1.0 / years) - 1)


def calculate_volatility(df: pd.DataFrame, column: str = "Close") -> float:
    """
    Calcule la volatilité annualisée à partir des log-rendements quotidiens.

    Formule : σ_annuelle = σ_journalière × √252

    Args:
        df:     DataFrame OHLCV.
        column: Colonne de prix à utiliser.

    Returns:
        Volatilité annualisée (ex: 0.20 = 20 %). 0.0 si calcul impossible.
    """
    if df.empty or len(df) < 2:
        return 0.0

    log_returns = np.log(df[column] / df[column].shift(1)).dropna()
    return float(log_returns.std() * np.sqrt(TRADING_DAYS_PER_YEAR))


def calculate_max_drawdown(df: pd.DataFrame, column: str = "Close") -> float:
    """
    Calcule le Maximum Drawdown : la perte maximale depuis un pic historique.

    Args:
        df:     DataFrame OHLCV.
        column: Colonne de prix à utiliser.

    Returns:
        Max Drawdown sous forme décimale négative (ex: -0.35 = -35 %).
    """
    if df.empty:
        return 0.0

    rolling_peak = df[column].cummax()
    drawdowns = (df[column] - rolling_peak) / rolling_peak
    return float(drawdowns.min())


def calculate_sharpe_ratio(
    df: pd.DataFrame,
    column: str = "Close",
    risk_free_rate: float = UEMOA_RISK_FREE_RATE,
) -> float:
    """
    Calcule le Ratio de Sharpe : rendement excédentaire par unité de risque.

    Formule : Sharpe = (CAGR - Rf) / Volatilité

    Le taux sans risque de référence est celui des OAT de la zone UEMOA (~5.5 %).

    Args:
        df:              DataFrame OHLCV.
        column:          Colonne de prix à utiliser.
        risk_free_rate:  Taux sans risque annuel (défaut : 5.5 %).

    Returns:
        Ratio de Sharpe. Un ratio > 1 est considéré comme bon.
    """
    cagr = calculate_cagr(df, column)
    vol  = calculate_volatility(df, column)

    if vol == 0:
        return 0.0

    return float((cagr - risk_free_rate) / vol)


def calculate_average_volume(df: pd.DataFrame, window: int = 30) -> float:
    """
    Calcule le volume moyen d'échange sur une fenêtre glissante (proxy de liquidité).

    Un volume moyen élevé indique qu'il est facile d'acheter / vendre le titre.

    Args:
        df:     DataFrame OHLCV (doit contenir une colonne 'Volume').
        window: Nombre de jours de bourse à considérer (défaut: 30 jours).

    Returns:
        Volume moyen en nombre de titres échangés.
    """
    if df.empty or "Volume" not in df.columns:
        return 0.0

    return float(df["Volume"].tail(window).mean())
