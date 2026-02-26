from Config.database import DatabaseConnection

"""
AdminService (Service d'Administration).
Ce fichier gère la logique spécifique au tableau de bord de l'Administrateur.
Même si certaines requêtes semblent simples, passer par un "Service" permet de 
garder notre code bien organisé au cas où on voudrait ajouter des calculs ou des 
vérifications avant de parler à la base de données.
"""

class AdminService:
    def __init__(self):
        # On récupère directement la connexion Singleton pour ce vieux module
        self.db = DatabaseConnection()

    def get_unverified_technicians(self):
        """Récupère la liste des techniciens qui attendent d'être validés."""
        connection = self.db.get_connection()
        if not connection: 
            return []
            
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM users WHERE role = 'TECHNICIEN' AND is_verified = FALSE"
        try:
            cursor.execute(query)
            return cursor.fetchall()
            
        except Exception:
            return []
            
        finally:
            cursor.close()

    def validate_technician(self, tech_id):
        """Valide le compte d'un technicien (is_verified = TRUE)."""
        connection = self.db.get_connection()
        if not connection: 
            return False
            
        cursor = connection.cursor()
        try:
            cursor.execute("UPDATE users SET is_verified = TRUE WHERE id = %s", (tech_id,))
            connection.commit()
            
            # rowcount vérifie si au moins une ligne a été modifiée par l'UPDATE
            return cursor.rowcount > 0
            
        except Exception:
            return False
            
        finally:
            cursor.close()

    def get_statistics(self):
        """
        Récupère un gros dictionnaire avec plein de statistiques différentes.
        C'est très utile pour afficher des graphiques sur le Dashboard Administrateur.
        """
        connection = self.db.get_connection()
        if not connection: 
            return {}
            
        stats = {}
        cursor = connection.cursor()
        try:
            # 1. On compte les utilisateurs groupés par rôle (ex: 10 Clients, 5 Entreprises)
            cursor.execute("SELECT role, COUNT(*) FROM users GROUP BY role")
            stats['users'] = cursor.fetchall()
            
            # 2. On compte les interventions groupées par statut (ex: 20 Terminées, 5 En Attente)
            cursor.execute("SELECT statut, COUNT(*) FROM interventions GROUP BY statut")
            stats['interventions'] = cursor.fetchall()
            
            # 3. On fait la somme des prix estimés pour toutes les missions Terminées pour avoir le Chiffre d'Affaires
            cursor.execute("SELECT SUM(prix_estime) FROM interventions WHERE statut = 'TERMINEE'")
            # fetchone()[0] permet de récupérer directement la valeur (la somme), et le "or 0.0" évite d'avoir None si c'est vide
            stats['ca_total'] = cursor.fetchone()[0] or 0.0
            
            return stats
            
        except Exception as erreur:
            print(f"Erreur lors de la récupération des statistiques : {erreur}")
            return {}
            
        finally:
            cursor.close()