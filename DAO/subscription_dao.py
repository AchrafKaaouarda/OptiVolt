from Config.database import DatabaseConnection
from models.company import SubscriptionPlan

"""
SubscriptionDAO (Data Access Object pour les Abonnements).
Gère la récupération des plans tarifaires et l'abonnement des entreprises.
"""

class SubscriptionDAO:
    def __init__(self):
        # Initialisation de la connexion à la base de données
        self.db = DatabaseConnection()

    def get_all_plans(self):
        """Récupère tous les forfaits d'abonnement disponibles, triés par prix croissant."""
        connection = self.db.get_connection()
        if not connection: 
            return []
            
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM subscription_plans ORDER BY prix_mensuel ASC")
            
            # On transforme chaque ligne de résultat (Dictionnaire) en un objet Python "SubscriptionPlan"
            lignes = cursor.fetchall()
            liste_plans = []
            for ligne_db in lignes:
                plan_obj = self._map_plan(ligne_db)
                liste_plans.append(plan_obj)
                
            return liste_plans
            
        finally:
            cursor.close()

    def get_plan_by_id(self, plan_id):
        """Récupère un forfait spécifique en utilisant son ID."""
        connection = self.db.get_connection()
        if not connection: 
            return None
            
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM subscription_plans WHERE id = %s", (plan_id,))
            row = cursor.fetchone()
            
            # Si on a trouvé le plan, on le transforme en objet, sinon on renvoie None
            if row is not None:
                return self._map_plan(row)
            else:
                return None
                
        finally:
            cursor.close()

    def subscribe_company(self, company_id, plan_id, duree_jours=30):
        """Met à jour l'abonnement d'une entreprise."""
        connection = self.db.get_connection()
        if not connection: 
            return False
            
        cursor = connection.cursor()
        try:
            # CURDATE() = Aujourd'hui. DATE_ADD(...) = Aujourd'hui + duree_jours
            sql = """
                UPDATE companies 
                SET subscription_plan_id = %s, 
                    subscription_start = CURDATE(),
                    subscription_expires_at = DATE_ADD(CURDATE(), INTERVAL %s DAY)
                WHERE id = %s
            """
            cursor.execute(sql, (plan_id, duree_jours, company_id))
            connection.commit()
            return True
            
        except Exception as erreur:
            print(f"Erreur lors de l'abonnement : {erreur}")
            return False
            
        finally:
            cursor.close()

    def get_subscription_revenue(self):
        """
        Calcule les revenus générés par les abonnements ACTIFS.
        Utilise COUNT pour compter les abonnés, et SUM pour additionner les prix.
        Le GROUP BY permet d'avoir le total PAR type de forfait (ex: Basic, Pro, Premium).
        """
        connection = self.db.get_connection()
        if not connection: 
            return {}
            
        cursor = connection.cursor(dictionary=True)
        try:
            sql = """
                SELECT 
                    COUNT(c.id) as nb_abonnes,
                    COALESCE(SUM(sp.prix_mensuel), 0) as revenu_mensuel,
                    sp.nom as plan_nom
                FROM companies c
                JOIN subscription_plans sp ON c.subscription_plan_id = sp.id
                WHERE c.subscription_expires_at >= CURDATE()
                GROUP BY sp.id, sp.nom
            """
            cursor.execute(sql)
            return cursor.fetchall()
            
        finally:
            cursor.close()

    def _map_plan(self, row):
        """Méthode utilitaire interne pour transformer un dictionnaire MySQL en objet Python."""
        return SubscriptionPlan(
            id=row['id'],
            nom=row['nom'],
            prix_mensuel=row['prix_mensuel'],
            duree_jours=row['duree_jours'],
            max_services=row['max_services'],
            has_scheduling=row['has_scheduling'],
            has_priority_support=row['has_priority_support'],
            has_analytics=row['has_analytics'],
            description=row['description']
        )

