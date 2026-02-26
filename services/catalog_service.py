from DAO.company_dao import CompanyDAO
from DAO.booking_dao import BookingDAO
from utils.logger import Logger

"""
La couche 'Service' (Business Logic).
Contrairement aux DAOs qui ne font QUE parler à la base de données,
les Services contiennent la vraie logique de l'application (ex: calculer un prix final,
vérifier des règles, envoyer des emails, etc.).
Un Service utilise souvent plusieurs DAOs différents pour accomplir sa mission.
"""

class CatalogService:
    def __init__(self):
        # Le Service a besoin de parler aux tables 'companies' et 'bookings'
        self.company_dao = CompanyDAO()
        self.booking_dao = BookingDAO()
        self.logger = Logger()  # Pour garder une trace de tout ce qui se passe

    def get_service_types(self):
        """Récupère toutes les grandes catégories de services disponibles."""
        types = self.company_dao.get_service_types()
        self.logger.log_info(f"Catégories de services récupérées : {len(types)}")
        return types

    def list_companies(self, ville=None):
        """Liste les entreprises vérifiées (avec filtre optionnel par ville)."""
        companies = self.company_dao.get_all_companies(ville)
        self.logger.log_info(f"Recherche Entreprises (Ville={ville}): {len(companies)} trouvées.")
        return companies

    def get_companies_for_service(self, service_type_id):
        """Trouve quelles entreprises proposent un service précis (ex: Nettoyage)."""
        results = self.company_dao.get_companies_by_service(service_type_id)
        self.logger.log_info(f"Entreprises pour le service {service_type_id}: {len(results)} trouvées.")
        return results

    def get_company_catalog(self, company_id):
        """Récupère toutes les offres d'une entreprise spécifique."""
        return self.company_dao.get_catalog(company_id)

    def calculate_price(self, item, quantite, user_ville=None):
        """
        Calcule le prix final pour le client.
        C'est typiquement le genre de logique "métier" qui va dans un Service.
        """
        # Prix de base + (Prix unitaire * Quantité)
        base = item.prix_base + (item.prix_par_unite * quantite)
        
        # On utilise le design pattern Strategy pour appliquer la TVA ou des taxes locales
        from services.pricing_strategy import PricingFactory
        # Si la ville n'est pas précisée, on envoie une chaîne vide ("")
        ville_choisie = user_ville if user_ville is not None else ""
        
        strategy = PricingFactory.get_strategy(ville_choisie)
        final_price = strategy.calculate_price(base)
        
        # On retourne le prix final ET une petite description de la taxe appliquée (ex: "TVA 20%")
        return final_price, strategy.get_description()

    def create_booking_request(self, client_id, company_id, service_type_id, catalog_id, quantite, description, prix_total, rdv_date, rdv_heure, mode_paiement='ONLINE'):
        """
        Crée la réservation dans la base de données.
        Si le paiement est En Ligne, on simule le paiement direct et on passe le statut à PAYE.
        """
        # 1. On demande au DAO de créer la réservation
        booking_id = self.booking_dao.create_booking(
            client_id, company_id, service_type_id, catalog_id,
            quantite, prix_total, description, rdv_date, rdv_heure, mode_paiement
        )
        
        # 2. Logique métier : Si la création a réussi
        if booking_id:
            self.logger.log_info(f" Réservation #{booking_id} créée - Client {client_id}, Prix {prix_total} DH, RDV {rdv_date} {rdv_heure}, Paiement {mode_paiement}")
            
            # Si le client paie en ligne, on SIMULE le paiement réussi et on met le statut à 'PAYEE'
            if mode_paiement == 'ONLINE':
                self.booking_dao.update_status(booking_id, 'PAYEE')
                self.logger.log_info(f" Paiement en ligne simulé pour la réservation #{booking_id}")
                
            return booking_id, prix_total
            
        # 3. Si échec
        self.logger.log_error(f" Échec de la création de la réservation pour le Client {client_id}.")
        return None, 0

