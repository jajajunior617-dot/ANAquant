"""
Moteur de backtesting vectorisé pour les stratégies BRVM.

Approche : backtesting vectorisé pur pandas/numpy.
  - Pas de boucle jour par jour → performant sur 5 ans de données.
  - Rebalancement périodique (mensuel par défaut) sur le portefeuille top-N.
  - Métriques de performance : rendement total, CAGR, Sharpe, Max Drawdown.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.models.metrics import (
    calculate_cagr,
    calculate_max_drawdown,
    calculate_sharpe_ratio,
    UEMOA_RISK_FREE_RATE,
    TRADING_DAYS_PER_YEAR,
)
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# Résultat de backtest
# ──────────────────────────────────────────────────────────────────────────────

class BacktestResult:
    """Conteneur des résultats d'un backtest."""

    def __init__(self, equity_curve: pd.Series, trades: pd.DataFrame):
        self.equity_curve = equity_curve  # valeur du portefeuille indexée par Date
        self.trades       = trades        # journal des transactions

    # Métriques dérivées de la courbe de valeur
    @property
    def total_return(self) -> float:
        if len(self.equity_curve) < 2:
            return 0.0
        return float(self.equity_curve.iloc[-1] / self.equity_curve.iloc[0] - 1)

    @property
    def cagr(self) -> float:
        df = self.equity_curve.rename("Close").to_frame()
        return calculate_cagr(df)

    @property
    def max_drawdown(self) -> float:
        df = self.equity_curve.rename("Close").to_frame()
        return calculate_max_drawdown(df)

    @property
    def sharpe(self) -> float:
        df = self.equity_curve.rename("Close").to_frame()
        return calculate_sharpe_ratio(df, risk_free_rate=UEMOA_RISK_FREE_RATE)

    @property
    def volatility(self) -> float:
        log_rets = np.log(self.equity_curve / self.equity_curve.shift(1)).dropna()
        return float(log_rets.std() * np.sqrt(TRADING_DAYS_PER_YEAR))

    def summary(self) -> dict:
        return {
            "Rendement_Total":  f"{self.total_return:.2%}",
            "CAGR":             f"{self.cagr:.2%}",
            "Volatilite":       f"{self.volatility:.2%}",
            "Max_Drawdown":     f"{self.max_drawdown:.2%}",
            "Sharpe":           f"{self.sharpe:.2f}",
            "Nb_Transactions":  len(self.trades),
        }


# ──────────────────────────────────────────────────────────────────────────────
# Moteur de backtesting
# ──────────────────────────────────────────────────────────────────────────────

def run_backtest(
    prices: dict[str, pd.DataFrame],
    scores: dict[str, float],
    top_n: int = 3,
    initial_capital: float = 1_000_000.0,
    rebalance_freq: str = "ME",
) -> BacktestResult:
    """
    Backtest vectorisé d'une stratégie de portefeuille equal-weight top-N.

    Args:
        prices:          Dict {ticker: DataFrame OHLCV} pour chaque titre.
        scores:          Dict {ticker: score_global} issu du screener.
        top_n:           Nombre de titres à conserver dans le portefeuille.
        initial_capital: Capital de départ en FCFA (défaut : 1 000 000).
        rebalance_freq:  Fréquence de rebalancement pandas ('ME'=mois, 'QE'=trimestre).

    Returns:
        BacktestResult contenant la courbe de valeur et le journal des trades.
    """
    # Sélection des top-N titres par score
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    selected = [ticker for ticker, _ in ranked[:top_n]]
    logger.info("Portefeuille backtest — top %d : %s", top_n, selected)

    # Construire la matrice de prix Close, alignée sur l'intersection des dates
    close_frames = {}
    for ticker in selected:
        if ticker in prices and not prices[ticker].empty:
            close_frames[ticker] = prices[ticker]["Close"]

    if not close_frames:
        logger.error("Aucune donnée de prix disponible pour le backtest.")
        return BacktestResult(pd.Series(dtype=float), pd.DataFrame())

    close = pd.DataFrame(close_frames).dropna()

    if close.empty:
        logger.error("Intersection de dates vide entre les tickers sélectionnés.")
        return BacktestResult(pd.Series(dtype=float), pd.DataFrame())

    # Rendements journaliers
    daily_returns = close.pct_change().fillna(0.0)

    # Dates de rebalancement (fin de période)
    rebalance_dates = pd.date_range(
        start=close.index[0], end=close.index[-1], freq=rebalance_freq
    )

    # Poids equal-weight (rééquilibré à chaque période)
    n_assets = len(close.columns)
    weight   = 1.0 / n_assets

    equity  = pd.Series(index=close.index, dtype=float)
    capital = initial_capital
    trades  = []

    # Allocation initiale
    shares: dict[str, float] = {}
    entry_prices: dict[str, float] = {}

    current_prices = close.iloc[0]
    for ticker in close.columns:
        allocated    = capital * weight
        shares[ticker]       = allocated / current_prices[ticker]
        entry_prices[ticker] = current_prices[ticker]
        trades.append({
            "Date": close.index[0],
            "Ticker": ticker,
            "Action": "BUY",
            "Prix": round(current_prices[ticker], 2),
            "Quantite": round(shares[ticker], 4),
        })

    rebal_set = set(rebalance_dates.normalize())

    for date, row in close.iterrows():
        # Valeur du portefeuille à la date courante
        portfolio_value = sum(shares[t] * row[t] for t in close.columns)
        equity[date] = portfolio_value

        # Rebalancement si date cible
        if pd.Timestamp(date).normalize() in rebal_set:
            for ticker in close.columns:
                target_value = portfolio_value * weight
                new_shares   = target_value / row[ticker]
                diff         = new_shares - shares[ticker]
                if abs(diff) > 0.001:
                    trades.append({
                        "Date":     date,
                        "Ticker":   ticker,
                        "Action":   "BUY" if diff > 0 else "SELL",
                        "Prix":     round(float(row[ticker]), 2),
                        "Quantite": round(abs(diff), 4),
                    })
                shares[ticker] = new_shares

    trades_df = pd.DataFrame(trades)
    logger.info(
        "Backtest terminé — Rendement total : %.2f%% | Sharpe : %.2f",
        BacktestResult(equity, trades_df).total_return * 100,
        BacktestResult(equity, trades_df).sharpe,
    )
    return BacktestResult(equity, trades_df)
