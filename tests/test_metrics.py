"""
Tests unitaires pour le module src.models.metrics.

Vérifie le bon calcul des indicateurs financiers :
  - CAGR, Volatilité, Max Drawdown, Sharpe, Volume moyen
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Ajout de la racine du projet au sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.models.metrics import (
    calculate_cagr,
    calculate_volatility,
    calculate_max_drawdown,
    calculate_sharpe_ratio,
    calculate_average_volume,
    UEMOA_RISK_FREE_RATE,
)


# ──────────────────────────────────────────────────────────────────────────────
# Fixtures de test
# ──────────────────────────────────────────────────────────────────────────────

def _flat_df(price: float = 100.0, n: int = 252) -> pd.DataFrame:
    """Série de prix constants — aucun rendement, volatilité = 0."""
    index = pd.date_range("2023-01-01", periods=n, freq="B")
    return pd.DataFrame({"Close": [price] * n, "Volume": [10_000] * n}, index=index)


def _linear_df(start: float = 100.0, end: float = 200.0, n: int = 252) -> pd.DataFrame:
    """Série linéaire croissante de start à end."""
    prices = np.linspace(start, end, n)
    index = pd.date_range("2023-01-01", periods=n, freq="B")
    return pd.DataFrame({"Close": prices, "Volume": [5_000] * n}, index=index)


# ──────────────────────────────────────────────────────────────────────────────
# Tests
# ──────────────────────────────────────────────────────────────────────────────

def test_cagr_constant_series():
    """Un prix qui ne bouge pas doit produire un CAGR = 0."""
    df = _flat_df()
    assert calculate_cagr(df) == 0.0, "CAGR d'une série plate doit être 0"


def test_cagr_doubling():
    """Un doublement de prix en exactement 1 an → CAGR = 100 % (série exponentielle exacte)."""
    # Série exponentielle : price[t] = 100 * exp(log(2) * t/n)
    # Garantit end/start = 2.0 exactement, donc CAGR = (2)^(1/1) - 1 = 1.0
    n = 252
    t = np.arange(n)
    prices = 100.0 * np.exp(np.log(2) * t / (n - 1))
    index = pd.date_range("2023-01-01", periods=n, freq="B")
    df = pd.DataFrame({"Close": prices, "Volume": [5_000] * n}, index=index)
    cagr = calculate_cagr(df)
    assert abs(cagr - 1.0) < 0.001, f"CAGR attendu 100 %, obtenu {cagr:.4%}"


def test_cagr_empty():
    """DataFrame vide → CAGR = 0.0."""
    assert calculate_cagr(pd.DataFrame()) == 0.0


def test_volatility_constant():
    """Série de prix constants → volatilité = 0."""
    df = _flat_df()
    assert calculate_volatility(df) == 0.0, "Volatilité d'une série plate doit être 0"


def test_volatility_positive():
    """Série aléatoire → volatilité > 0."""
    rng = np.random.default_rng(42)
    prices = 100 * np.exp(np.cumsum(rng.normal(0, 0.01, 252)))
    index = pd.date_range("2023-01-01", periods=252, freq="B")
    df = pd.DataFrame({"Close": prices}, index=index)
    assert calculate_volatility(df) > 0.0


def test_max_drawdown_constant():
    """Aucune baisse → drawdown = 0."""
    df = _flat_df()
    assert calculate_max_drawdown(df) == 0.0


def test_max_drawdown_negative():
    """Série avec une baisse → max drawdown doit être négatif."""
    prices = [100, 120, 80, 90, 100]
    df = pd.DataFrame({"Close": prices}, index=pd.date_range("2023-01-01", periods=5, freq="B"))
    dd = calculate_max_drawdown(df)
    assert dd < 0.0, f"Max Drawdown doit être négatif, obtenu {dd:.2%}"
    assert abs(dd - (-1/3)) < 0.01, f"Attendu ~-33.3%, obtenu {dd:.2%}"


def test_sharpe_positive_above_rf():
    """Série très croissante → Sharpe > 0."""
    df = _linear_df(start=100, end=200)
    sharpe = calculate_sharpe_ratio(df, risk_free_rate=UEMOA_RISK_FREE_RATE)
    assert sharpe > 0.0, "Sharpe doit être positif pour une série haussière"


def test_sharpe_zero_volatility():
    """Volatilité nulle → Sharpe = 0 (protection contre division par 0)."""
    df = _flat_df()
    assert calculate_sharpe_ratio(df) == 0.0


def test_average_volume():
    """Volume moyen sur 30 jours doit correspondre à la moyenne des 30 dernières lignes."""
    df = _flat_df(n=100)
    avg = calculate_average_volume(df, window=30)
    assert avg == 10_000, f"Volume moyen attendu 10000, obtenu {avg}"


def test_average_volume_no_column():
    """DataFrame sans colonne Volume → retourne 0.0."""
    df = pd.DataFrame({"Close": [100, 110]}, index=pd.date_range("2023-01-01", periods=2, freq="B"))
    assert calculate_average_volume(df) == 0.0


# ──────────────────────────────────────────────────────────────────────────────
# Runner
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    tests = [
        test_cagr_constant_series,
        test_cagr_doubling,
        test_cagr_empty,
        test_volatility_constant,
        test_volatility_positive,
        test_max_drawdown_constant,
        test_max_drawdown_negative,
        test_sharpe_positive_above_rf,
        test_sharpe_zero_volatility,
        test_average_volume,
        test_average_volume_no_column,
    ]

    print("=" * 65)
    print("  TESTS UNITAIRES - src.models.metrics")
    print("=" * 65)

    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            print(f"  [PASS] {test.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"  [FAIL] {test.__name__} — {e}")
            failed += 1
        except Exception as e:
            print(f"  [ERROR] {test.__name__} — {type(e).__name__}: {e}")
            failed += 1

    print("-" * 65)
    print(f"  Résultat : {passed} passés / {passed + failed} total")
    print("=" * 65)

    if failed > 0:
        sys.exit(1)
