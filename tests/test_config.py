import os
import sys
from pathlib import Path

# Ajouter la racine du projet au sys.path pour les imports robustes de src
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from src.utils.config import settings
from src.utils.logger import logger, setup_logger

def run_diagnostic():
    print("==============================================================================")
    print("                DIAGNOSTIC DE LA CONFIGURATION GLOBALE DU PROJET              ")
    print("==============================================================================")

    # 1. Vérification du chargement de l'environnement
    logger.info(f"Environnement charge : '{settings.ENV}' (Mode Debug: {settings.DEBUG})")
    
    # 2. Vérification des chemins de répertoires
    logger.info("--- Verification des Chemins Absolus de l'arborescence ---")
    logger.info(f"Projet Racine : {settings.ROOT_DIR}")
    logger.info(f"Dossier Data  : {settings.DATA_DIR}")
    logger.info(f"Dossier Raw   : {settings.RAW_DATA_DIR}")
    logger.info(f"Dossier Proc  : {settings.PROCESSED_DATA_DIR}")
    logger.info(f"Dossier Notebooks : {settings.NOTEBOOKS_DIR}")
    logger.info(f"Dossier Logs  : {settings.LOGS_DIR}")
    logger.info(f"Dossier SQL   : {settings.SQL_DIR}")

    # Vérification de l'existence physique des répertoires
    for path_name, path in [
        ("DATA_DIR", settings.DATA_DIR),
        ("RAW_DATA_DIR", settings.RAW_DATA_DIR),
        ("PROCESSED_DATA_DIR", settings.PROCESSED_DATA_DIR),
        ("NOTEBOOKS_DIR", settings.NOTEBOOKS_DIR),
        ("LOGS_DIR", settings.LOGS_DIR),
        ("SQL_DIR", settings.SQL_DIR)
    ]:
        if path.exists():
            logger.info(f"[OK] Repertoire {path_name} existe et est operationnel.")
        else:
            logger.error(f"[ERREUR] Le repertoire {path_name} ({path}) est introuvable !")

    # 3. Vérification de la configuration de Base de Données & Clés API
    logger.info("--- Configuration de la Base de Données & APIs ---")
    logger.info(f"URL de connexion de la Base de Donnes : {settings.DATABASE_URL}")
    
    if "sqlite" in settings.DATABASE_URL:
        logger.info("[INFO] Utilisation de SQLite locale (developpement).")
    else:
        logger.info("[INFO] Utilisation d'une base PostgreSQL distante.")

    # API Keys (affichage tronqué pour des raisons de sécurité)
    av_key = settings.ALPHA_VANTAGE_API_KEY
    av_masked = av_key[:4] + "*" * (len(av_key) - 4) if len(av_key) > 4 else "Non definie"
    logger.info(f"Alpha Vantage API Key : {av_masked}")
    
    logger.info(f"Default Ticker        : {settings.DEFAULT_TICKER}")
    logger.info(f"Default Benchmark     : {settings.DEFAULT_BENCHMARK}")

    # 4. Démonstration des différents niveaux de Logs
    logger.info("--- Demonstration des differents niveaux de Logs ---")
    logger.debug("Ceci est un message de DEBUG (Tres detaille, couleur Cyan)")
    logger.info("Ceci est un message d'INFO (Standard, couleur Verte)")
    logger.warning("Ceci est un message d'AVERTISSEMENT (Warning, couleur Jaune)")
    logger.error("Ceci est un message d'ERREUR (Error, couleur Rouge)")
    logger.critical("Ceci est un message CRITIQUE (Critical, couleur Rouge Gras)")

    # 5. Vérification du fichier de logs
    logger.info("--- Verification de l'ecriture physique dans le fichier de logs ---")
    if settings.LOG_FILE_PATH.exists():
        logger.info(f"[OK] Le fichier de log a ete correctement cree sous : {settings.LOG_FILE_PATH}")
        # Petite vérification de sa taille
        size = settings.LOG_FILE_PATH.stat().st_size
        logger.info(f"[OK] Taille actuelle du fichier de logs : {size} octets")
    else:
        logger.error(f"[ERREUR] Le fichier de logs est introuvable à l'emplacement : {settings.LOG_FILE_PATH}")

    print("==============================================================================")
    print("                    DIAGNOSTIC TERMINE AVEC SUCCES                            ")
    print("==============================================================================")


if __name__ == "__main__":
    run_diagnostic()
