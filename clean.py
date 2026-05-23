#!/usr/bin/env python
import os
import shutil
import stat
from pathlib import Path

# Racine du projet
PROJECT_ROOT = Path(__file__).resolve().parent

# Dossiers à exclure absolument du nettoyage (comme l'environnement virtuel)
EXCLUDE_DIRS = {"ana_env", "data_env", "venv", ".venv", "env", ".git"}

def remove_readonly(func, path, excinfo):
    """Gestionnaire d'erreurs pour forcer la suppression des fichiers en lecture seule sous Windows."""
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception:
        pass

def clean_project():
    print("==============================================================================")
    print("                 NETTOYAGE DE L'ENVIRONNEMENT DE DÉVELOPPEMENT                ")
    print("==============================================================================")
    
    deleted_folders_count = 0
    deleted_files_count = 0
    freed_bytes = 0
    
    # 1. Parcours récursif pour chercher les caches et fichiers compilés
    for root, dirs, files in os.walk(PROJECT_ROOT, topdown=True):
        # Modifier dirs sur place pour ignorer les répertoires exclus (optimise le parcours)
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        
        # Détection des dossiers à supprimer
        for d in list(dirs):
            dir_path = Path(root) / d
            if d in ("__pycache__", ".ipynb_checkpoints", ".pytest_cache", ".mypy_cache"):
                try:
                    # Calculer la taille libérée
                    dir_size = sum(f.stat().st_size for f in dir_path.glob('**/*') if f.is_file())
                    shutil.rmtree(dir_path, onerror=remove_readonly)
                    dirs.remove(d) # Ne pas descendre dedans puisqu'il est supprimé
                    print(f"[-] Dossier supprime : {dir_path.relative_to(PROJECT_ROOT)} ({dir_size} octets)")
                    deleted_folders_count += 1
                    freed_bytes += dir_size
                except Exception as e:
                    print(f"[!] Erreur de suppression du dossier {dir_path} : {e}")

        # Détection des fichiers compilés individuels
        for f in files:
            file_path = Path(root) / f
            if f.endswith((".pyc", ".pyo", ".pyd")):
                try:
                    file_size = file_path.stat().st_size
                    file_path.unlink()
                    print(f"[-] Fichier supprime : {file_path.relative_to(PROJECT_ROOT)} ({file_size} octets)")
                    deleted_files_count += 1
                    freed_bytes += file_size
                except Exception as e:
                    print(f"[!] Erreur de suppression du fichier {file_path} : {e}")

    # 2. Rapport final
    print("------------------------------------------------------------------------------")
    print(f"Diagnostic du nettoyage :")
    print(f"  - Dossiers de cache supprimes : {deleted_folders_count}")
    print(f"  - Fichiers compiles supprimes  : {deleted_files_count}")
    print(f"  - Espace disque libere         : {freed_bytes} octets")
    print("==============================================================================")
    print("                 NETTOYAGE TERMINE - TOUT EST PROPRE !                        ")
    print("==============================================================================")

if __name__ == "__main__":
    clean_project()
