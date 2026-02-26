from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt
from rich.columns import Columns
from rich import print as rprint
from datetime import datetime, timedelta

from Config.database import DatabaseConnection
from models.user import UserFactory
from DAO.user_dao import UserDAO
from DAO.company_dao import CompanyDAO
from DAO.booking_dao import BookingDAO
from DAO.subscription_dao import SubscriptionDAO
from services.catalog_service import CatalogService
from models.company import Company, CatalogItem
from Config.settings import Config
from utils.logger import Logger

"""
================================================================================
Fichier Principal (Point d'Entrée).
C'est ici que l'application démarre. On utilise la bibliothèque 'rich' pour 
créer une interface en ligne de commande (CLI) colorée et interactive.
================================================================================
"""

console = Console()
logger = Logger()

def print_header():
    """Affiche le grand titre de l'application."""
    console.print(Panel.fit("[bold yellow]  OPTIVOLT — MARKETPLACE SOLAIRE  [/bold yellow]", border_style="bright_blue"))

# ═══════════════════════════════════════════
#  MENU CLIENT
# ═══════════════════════════════════════════
def client_menu(user, catalog_service, booking_dao):
    """
    Boucle infinie du menu client. 
    Tant que le client ne choisit pas '0', on lui réaffiche les options.
    """
    while True:
        console.rule(f"[bold green] Espace Client : {user.nom}[/bold green]")
        console.print(f"[dim] {user.ville or 'Ville non définie'} | {user.email}[/dim]")
        
        # Options disponibles
        console.print("[1] Parcourir les Services")
        console.print("[2] Mes Réservations")
        console.print("[0] Déconnexion")
        
        # 'Prompt.ask' force l'utilisateur à choisir entre 1, 2 ou 0.
        choice = Prompt.ask("Choix", choices=["1", "2", "0"])

        if choice == "0":
            logger.log_info(f"Client {user.nom} déconnecté.")
            return # 'return' fait sortir de la fonction (et donc de la boucle infinie)

        elif choice == "1":
            browse_services(user, catalog_service, booking_dao)

        elif choice == "2":
            my_reservations(user, booking_dao)


def browse_services(user, catalog_service, booking_dao):
    """Processus de réservation : Catégorie -> Entreprise -> RDV -> Paiement."""
    # Étape 1 : Récupérer toutes les catégories de services
    service_types = catalog_service.get_service_types()
    if not service_types:
        console.print("[yellow]Aucun service disponible.[/yellow]")
        return

    console.rule("[cyan] Catégories de Services[/cyan]")
    
    # On groupe les services par catégorie dans un dictionnaire
    categories = {}
    for st in service_types:
        cat = st.category or 'Autre'
        categories.setdefault(cat, []).append(st)

    # Affichage des services regroupés
    for cat, services in categories.items():
        console.print(f"\n[bold magenta]── {cat} ──[/bold magenta]")
        for s in services:
            console.print(f"  [{s.id}] {s.nom_service} — [dim]{s.description}[/dim]")
            
    console.print("\n[0] ⬅ Retour")

    # On demande au client de taper l'identifiant (ID) du service qu'il désire
    sid = IntPrompt.ask("Choisir un Service (ID)")
    if sid == 0: return

    # On recherche l'objet 'service' correspondant à l'ID saisi
    selected_service = next((s for s in service_types if s.id == sid), None)
    if not selected_service:
        console.print("[red]Service non trouvé.[/red]")
        return

    logger.log_info(f"Client {user.nom} consulte service: {selected_service.nom_service}")

    # Étape 2 : Afficher les entreprises (sous forme de Cartes)
    companies = catalog_service.get_companies_for_service(sid)
    if not companies:
        console.print("[yellow]Aucune entreprise ne propose ce service actuellement.[/yellow]")
        return

    console.rule(f"[cyan] Entreprises proposant : {selected_service.nom_service}[/cyan]")
    cards = []
    comp_map = {}
    
    # Création visuelle d'une 'carte' par entreprise trouvée
    for i, c in enumerate(companies, 1):
        comp_map[i] = c
        horaire = f"{c.get('horaire_debut','08:00')}-{c.get('horaire_fin','18:00')}"
        
        card_text = (
            f"[bold]{c['nom_entreprise']}[/bold]\n"
            f" {c['ville']}\n"
            f" [green]{c['prix_base']} DH[/green] + {c['prix_par_unite']} DH/{c.get('unite_nom','unité')}\n"
            f" {c.get('produits_inclus') or 'Non spécifié'}\n"
            f" Durée: {c.get('duree_estimee') or 'Non spécifié'}\n"
            f" Horaires: {horaire} ({c.get('jours_travail','Lun-Sam')})\n"
            f" {c.get('description_offre') or ''}\n"
            f" Abonnement: [cyan]{c.get('plan_nom', 'N/A')}[/cyan]"
        )
        
        # 'Panel' dessine un joli carré autour du texte
        cards.append(Panel(card_text, title=f"[{i}]", border_style="blue", width=45))
    
    # 'Columns' permet d'afficher les cartes côte à côte
    console.print(Columns(cards, equal=True, expand=True))
    console.print("\n[0] ⬅ Retour")
    
    cidx = IntPrompt.ask("Choisir une Entreprise (N°)")
    if cidx == 0: return
    
    if cidx not in comp_map:
        console.print("[red]Choix invalide.[/red]")
        return

    selected = comp_map[cidx]
    logger.log_info(f"Client {user.nom} sélectionne entreprise: {selected['nom_entreprise']}")

    # Étape 3 : Confirmation & Choix de la Quantité
    console.rule(f"[green] Réservation chez {selected['nom_entreprise']}[/green]")
    qty = IntPrompt.ask(f"Quantité ({selected.get('unite_nom', 'panneau')}s)", default=1)
    
    # Calcul du prix via le 'Service' (qui utilise le pattern Stratégie)
    from optivolt.services.pricing_strategy import PricingFactory
    base = selected['prix_base'] + (selected['prix_par_unite'] * qty)
    strategy = PricingFactory.get_strategy(user.ville or "")
    prix_final = strategy.calculate_price(base)
    desc_prix = strategy.get_description()

    # Petit récapitulatif visuel
    console.print(Panel(
        f"Service: [bold]{selected_service.nom_service}[/bold]\n"
        f"Entreprise: {selected['nom_entreprise']}\n"
        f"Quantité: {qty}\n"
        f"Prix: [bold green]{prix_final:.2f} DH[/bold green] ({desc_prix})\n"
        f"Produits: {selected.get('produits_inclus') or 'N/A'}",
        title=" Récapitulatif", border_style="green"
    ))

    # Étape 4 : Choix de la Date et de l'Heure (RDV)
    # On fait appel à une fonction spéciale qui gère l'agenda
    rdv_date, rdv_heure = pick_available_slot(selected, booking_dao)
    
    # Si le client annule au moment de choisir la date, la commande est abandonnée
    if not rdv_date:
        console.print("[yellow]Réservation annulée.[/yellow]")
        return

    desc = Prompt.ask(" Détails / Adresse précise", default=user.adresse or "")
    mode = Prompt.ask(" Mode de paiement", choices=["ONLINE", "CASH"], default="ONLINE")

    # Étape finale : Validation
    console.print(Panel(
        f" RDV: [bold]{rdv_date}[/bold] à [bold]{rdv_heure}[/bold]\n"
        f" Paiement: {mode}\n"
        f" Total: [bold green]{prix_final:.2f} DH[/bold green]",
        title=" Confirmation Finale", border_style="cyan"
    ))
    
    console.print("[1]  Confirmer la réservation")
    console.print("[0]  Annuler")
    confirm = Prompt.ask("Choix", choices=["1", "0"])
    
    if confirm == "0":
        console.print("[yellow]Réservation annulée.[/yellow]")
        return

    # Si on arrive ici, on enregistre enfin en Base de Données !
    bid, prix = catalog_service.create_booking_request(
        user.id, selected['id'], selected_service.id, selected.get('catalog_id'),
        qty, desc, prix_final, rdv_date, rdv_heure, mode
    )
    
    if bid:
        logger.log_info(f"Réservation #{bid} créée par Client {user.nom} - {prix_final} DH")
        if mode == 'ONLINE':
            console.print("[bold green] Paiement en ligne simulé...  Accepté ![/bold green]")
            
        console.print(Panel(
            f"Commande [bold]#{bid}[/bold] enregistrée !\n"
            f"RDV confirmé: {rdv_date} à {rdv_heure}\n"
            f"Montant: {prix_final:.2f} DH ({mode})\n"
            f"L'entreprise vous attend à cette date.",
            title="Confirmation", border_style="green"
        ))


def pick_available_slot(company_data, booking_dao):
    """
    Fonction utilitaire pour proposer un choix de date/heure au client 
    en fonction des horaires de l'entreprise.
    Retourne la date (YYYY-MM-DD) et l'heure (HH:00) choisies.
    """
    h_debut = company_data.get('horaire_debut', '08:00')
    h_fin = company_data.get('horaire_fin', '18:00')
    jours = company_data.get('jours_travail', 'Lun-Sam')
    company_id = company_data['id']

    # On génère tous les créneaux horaire (ex: 08:00, 09:00, 10:00) 
    # de l'heure de début à l'heure de fin
    start_h = int(h_debut.split(':')[0])
    end_h = int(h_fin.split(':')[0])
    all_hours = [f"{h:02d}:00" for h in range(start_h, end_h)]

    # Dictionnaire pour traduire le mot du jour en Numéro (0=Lundi, 6=Dimanche)
    jour_map = {'Lun': 0, 'Mar': 1, 'Mer': 2, 'Jeu': 3, 'Ven': 4, 'Sam': 5, 'Dim': 6}
    working_days = set()
    
    # Comprendre si l'entreprise demande "Lun-Sam" (Plage) ou "Lun,Mar,Jeu" (Liste)
    if '-' in jours:
        parts = jours.split('-')
        start_day = jour_map.get(parts[0].strip(), 0)
        end_day = jour_map.get(parts[1].strip(), 5)
        working_days = set(range(start_day, end_day + 1))
    else:
        working_days = {jour_map.get(j.strip(), 0) for j in jours.split(',')}

    # 1. Montrer les dates disponibles (les 7 prochains jours ouvrés)
    console.rule(f"[cyan]Créneaux Disponibles — {company_data['nom_entreprise']}[/cyan]")
    console.print(f"[dim]Horaires: {h_debut} - {h_fin} | Jours: {jours}[/dim]\n")

    today = datetime.now().date()
    available_dates = []
    
    # On cherche dans les 21 prochains jours pour trouver 7 jours de travail effectifs
    for i in range(1, 22):  
        d = today + timedelta(days=i)
        # weekday() renvoie 0 pour Lundi, 6 pour Dimanche
        if d.weekday() in working_days:
            available_dates.append(d)
        if len(available_dates) >= 7:
            break

    jour_noms = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim']
    for idx, d in enumerate(available_dates, 1):
        nom_jour = jour_noms[d.weekday()]
        console.print(f"  [{idx}] {nom_jour} {d.strftime('%Y-%m-%d')}")
    console.print("  [0] ⬅ Retour")

    date_choice = IntPrompt.ask("Choisir une date (N°)")
    if date_choice == 0: return None, None
    if date_choice < 1 or date_choice > len(available_dates):
        console.print("[red]Choix invalide.[/red]")
        return None, None

    chosen_date = available_dates[date_choice - 1]
    date_str = chosen_date.strftime('%Y-%m-%d')

    # 2. Une fois la date choisie, afficher les HEURES Libres
    # On demande au DAO les heures qui sont DÉJÀ RÉSERVÉES
    booked = booking_dao.get_booked_slots(company_id, date_str)
    
    # Filtre magique en Python : Garder les heures qui ne sont PAS dans la liste des occupées
    free_hours = [h for h in all_hours if h not in booked]

    if not free_hours:
        console.print(f"[yellow]Aucun créneau libre le {date_str}. Choisissez un autre jour.[/yellow]")
        # S'il n'y a plus de place à date, on redemande (récursivité)
        return pick_available_slot(company_data, booking_dao)

    nom_jour = jour_noms[chosen_date.weekday()]
    console.rule(f"[cyan]Heures libres — {nom_jour} {date_str}[/cyan]")
    for idx, h in enumerate(free_hours, 1):
        console.print(f"  [{idx}] {h}")
        
    if booked:
        console.print(f"\n  [dim]Créneaux occupés dans la journée : {', '.join(booked)}[/dim]")
        
    console.print("  [0] ⬅ Retour")

    heure_choice = IntPrompt.ask("Choisir une heure (N°)")
    if heure_choice == 0: return None, None
    if heure_choice < 1 or heure_choice > len(free_hours):
        console.print("[red]Choix invalide.[/red]")
        return None, None

    return date_str, free_hours[heure_choice - 1]


def my_reservations(user, booking_dao):
    """Permet au client de voir, annuler, et noter ses propres réservations."""
    while True:
        bookings = booking_dao.get_client_bookings(user.id)
        if not bookings:
            console.print("[yellow]Aucune réservation.[/yellow]")
            return

        console.rule("[cyan]Mes Réservations[/cyan]")
        for b in bookings:
            # Code couleur visuel basé sur le statut
            style = {"CONFIRMEE": "green", "PAYEE": "yellow", "TERMINEE": "blue", "REFUSEE": "red", "ANNULEE_CLIENT": "dim"}.get(b['statut'], "white")
            
            console.print(Panel(
                f"Service: [bold]{b['nom_service']}[/bold] | Entreprise: {b['nom_entreprise']}\n"
                f"Statut: [{style}]{b['statut']}[/{style}] | Prix: {b['prix_total']} DH\n"
                f"RDV: {b.get('rdv_date') or '—'} à {b.get('rdv_heure') or '—'}\n"
                f"Superviseur: {b.get('technician_superior_contact') or 'En attente'}\n"
                f"Paiement: {b.get('mode_paiement', 'N/A')}",
                title=f"Réservation #{b['id']}", border_style=style
            ))

        console.print("\n[1] Annuler une réservation")
        console.print("[2] Noter un service terminé")
        console.print("[0] ⬅ Retour")
        choice = Prompt.ask("Choix", choices=["1", "2", "0"])

        if choice == "0": 
            return
            
        elif choice == "1":
            bid = IntPrompt.ask("ID de la réservation à annuler")
            # Le DAO vérifiera tout seul si l'annulation est valide (Si le service n'est pas déjà commencé)
            if booking_dao.cancel_booking(bid, user.id):
                logger.log_info(f"Client {user.nom} annule réservation #{bid}")
                console.print("[green] Réservation annulée.[/green]")
            else:
                console.print("[red]Impossible (déjà confirmée ou introuvable).[/red]")
                
        elif choice == "2":
            bid = IntPrompt.ask("ID de la réservation à noter")
            rating = IntPrompt.ask("Note (1-5)", default=5)
            comment = Prompt.ask("Commentaire (optionnel)", default="")
            
            # Le _Tuple_ reçu du DAO contient (Vrai/Faux, Le message textuel)
            success, msg = booking_dao.add_review(bid, user.id, rating, comment)
            if success:
                logger.log_info(f"Client {user.nom} note réservation #{bid}: {rating}/5")
                console.print(f"[green] {msg}[/green]")
            else:
                console.print(f"[red] {msg}[/red]")


# ═══════════════════════════════════════════
#  MENU ENTREPRISE
# ═══════════════════════════════════════════
def entreprise_menu(user, catalog_service, booking_dao, company_dao, subscription_dao):
    """
    Interface principale pour les entreprises prestataires.
    L'affichage dépend du type d'abonnement que l'Entreprise possède !
    """
    company = company_dao.get_company_by_user_id(user.id)
    if not company:
        console.print("[red]Profil entreprise introuvable. Contactez l'admin.[/red]")
        return

    while True:
        # On rafraîchit les infos de l'entreprise à chaque tour
        company = company_dao.get_company_by_user_id(user.id)
        plan = company.subscription_plan
        plan_nom = plan.nom if plan else "Aucun"

        console.rule(f"[bold blue] {company.nom_entreprise} — [{plan_nom}][/bold blue]")
        console.print("[1]  Traiter les Demandes")
        console.print("[2]  Mon Catalogue")
        console.print("[3]  Soumettre un Rapport")
        console.print("[4]  Modifier Infos Entreprise")
        console.print("[5]  Mon Abonnement")
        
        # Le planning n'est disponible que pour les plans qui incluent 'has_scheduling'
        if plan and plan.has_scheduling:
            console.print("[6] Planning [PRO]")
            
        console.print("[0] Déconnexion")

        choices = ["0", "1", "2", "3", "4", "5"]
        if plan and plan.has_scheduling:
             choices.append("6")
             
        choice = Prompt.ask("Choix", choices=choices)

        if choice == "0":
            logger.log_info(f"Entreprise {company.nom_entreprise} déconnectée.")
            return
        elif choice == "1": manage_demands(company, booking_dao)
        elif choice == "2": manage_catalog(company, company_dao, catalog_service)
        elif choice == "3": submit_report(company, booking_dao)
        elif choice == "4": edit_company(company, company_dao)
        elif choice == "5": view_subscription(company, subscription_dao)
        elif choice == "6": planning_view(company, booking_dao)


def manage_demands(company, booking_dao):
    """Permet à l'entreprise d'accepter une intervention et de nommer un responsable."""
    while True:
        bookings = booking_dao.get_company_bookings(company.id)
        if not bookings:
            console.print("[yellow]Aucune demande reçue.[/yellow]")
            return

        console.rule("[cyan] Demandes Clients[/cyan]")
        for b in bookings:
            style = {"CONFIRMEE": "green", "PAYEE": "yellow", "TERMINEE": "blue", "REFUSEE": "red", "ANNULEE_CLIENT": "dim"}.get(b['statut'], "white")
            console.print(Panel(
                f"Client: [bold]{b['client_nom']}[/bold] | Tel: {b['client_tel']} | Ville: {b.get('client_ville', '—')}\n"
                f"Service: {b['nom_service']} | Qté: {b['quantite']}\n"
                f"Statut: [{style}]{b['statut']}[/{style}] | Prix: {b['prix_total']} DH\n"
                f"RDV: [bold]{b.get('rdv_date') or '—'}[/bold] à [bold]{b.get('rdv_heure') or '—'}[/bold]\n"
                f"Paiement: {b.get('mode_paiement', 'N/A')}",
                title=f"Demande #{b['id']}", border_style=style
            ))

        console.print("\n[0] ⬅ Retour")
        bid = IntPrompt.ask("ID à traiter (0 retour)")
        if bid == 0: return

        # Recherche de la demande exacte dans la liste qu'on vient de télécharger
        target = next((b for b in bookings if b['id'] == bid), None)
        if not target:
            console.print("[red]Demande introuvable.[/red]")
            continue
            
        if target['statut'] not in ('EN_ATTENTE', 'PAYEE'):
            console.print(f"[yellow]Cette demande est déjà {target['statut']}.[/yellow]")
            continue

        console.print(Panel(
            f"Client: [bold]{target['client_nom']}[/bold]\n"
            f"Service: {target['nom_service']} | Qté: {target['quantite']}\n"
            f"RDV choisi par le client: [bold green]{target.get('rdv_date')} à {target.get('rdv_heure')}[/bold green]\n"
            f"Prix: {target['prix_total']} DH | {target.get('mode_paiement')}",
            title=f"Détails Demande #{bid}", border_style="cyan"
        ))

        action = Prompt.ask("Action", choices=["accepter", "refuser", "retour"])
        if action == "retour": 
            continue
            
        elif action == "accepter":
            contact = Prompt.ask("Contact superviseur (nom + tel)")
            if booking_dao.confirm_booking(bid, contact):
                logger.log_info(f"Entreprise {company.nom_entreprise} accepte demande #{bid}")
                console.print(Panel(
                    f"Demande acceptée !\n"
                    f"Intervention: {target.get('rdv_date')} à {target.get('rdv_heure')}\n"
                    f"Superviseur: {contact}",
                    title="Confirmation", border_style="green"
                ))
            else:
                console.print("[red]Erreur lors de la confirmation.[/red]")
                
        elif action == "refuser":
            booking_dao.update_status(bid, 'REFUSEE')
            logger.log_info(f"Entreprise {company.nom_entreprise} refuse demande #{bid}")
            console.print("[red]Demande refusée.[/red]")


def manage_catalog(company, company_dao, catalog_service):
    """Ajouter ou supprimer des services du profil de l'Entreprise."""
    while True:
        catalog = company_dao.get_catalog(company.id)
        console.rule(f"[cyan]Catalogue — {company.nom_entreprise}[/cyan]")
        
        if catalog:
            for item in catalog:
                console.print(Panel(
                    f"Service: [bold]{item.service_type.nom_service}[/bold] ({item.service_type.category})\n"
                    f"Base: {item.prix_base} DH + {item.prix_par_unite} DH/{item.unite_nom}\n"
                    f"Produits: {item.produits_inclus or 'N/A'}\n"
                    f"Durée: {item.duree_estimee or 'N/A'}\n"
                    f"{item.description_offre or ''}",
                    title=f"ID [{item.id}]", border_style="blue", width=50
                ))
        else:
            console.print("[yellow]Catalogue vide.[/yellow]")

        console.print("\n[1]  Ajouter un service")
        console.print("[2]  Supprimer un service")
        console.print("[0] ⬅ Retour")
        choice = Prompt.ask("Choix", choices=["0", "1", "2"])

        if choice == "0": 
            return
            
        elif choice == "1":
            # On liste les "Catégories Globales" disponibles
            types = company_dao.get_service_types()
            for st in types:
                console.print(f"  [{st.id}] {st.nom_service} ({st.category})")
                
            st_id = IntPrompt.ask("ID du type de service à ajouter")
            selected_type = next((t for t in types if t.id == st_id), None)
            
            if not selected_type:
                console.print("[red]Type non trouvé.[/red]"); continue
                
            prix_base = float(Prompt.ask("Prix de base (DH)"))
            prix_unite = float(Prompt.ask("Prix par unité (DH)", default="0"))
            unite = Prompt.ask("Nom de l'unité", default="panneau")
            desc = Prompt.ask("Description de l'offre (Ce que vous allez faire)")
            produits = Prompt.ask("Produits inclus dans ce tarif", default="")
            duree = Prompt.ask("Durée estimée (ex: 2h)", default="")
            
            # Création de l'objet 'Offre'
            item = CatalogItem(
                company_id=company.id, service_type=selected_type,
                prix_base=prix_base, prix_par_unite=prix_unite, unite_nom=unite,
                description_offre=desc, produits_inclus=produits, duree_estimee=duree
            )
            
            if company_dao.add_service_to_catalog(item):
                logger.log_info(f"Entreprise {company.nom_entreprise} ajoute service {selected_type.nom_service}")
                console.print("[green]Service ajouté au catalogue ![/green]")
                
        elif choice == "2":
            cat_id = IntPrompt.ask("ID du service à supprimer")
            if company_dao.remove_from_catalog(cat_id):
                logger.log_info(f"Entreprise {company.nom_entreprise} supprime catalogue #{cat_id}")
                console.print("[green]Supprimé.[/green]")


def submit_report(company, booking_dao):
    """Les rapports déclenchent le statut 'TERMINEE' et permettent au client de noter les entreprises."""
    bookings = booking_dao.get_company_bookings(company.id)
    confirmed = [b for b in bookings if b['statut'] == 'CONFIRMEE']
    
    if not confirmed:
        console.print("[yellow]Aucune intervention confirmée à rapporter.[/yellow]")
        return

    console.rule("[cyan]Soumettre un Rapport de Fin d'Intervention[/cyan]")
    for b in confirmed:
        console.print(f"  #{b['id']} — {b['client_nom']} — {b['nom_service']}")
    console.print("[0] ⬅ Retour")

    bid = IntPrompt.ask("ID de la réservation")
    if bid == 0: return
    
    avant = Prompt.ask("État (Description) AVANT intervention")
    apres = Prompt.ask("État (Description) APRÈS intervention")
    details = Prompt.ask("Résumé détaillé de vos travaux")
    
    if booking_dao.submit_report(bid, avant, apres, details):
        logger.log_info(f"Entreprise {company.nom_entreprise} soumet rapport pour #{bid}")
        console.print("[green] Rapport soumis. Service marqué TERMINÉ. Le client va pouvoir vous noter.[/green]")


def edit_company(company, company_dao):
    console.rule("[cyan] Modifier Infos Entreprise[/cyan]")
    console.print(f"Nom actuel: {company.nom_entreprise}")
    console.print(f"Description: {company.description}")
    console.print(f"Ville: {company.ville}")
    console.print(f"Tel: {company.contact_phone}")
    console.print(f"Email: {company.contact_email}")
    
    console.print("\n[dim](Appuyez simplement sur Entrée pour garder la valeur actuelle)[/dim]")
    nom = Prompt.ask("Nouveau nom", default=company.nom_entreprise)
    desc = Prompt.ask("Nouvelle description", default=company.description or "")
    ville = Prompt.ask("Nouvelle ville", default=company.ville or "")
    phone = Prompt.ask("Nouveau tel", default=company.contact_phone or "")
    email = Prompt.ask("Nouveau email", default=company.contact_email or "")
    
    if company_dao.update_company(company.id, nom, desc, ville, phone, email):
        logger.log_info(f"Entreprise {company.nom_entreprise} mise à jour.")
        console.print("[green]Informations mises à jour ![/green]")
        company.nom_entreprise = nom
        company.description = desc
        company.ville = ville


def view_subscription(company, subscription_dao):
    console.rule("[cyan]Mon Abonnement[/cyan]")
    plan = company.subscription_plan
    
    if plan:
        console.print(Panel(
            f"Plan Actuel: [bold]{plan.nom}[/bold]\n"
            f"Expire le: {company.subscription_expires_at}\n"
            f"Max services: {plan.max_services}\n"
            f"Planning Personnel: {'✅' if plan.has_scheduling else '❌'}\n"
            f"Support prioritaire: {'✅' if plan.has_priority_support else '❌'}\n"
            f"Statistiques Avancées: {'✅' if plan.has_analytics else '❌'}",
            title="Abonnement Actif", border_style="green"
        ))
    else:
        console.print("[yellow]Aucun abonnement actif.[/yellow]")

    console.print("\n[1] Renouveler / Changer de Forfait")
    console.print("[0] ⬅ Retour")
    
    if Prompt.ask("Choix", choices=["0", "1"]) == "1":
        plans = subscription_dao.get_all_plans()
        show_subscription_plans(plans)
        
        pid = IntPrompt.ask("ID du nouveau plan")
        if subscription_dao.subscribe_company(company.id, pid):
            logger.log_info(f"Entreprise {company.nom_entreprise} change abonnement vers plan {pid}")
            console.print("[green]Félicitations, Abonnement mis à jour ![/green]")


def planning_view(company, booking_dao):
    """Vue Premium: Avoir un grand tableau (Table 'rich') qui liste son agenda."""
    console.rule("[cyan]Planning Global — Vue Avancée [PRO][/cyan]")
    bookings = booking_dao.get_company_bookings(company.id)
    confirmed = [b for b in bookings if b['statut'] in ('CONFIRMEE', 'PAYEE')]
    
    if not confirmed:
        console.print("[yellow]Aucune intervention planifiée pour le moment.[/yellow]")
        return
        
    table = Table(title="Vos Prochaines Interventions Confirmees")
    table.add_column("#", style="cyan"); table.add_column("Client"); table.add_column("Service"); table.add_column("RDV", style="bold green"); table.add_column("Statut")
    
    for b in confirmed:
        table.add_row(str(b['id']), b['client_nom'], b['nom_service'], f"{b.get('rdv_date', '—')} {b.get('rdv_heure', '')}", b['statut'])
        
    console.print(table)
    Prompt.ask("[0] ⬅ Retour", choices=["0"])


# ═══════════════════════════════════════════
#  MENU ADMIN
# ═══════════════════════════════════════════
def admin_menu(user, user_dao, company_dao, booking_dao, subscription_dao, catalog_service):
    """Le saint graal de l'administrateur, un menu avec tous les privilèges."""
    while True:
        console.rule("[bold red] Administration Centrale — OptiVolt[/bold red]")
        console.print("[1] Dashboard & Statistiques Financières")
        console.print("[2] Gérer (Toutes) les Demandes")
        console.print("[3] Gérer les Comptes Utilisateurs (Bannir)")
        console.print("[4] Gérer les Entreprises (Validations)")
        console.print("[5] Gérer les Catégories de Services")
        console.print("[0] Déconnexion")
        
        choice = Prompt.ask("Choix", choices=["0", "1", "2", "3", "4", "5"])

        if choice == "0":
            logger.log_info("Admin déconnecté.")
            return

        elif choice == "1": admin_dashboard(booking_dao, subscription_dao, user_dao)
        elif choice == "2": admin_demands(booking_dao)
        elif choice == "3": admin_users(user_dao)
        elif choice == "4": admin_companies(company_dao, subscription_dao)
        elif choice == "5": admin_categories(company_dao)


def admin_dashboard(booking_dao, subscription_dao, user_dao):
    """Aggrège toutes les données pour avoir une vision globale temps-réel."""
    console.rule("[cyan]Tableau de Bord (Dashboard)[/cyan]")
    stats = booking_dao.get_stats()
    sub_rev = subscription_dao.get_subscription_revenue()
    users = user_dao.get_all_users()

    # Calculs rapides en Python 
    total_rev = sum(r['revenu_mensuel'] for r in sub_rev) if sub_rev else 0
    nb_clients = sum(1 for u in users if u['role'] == 'CLIENT')
    nb_entreprises = sum(1 for u in users if u['role'] == 'ENTREPRISE')

    console.print(Panel(
        f"[bold]Demandes (Réservations):[/bold]\n"
        f"  Total: {stats.get('total_demandes', 0)} | Terminées: {stats.get('terminees', 0)} | En attente: {stats.get('en_attente', 0)}\n"
        f"  Confirmées: {stats.get('confirmees', 0)} | Refusées: {stats.get('refusees', 0)} | Annulées client: {stats.get('annulees_client', 0)}\n\n"
        f"[bold]Chiffre d'Affaires Produit par les Entreprises:[/bold] {stats.get('chiffre_affaires', 0):.2f} DH\n\n"
        f"[bold]Revenus de nos Abonnements (Plateforme mensuel):[/bold] [green]{total_rev:.2f} DH[/green]\n"
        f"[bold]Taille de la base Utilisateurs:[/bold] {nb_clients} clients, {nb_entreprises} entreprises",
        title="Statistiques Globales", border_style="blue"
    ))

    # Tableau séparé juste pour voir quel Forfait marche le mieux financièrement
    if sub_rev:
        table = Table(title="Détail Revenus par Plan")
        table.add_column("Plan d'abonnement"); table.add_column("Nb Entreprises Abonnées"); table.add_column("Revenu Mensuel")
        for r in sub_rev:
            table.add_row(r['plan_nom'], str(r['nb_abonnes']), f"{r['revenu_mensuel']:.2f} DH")
        console.print(table)

    logger.log_info(f"Admin consulte dashboard. CA: {stats.get('chiffre_affaires', 0)}, Rev Abo: {total_rev}")
    Prompt.ask("[0] ⬅ Retour", choices=["0"])


def admin_demands(booking_dao):
    while True:
        bookings = booking_dao.get_all_bookings()
        console.rule("[cyan]Registre Complet des Opérations[/cyan]")
        table = Table()
        table.add_column("#"); table.add_column("Client"); table.add_column("Entreprise"); table.add_column("Service"); table.add_column("Statut"); table.add_column("Prix"); table.add_column("RDV")
        for b in bookings:
            table.add_row(str(b['id']), b['client_nom'], b['nom_entreprise'], b['nom_service'], b['statut'], f"{b['prix_total']} DH", str(b.get('rdv_date') or '—'))
        console.print(table)
        console.print("[0] ⬅ Retour")
        if Prompt.ask("Choix", choices=["0"]) == "0": return


def admin_users(user_dao):
    """Menu permettant de restreindre l'accès à un client qui pose problème."""
    while True:
        users = user_dao.get_all_users()
        console.rule("[cyan]Centre de Gestion des Utilisateurs[/cyan]")
        table = Table()
        table.add_column("ID"); table.add_column("Nom"); table.add_column("Email"); table.add_column("Rôle"); table.add_column("Ville"); table.add_column("Suspendu ?")
        for u in users:
            ban_status = "[red]OUI (Banni)[/red]" if u.get('is_banned') else "[green]NON (Actif)[/green]"
            table.add_row(str(u['id']), u['nom'], u['email'], u['role'], u.get('ville', '—'), ban_status)
        console.print(table)

        console.print("\n[1] Bannir un utilisateur")
        console.print("[2] Débannir un utilisateur")
        console.print("[3] Supprimer un utilisateur")
        console.print("[0] ⬅ Retour")
        choice = Prompt.ask("Choix", choices=["0", "1", "2", "3"])

        if choice == "0": return
        elif choice == "1":
            uid = IntPrompt.ask("ID de l'utilisateur à bannir")
            if user_dao.ban_user(uid):
                logger.log_info(f"Admin bannit user #{uid}")
                console.print("[green] Utilisateur banni. Il ne s'y connectera plus.[/green]")
        elif choice == "2":
            uid = IntPrompt.ask("ID de l'utilisateur à débannir")
            if user_dao.unban_user(uid):
                logger.log_info(f"Admin débannit user #{uid}")
                console.print("[green] Utilisateur débanni. Ses droits sont restaurés.[/green]")
        elif choice == "3":
            uid = IntPrompt.ask("ID")
            if user_dao.delete_user(uid):
                logger.log_info(f"Admin supprime user #{uid}")
                console.print("[green] Compte effacé de la base de données.[/green]")


def admin_companies(company_dao, subscription_dao):
    while True:
        companies = company_dao.get_all_companies_admin()
        console.rule("[cyan] Gestion Parc Entreprises[/cyan]")
        table = Table()
        table.add_column("ID", style="cyan"); table.add_column("Label"); table.add_column("Ville"); table.add_column("Compte Vérifié"); table.add_column("Forfait Actuel"); table.add_column("Expire")
        for c in companies:
            v = "[green] OUI[/green]" if c['is_verified'] else "[red] NON[/red]"
            table.add_row(str(c['id']), c['nom_entreprise'], c.get('ville','—'), v, c.get('plan_nom','—'), str(c.get('subscription_expires_at','—')))
        console.print(table)

        console.print("\n[1] Marquer une entreprise comme VÉRIFIÉE (Elle apparaîtra pour les clients)")
        console.print("[2] Bannir/Supprimer une entreprise")
        console.print("[3] Ajouter une entreprise physiquement")
        console.print("[0] ⬅ Retour")
        choice = Prompt.ask("Choix", choices=["0", "1", "2", "3"])

        if choice == "0": return
        elif choice == "1":
            cid = IntPrompt.ask("ID de l'entreprise")
            if company_dao.verify_company(cid):
                logger.log_info(f"Admin vérifie entreprise #{cid}")
                console.print("[green] Entreprise marquée comme vérifiée de confiance.[/green]")
        elif choice == "2":
            cid = IntPrompt.ask("ID de l'entreprise")
            if company_dao.delete_company(cid):
                logger.log_info(f"Admin supprime entreprise #{cid}")
                console.print("[green] Entreprise et ses catalogues radiés.[/green]")
        elif choice == "3":
            console.print("[dim]Il est préférable de créer un compte ENTREPRISE via le Menu d'Inscription normal de l'écran d'accueil.[/dim]")


def admin_categories(company_dao):
    """Permet aux admins d'ajouter de nouvelles sections de services dans lesquelles les entreprises pourront publier."""
    while True:
        types = company_dao.get_service_types()
        console.rule("[cyan] Dictionnaire des Services Autorisés[/cyan]")
        for t in types:
            console.print(f"  [{t.id}] {t.nom_service} — {t.category} — [dim]{t.description}[/dim]")

        console.print("\n[1] Créer une nouvelle branche (Catégorie)")
        console.print("[0] ⬅ Retour")
        choice = Prompt.ask("Choix", choices=["0", "1"])

        if choice == "0": return
        elif choice == "1":
            nom = Prompt.ask("Nom court du service (Ex: 'Dépannage Onduleur')")
            desc = Prompt.ask("Description détaillée")
            cat = Prompt.ask("Type", choices=["Maintenance", "Installation", "Nettoyage", "Diagnostic", "Autre"])
            if company_dao.add_service_type(nom, desc, cat):
                logger.log_info(f"Admin ajoute catégorie: {nom} ({cat})")
                console.print("[green] Catégorie validée. Les entreprises pourront s'y greffer.[/green]")


# ═══════════════════════════════════════════
#  AFFICHAGES & CONNEXION
# ═══════════════════════════════════════════
def show_subscription_plans(plans):
    """Mini-outil visuel pour afficher les offres OptiVolt aux entreprises."""
    cards = []
    for p in plans:
        features = ""
        features += f" Jusqu'à {p.max_services} services en ligne\n"
        features += f" Module Agenda Personnel: {'Inclus' if p.has_scheduling else ' Non'}\n"
        features += f" Support en Direct: {'Inclus' if p.has_priority_support else ' Non'}\n"
        features += f" Statistiques de Croissance: {'✅' if p.has_analytics else '❌'}\n"
        features += f"\n[dim]{p.description}[/dim]"
        
        cards.append(Panel(
            f"[bold green]Seulement {p.prix_mensuel} DH/mois[/bold green]\n\n{features}",
            title=f"Forfait n°[{p.id}] : {p.nom.upper()}", border_style="cyan", width=35
        ))
    console.print(Columns(cards, equal=True, expand=True))


def login_register(user_dao, subscription_dao, company_dao):
    """
    Retourne l'objet User une fois connecté avec succès. 
    Gère aussi le tunnel de vente pour l'inscription des Entreprises.
    """
    while True:
        console.print("\n[bold]1.[/bold]  Se Connecter à mon compte")
        console.print("[bold]2.[/bold] Rejoindre OptiVolt (S'inscrire)")
        console.print("[bold]0.[/bold]  Quitter OptiVolt")
        choice = Prompt.ask("Que voulez vous faire ?", choices=["0", "1", "2"])

        if choice == "0":
            return None

        elif choice == "1":
            login = Prompt.ask("Adresse Email")
            password = Prompt.ask("Mot de passe", password=True)
            user = user_dao.find_by_login(login)
            
            # Simple vérification de mot de passe (En production on utiliserait BCrypt/Hashage de Mots de Passe)
            if user and user.password == password:
                # Vérification Admin d'un compte suspendu
                if user.is_banned:
                    console.print("[red] Votre compte est suspendu suite à des réclamations. Contactez le support.[/red]")
                    logger.log_warning(f"Tentative de connexion d'un utilisateur banni: {login}")
                    continue
                    
                logger.log_info(f"Connexion réussie: {user.nom} ({user.role})")
                console.print(f"[green]Bienvenue {user.nom} ![/green]")
                return user
            else:
                logger.log_warning(f"Échec connexion: {login}")
                console.print("[red]Email ou mot de passe incorrect. Réessayez.[/red]")

        elif choice == "2":
            console.print("\n[1]  Je suis un Particulier (Local Solaire, Maison)")
            console.print("[2]  Je suis un Professionnel (Je veux proposer mes services)")
            console.print("[0] ⬅ Retour")
            
            role_choice = Prompt.ask("Type de profil", choices=["0", "1", "2"])
            if role_choice == "0": continue

            if role_choice == "1":
                # Inscription simple
                nom = Prompt.ask("Votre Nom Complet")
                email = Prompt.ask("Votre Adresse Email")
                pwd = Prompt.ask("Créez un Mot de passe fort", password=True)
                tel = Prompt.ask("Numéro de Téléphone Marocain")
                ville = Prompt.ask("Votre Ville (Ex: Casablanca, Rabat...)")
                adresse = Prompt.ask("Adresse exacte ou Quartier")
                try:
                    # On utilise la "Factory" de modèles pour construire le bon objet Python
                    user = UserFactory.create_user("CLIENT", nom, email, pwd, tel, ville=ville, adresse=adresse)
                    if user_dao.create(user):
                        logger.log_info(f"Nouveau client inscrit: {nom} ({email})")
                        console.print("[green] Super ! Bienvenue sur OptiVolt. Vous pouvez désormais vous connecter.[/green]")
                except Exception as e:
                    console.print(f"[red]Erreur lors de l'enregistrement de vos données : {e}[/red]")

            elif role_choice == "2":
                # L'inscription entreprise est beaucoup plus poussée à cause des données de facturation
                console.rule("[cyan] Espace Partenaire — Devenez Prestataire OptiVolt[/cyan]")
                nom = Prompt.ask("Label ou Nom de votre entreprise (Le plus officiel possible)")
                email = Prompt.ask("Email professionnel de contact")
                pwd = Prompt.ask("Créez votre mot de passe pour OptiVolt", password=True)
                tel = Prompt.ask("Numéro de Téléphone central pour vous joindre")
                ville = Prompt.ask("Ville de domiciliation ou d'opérations principales")
                adresse = Prompt.ask("Siège social ou adresse locale")
                description = Prompt.ask("Slogan ou petite description pour attirer les clients (Pitch)")
                contact_phone = Prompt.ask("Numéro d'Urgence à communiquer aux clients confirmés (Le numéro du chef)")
                contact_email = Prompt.ask("Email d'assistance directe", default=email)

                # Étape Commerciale de la Plateforme (Upselling)
                console.rule("[cyan] Choisissez votre Formule pour Héberger votre Catalogue chez Nous[/cyan]")
                plans = subscription_dao.get_all_plans()
                if not plans:
                    console.print("[red]Désolé, une erreur serveur empêche de charger nos offres. Contactez la plateforme par téléphone.[/red]")
                    continue
                show_subscription_plans(plans)

                plan_id = IntPrompt.ask("Tapez le Numéro ID du plan choisi (Au dessus de chaque carte)")
                selected_plan = next((p for p in plans if p.id == plan_id), None)
                if not selected_plan:
                    console.print("[red]Ce forfait n'existe pas.[/red]"); continue

                # Écran final de Caisse (Checkout / Stripe Simulateur)
                console.print(Panel(
                    f"Plan Choisi: [bold]{selected_plan.nom}[/bold]\nEngagement Mensuel: [green]{selected_plan.prix_mensuel} DH/mois[/green]",
                    title=" Validation du Contrat", border_style="yellow"
                ))
                console.print("[1]  J'accepte les CGU et je Confirme ma Souscription")
                console.print("[0]  Oh, je me retire, Annuler l'inscription")
                if Prompt.ask("Votre décision", choices=["0", "1"]) == "0":
                    continue

                console.print("[yellow] Interrogation de votre banque, veuillez patienter...[/yellow]")

                try:
                    # Transaction d'Insertion Globale réussie !
                    user = UserFactory.create_user("ENTREPRISE", nom, email, pwd, tel, ville=ville, adresse=adresse)
                    created_user = user_dao.create(user)
                    if created_user:
                        comp = Company(
                            user_id=created_user.id, nom_entreprise=nom, description=description,
                            ville=ville, contact_phone=contact_phone, contact_email=contact_email,
                            is_verified=False, subscription_plan_id=plan_id
                        )
                        company_dao.create_company(comp)
                        
                        logger.log_info(f"Nouvelle entreprise inscrite: {nom} — Plan {selected_plan.nom}")
                        console.print("[green] Paiement Validé ! Souscription actée avec succès ![/green]")
                        console.print("[dim]Note de l'Administration : Votre fiche va être étudiée par nos services sous 48h afin de valider 'is_verified'.\nVous pouvez tout de même commencer à configurer votre catalogue ![/dim]")
                except Exception as e:
                    console.print(f"[red]La caisse a rencontré une erreur technique fatale: {e}[/red]")


# ═══════════════════════════════════════════
#  CŒUR DE L'APPLICATION (BOOTSTRAP)
# ═══════════════════════════════════════════
def main():
    """Initialise la base de données, lance l'application, et route les utilisateurs."""
    print_header()

    # Paramètres importés depuis settings.py
    HOST = Config.DB_HOST
    USER = Config.DB_USER
    PASSWORD = Config.DB_PASSWORD
    DATABASE = Config.DB_NAME

    # Tentative d'ouverture du Singleton Base de Données
    try:
        db = DatabaseConnection()
        db.connect(HOST, USER, PASSWORD, DATABASE)
    except Exception as e:
        console.print(f"[bold red]Alerte Critique : Échec du pont avec le serveur Base de Données => {e}[/bold red]")
        console.print("[dim]Avez-vous bien lancé WAMP/MAMP/XAMPP et le script de Seed (db_init) ?[/dim]")
        return

    # On charge nos outils d'extraction (DAOs) et notre Logique Métier (Services)
    user_dao = UserDAO()
    company_dao = CompanyDAO()
    booking_dao = BookingDAO()
    subscription_dao = SubscriptionDAO()
    catalog_service = CatalogService()

    logger.log_info("Démarrage des Moteurs OptiVolt ")

    # La Grande Boucle qui fait tourner l'interface !
    while True:
        # Tant qu'il n'y a pas d'utilisateur connecté, on affiche l'écran d'accueil
        user = login_register(user_dao, subscription_dao, company_dao)
        
        # S"il appuie sur 0, user vaudra None. C'est l'ordre de fermeture.
        if user is None:
            console.print("[bold]Au revoir et à bientôt sur OptiVolt ! ☀️[/bold]")
            logger.log_info("Fermeture Volontaire de l'Application.")
            break

        # S'il est connecté (Client, Entreprise, ou Admin), on le téléporte sur le bon espace !
        if user.role == 'CLIENT':
            client_menu(user, catalog_service, booking_dao)
        elif user.role == 'ENTREPRISE':
            entreprise_menu(user, catalog_service, booking_dao, company_dao, subscription_dao)
        elif user.role == 'ADMIN':
            admin_menu(user, user_dao, company_dao, booking_dao, subscription_dao, catalog_service)


# Demande formelle à Python : "Si ce fichier est celui que l'utilisateur a appelé dans son Terminal, alors lance Main()"
if __name__ == "__main__":
    main()
