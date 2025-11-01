'''
Utilisateurs créés :
- dbAdminUser: Peut gérer la structure de la base de données (collections, index), 
  mais pas les données elles-mêmes.
- readWriteUser: Peut lire et écrire des données dans toutes les collections, 
  mais ne peut pas modifier la structure de la base de données.
'''

import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure

USERS_TO_CREATE = [
    {
        "username": "dbAdminUser",
        "password": "dbAdminPassword",
        "roles": [
            {
                "role": "dbAdmin", 
                "db": "healthcare"
            }
        ]
    },
    {
        "username": "readWriteUser",
        "password": "readWritePassword",
        "roles": [
            {
                "role": "readWrite", 
                "db": "healthcare"
            }
        ]
    }
]

def create_database_users():
 
    mongo_uri = os.getenv("MONGO_URI", "mongodb://root:password@localhost:27017/admin")
    
    client = None
    try:
        print("Connexion à MongoDB en tant qu'administrateur...")
        client = MongoClient(mongo_uri)
        # Valider la connexion
        client.admin.command('ping')
        print("Connecté avec succès à MongoDB.")

        db_healthcare = client.healthcare

        for user in USERS_TO_CREATE:
            username = user["username"]
            password = user["password"]
            roles = user["roles"]
            
            print(f"--- Traitement de l'utilisateur : {username} ---")

            # Tenter de supprimer l'utilisateur s'il existe déjà pour un état propre
            try:
                db_healthcare.command("dropUser", username)
                print(f"Utilisateur existant '{username}' supprimé.")
            except OperationFailure as e:

            # Créer le nouvel utilisateur avec les rôles définis
            db_healthcare.command("createUser", username, pwd=password, roles=roles)
            print(f"Utilisateur '{username}' créé avec succès avec les rôles spécifiés.")

    except ConnectionFailure as e:
        print(f"ERREUR : Impossible de se connecter à MongoDB. Vérifiez l'URI et que le service est bien lancé. Détails : {e}")
    except OperationFailure as e:
        print(f"ERREUR : Une opération sur la base de données a échoué. Détails : {e}")
    except Exception as e:
        print(f"Une erreur inattendue est survenue : {e}")
    finally:
        if client:
            client.close()
            print("\nConnexion MongoDB fermée.")

if __name__ == "__main__":
    create_database_users()
