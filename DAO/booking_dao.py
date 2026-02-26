from Config.database import DatabaseConnection

"""
BookingDAO (Data Access Object pour les Réservations).
Gère toutes les requêtes SQL liées aux interventions (création, confirmation, annulation, rapports).
"""

class BookingDAO:
    def __init__(self):
        # Initialisation de la connexion à la base de données
        self.db = DatabaseConnection()

    def create_booking(self, client_id, company_id, service_type_id, catalog_id, quantite, prix_total, description, rdv_date, rdv_heure, mode_paiement='ONLINE'):
        """Insère une nouvelle réservation dans la base, avec le statut par défaut 'EN_ATTENTE'."""
        connection = self.db.get_connection()
        if not connection: 
            return None
            
        cursor = connection.cursor()
        try:
            query = """
                INSERT INTO bookings 
                (client_id, company_id, service_type_id, catalog_id, quantite, prix_total, description_client, rdv_date, rdv_heure, mode_paiement, statut)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'EN_ATTENTE')
            """
            valeurs = (client_id, company_id, service_type_id, catalog_id, quantite, prix_total, description, rdv_date, rdv_heure, mode_paiement)
            
            cursor.execute(query, valeurs)
            connection.commit()
            
            # On retourne l'ID de la réservation nouvellement créée
            return cursor.lastrowid
            
        except Exception as erreur:
            print(f" Erreur lors de la création de la réservation : {erreur}")
            return None
            
        finally: 
            cursor.close()

    def confirm_booking(self, booking_id, supervisor_contact):
        """
        L'entreprise confirme la réservation. 
        On récupère la date et l'heure déjà choisies par le client pour créer la 'date_debut_prevue',
        et on passe le statut à 'CONFIRMEE'.
        """
        connection = self.db.get_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            # 1. On récupère la date et l'heure du RDV depuis la base
            cursor.execute("SELECT rdv_date, rdv_heure FROM bookings WHERE id = %s", (booking_id,))
            booking = cursor.fetchone()
            
            if not booking:
                return False
                
            # 2. On construit la chaîne de caractères finale (YYYY-MM-DD HH:MM:00)
            rdv_date = str(booking['rdv_date'])
            rdv_heure = booking['rdv_heure'] or '08:00'
            date_debut = f"{rdv_date} {rdv_heure}:00"
            
            # 3. On met à jour la réservation
            sql = """
                UPDATE bookings 
                SET statut = 'CONFIRMEE', date_debut_prevue = %s, technician_superior_contact = %s 
                WHERE id = %s
            """
            cursor.execute(sql, (date_debut, supervisor_contact, booking_id))
            connection.commit()
            return True
            
        except Exception as erreur:
            print(f" Erreur lors de la confirmation : {erreur}")
            return False
            
        finally: 
            cursor.close()

    def cancel_booking(self, booking_id, client_id):
        """
        Le client annule sa réservation. 
        Possible UNIQUEMENT si le statut est 'EN_ATTENTE' ou 'PAYEE'.
        """
        connection = self.db.get_connection()
        cursor = connection.cursor()
        try:
            sql = "UPDATE bookings SET statut = 'ANNULEE_CLIENT' WHERE id = %s AND client_id = %s AND statut IN ('EN_ATTENTE', 'PAYEE')"
            cursor.execute(sql, (booking_id, client_id))
            connection.commit()
            
            # rowcount indique combien de lignes ont été modifiées. 
            # Si c'est > 0, l'annulation a marché. Si c'est 0, ça veut dire que la condition (statut ou client_id) n'était pas remplie.
            return cursor.rowcount > 0
            
        except Exception as erreur:
            print(f" Erreur lors de l'annulation : {erreur}")
            return False
            
        finally: 
            cursor.close()

    def submit_report(self, booking_id, rapport_avant, rapport_apres, rapport_details):
        """L'entreprise soumet un rapport de fin d'intervention. Le statut passe à 'TERMINEE'."""
        connection = self.db.get_connection()
        cursor = connection.cursor()
        try:
            sql = """
                UPDATE bookings 
                SET statut = 'TERMINEE', rapport_avant = %s, rapport_apres = %s, rapport_details = %s 
                WHERE id = %s
            """
            cursor.execute(sql, (rapport_avant, rapport_apres, rapport_details, booking_id))
            connection.commit()
            return True
            
        except Exception as erreur:
            print(f" Erreur lors de la soumission du rapport : {erreur}")
            return False
            
        finally: 
            cursor.close()

    def update_status(self, booking_id, new_status):
        """Mise à jour générique du statut d'une réservation."""
        connection = self.db.get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("UPDATE bookings SET statut = %s WHERE id = %s", (new_status, booking_id))
            connection.commit()
            return True
        except Exception: 
            return False
        finally: 
            cursor.close()

    def get_client_bookings(self, client_id):
        """
        Récupère l'historique des réservations d'un client.
        Utilise des 'JOIN' pour récupérer aussi le nom de l'entreprise et le nom du service 
        plutôt que de n'avoir que leurs IDs.
        """
        connection = self.db.get_connection()
        if not connection: return []
        cursor = connection.cursor(dictionary=True)
        try:
            sql = """
                SELECT b.*, c.nom_entreprise, s.nom_service
                FROM bookings b
                JOIN companies c ON b.company_id = c.id
                JOIN service_types s ON b.service_type_id = s.id
                WHERE b.client_id = %s 
                ORDER BY b.date_demande DESC
            """
            cursor.execute(sql, (client_id,))
            return cursor.fetchall()
        finally: 
            cursor.close()

    def get_company_bookings(self, company_id):
        """Même principe que get_client_bookings, mais pour l'historique de l'entreprise."""
        connection = self.db.get_connection()
        if not connection: return []
        cursor = connection.cursor(dictionary=True)
        try:
            sql = """
                SELECT b.*, u.nom as client_nom, u.telephone as client_tel, u.ville as client_ville, s.nom_service
                FROM bookings b
                JOIN users u ON b.client_id = u.id
                JOIN service_types s ON b.service_type_id = s.id
                WHERE b.company_id = %s 
                ORDER BY b.date_demande DESC
            """
            cursor.execute(sql, (company_id,))
            return cursor.fetchall()
        finally: 
            cursor.close()

    def get_all_bookings(self):
        """Admin : voit toutes les réservations du système."""
        connection = self.db.get_connection()
        if not connection: return []
        cursor = connection.cursor(dictionary=True)
        try:
            sql = """
                SELECT b.*, u.nom as client_nom, c.nom_entreprise, s.nom_service
                FROM bookings b
                JOIN users u ON b.client_id = u.id
                JOIN companies c ON b.company_id = c.id
                JOIN service_types s ON b.service_type_id = s.id
                ORDER BY b.date_demande DESC
            """
            cursor.execute(sql)
            return cursor.fetchall()
        finally: 
            cursor.close()

    def get_stats(self):
        """
        Récupère des statistiques globales pour le Dashboard Administrateur.
        Utilise des fonctions SQL (COUNT, SUM, CASE WHEN) pour tout calculer en une seule requête optimisée.
        """
        connection = self.db.get_connection()
        if not connection: return {}
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_demandes,
                    SUM(CASE WHEN statut = 'TERMINEE' THEN 1 ELSE 0 END) as terminees,
                    SUM(CASE WHEN statut = 'EN_ATTENTE' THEN 1 ELSE 0 END) as en_attente,
                    SUM(CASE WHEN statut = 'CONFIRMEE' THEN 1 ELSE 0 END) as confirmees,
                    SUM(CASE WHEN statut = 'REFUSEE' THEN 1 ELSE 0 END) as refusees,
                    SUM(CASE WHEN statut = 'ANNULEE_CLIENT' THEN 1 ELSE 0 END) as annulees_client,
                    COALESCE(SUM(CASE WHEN statut = 'TERMINEE' THEN prix_total ELSE 0 END), 0) as chiffre_affaires
                FROM bookings
            """)
            return cursor.fetchone()
        finally: 
            cursor.close()

    def add_review(self, booking_id, client_id, rating, comment):
        """Prend en compte l'avis d'un client et lui attribue une note."""
        connection = self.db.get_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            # 1. Vérifie que la réservation existe et appartient au client
            cursor.execute("SELECT id, statut FROM bookings WHERE id = %s AND client_id = %s", (booking_id, client_id))
            booking = cursor.fetchone()
            
            if not booking:
                return False, "Réservation introuvable ou ne vous appartient pas."
                
            # 2. Vérifie que le statut est bien 'TERMINEE'
            if booking['statut'] != 'TERMINEE':
                return False, f"Impossible de noter (statut : {booking['statut']}). Le service doit être TERMINÉ."
                
            # 3. Vérifie que le client n'a pas déjà noté cette intervention
            cursor.execute("SELECT id FROM reviews WHERE booking_id = %s", (booking_id,))
            if cursor.fetchone():
                return False, "Vous avez déjà noté ce service."
                
            # 4. Insertion de la note
            cursor.execute("INSERT INTO reviews (booking_id, client_id, rating, comment) VALUES (%s, %s, %s, %s)", 
                          (booking_id, client_id, rating, comment))
            connection.commit()
            
            # On renvoie un Tuple (Réussite: True/False, Message)
            return True, "Merci pour votre avis !"
            
        except Exception as erreur:
            return False, f"Erreur : {erreur}"
            
        finally: 
            cursor.close()

    def get_booked_slots(self, company_id, date):
        """
        Vérifie tous les créneaux déjà réservés pour une entreprise donnée à une date précise.
        Cela permet à OptiVolt de ne pas proposer ces mêmes créneaux aux futurs clients.
        """
        connection = self.db.get_connection()
        if not connection: return []
        cursor = connection.cursor(dictionary=True)
        try:
            sql = """
                SELECT rdv_heure FROM bookings 
                WHERE company_id = %s AND rdv_date = %s 
                AND statut NOT IN ('REFUSEE', 'ANNULEE', 'ANNULEE_CLIENT')
            """
            cursor.execute(sql, (company_id, date))
            
            # On transforme la liste de dictionnaires en une liste simple d'heures (ex: ['10:00', '14:00'])
            return [row['rdv_heure'] for row in cursor.fetchall()]
            
        finally: 
            cursor.close()


