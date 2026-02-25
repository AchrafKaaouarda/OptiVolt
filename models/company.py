from dataclasses import dataclass, field
from typing import Optional

"""
L'utilisation de "@dataclass" simplifie la création de classes en Python.
Au lieu d'écrire une longue méthode __init__ pour assigner toutes les variables une par une
(ex: self.nom = nom, self.prix = prix, etc.), Python va le faire automatiquement pour nous.
Il suffit juste de lister les attributs avec leur type attendu (ex: str, int, float, bool).
C'est très utile pour les classes qui servent principalement à stocker des données.
"""

@dataclass
class SubscriptionPlan:
    """Modèle représentant un plan d'abonnement (Basic, Pro, Premium)."""
    id: int = None
    nom: str = None
    prix_mensuel: float = 0.0
    duree_jours: int = 30
    max_services: int = 5
    has_scheduling: bool = False
    has_priority_support: bool = False
    has_analytics: bool = False
    description: str = None

@dataclass
class ServiceType:
    """Modèle représentant une catégorie de service (Nettoyage, Installation, etc.)."""
    id: int = None
    nom_service: str = None
    description: str = None
    category: str = None

@dataclass
class CatalogItem:
    """Modèle représentant une prestation proposée par une entreprise spécifique."""
    id: int = None
    company_id: int = None
    service_type: ServiceType = None
    prix_base: float = 0.0
    prix_par_unite: float = 0.0
    unite_nom: str = 'panneau'
    description_offre: str = None
    produits_inclus: str = None
    duree_estimee: str = None

@dataclass
class Company:
    """Modèle représentant une entreprise partenaire inscrite sur OptiVolt."""
    id: int = None
    user_id: int = None
    nom_entreprise: str = None
    description: str = None
    ville: str = None
    contact_phone: str = None
    contact_email: str = None
    
    # Horaires d'ouverture de l'entreprise
    horaire_debut: str = '08:00'
    horaire_fin: str = '18:00'
    jours_travail: str = 'Lun-Sam'
    
    # Statut de l'entreprise
    is_verified: bool = False
    
    # Informations sur l'abonnement en cours
    subscription_plan_id: int = None
    subscription_start: str = None
    subscription_expires_at: str = None
    
    # Cet attribut permet de relier l'objet Company à son plan d'abonnement (SubscriptionPlan)
    subscription_plan: SubscriptionPlan = None
    
    # 'field(default_factory=list)' demande à Python de créer une NOUVELLE liste vide []
    # pour chaque nouvelle entreprise créée, afin de stocker ses offres.
    catalog: list = field(default_factory=list)

