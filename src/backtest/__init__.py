"""Package src.backtest — Moteur de backtesting des stratégies de trading BRVM."""
from src.backtest.engine import run_backtest, BacktestResult

__all__ = ["run_backtest", "BacktestResult"]
