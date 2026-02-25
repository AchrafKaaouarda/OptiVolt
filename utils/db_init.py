import os
from Config.database import DatabaseConnection
import mysql.connector

"""
Script d'Initialisation de la Base de Données.
Ce script détruit complètement l'ancienne base de données, la recrée à neuf, 
et exécute le fichier sql/schema.sql pour créer toutes les tables vides.
C'est comme un "Reset D'Usine" pour notre application.
"""

def init_db(host, user, password, database):
    # 1. On se connecte à MySQL SANS spécifier de base de données.
    # Pourquoi ? Parce qu'on veut pouvoir créer la base de données si elle n'existe pas encore !
    try:
        conn = mysql.connector.connect(host=host, user=user, password=password)
        cursor = conn.cursor()
        
        # On supprime la DB si elle existe déjà, puis on en crée une nouvelle
        cursor.execute(f"DROP DATABASE IF EXISTS {database}")
        cursor.execute(f"CREATE DATABASE {database}")
        
        print(f"Base de données '{database}' recréée à neuf.")
        cursor.close()
        conn.close()
        
    except Exception as erreur:
        print(f" Impossible de créer la DB (peut-être déjà existante ou droits insuffisants, ex: Utilisateur sans droit CREATE) : {erreur}")

    # 2. Maintenant que la base est créée, on s'y connecte avec notre outil de connexion habituel
    db = DatabaseConnection()
    db.connect(host, user, password, database)
    conn = db.get_connection()
    
    if not conn:
        print(" Impossible d'initialiser la DB : pas de connexion.")
        return

    # 3. On va chercher le fichier SQL qui contient toutes nos tables
    # os.path.join et os.path.dirname(__file__) permettent de trouver le fichier 
    # sans erreur, peu importe d'où on lance le script Python.
    schema_path = os.path.join(os.path.dirname(__file__), '../database/Schema.sql')
    
    with open(schema_path, 'r') as f:
        schema = f.read()

    # 4. On lit le fichier SQL et on l'exécute commande par commande
    cursor = conn.cursor()
    try:
        # Les requêtes SQL dans le fichier sont séparées par des points-virgules (;)
        commands = schema.split(';')
        
        for command in commands:
            # S'il y a du texte (et pas juste des espaces vides)
            if command.strip():
                cursor.execute(command)
                
        # On valide toutes ces créations de tables
        conn.commit()
        print("Base de données initialisée avec succès (Toutes les tables ont été créées).")
        
    except Exception as erreur:
        print(f"Erreur lors de l'initialisation des tables : {erreur}")
        
    finally:
        cursor.close()

# Ce bloc s'exécute uniquement si on lance directement ce fichier (ex: `python db_init.py`)
if __name__ == "__main__":
    from Config.settings import Config
    init_db(Config.DB_HOST, Config.DB_USER, Config.DB_PASSWORD, Config.DB_NAME)

