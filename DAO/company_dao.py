from Config.database import DatabaseConnection
from models.company import Company, CatalogItem, ServiceType, SubscriptionPlan

"""
CompanyDAO (Data Access Object pour les Entreprises).
Cette classe regroupe toutes les requêtes SQL (CRUD) liées aux entreprises 
et à leur catalogue de services.
"""

class CompanyDAO:
    def __init__(self):
        # On instancie la connexion (Singleton)
        self.db = DatabaseConnection()

    def create_company(self, company: Company):
        """Ajoute une nouvelle entreprise dans la base de données."""
        connection = self.db.get_connection()
        if not connection: 
            return None
            
        cursor = connection.cursor()
        try:
            # CURDATE() donne la date d'aujourd'hui. 
            # DATE_ADD permet d'ajouter 30 jours pour l'expiration de l'abonnement.
            query = """
                INSERT INTO companies 
                (user_id, nom_entreprise, description, ville, contact_phone, contact_email, is_verified, subscription_plan_id, subscription_start, subscription_expires_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, CURDATE(), DATE_ADD(CURDATE(), INTERVAL 30 DAY))
            """
            valeurs = (
                company.user_id, company.nom_entreprise, company.description, 
                company.ville, company.contact_phone, company.contact_email, 
                company.is_verified, company.subscription_plan_id
            )
            
            cursor.execute(query, valeurs)
            connection.commit()
            
            # On récupère l'ID généré et on le met dans l'objet
            company.id = cursor.lastrowid
            return company
            
        except Exception as erreur:
            print(f"Erreur lors de la création de l'entreprise : {erreur}")
            return None
            
        finally:
            cursor.close()

    def update_company(self, company_id, nom=None, description=None, ville=None, contact_phone=None, contact_email=None):
        """Met à jour les informations d'une entreprise (uniquement les champs fournis)."""
        connection = self.db.get_connection()
        if not connection: 
            return False
            
        cursor = connection.cursor()
        try:
            fields = []
            params = []
            
            # On construit la requête de mise à jour de manière dynamique
            if nom is not None: 
                fields.append("nom_entreprise = %s")
                params.append(nom)
            if description is not None: 
                fields.append("description = %s")
                params.append(description)
            if ville is not None: 
                fields.append("ville = %s")
                params.append(ville)
            if contact_phone is not None: 
                fields.append("contact_phone = %s")
                params.append(contact_phone)
            if contact_email is not None: 
                fields.append("contact_email = %s")
                params.append(contact_email)
                
            # Si aucun champ n'a été fourni, on s'arrête là
            if len(fields) == 0: 
                return False
                
            # On ajoute l'ID à la fin des paramètres pour la clause WHERE
            params.append(company_id)
            
            # Assemblage de la requête finale (ex: UPDATE companies SET ville = %s WHERE id = %s)
            sql = f"UPDATE companies SET {', '.join(fields)} WHERE id = %s"
            
            cursor.execute(sql, tuple(params))
            connection.commit()
            return True
            
        except Exception as erreur:
            print(f"Erreur lors de la mise à jour de l'entreprise : {erreur}")
            return False
            
        finally: 
            cursor.close()

    def delete_company(self, company_id):
        """Supprime une entreprise."""
        connection = self.db.get_connection()
        if not connection: return False
        cursor = connection.cursor()
        try:
            cursor.execute("DELETE FROM companies WHERE id = %s", (company_id,))
            connection.commit()
            return True
        except Exception as erreur:
            print(f"Erreur lors de la suppression de l'entreprise : {erreur}")
            return False
        finally: 
            cursor.close()

    def verify_company(self, company_id, verified=True):
        """Valide (ou invalide) une entreprise par un administrateur."""
        connection = self.db.get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("UPDATE companies SET is_verified = %s WHERE id = %s", (verified, company_id))
            connection.commit()
            return True
        except Exception: 
            return False
        finally: 
            cursor.close()

    def add_service_to_catalog(self, catalog_item: CatalogItem):
        """Ajoute une nouvelle offre (prestation) dans le catalogue d'une entreprise."""
        connection = self.db.get_connection()
        cursor = connection.cursor()
        try:
            query = """
                INSERT INTO catalog 
                (company_id, service_type_id, prix_base, prix_par_unite, unite_nom, description_offre, produits_inclus, duree_estimee)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            valeurs = (
                catalog_item.company_id, 
                catalog_item.service_type.id, 
                catalog_item.prix_base,
                catalog_item.prix_par_unite, 
                catalog_item.unite_nom, 
                catalog_item.description_offre,
                catalog_item.produits_inclus, 
                catalog_item.duree_estimee
            )
            cursor.execute(query, valeurs)
            connection.commit()
            
            # On sauvegarde l'ID généré
            catalog_item.id = cursor.lastrowid
            return True
            
        except Exception as erreur:
            print(f"Erreur d'ajout au catalogue : {erreur}")
            return False
            
        finally: 
            cursor.close()

    def remove_from_catalog(self, catalog_id):
        """Supprime une offre du catalogue."""
        connection = self.db.get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("DELETE FROM catalog WHERE id = %s", (catalog_id,))
            connection.commit()
            return True
        except Exception: 
            return False
        finally: 
            cursor.close()

    def get_all_companies(self, ville_filter=None):
        """
        Récupère toutes les entreprises VÉRIFIÉES ayant un abonnement ACTIF.
        (C'est ce que les clients voient).
        """
        connection = self.db.get_connection()
        if not connection: 
            return []
            
        cursor = connection.cursor(dictionary=True)
        try:
            # On utilise un LEFT JOIN pour combiner la table companies avec la table subscription_plans
            # Cela permet de récupérer le nom du plan (ex: "Premium") en une seule requête.
            sql = """
                SELECT c.*, sp.nom as plan_nom, sp.prix_mensuel 
                FROM companies c 
                LEFT JOIN subscription_plans sp ON c.subscription_plan_id = sp.id
                WHERE c.is_verified = TRUE AND c.subscription_expires_at >= CURDATE()
            """
            params = []
            
            # Filtre optionnel par ville
            if ville_filter is not None:
                sql = sql + " AND c.ville = %s"
                params.append(ville_filter)
                
            cursor.execute(sql, tuple(params))
            
            # On transforme chaque ligne retournée par la base de données en objet Company (via _map_company)
            lignes = cursor.fetchall()
            entreprises = []
            for ligne_db in lignes:
                entreprise_obj = self._map_company(ligne_db)
                entreprises.append(entreprise_obj)
                
            return entreprises
            
        finally: 
            cursor.close()

    def get_all_companies_admin(self):
        """L'Administrateur peut voir TOUTES les entreprises (même non vérifiées ou expirées)."""
        connection = self.db.get_connection()
        if not connection: return []
        cursor = connection.cursor(dictionary=True)
        try:
            sql = """
                SELECT c.*, sp.nom as plan_nom, sp.prix_mensuel, u.email as user_email
                FROM companies c
                LEFT JOIN subscription_plans sp ON c.subscription_plan_id = sp.id
                LEFT JOIN users u ON c.user_id = u.id
                ORDER BY c.id
            """
            cursor.execute(sql)
            return cursor.fetchall()  # On renvoie directement les dictionnaires pour l'admin
        finally: 
            cursor.close()

    def get_companies_by_service(self, service_type_id):
        """Trouve les entreprises proposant un type de service précis."""
        connection = self.db.get_connection()
        if not connection: return []
        cursor = connection.cursor(dictionary=True)
        try:
            # On doit faire la jointure entre companies, le catalogue (pour savoir si elles l'offrent), et les abonnements.
            sql = """
                SELECT c.*, cat.id as catalog_id, cat.prix_base, cat.prix_par_unite, cat.unite_nom,
                       cat.description_offre, cat.produits_inclus, cat.duree_estimee,
                       sp.nom as plan_nom,
                       c.horaire_debut, c.horaire_fin, c.jours_travail
                FROM companies c
                JOIN catalog cat ON c.id = cat.company_id
                LEFT JOIN subscription_plans sp ON c.subscription_plan_id = sp.id
                WHERE cat.service_type_id = %s 
                  AND c.is_verified = TRUE 
                  AND c.subscription_expires_at >= CURDATE()
            """
            cursor.execute(sql, (service_type_id,))
            return cursor.fetchall()
        finally: 
            cursor.close()

    def get_catalog(self, company_id):
        """Récupère toutes les offres du catalogue d'une entreprise spécifique."""
        connection = self.db.get_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            sql = """
                SELECT c.*, s.nom_service, s.description as type_desc, s.category
                FROM catalog c 
                JOIN service_types s ON c.service_type_id = s.id
                WHERE c.company_id = %s
            """
            cursor.execute(sql, (company_id,))
            
            liste_offres = []
            for row in cursor.fetchall():
                # On recrée d'abord l'objet ServiceType
                st = ServiceType(
                    id=row['service_type_id'], 
                    nom_service=row['nom_service'], 
                    description=row['type_desc'], 
                    category=row.get('category')
                )
                
                # Puis on recrée l'objet CatalogItem qui contient notre ServiceType
                item = CatalogItem(
                    id=row['id'], 
                    company_id=row['company_id'], 
                    service_type=st,
                    prix_base=row['prix_base'], 
                    prix_par_unite=row['prix_par_unite'],
                    unite_nom=row['unite_nom'], 
                    description_offre=row['description_offre'],
                    produits_inclus=row.get('produits_inclus'), 
                    duree_estimee=row.get('duree_estimee')
                )
                liste_offres.append(item)
                
            return liste_offres
            
        finally: 
            cursor.close()

    def get_company_by_user_id(self, user_id):
        """Récupère le profil entreprise complet via l'ID de l'utilisateur."""
        connection = self.db.get_connection()
        if not connection: return None
        cursor = connection.cursor(dictionary=True)
        try:
            sql = """
                SELECT c.*, sp.nom as plan_nom, sp.has_scheduling, sp.has_analytics, sp.has_priority_support, sp.max_services
                FROM companies c
                LEFT JOIN subscription_plans sp ON c.subscription_plan_id = sp.id
                WHERE c.user_id = %s
            """
            cursor.execute(sql, (user_id,))
            row = cursor.fetchone()
            
            if row: 
                # On convertit le résultat de la BD en objet métier
                return self._map_company(row)
                
            return None
        finally: 
            cursor.close()

    def get_service_types(self):
        """Récupère toutes les catégories de services disponibles globalement."""
        connection = self.db.get_connection()
        if not connection: return []
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM service_types ORDER BY category, nom_service")
            
            liste_services = []
            for r in cursor.fetchall():
                service = ServiceType(
                    id=r['id'], 
                    nom_service=r['nom_service'], 
                    description=r['description'], 
                    category=r.get('category')
                )
                liste_services.append(service)
                
            return liste_services
        finally: 
            cursor.close()

    def add_service_type(self, nom, description, category):
        """Permet à l'Admin d'ajouter une nouvelle catégorie de service globale."""
        connection = self.db.get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("INSERT INTO service_types (nom_service, description, category) VALUES (%s, %s, %s)", (nom, description, category))
            connection.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Erreur lors de l'ajout d'une catégorie : {e}")
            return None
        finally: 
            cursor.close()

    def _map_company(self, row):
        """
        Méthode interne (commençant par '_') utilisée pour éviter de répéter du code.
        Elle prend un dictionnaire issu de MySQL (row) et construit l'objet Python "Company".
        """
        plan_abonnement = None
        
        # Si la requête SQL a remonté des informations sur l'abonnement
        if row.get('plan_nom') is not None:
            plan_abonnement = SubscriptionPlan(
                id=row.get('subscription_plan_id'),
                nom=row.get('plan_nom'),
                has_scheduling=row.get('has_scheduling', False),
                has_analytics=row.get('has_analytics', False),
                has_priority_support=row.get('has_priority_support', False),
                max_services=row.get('max_services', 5)
            )
            
        # Création et retour de l'objet d'entreprise final
        entreprise = Company(
            id=row['id'], 
            user_id=row['user_id'], 
            nom_entreprise=row['nom_entreprise'],
            description=row['description'], 
            ville=row['ville'],
            contact_phone=row.get('contact_phone'), 
            contact_email=row.get('contact_email'),
            horaire_debut=row.get('horaire_debut', '08:00'),
            horaire_fin=row.get('horaire_fin', '18:00'),
            jours_travail=row.get('jours_travail', 'Lun-Sam'),
            is_verified=row['is_verified'],
            subscription_plan_id=row.get('subscription_plan_id'),
            subscription_start=str(row.get('subscription_start') or ''),
            subscription_expires_at=str(row.get('subscription_expires_at') or ''),
            subscription_plan=plan_abonnement
        )
        return entreprise