from abc import ABC, abstractmethod

# --- Abstract Product (Produit Abstrait) ---
class User(ABC):
    """
    La classe User est une classe "abstraite" (qui hérite de ABC).
    Cela signifie qu'on ne peut pas créer un simple "User" directement.
    Un utilisateur doit toujours être soit un Client, une Entreprise, ou un Admin.
    Cette classe sert de "moule" ou de "modèle de base" contenant les informations communes
    à tous les utilisateurs (nom, email, etc.).
    """
    
    def __init__(self, nom, email, password, telephone=None, id=None, ville=None, adresse=None, is_banned=False):
        # Initialisation des attributs communs à chaque utilisateur
        self.id = id
        self.nom = nom
        self.email = email
        self.password = password
        self.telephone = telephone
        self.ville = ville
        self.adresse = adresse
        self.is_banned = is_banned
        
        # Le rôle n'est pas défini ici, il sera défini par les classes "filles" (Client, Admin, etc.)
        self.role = None

    def __str__(self):
        """
        La méthode magique __str__ permet de définir comment afficher cet objet
        quand on utilise la fonction print().
        """
        # Si on n'a pas de ville, on affiche l'email à la place
        information_secondaire = self.ville if self.ville is not None else self.email
        return f"[{self.role}] {self.nom} ({information_secondaire})"

# --- Concrete Products (Produits Concrets) ---
# Ces classes "héritent" de la classe User. 
# Elles récupèrent tous les attributs et méthodes de User automatiquement.

class Client(User):
    """Classe représentant un client normal."""
    def __init__(self, nom, email, password, telephone=None, id=None, ville=None, adresse=None, is_banned=False):
        # La fonction super() permet d'appeler le __init__ de la classe parent (User)
        # pour éviter de réécrire l'initialisation de nom, email, etc.
        super().__init__(nom, email, password, telephone, id, ville, adresse, is_banned)
        
        # On définit le rôle spécifique à cette classe
        self.role = "CLIENT"

class Admin(User):
    """Classe représentant un administrateur du système."""
    def __init__(self, nom, email, password, telephone=None, id=None, ville=None, adresse=None, is_banned=False):
        super().__init__(nom, email, password, telephone, id, ville, adresse, is_banned)
        self.role = "ADMIN"

class Enterprise(User):
    """Classe représentant une entreprise partenaire."""
    def __init__(self, nom, email, password, telephone=None, id=None, ville=None, adresse=None, is_banned=False):
        super().__init__(nom, email, password, telephone, id, ville, adresse, is_banned)
        self.role = "ENTREPRISE"

# --- Creator (Factory) ---
class UserFactory:
    """
    Le Design Pattern "Factory" (Usine ou Fabrique) :
    Au lieu de demander au programmeur de devoir savoir quelle classe instancier (Client, Admin ou Enterprise),
    on centralise la création dans cette "usine". 
    On donne juste une chaîne de caractères (le rôle) à la méthode create_user, 
    et l'usine nous construit le bon objet.
    """
    
    @classmethod
    def create_user(cls,role, nom, email, password, telephone=None, ville=None, adresse=None, is_banned=False, **kwargs):
    
        # On met le rôle en majuscule pour éviter les erreurs de casse (ex: "client" -> "CLIENT")
        role_en_majuscule = role.upper()
        
        # On vérifie le rôle et on retourne l'objet correspondant
        if role_en_majuscule == "CLIENT":
            return Client(nom, email, password, telephone, ville=ville, adresse=adresse, is_banned=is_banned)
        
        elif role_en_majuscule == "ENTREPRISE":
            return Enterprise(nom, email, password, telephone, ville=ville, adresse=adresse, is_banned=is_banned)
            
        elif role_en_majuscule == "ADMIN":
            return Admin(nom, email, password, telephone, ville=ville, adresse=adresse, is_banned=is_banned)
            
        else:
            # Si le rôle n'existe pas, on lève une exception (erreur)
            raise ValueError(f"Erreur : Le rôle spécifié ({role}) est inconnu.")

