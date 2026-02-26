from abc import ABC, abstractmethod

"""
Le Design Pattern "Strategy" (Stratégie).
Imagine qu'on ait besoin de calculer le prix final différemment selon la ville
(Rabat a une TVA de 20%, Casa a un frais de déplacement fixe, etc.).
Au lieu de faire un gigantesque "if ville == 'Rabat' elif ville == 'Casa' elif...",
on crée une "Stratégie" (une classe) par ville.
Ça respecte le principe OCP (Open/Closed Principle) : on peut ajouter de nouvelles villes
sans jamais modifier le code existant !
"""

class PricingStrategy(ABC):
    """
    Ceci est l'"Interface" ou le "Moule" de nos stratégies.
    Toute classe qui veut être une stratégie de prix DOIT obligatoirement 
    implémenter ces deux méthodes (@abstractmethod).
    """
    
    @abstractmethod
    def calculate_price(self, base_price: float) -> float:
        # Calcule le prix final à partir du prix de base
        pass

    @abstractmethod
    def get_description(self) -> str:
        # Retourne une petite explication texte (ex: "+50 DH frais de route")
        pass

class StandardPricingStrategy(PricingStrategy):
    """Stratégie par défaut (pas de taxe ni de frais supplémentaires)."""
    
    def calculate_price(self, base_price: float) -> float:
        return base_price

    def get_description(self) -> str:
        return "Tarif Standard (Sans frais supp.)"

class RabatPricingStrategy(PricingStrategy):
    """Stratégie pour Rabat : on ajoute 20% de TVA au prix de base."""
    
    def calculate_price(self, base_price: float) -> float:
        # base_price * 1.20 ajoute 20%
        return base_price * 1.20 

    def get_description(self) -> str:
        return "Tarif Rabat (TVA 20% incluse)"

class CasablancaPricingStrategy(PricingStrategy):
    """Stratégie pour Casablanca : frais fixe de 50 DH pour le déplacement."""
    
    def calculate_price(self, base_price: float) -> float:
        return base_price + 50 

    def get_description(self) -> str:
        return "Tarif Casa (+50 DH Déplacement)"

class PricingFactory:
    """
    Le Design Pattern "Factory" (Usine).
    Comme pour les Utilisateurs (UserFactory), on utilise une usine pour
    décider automatiquement quelle Stratégie instancier en fonction du nom de la ville.
    """
    
    @staticmethod
    def get_strategy(ville: str) -> PricingStrategy:
        # On nettoie la chaîne (minuscules, on enlève les espaces autour) pour éviter les erreurs
        ville_propre = ville.lower().strip()
        
        if ville_propre == "rabat":
            return RabatPricingStrategy()
            
        elif ville_propre == "casablanca" or ville_propre == "casa":
            return CasablancaPricingStrategy()
            
        else:
            # Si on ne connaît pas la ville (ou si elle est vide), on retourne la stratégie standard
            return StandardPricingStrategy()

