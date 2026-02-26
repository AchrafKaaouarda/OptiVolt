import logging
import os

"""
Un 'Logger' sert à garder une trace (un journal) de tout ce qui se passe 
dans l'application (erreurs, connexions, succès, crashs).
On utilise ici le design pattern "Singleton" pour s'assurer qu'il n'y a qu'un 
seul et unique journal ouvert dans notre programme.
"""

class Logger:
    # Attribut de classe qui va stocker notre unique instance
    _instance = None

    def __new__(cls):
        """
        Méthode appelée avant la création de l'objet.
        Si notre journal unique n'existe pas encore, on le crée.
        S'il existe déjà, on le retourne directement.
        """
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            
            # Une fois l'instance créée pour la 1ère fois, on configure ses options
            cls._instance._initialize()
            
        return cls._instance

    def _initialize(self):
        """
        Méthode interne (cachée) qui s'occupe de la configuration de 'logging'.
        """
        # On donne un nom à notre journal
        self.logger = logging.getLogger("OptiVoltLogger")
        
        # On dit au logger de tout enregistrer à partir du niveau INFO (INFO, WARNING, ERROR)
        self.logger.setLevel(logging.INFO)
        
        # logging.handlers sert à dire "OÙ" on écrit ces logs.
        # On vérifie si on n'a pas déjà ajouté notre instruction d'écriture.
        if not self.logger.handlers:
            
            # On veut écrire ces logs dans un fichier texte appelé 'optivolt.log'
            # (Ce fichier sera créé deux dossiers plus haut par rapport au logger actuel)
            chemin_log = os.path.join(os.path.dirname(__file__), '../logs/optivolt.log')
            
            file_handler = logging.FileHandler(chemin_log)
            
            # On définit le format : Date/Heure - Niveau d'urgence - Le message
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            
            # On accroche ce comportement à notre journal
            self.logger.addHandler(file_handler)

    def log_info(self, message):
        """Pour les informations normales (ex: "Nouvelle réservation confirmée")."""
        self.logger.info(message)

    def log_warning(self, message):
        """Pour les choses étranges mais pas bloquantes (ex: "Tentative de connexion avec faux mot de passe")."""
        self.logger.warning(message)

    def log_error(self, message):
        """Pour les vraies erreurs (ex: "Impossible de se connecter à la base de données")."""
        self.logger.error(message)


