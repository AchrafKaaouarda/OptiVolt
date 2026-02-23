import mysql.connector
from settings import Config

DB_CONFIG = {
    "host": Config.DB_HOST,
    "user": Config.DB_USER,
    "password": Config.DB_PASSWORD,
    "database": Config.DB_NAME
}
conn = mysql.connector.connect(**DB_CONFIG)
print("Connecté:", conn.is_connected())
conn.close()