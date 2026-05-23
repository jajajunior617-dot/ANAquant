"""Package src.data — Acquisition et chargement des données boursières BRVM."""
from src.data.brvm_loader import (
    get_historical_data,
    get_dividend_yield,
    get_all_tickers,
    get_ticker_info,
    generate_mock_data,
)

__all__ = [
    "get_historical_data",
    "get_dividend_yield",
    "get_all_tickers",
    "get_ticker_info",
    "generate_mock_data",
]
