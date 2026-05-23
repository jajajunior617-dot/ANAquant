"""
Module de scoring et de classement des actions BRVM.

Stratégies disponibles :
  - 'balanced'  : Stratégie Mixte — compromis optimal entre Croissance,
                  Dividendes et Maîtrise du Risque.
                  Poids : 30 % Croissance | 30 % Dividende |
                          20 % Risque maîtrisé | 20 % Sharpe

Note : Le scoring utilise une normalisation Min-Max (0→1) sur l'ensemble
de l'univers pour que les poids soient comparables.
"""

import pandas as pd

from src.data.brvm_loader import get_dividend_yield, get_ticker_info
from src.models.metrics import (
    calculate_average_volume,
    calculate_cagr,
    calculate_max_drawdown,
    calculate_sharpe_ratio,
    calculate_volatility,
)
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

# Poids de la stratégie MIXTE / ÉQUILIBRÉE
# 30% Croissance | 25% Dividende | 20% Risque | 15% Sharpe | 10% Liquidité
BALANCED_WEIGHTS: dict[str, float] = {
    "Score_Croissance": 0.30,
    "Score_Dividende":  0.25,
    "Score_Risque":     0.20,
    "Score_Sharpe":     0.15,
    "Score_Liquidite":  0.10,
}


def _normalize(series: pd.Series) -> pd.Series:
    """Normalisation Min-Max sur [0, 1]. Robuste aux séries constantes."""
    rng = series.max() - series.min()
    if rng == 0:
        return pd.Series([0.5] * len(series), index=series.index)
    return (series - series.min()) / rng


def evaluate_stock(ticker: str, df: pd.DataFrame) -> dict:
    """
    Calcule l'ensemble des métriques financières d'une action BRVM.

    Args:
        ticker: Code du titre (ex: 'SNTS.SN').
        df:     DataFrame OHLCV du titre.

    Returns:
        Dictionnaire contenant les métriques clés, ou {} si le DataFrame est vide.
    """
    if df.empty:
        logger.warning("DataFrame vide pour %s — évaluation ignorée.", ticker)
        return {}

    info = get_ticker_info(ticker)

    metrics = {
        "Ticker":         ticker,
        "Nom":            info.get("name", ticker),
        "Secteur":        info.get("sector", "N/A"),
        "Pays":           info.get("country", "N/A"),
        "CAGR":           calculate_cagr(df),
        "Volatility":     calculate_volatility(df),
        "Max_Drawdown":   calculate_max_drawdown(df),
        "Sharpe_Ratio":   calculate_sharpe_ratio(df),
        "Volume_30d":     calculate_average_volume(df, window=30),
        "Dividend_Yield": get_dividend_yield(ticker),
    }

    logger.debug(
        "%s | CAGR=%.2f%% | Vol=%.2f%% | Sharpe=%.2f | Div=%.2f%%",
        ticker,
        metrics["CAGR"] * 100,
        metrics["Volatility"] * 100,
        metrics["Sharpe_Ratio"],
        metrics["Dividend_Yield"] * 100,
    )
    return metrics


def score_and_rank_stocks(
    metrics_list: list[dict],
    strategy: str = "balanced",
) -> pd.DataFrame:
    """
    Applique une stratégie de notation multicritères et retourne le classement.

    Stratégies supportées :
      - ``'balanced'`` : 30 % Croissance | 30 % Dividende |
                         20 % Risque maîtrisé | 20 % Ratio de Sharpe

    Args:
        metrics_list: Liste de dictionnaires produits par ``evaluate_stock``.
        strategy:     Identifiant de la stratégie (défaut: 'balanced').

    Returns:
        DataFrame trié par Score_Global décroissant avec métriques formatées.
    """
    df = pd.DataFrame([m for m in metrics_list if m])

    if df.empty:
        logger.error("Aucune métrique valide pour le scoring.")
        return df

    # ── Normalisation ──────────────────────────────────────────────────────────
    df["Score_Croissance"] = _normalize(df["CAGR"])
    df["Score_Dividende"]  = _normalize(df["Dividend_Yield"])
    df["Score_Risque"]     = 1 - _normalize(df["Volatility"])  # moins de risque = meilleur
    df["Score_Sharpe"]     = _normalize(df["Sharpe_Ratio"])
    df["Score_Liquidite"]  = _normalize(df["Volume_30d"])      # plus de volume = meilleure liquidité

    # ── Calcul du score global ─────────────────────────────────────────────────
    if strategy == "balanced":
        weights = BALANCED_WEIGHTS
    else:
        logger.warning("Stratégie '%s' inconnue. Utilisation de 'balanced'.", strategy)
        weights = BALANCED_WEIGHTS

    df["Score_Global"] = sum(
        w * df[col] for col, w in weights.items()
    ) * 100  # note sur 100

    df = df.sort_values("Score_Global", ascending=False).reset_index(drop=True)
    df.index += 1  # classement commence à 1

    # ── Formatage lisible ──────────────────────────────────────────────────────
    df_display = df.copy()
    for pct_col in ["CAGR", "Volatility", "Max_Drawdown", "Dividend_Yield"]:
        df_display[pct_col] = df_display[pct_col].map(lambda x: f"{x:.2%}")
    df_display["Sharpe_Ratio"]  = df_display["Sharpe_Ratio"].map(lambda x: f"{x:.2f}")
    df_display["Volume_30d"]    = df_display["Volume_30d"].map(lambda x: f"{x:,.0f}")
    df_display["Score_Liquidite"] = df_display["Score_Liquidite"].map(lambda x: round(x, 3))
    df_display["Score_Global"]  = df_display["Score_Global"].map(lambda x: round(x, 1))

    logger.info(
        "Classement BRVM (%s) — %d valeurs analysées.", strategy, len(df_display)
    )
    return df_display
