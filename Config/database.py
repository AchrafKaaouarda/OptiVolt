import mysql.connector
from mysql.connector import Error

class DatabaseConnection:
    """
    Cette classe gère la connexion à la base de données MySQL.
    Elle utilise le design pattern (patron de conception) "Singleton".
    Le but du Singleton est de s'assurer qu'il n'y a qu'une seule connexion active
    partagée dans tout le programme, pour éviter d'ouvrir 50 connexions différentes.
    """
    
    # Cet attribut de classe va stocker l'unique instance de notre connexion
    _instance = None

    def __new__(cls):
        """
        La méthode magique __new__ est appelée AVANT __init__ quand on crée un objet.
        C'est ici qu'on implémente le Singleton : si l'instance n'existe pas, on la crée.
        Si elle existe déjà, on renvoie simplement celle qui existe.
        """
        if cls._instance is None:
            # Création de la seule et unique instance
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            # Initialisation de notre variable de connexion à None
            cls._instance.connection = None
        
        # On retourne toujours la même instance
        return cls._instance

    def connect(self, host, user, password, database):
        """
        Cette méthode établit la vraie connexion au serveur MySQL.
        """
        # On vérifie d'abord si on n'est pas déjà connecté
        is_already_connected = self.connection is not None and self.connection.is_connected()
        
        if not is_already_connected:
            try:
                # On essaie de se connecter avec les informations fournies
                self.connection = mysql.connector.connect(
                    host=host,
                    user=user,
                    password=password,
                    database=database
                )
                
                # Si ça marche, on affiche un message de succès
                if self.connection.is_connected():
                    print("✅ Connexion à la base de données réussie (Singleton).")
                    
            except Error as error_message:
                # Si une erreur survient, on l'attrape (try/except) et on l'affiche
                print(f"❌ Erreur lors de la connexion à MySQL : {error_message}")
                self.connection = None

    def get_connection(self):
        """
        Une méthode simple (un "getter") pour récupérer la connexion active
        afin de l'utiliser dans d'autres fichiers (les DAOs).
        """
        return self.connection

    def close(self):
        """
        Ferme la connexion proprement quand on n'en a plus besoin (ex: à la fin du programme).
        """
        # Si on a une connexion et qu'elle est bien active...
        if self.connection is not None and self.connection.is_connected():
            # ... on la ferme
            self.connection.close()
            print("Connexion MySQL fermée.")

