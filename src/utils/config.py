import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# ------------------------------------------------------------------------------
# RÉSOLUTION DYNAMIQUE DES CHEMINS (ZÉRO ERREUR D'IMPORT)
# ------------------------------------------------------------------------------
# Le fichier config.py se trouvant dans src/utils/, la racine du projet est 3 niveaux plus haut
SRC_UTILS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SRC_UTILS_DIR.parent.parent

# Chargement explicite du fichier .env depuis la racine du projet
ENV_FILE_PATH = PROJECT_ROOT / ".env"
if ENV_FILE_PATH.exists():
    load_dotenv(dotenv_path=ENV_FILE_PATH)
else:
    # Fallback si exécuté depuis un autre répertoire de travail sans .env
    load_dotenv()


class Settings:
    """
    Classe de configuration globale du projet.
    Charge et valide les variables d'environnement tout en fournissant des valeurs par défaut.
    """
    
    # --------------------------------------------------------------------------
    # CONFIGURATION DE BASE
    # --------------------------------------------------------------------------
    ENV: str = os.getenv("ENV", "development").lower()
    DEBUG: bool = ENV in ("development", "dev", "local")
    
    # --------------------------------------------------------------------------
    # ARCHITECTURE DES DOSSIERS (RÉSOLUS EN ABSOLU)
    # --------------------------------------------------------------------------
    ROOT_DIR: Path = PROJECT_ROOT
    SRC_DIR: Path = PROJECT_ROOT / "src"
    DATA_DIR: Path = PROJECT_ROOT / "data"
    RAW_DATA_DIR: Path = PROJECT_ROOT / "data" / "raw"
    PROCESSED_DATA_DIR: Path = PROJECT_ROOT / "data" / "processed"
    NOTEBOOKS_DIR: Path = PROJECT_ROOT / "notebooks"
    SQL_DIR: Path = PROJECT_ROOT / "sql"
    LOGS_DIR: Path = PROJECT_ROOT / "logs"
    
    def __init__(self):
        # S'assurer que tous les répertoires de base existent
        for folder in [self.DATA_DIR, self.RAW_DATA_DIR, self.PROCESSED_DATA_DIR, 
                       self.NOTEBOOKS_DIR, self.SQL_DIR, self.LOGS_DIR]:
            folder.mkdir(parents=True, exist_ok=True)
            
    # --------------------------------------------------------------------------
    # JOURNALISATION
    # --------------------------------------------------------------------------
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()
    LOG_FILE_PATH: Path = PROJECT_ROOT / "logs" / "app.log"
    
    # --------------------------------------------------------------------------
    # CLÉS D'API FINANCIÈRES
    # --------------------------------------------------------------------------
    ALPHA_VANTAGE_API_KEY: str = os.getenv("ALPHA_VANTAGE_API_KEY", "")
    QUANDL_API_KEY: str = os.getenv("QUANDL_API_KEY", "")
    ALPACA_API_KEY: str = os.getenv("ALPACA_API_KEY", "")
    ALPACA_SECRET_KEY: str = os.getenv("ALPACA_SECRET_KEY", "")
    
    # --------------------------------------------------------------------------
    # CONFIGURATION BASE DE DONNÉES
    # --------------------------------------------------------------------------
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    DB_NAME: str = os.getenv("DB_NAME", "quant_db")
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    
    @property
    def DATABASE_URL(self) -> str:
        """
        Génère dynamiquement l'URL de connexion PostgreSQL.
        Si aucun mot de passe ou utilisateur n'est configuré, bascule automatiquement sur SQLite local.
        """
        if not self.DB_PASSWORD or self.DB_USER == "postgres" and not os.getenv("DB_PASSWORD"):
            # Fallback sur une base de données SQLite de développement locale
            db_path = self.RAW_DATA_DIR / "local_database.db"
            return f"sqlite:///{db_path.as_posix()}"
        
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    # --------------------------------------------------------------------------
    # CONSTANTES FINANCIÈRES PAR DÉFAUT
    # --------------------------------------------------------------------------
    DEFAULT_TICKER: str = os.getenv("DEFAULT_TICKER", "AAPL")
    DEFAULT_BENCHMARK: str = os.getenv("DEFAULT_BENCHMARK", "^GSPC")


# Instanciation de l'objet singleton global accessible dans tout le projet
settings = Settings()
