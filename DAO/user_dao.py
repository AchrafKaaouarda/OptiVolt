from Config.database import DatabaseConnection
from models.user import UserFactory

"""
DAO signifie "Data Access Object" (Objet d'Accès aux Données).
Le rôle de cette classe est de s'occuper EXCLUSIVEMENT de la base de données.
Elle fait le pont entre nos objets Python (les instances de User) et les tables MySQL.
"""

class UserDAO:
    def __init__(self):
        # On récupère notre connexion Singleton (créée dans config/database.py)
        self.db = DatabaseConnection()

    def create(self, user):
        """Insère un nouvel utilisateur dans la base de données."""
        connection = self.db.get_connection()
        if not connection: 
            return None
            
        cursor = connection.cursor()
        
        # On utilise des %s pour sécuriser la requête contre les "Injections SQL"
        # Les vraies valeurs seront remplacées en toute sécurité par la librairie
        query = """
        INSERT INTO users (nom, email, password_hash, role, telephone, ville, adresse)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        values = (user.nom, user.email, user.password, user.role, user.telephone, user.ville, user.adresse)
        
        try:
            # On exécute la requête avec les valeurs
            cursor.execute(query, values)
            
            # "commit" valide et sauvegarde définitivement les changements dans la base
            connection.commit()
            
            # On récupère l'ID généré automatiquement par MySQL (AUTO_INCREMENT)
            user.id = cursor.lastrowid
            return user
            
        except Exception as erreur:
            print(f" Erreur lors de la création de l'utilisateur : {erreur}")
            return None
            
        finally:
            # Le bloc "finally" s'exécute TOUJOURS, qu'il y ait eu une erreur ou non.
            # C'est parfait pour fermer le curseur proprement.
            cursor.close()

    def find_by_login(self, login):
        """Recherche un utilisateur par son email OU son numéro de téléphone."""
        connection = self.db.get_connection()
        if not connection: 
            return None
            
        # dictionary=True permet de récupérer les résultats sous forme de dictionnaire 
        # (ex: row['email'] au lieu de row[2]) ce qui est beaucoup plus lisible.
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM users WHERE email = %s OR telephone = %s"
        
        try:
            # On passe le 'login' deux fois car on a deux '%s' dans la requête
            cursor.execute(query, (login, login))
            
            # fetchone() récupère la première ligne de résultat
            row = cursor.fetchone()
            
            if row:
                # Si on a trouvé un utilisateur, on utilise notre Factory pour recréer l'objet Python !
                user = UserFactory.create_user(
                    role=row['role'], 
                    nom=row['nom'], 
                    email=row['email'], 
                    password=row['password_hash'],
                    telephone=row['telephone'], 
                    ville=row.get('ville'), 
                    adresse=row.get('adresse'),
                    is_banned=bool(row.get('is_banned', False))
                )
                user.id = row['id']
                return user
                
            # Si on n'a rien trouvé
            return None
            
        except Exception as erreur:
            print(f" Erreur lors de la recherche du login : {erreur}")
            return None
            
        finally:
            cursor.close()

    def get_all_users(self):
        """Récupère la liste de tous les utilisateurs (utile pour l'Admin)."""
        connection = self.db.get_connection()
        if not connection: 
            return []
            
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SELECT id, nom, email, role, telephone, ville, is_banned, created_at FROM users ORDER BY created_at DESC")
            # fetchall() renvoie toutes les lignes trouvées sous forme de liste
            return cursor.fetchall()
        finally:
            cursor.close()

    def ban_user(self, user_id):
        """Bannit un utilisateur (met son statut is_banned à Vrai)."""
        connection = self.db.get_connection()
        if not connection: 
            return False
            
        cursor = connection.cursor()
        try:
            # On met à jour la ligne correspondante
            cursor.execute("UPDATE users SET is_banned = TRUE WHERE id = %s", (user_id,))
            connection.commit()
            return True
        except Exception: 
            return False
        finally: 
            cursor.close()

    def unban_user(self, user_id):
        """Débannit un utilisateur (met son statut is_banned à Faux)."""
        connection = self.db.get_connection()
        if not connection: 
            return False
            
        cursor = connection.cursor()
        try:
            cursor.execute("UPDATE users SET is_banned = FALSE WHERE id = %s", (user_id,))
            connection.commit()
            return True
        except Exception: 
            return False
        finally: 
            cursor.close()

    def delete_user(self, user_id):
        """Supprime définitivement un utilisateur de la base."""
        connection = self.db.get_connection()
        if not connection: 
            return False
            
        cursor = connection.cursor()
        try:
            cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
            connection.commit()
            return True
        except Exception: 
            return False
        finally: 
            cursor.close()