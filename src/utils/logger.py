import logging
import sys
from logging.handlers import RotatingFileHandler
from src.utils.config import settings

# ------------------------------------------------------------------------------
# FORMATEUR DE CONSOLE COULEUR DE HAUTE QUALITÉ (ANSI ESCAPES)
# ------------------------------------------------------------------------------
class CustomFormatter(logging.Formatter):
    """
    Formateur de logs personnalisé ajoutant des codes couleur ANSI 
    pour une visibilité maximale en console de développement.
    """
    # Palettes de couleurs HSL simulées en codes ANSI standard
    GREY = "\x1b[38;20m"
    CYAN = "\x1b[36;20m"
    GREEN = "\x1b[32;20m"
    YELLOW = "\x1b[33;20m"
    RED = "\x1b[31;20m"
    BOLD_RED = "\x1b[31;1m"
    RESET = "\x1b[0m"
    
    FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: CYAN + FORMAT + RESET,
        logging.INFO: GREEN + FORMAT + RESET,
        logging.WARNING: YELLOW + FORMAT + RESET,
        logging.ERROR: RED + FORMAT + RESET,
        logging.CRITICAL: BOLD_RED + FORMAT + RESET
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno, self.GREY + self.FORMAT + self.RESET)
        formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)


def setup_logger(name: str = "project_logger") -> logging.Logger:
    """
    Configure et retourne une instance de logger avec double destination :
    1. Console (avec formatage couleur ANSI, optimisé pour dev).
    2. Fichier de log rotatif (logs/app.log, formatage texte standard propre).
    """
    logger = logging.getLogger(name)
    
    # Éviter de rajouter des handlers si le logger a déjà été initialisé
    if logger.hasHandlers():
        return logger
        
    logger.setLevel(settings.LOG_LEVEL)

    # 1. Handler Console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(settings.LOG_LEVEL)
    console_handler.setFormatter(CustomFormatter())
    logger.addHandler(console_handler)

    # 2. Handler Fichier Rotatif (Max 5Mo par fichier, garde 5 fichiers en historique)
    try:
        # S'assurer que le dossier des logs existe (géré normalement par config.py)
        settings.LOGS_DIR.mkdir(parents=True, exist_ok=True)
        
        file_handler = RotatingFileHandler(
            filename=settings.LOG_FILE_PATH,
            maxBytes=5 * 1024 * 1024,  # 5 Mo
            backupCount=5,
            encoding="utf-8"
        )
        file_handler.setLevel(settings.LOG_LEVEL)
        
        # Format propre sans caractères de couleur ANSI pour le fichier texte
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - [%(levelname)s] - %(message)s - (%(filename)s:%(lineno)d)",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
    except Exception as e:
        # Fallback silencieux en console si problème d'écriture de fichier
        print(f"\x1b[31;20m[WARNING] Impossible d'initialiser le fichier de logs : {e}\x1b[0m")

    return logger

# Logger principal de l'application
logger = setup_logger("app")
