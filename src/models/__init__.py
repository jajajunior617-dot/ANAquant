"""Package src.models — Calcul des indicateurs financiers quantitatifs."""
from src.models.metrics import (
    calculate_cagr,
    calculate_volatility,
    calculate_max_drawdown,
    calculate_sharpe_ratio,
    calculate_average_volume,
    UEMOA_RISK_FREE_RATE,
    TRADING_DAYS_PER_YEAR,
)

__all__ = [
    "calculate_cagr",
    "calculate_volatility",
    "calculate_max_drawdown",
    "calculate_sharpe_ratio",
    "calculate_average_volume",
    "UEMOA_RISK_FREE_RATE",
    "TRADING_DAYS_PER_YEAR",
]
