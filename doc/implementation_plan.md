# Plan d'Analyse Quantitative - Marché BRVM

L'objectif de cette implémentation est de construire un pipeline d'analyse financière automatisé pour la Bourse Régionale des Valeurs Mobilières (BRVM). L'outil évaluera la **rentabilité**, le **risque**, la **liquidité** et la politique de **dividendes** des entreprises cotées afin de faciliter la sélection d'actions et l'aide à la décision d'investissement.

## ⚠️ Questions Ouvertes (Votre Avis est Requis)

> [!IMPORTANT]
> **Source de données :** Yahoo Finance ne couvre pas bien la BRVM. Il existe un package Python communautaire nommé `brvm` qui permet de récupérer des données, ou nous pouvons créer un scraper sur mesure (par exemple depuis Sika Finance), ou encore utiliser des fichiers de données si vous en avez déjà. 
> *Souhaitez-vous que j'installe et utilise la librairie Python `brvm` pour automatiser la récupération des données historiques ?*

> [!NOTE]
> **Horizon d'investissement :** Afin de bien pondérer les indicateurs (rentabilité vs volatilité), quelle est votre stratégie globale ? Êtes-vous orienté "Bon père de famille" (dividendes à long terme, risque faible) ou cherchez-vous la croissance rapide ?

## Changements Proposés

### 1. Module d'Acquisition de Données (`src/data`)
Création du gestionnaire de données pour la BRVM.
- **[NEW] [brvm_loader.py](file:///c:/Users/Lenovo/OneDrive/Desktop/ANAquant/src/data/brvm_loader.py)** : Script permettant de télécharger l'historique des cours (Prix, Volumes) et l'historique des dividendes de toutes les valeurs de la BRVM.

### 2. Moteur de Calcul des Métriques (`src/models`)
Implémentation des modèles mathématiques et financiers.
- **[NEW] [metrics.py](file:///c:/Users/Lenovo/OneDrive/Desktop/ANAquant/src/models/metrics.py)** : 
  - *Rentabilité* : Calcul des rendements journaliers, mensuels et annualisés (CAGR).
  - *Risque* : Volatilité annualisée, Maximum Drawdown (perte maximale), Ratio de Sharpe.
  - *Liquidité* : Volume moyen d'échange quotidien sur 30 jours et 90 jours (pour éviter les valeurs illiquides où il est difficile de sortir).
  - *Dividendes* : Rendement du dividende (Dividend Yield).

### 3. Logique de Notation (Scoring) et Stratégie (`src/strategies`)
- **[NEW] [scoring.py](file:///c:/Users/Lenovo/OneDrive/Desktop/ANAquant/src/strategies/scoring.py)** : Système de notation multicritères qui attribue un score (sur 100) à chaque action en pondérant les 4 facteurs (Rentabilité, Risque, Liquidité, Dividende) pour générer un classement (Screener).

### 4. Tableau de Bord et Exploration (`notebooks`)
- **[NEW] [01_brvm_analysis.ipynb](file:///c:/Users/Lenovo/OneDrive/Desktop/ANAquant/notebooks/01_brvm_analysis.ipynb)** : Un Notebook Jupyter interactif qui :
  - Télécharge les données.
  - Calcule les métriques pour toutes les actions.
  - Affiche des classements sous forme de tableaux lisibles avec `pandas`.
  - Trace des graphiques (Nuage de points Risque vs Rendement) en utilisant `matplotlib` et `seaborn`.

## Plan de Vérification
### Vérification Automatisée
- Lancer le téléchargement pour un échantillon de valeurs (ex: SONATEL, CIE, SGBCI).
- Exécuter les fonctions de `metrics.py` avec `pytest` pour valider l'exactitude mathématique (ex: vérification que la volatilité d'une série constante est de 0).

### Vérification Manuelle
- Ouvrir le Jupyter Notebook et observer le résultat visuel du screener. Vérifier si les valeurs les mieux classées correspondent intuitivement aux leaders actuels de la BRVM.
