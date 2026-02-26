from Config.database import DatabaseConnection
from Config.settings import Config

"""
Script de Migration de la Base de Données.
Une "Migration" sert à modifier la structure d'une base de données EXISTANTE sans perdre les données
(ex: rajouter une colonne dans une table).
Ici, ce vieux script ajoutait la colonne 'is_available' aux utilisateurs.
"""

def migrate():
    print(" Migration de la base de données (Vérification de structure)...")
    db = DatabaseConnection()
    # On se connecte à la DB avec les paramètres configurés
    db.connect(Config.DB_HOST, Config.DB_USER, Config.DB_PASSWORD, Config.DB_NAME)
    
    conn = db.get_connection()
    if not conn: 
        return
    
    cursor = conn.cursor()
    try:
        # En MySQL, "information_schema.COLUMNS" est une table cachée qui contient la liste 
        # de TOUTES les colonnes de TOUTES les tables. On s'en sert pour faire une vérification.
        # On vérifie si la colonne "is_available" existe déjà dans la table "users".
        check_query = """
            SELECT count(*) 
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = %s 
              AND TABLE_NAME = 'users' 
              AND COLUMN_NAME = 'is_available'
        """
        cursor.execute(check_query, (Config.DB_NAME,))
        colonne_existante = cursor.fetchone()[0]
        
        # Si le compte est de 0, la colonne n'existe pas encore.
        if colonne_existante == 0:
            print("Ajout de la colonne 'is_available' dans la table users...")
            # On utilise "ALTER TABLE" pour modifier une table existante en rajoutant la colonne
            cursor.execute("ALTER TABLE users ADD COLUMN is_available BOOLEAN DEFAULT TRUE")
            conn.commit()
            print("Migration réussie.")
        else:
            print(" La colonne 'is_available' est déjà présente, aucune modification requise.")
            
    except Exception as erreur:
        print(f"Erreur lors de la migration : {erreur}")
        
    finally:
        cursor.close()

if __name__ == "__main__":
    migrate()

