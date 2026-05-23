import sys
from pathlib import Path

# Ajouter la racine du projet au sys.path pour les imports robustes
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import seaborn as sns

print("[OK] Bibliotheques importees avec succes !")

# 1. Test de Data Engineering (Création de DataFrame)
print("\n--- Test Data Engineering / Pandas ---")
data = {
    'Date': pd.date_range(start='2023-01-01', periods=5, freq='D'),
    'Value': np.random.randn(5)
}
df = pd.DataFrame(data)
print(df)

# 2. Test Quant Finance (Téléchargement de données via yfinance)
print("\n--- Test Quant Finance (yfinance) ---")
try:
    ticker = "AAPL"
    print(f"Téléchargement des données pour {ticker}...")
    stock_data = yf.download(ticker, start="2023-01-01", end="2023-01-10", progress=False)
    print(stock_data.head())
    
    # 3. Test Data Science / Analyse (Visualisation)
    print("\n--- Test Data Analysis (Matplotlib/Seaborn) ---")
    sns.set_theme(style="darkgrid")
    plt.figure(figsize=(10, 5))
    plt.plot(stock_data.index, stock_data['Close'], marker='o', color='b', label=f'Prix de clôture {ticker}')
    plt.title(f"Évolution du prix de l'action {ticker}")
    plt.xlabel("Date")
    plt.ylabel("Prix (USD)")
    plt.legend()
    
    # Résolution absolue robuste du chemin d'enregistrement du graphique
    plot_path = PROJECT_ROOT / "data" / "raw" / "test_plot.png"
    plt.savefig(plot_path)
    print(f"[OK] Graphique sauvegarde sous '{plot_path}'")
except Exception as e:
    print(f"[ERREUR] Erreur lors du test financier : {e}")
