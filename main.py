from Config.database import DatabaseConnection
from Config.settings import Config

def main():
    # On crée une instance de notre classe de connexion à la base de données
    db = DatabaseConnection()
    
    # On établit la connexion en utilisant les paramètres de configuration
    db.connect(
        host=Config.DB_HOST,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME
    )
    
    # Ici, on pourrait ajouter du code pour interagir avec la base de données via les DAOs...
    
    # Enfin, on ferme la connexion proprement à la fin du programme
    db.close()
    
if __name__ == "__main__":
    main()