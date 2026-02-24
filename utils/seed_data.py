from faker import Faker
from Config.database import DatabaseConnection
from models.user import UserFactory
from DAO.user_dao import UserDAO
from DAO.company_dao import CompanyDAO
from DAO.subscription_dao import SubscriptionDAO
from models.company import Company, CatalogItem, ServiceType
from Config.settings import Config
from utils.logger import Logger
import random

"""
Script de 'Seeding' (Remplissage) de la base de données.
Permet d'insérer de fausses données (mocks) dans la base pour pouvoir tester l'application 
sans avoir à tout créer à la main.
Le module 'Faker' est très connu pour générer des faux noms, adresses, emails réalistes.
"""

# On initialise le générateur de fausses données en français
fake = Faker('fr_FR')
logger = Logger()

# Quelques exemples de produits pour rendre le catalogue réaliste
PRODUITS = [
    "Eau déminéralisée, Raclettes pro, Chiffons microfibre",
    "Nettoyeur haute pression Kärcher, Savon biodégradable",
    "Onduleur SMA Sunny Boy 5.0, Câbles DC 6mm²",
    "Multimètre Fluke, Caméra thermique FLIR",
    "Panneaux JA Solar 550W, Rails K2, Micro-onduleurs Enphase",
    "Kit de maintenance préventive, Graisse silicone, Connecteurs MC4",
]

DUREES = ["1h", "2h", "3h", "½ journée", "1 jour", "2 jours"]

def seed_data():
    print("🌱 Démarrage du remplissage (Seeding) de OptiVolt Marketplace...")
    
    # 1. Connexion à la base
    db = DatabaseConnection()
    db.connect(Config.DB_HOST, Config.DB_USER, Config.DB_PASSWORD, Config.DB_NAME)
    
    # Initialisation de nos outils pour interagir avec la base
    user_dao = UserDAO()
    company_dao = CompanyDAO()
    subscription_dao = SubscriptionDAO()

    # 2. Création de l'Administrateur par défaut
    admin = UserFactory.create_user("ADMIN", "Admin OptiVolt", "admin@optivolt.ma", "admin123", "0600000000", ville="Rabat")
    
    # On vérifie qu'il n'existe pas déjà avant de le créer
    if not user_dao.find_by_login(admin.email):
        user_dao.create(admin)
        print(" Compte Administrateur créé.")
    logger.log_info("Seed: Admin créé.")

    # 3. Récupération des Types de Services de base et des Plans d'abonnements
    connection = db.get_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM service_types")
    
    # On transforme les résultats SQL en objets Python
    service_types = [ServiceType(id=r['id'], nom_service=r['nom_service'], description=r['description'], category=r.get('category')) for r in cursor.fetchall()]
    cursor.close()
    
    plans = subscription_dao.get_all_plans()
    
    if not plans:
        print(" Aucun plan d'abonnement trouvé. Exécutez d'abord le db_init.py pour charger le schema.")
        return
    if not service_types:
        print(" Aucun service type trouvé.")
        return

    # 4. Création de fausses Entreprises
    villes = ["Casablanca", "Rabat", "Marrakech", "Tanger", "Fès"]
    companies_created = 0
    
    for _ in range(5):
        # Faker invente des informations d'entreprise
        nom = fake.company()
        email = fake.company_email()
        ville = random.choice(villes)
        plan = random.choice(plans) # L'entreprise prend un abonnement au hasard

        # Étape A: Créer le compte Utilisateur de l'entreprise
        company_user = UserFactory.create_user("ENTREPRISE", nom, email, "1234", fake.phone_number(), ville=ville, adresse=fake.address())
        created_user = user_dao.create(company_user)
        
        if created_user:
            # Étape B: Créer le profil Entreprise avec son abonnement
            comp = Company(
                user_id=created_user.id,
                nom_entreprise=nom,
                description=fake.catch_phrase(),
                ville=ville,
                contact_phone=fake.phone_number(),
                contact_email=email,
                is_verified=True,
                subscription_plan_id=plan.id
            )
            created_comp = company_dao.create_company(comp)
            
            if created_comp:
                # Étape C: Ajouter des offres au catalogue de l'entreprise
                # Plus le plan est cher, plus on peut avoir d'offres
                nb_services = random.randint(2, min(4, plan.max_services))
                for _ in range(nb_services):
                    st = random.choice(service_types)
                    item = CatalogItem(
                        company_id=created_comp.id,
                        service_type=st,
                        prix_base=random.randint(100, 800),
                        prix_par_unite=random.randint(15, 80),
                        unite_nom="panneau",
                        description_offre=fake.sentence(),
                        produits_inclus=random.choice(PRODUITS),
                        duree_estimee=random.choice(DUREES)
                    )
                    # On insère le service fictif dans la base
                    company_dao.add_service_to_catalog(item)
                    
                companies_created += 1
    
    print(f"{companies_created} Entreprises factices créées avec catalogues et abonnements.")
    logger.log_info(f"Seed: {companies_created} entreprises créées.")

    # 5. Création de faux Clients
    for _ in range(5):
        ville = random.choice(villes)
        client = UserFactory.create_user("CLIENT", fake.name(), fake.email(), "1234", fake.phone_number(), ville=ville, adresse=fake.address())
        user_dao.create(client)
    
    print(" 5 Clients factices créés.")
    logger.log_info("Seed: 5 clients créés.")
    print(" Nettoyage et remplissage (Seeding) terminés avec succès !")

# Exécutable directement via terminal
if __name__ == "__main__":
    seed_data()