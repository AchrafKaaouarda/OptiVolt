#!/usr/bin/env python3
import sys
import os

# Ensure the 'optivolt' package is importable
# Add the current directory (project root) to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

if __name__ == "__main__":
    try:
        from optivolt.main import main
        main()
    except ImportError as e:
        print(f"Erreur d'import : {e}")
        print("Assurez-vous d'avoir installé les dépendances : pip install -r requirements.txt")
