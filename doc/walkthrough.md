# Pipeline d'Analyse Quantitative BRVM

L'architecture pour l'analyse des actions de la BRVM est maintenant en place. Face à l'impossibilité d'utiliser le package `brvm` (non compatible ou obsolète), nous avons conçu une infrastructure résiliente qui peut accueillir des données réelles issues de fichiers CSV, et qui utilise des données simulées très réalistes pour que vous puissiez tester le moteur d'analyse immédiatement.

## Ce qui a été construit :

### 1. Le Gestionnaire de Données (`src/data/brvm_loader.py`)
Ce module est chargé d'alimenter votre système.
- Il inclut actuellement les métadonnées (Rendement du dividende estimé, Volatilité) pour des valeurs clés de la BRVM comme **Sonatel**, **SGBCI**, **CIE CI**, etc.
- **Fonctionnement "Fallback"** : S'il détecte un fichier `data/SNTS.SN.csv`, il l'utilise. Sinon, il génère des données réalistes basées sur un modèle de *Geometric Brownian Motion* (marche aléatoire). Cela vous permet de développer sans être bloqué par l'absence d'API.

### 2. Le Moteur Financier (`src/models/metrics.py`)
Ce fichier calcule tous les indicateurs clés pour chaque action :
- **CAGR** (Rentabilité à long terme).
- **Volatilité et Max Drawdown** (Pour quantifier le risque et la perte historique la plus sévère).
- **Ratio de Sharpe** (Le rendement ajusté au risque).
- **Volume moyen** (La liquidité du titre).

### 3. Le Screener - Stratégie Mixte (`src/strategies/scoring.py`)
C'est le "cerveau" de l'outil. Comme vous avez demandé une stratégie mixte (équilibrée), le système de notation (`score_and_rank_stocks`) attribue une note sur 100 à chaque action en répartissant les pondérations de la manière suivante :
- **30% sur la Croissance (CAGR)**
- **30% sur les Dividendes (Dividend Yield)**
- **20% sur la Réduction du Risque (Faible volatilité)**
- **20% sur la Performance Ajustée au Risque (Sharpe)**

### 4. Le Tableau de Bord Interactif (`notebooks/01_brvm_analysis.ipynb`)
C'est ici que l'analyse prend vie. 
- Le Jupyter Notebook compile les données, lance les calculs via la stratégie de scoring et affiche un classement (DataFrame).
- Il inclut un graphique visuel dynamique (`Nuage de points`) qui vous montre le Risque par rapport au Rendement Estimé (CAGR + Dividendes), où la taille des bulles représente la liquidité (Volumes) et la couleur la force du dividende.

> [!TIP]
> **Prochaine étape** : Ouvrez le notebook [01_brvm_analysis.ipynb](file:///c:/Users/Lenovo/OneDrive/Desktop/ANAquant/notebooks/01_brvm_analysis.ipynb) dans JupyterLab ou VS Code et lancez toutes les cellules pour voir la stratégie mixte à l'œuvre !
> Une fois satisfait, il vous suffira de déposer vos fichiers `.csv` historiques (que vous pouvez télécharger par exemple via investir.lesechos ou autre pour les valeurs africaines) dans le dossier `/data/` pour que les vraies valeurs remplacent la simulation de façon transparente.
