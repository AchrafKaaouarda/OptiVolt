import os

class Config:
    DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD","Achra-ch11")
    DB_NAME = os.getenv("DB_NAME", "ur_mdp")