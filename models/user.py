from abc import ABC

class User(ABC):
    def __init__(self,id,nom,email,password,telphone,ville,adresse,is_banned=False,role='user'):
        self.id=id
        self.nom=nom
        self.email=email
        self.password=password
        self.telphone=telphone
        self.ville=ville
        self.adresse=adresse
        self.is_banned=is_banned
        self.role=role
    def __str__(self):
        return f"User(id={self.id}, nom='{self.nom}', email='{self.email}', password='{self.password}', telphone='{self.telphone}', ville='{self.ville}', adresse='{self.adresse}', id_banned={self.is_banned}, role='{self.role}')"
    
    
class Client(User):
    def __init__(self, id, nom, email, password, telphone, ville, adresse,is_banned=False):
        super().__init__(id, nom, email, password, telphone, ville, adresse,is_banned)
        self.role='client'
        
class Entreprise(User):
    def __init__(self, id, nom, email, password, telphone, ville, adresse,is_banned=False):
        super().__init__(id, nom, email, password, telphone, ville, adresse,is_banned)
        self.role='entreprise'
        
class Admin(User):
    def __init__(self, id, nom, email, password, telphone, ville, adresse,is_banned=False):
        super().__init__(id, nom, email, password, telphone, ville, adresse,is_banned)
        self.role='admin'
        
class UserFactory:
    @classmethod
    def create_user(cls, role, id, nom, email, password, telphone, ville, adresse, is_banned=False):
        role = role.upper()
        if role == 'CLIENT':
            return Client(id, nom, email, password, telphone, ville, adresse,is_banned)
        elif role == 'ENTREPRISE':
            return Entreprise(id, nom, email, password, telphone, ville, adresse,is_banned)
        elif role == 'ADMIN':
            return Admin(id, nom, email, password, telphone, ville, adresse,is_banned)
        else:
            raise ValueError(f"Role '{role}' non reconnu.")
        
user = UserFactory.create_user(
    "admin", 1, "Ali", "ali@mail.com", "1234",
    "0600000000", "Casablanca", "Centre ville"
)

print(user)